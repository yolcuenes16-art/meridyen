import re
import time

from backend.app.nlp.lexicon import (
    FOCUS_TERMS,
    FUN_TERMS,
    LEARN_TERMS,
    QUALITY_MARKERS,
    SPAM_TERMS,
    TOXIC_TERMS,
)
from backend.app.nlp.turkish import normalize_tr, stem_token, tokenize
from backend.app.schemas.analysis import ContentAnalysis

ENGINE_NAME = "tr-safety-ranking-v3"
BERT_SWAP_NOTE = (
    "Mentörlük fazında aynı girdi-çıktı sözleşmesiyle Türkçe BERT "
    "sınıflandırıcısına geçilecek; prototip gecikmeyi 150 ms altında tutar."
)


def _hit_count(text: str, stems: set[str], terms: set[str]) -> int:
    phrase_hits = sum(1 for term in terms if " " in term and term in text)
    token_hits = sum(
        1
        for term in terms
        if " " not in term and (term in text or stem_token(term) in stems)
    )
    return phrase_hits + token_hits


class ContentAnalysisService:
    engine = ENGINE_NAME

    def analyze(
        self,
        title: str,
        description: str,
        category: str = "Genel",
    ) -> ContentAnalysis:
        started = time.perf_counter()
        raw = f"{title} {description}".strip()
        text = normalize_tr(raw)
        words = tokenize(text)
        stems = {stem_token(word) for word in words}
        word_count = len(words)
        sentence_count = max(len(re.findall(r"[.!?]+", raw)), 1)

        toxic_hits = _hit_count(text, stems, TOXIC_TERMS)
        spam_hits = _hit_count(text, stems, SPAM_TERMS)
        focus_hits = _hit_count(text, stems, FOCUS_TERMS)
        learn_hits = _hit_count(text, stems, LEARN_TERMS)
        fun_hits = _hit_count(text, stems, FUN_TERMS)
        quality_hits = _hit_count(text, stems, QUALITY_MARKERS)

        shout_ratio = sum(1 for char in raw if char.isupper()) / max(len(raw), 1)
        repeated_punct = len(re.findall(r"[!?]{2,}", raw))
        url_count = len(re.findall(r"https?://|www\.", text))
        avg_word_len = sum(len(word) for word in words) / max(word_count, 1)

        safety_score = max(100 - toxic_hits * 58 - shout_ratio * 40, 0)
        spam_score = min(
            spam_hits * 22
            + repeated_punct * 12
            + url_count * 10
            + (25 if shout_ratio > 0.45 and word_count > 6 else 0)
            + (15 if word_count < 4 else 0),
            100,
        )

        quality_score = 48
        if word_count >= 12:
            quality_score += 14
        if word_count >= 28:
            quality_score += 10
        if 4.2 <= avg_word_len <= 8.5:
            quality_score += 8
        if sentence_count >= 2:
            quality_score += 8
        quality_score += min(quality_hits * 7, 21)
        if word_count >= 18 and (learn_hits >= 2 or quality_hits >= 2):
            quality_score += 10
        if re.search(r"\b\d+(?:[,.]\d+)?\b", text):
            quality_score += 4
        if any(marker in text for marker in {"kaynak", "araştırma", "veri", "örneğin"}):
            quality_score += 6
        quality_score -= min(spam_score * 0.25, 20)
        if toxic_hits:
            quality_score = min(quality_score, 10)
        quality_score = min(max(quality_score, 8), 100)

        educational_score = 40 + min(learn_hits * 9, 45)
        if normalize_tr(category) in {"egitim", "eğitim", "bilim", "teknoloji"}:
            educational_score += 10
        if "?" in raw:
            educational_score += 6
        educational_score = min(educational_score, 100)
        if word_count >= 18 and (quality_hits >= 2 or "kaynak" in text):
            educational_score = min(100, educational_score + 12)

        focus_fit = 30 + min(focus_hits * 12, 48)
        if 40 <= word_count <= 90:
            focus_fit += 10
        if toxic_hits == 0:
            focus_fit += 8
        focus_fit -= min(spam_score * 0.2, 16)
        focus_fit = min(max(focus_fit, 5), 100)

        learn_fit = 28 + min(learn_hits * 11, 52)
        learn_fit += min(educational_score * 0.12, 12)
        learn_fit = min(max(learn_fit, 5), 100)

        fun_fit = 32 + min(fun_hits * 12, 48)
        if word_count <= 40 and toxic_hits == 0:
            fun_fit += 8
        fun_fit = min(max(fun_fit, 5), 100)

        wellbeing_score = (
            safety_score * 0.34
            + quality_score * 0.22
            + (100 - spam_score) * 0.18
            + educational_score * 0.14
            + focus_fit * 0.12
        )
        wellbeing_score = min(max(wellbeing_score, 0), 100)
        if toxic_hits:
            wellbeing_score = min(wellbeing_score, 5)
        if spam_score >= 60:
            wellbeing_score = min(wellbeing_score, 20)

        overall_score = (
            wellbeing_score * 0.40
            + safety_score * 0.25
            + quality_score * 0.20
            + educational_score * 0.15
        )

        visibility_multiplier = round(0.55 + (wellbeing_score / 100) * 0.90, 3)
        if toxic_hits:
            visibility_multiplier = min(visibility_multiplier, 0.05)

        reasons: list[str] = []
        flags: list[str] = []
        if toxic_hits:
            reasons.append(
                "Zararlı dil kalıpları tespit edildi."
            )
            flags.append("toksik")
        if spam_score >= 45:
            reasons.append("Spam algılandı.")
            flags.append("spam")
        if learn_hits >= 2:
            reasons.append("Açıklayıcı anlatım, öğrenme modunda öne çıkar.")
            flags.append("öğretici")
        if focus_hits >= 2:
            reasons.append("Yapılandırılmış üslup, odak moduna uygun.")
            flags.append("odak")
        if fun_hits >= 2 and toxic_hits == 0:
            reasons.append("Hafif ton, eğlence modunu destekler.")
            flags.append("eğlence")
        if word_count >= 20 and quality_hits:
            reasons.append("Gerekçeli anlatım, kalite göstergesini güçlendirir.")
            flags.append("gerekçeli")
        if not reasons:
            reasons.append(
                "Nötr içerik; güvenlik ve mod uyumu temel sıralamayı belirler."
            )

        latency_ms = round((time.perf_counter() - started) * 1000, 2)

        return ContentAnalysis(
            quality_score=round(quality_score, 2),
            educational_score=round(educational_score, 2),
            safety_score=round(safety_score, 2),
            spam_score=round(spam_score, 2),
            wellbeing_score=round(wellbeing_score, 2),
            overall_score=round(overall_score, 2),
            focus_fit=round(focus_fit, 2),
            learn_fit=round(learn_fit, 2),
            fun_fit=round(fun_fit, 2),
            visibility_multiplier=visibility_multiplier,
            reasons=reasons[:4],
            flags=flags,
            engine=ENGINE_NAME,
            latency_ms=latency_ms,
        )


content_analysis_service = ContentAnalysisService()
