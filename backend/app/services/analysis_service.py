import re
import time

from backend.app.ml_inference import ml_inference
from backend.app.nlp.turkish import normalize_tr, stem_token, tokenize
from backend.app.schemas.analysis import ContentAnalysis

ENGINE_NAME = ml_inference.model_version if ml_inference.ready else "heuristic-v1"
BERT_SWAP_NOTE = (
    "Eğitilmiş TF-IDF + Logistic Regression modeli aktif. "
    "Mentörlük fazında Türkçe BERT sınıflandırıcısına geçilecek."
)


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
        word_count = len(words)
        sentence_count = max(len(re.findall(r"[.!?]+", raw)), 1)

        # ML model predictions
        ml = ml_inference.predict(raw)
        ml_toxicity = ml["toxicity"]
        ml_spam = ml["spam"]
        ml_sentiment = ml["sentiment"]
        ml_focus = ml["focus_fit"]
        ml_learn = ml["learn_fit"]
        ml_fun = ml["fun_fit"]
        ml_confidence = ml["confidence"]

        # Text statistics (still useful for quality derivation)
        shout_ratio = sum(1 for char in raw if char.isupper()) / max(len(raw), 1)
        repeated_punct = len(re.findall(r"[!?]{2,}", raw))
        avg_word_len = sum(len(word) for word in words) / max(word_count, 1)

        # ── Derived scores from ML signals + text stats ──

        # Safety: primarily driven by ML toxicity + spam, with text stat adjustments
        safety_score = 100 * (1 - max(ml_toxicity, ml_spam))
        safety_score -= shout_ratio * 15
        safety_score = min(max(safety_score, 0), 100)

        # Spam score: ML prediction + signal boosting
        spam_score = ml_spam * 100
        spam_score += repeated_punct * 8
        if shout_ratio > 0.45 and word_count > 6:
            spam_score += 15
        if word_count < 4:
            spam_score += 10
        spam_score = min(spam_score, 100)

        # Quality: ML confidence + text structure signals
        quality_score = 35 + ml_confidence * 30
        if word_count >= 12:
            quality_score += 10
        if word_count >= 28:
            quality_score += 8
        if 4.2 <= avg_word_len <= 8.5:
            quality_score += 6
        if sentence_count >= 2:
            quality_score += 6
        if re.search(r"\b\d+(?:[,.]\d+)?\b", text):
            quality_score += 3
        if any(marker in text for marker in {"kaynak", "araştırma", "veri", "örneğin"}):
            quality_score += 5
        # Sentiment boost: positive content tends to be higher quality
        if ml_sentiment > 0.2:
            quality_score += 5
        quality_score -= min(spam_score * 0.2, 18)
        if ml_toxicity > 0.3:
            quality_score = min(quality_score, 12)
        quality_score = min(max(quality_score, 5), 100)

        # Educational score: ML learn_fit + text signals
        educational_score = 30 + ml_learn * 55
        if normalize_tr(category) in {"egitim", "egitim", "bilim", "teknoloji"}:
            educational_score += 8
        if "?" in raw:
            educational_score += 5
        if word_count >= 18 and ml_learn > 0.3:
            educational_score += 10
        educational_score = min(max(educational_score, 5), 100)

        # Mode fit scores from ML (boosted base for meaningful scores)
        focus_fit = 25 + ml_focus * 70
        if 40 <= word_count <= 90:
            focus_fit += 5
        if ml_toxicity < 0.1:
            focus_fit += 5
        focus_fit -= min(spam_score * 0.15, 12)
        focus_fit = min(max(focus_fit, 15), 100)

        learn_fit = 25 + ml_learn * 70
        learn_fit += min(educational_score * 0.08, 8)
        learn_fit = min(max(learn_fit, 15), 100)

        fun_fit = 25 + ml_fun * 70
        if word_count <= 40 and ml_toxicity < 0.1:
            fun_fit += 5
        fun_fit = min(max(fun_fit, 15), 100)

        # Wellbeing: weighted composite
        wellbeing_score = (
            safety_score * 0.34
            + quality_score * 0.22
            + (100 - spam_score) * 0.18
            + educational_score * 0.14
            + focus_fit * 0.12
        )
        wellbeing_score = min(max(wellbeing_score, 0), 100)
        if ml_toxicity > 0.3:
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
        if ml_toxicity > 0.3:
            visibility_multiplier = min(visibility_multiplier, 0.05)

        # Reasons and flags
        reasons: list[str] = []
        flags: list[str] = []
        if ml_toxicity > 0.3:
            reasons.append("Zararlı dil kalıpları tespit edildi.")
            flags.append("toksik")
        if spam_score >= 45:
            reasons.append("Spam algılandı.")
            flags.append("spam")
        if ml_learn > 0.4:
            reasons.append("Açıklayıcı anlatım, öğrenme modunda öne çıkar.")
            flags.append("ogretici")
        if ml_focus > 0.4:
            reasons.append("Yapılandırılmış üslup, odak moduna uygun.")
            flags.append("odak")
        if ml_fun > 0.4 and ml_toxicity < 0.1:
            reasons.append("Hafif ton, eğlence modunu destekler.")
            flags.append("eglence")
        if word_count >= 20 and ml_sentiment > 0.1:
            reasons.append("Gerekçeli anlatım, kalite göstergesini güçlendirir.")
            flags.append("gerekceli")
        if ml_sentiment > 0.4:
            reasons.append("Olumlu ton, genel dengeyi destekler.")
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
