import re

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.schemas.analysis import ContentAnalysis
from backend.app.services.analysis_service import (
    BERT_SWAP_NOTE,
    ENGINE_NAME,
    content_analysis_service,
)
from backend.app.services.ranking_service import MODE_WEIGHTS, rank_content


router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["Analysis"],
)


class AnalysisRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    category: str = "Genel"
    mode: str = "odak"


class SummarizeRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int
    word_count: int
    reading_time_minutes: float
    sentiment: str
    sentiment_score: float
    category_suggestions: list[str]


CATEGORY_KEYWORDS = {
    "Teknoloji": {"yazilim", "kod", "teknoloji", "bilgisayar", "yapay zeka", "uygulama", "web", "mobil", "donanim", "sunucu"},
    "Egitim": {"ogrenme", "egitim", "okul", "ders", "ogrenci", "kitap", "sinif", "ogretmen", "universite", "arastirma"},
    "Saglik": {"saglik", "doktor", "hastane", "ilaç", "tedavi", "egzersiz", "beslenme", "uyku", "stres", "psikoloji"},
    "Spor": {"spor", "futbol", "basketbol", "kosu", "antrenman", "mac", "takim", "lig", "oyuncu", "gol"},
    "Cevre": {"cevre", "iklim", "dogal", "yesil", "enerji", "geri donusum", "karbon", "su", "hava", "ekosistem"},
    "Bilim": {"bilim", "arastirma", "fizik", "kimya", "biyoloji", "deney", "teori", "atom", "evren", "uzay"},
    "Ekonomi": {"ekonomi", "piyasa", "yatirim", "borsa", "enflasyon", "ucret", "vergi", "uretim", "tuketim", "finans"},
    "Sanat": {"sanat", "muzik", "resim", "heykel", "fotoğraf", "sinema", "tiyatro", "edebiyat", "siir", "renk"},
    "Kultur": {"kultur", "gelenek", "tarih", "medeniyet", "dil", "dil", "turk", "osmanli", "anadolu", "festival"},
    "Eglence": {"eglence", "oyun", "film", "dizi", "muzik", "konser", "tatil", "seyahat", "yemek", "tarif"},
    "Gundem": {"gundem", "politika", "secim", "hukumet", "meclis", "yasa", "demokrasi", "ozgurluk", "hak", "adalet"},
    "Yasam": {"yasam", "ilişki", "aile", "arkadas", "mutluluk", "motivasyon", "kisisel gelisim", "zaman", "plan", "hedef"},
}


def _extractive_summary(text: str, max_chars: int = 200) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text

    sentences = re.split(r'(?<=[.!?])\s+', text)
    meaningful = [s for s in sentences if len(s.strip()) > 10]

    if not meaningful:
        return text[:max_chars].rsplit(' ', 1)[0] + '.'

    if len(meaningful) == 1:
        return meaningful[0][:max_chars]

    result = meaningful[0]
    for s in meaningful[1:]:
        candidate = f"{result} {s}"
        if len(candidate) <= max_chars:
            result = candidate
        else:
            break

    if len(result) > max_chars:
        result = meaningful[0][:max_chars].rsplit(' ', 1)[0] + '.'

    return result


def _simple_sentiment(text: str) -> tuple[str, float]:
    lower = text.lower()
    positive = {
        "guzel", "harika", "mukemmel", "memnun", "mutlu", "sevindim",
        "tebrikler", "basarili", "basari", "olumlu", "sper", "harcik",
        "keyifli", "eglenceli", "faydali", "onemli", "degerli", "guclu",
        "puan", "yetenek", "ilham", "heyecan", "cozum", "gelisme",
    }
    negative = {
        "kotu", "berbat", "uzgun", "kizgin", "sikinti", "sorun",
        "hata", "yanlis", "basarisiz", "olumsuz", "kayip", "zarar",
        "tehlike", "risk", "kaygi", "stres", "yorgun", "hasta",
        "kirik", "kirgin", "umutsuz", "bunaltici", "zor", "agir",
    }

    words = set(re.findall(r'[\w\u00C0-\u024F]+', lower))
    pos_count = len(words & positive)
    neg_count = len(words & negative)
    total = pos_count + neg_count

    if total == 0:
        return "notr", 0.0

    score = (pos_count - neg_count) / total
    if score > 0.2:
        return "olumlu", round(score, 2)
    elif score < -0.2:
        return "olumsuz", round(score, 2)
    return "notr", round(score, 2)


def _suggest_categories(text: str) -> list[str]:
    lower = text.lower()
    words = set(re.findall(r'[\w\u00C0-\u024F]+', lower))
    scores: list[tuple[str, int]] = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        overlap = len(words & keywords)
        if overlap > 0:
            scores.append((cat, overlap))
    scores.sort(key=lambda x: x[1], reverse=True)
    return [cat for cat, _ in scores[:3]]


@router.post(
    "/content",
    response_model=ContentAnalysis,
)
async def analyze_content(payload: AnalysisRequest) -> ContentAnalysis:
    return content_analysis_service.analyze(
        title=payload.title,
        description=payload.description,
        category=payload.category,
    )


@router.post("/preview")
async def analyze_and_rank(payload: AnalysisRequest):
    analysis = content_analysis_service.analyze(
        title=payload.title,
        description=payload.description,
        category=payload.category,
    )
    ranking = rank_content(analysis, payload.mode)
    return {
        "analysis": analysis,
        "ranking": ranking,
        "privacy": "Mod kullanıcı tarafından seçilir; gizli ruh hali tahmini yoktur.",
        "engine": ENGINE_NAME,
        "nlp_roadmap": BERT_SWAP_NOTE,
        "mode_weights": {
            key: [
                {"label": label, "field": field, "weight": weight}
                for label, field, weight in weights
            ]
            for key, weights in MODE_WEIGHTS.items()
        },
    }


@router.post(
    "/summarize",
    response_model=SummarizeResponse,
)
async def summarize_content(payload: SummarizeRequest) -> SummarizeResponse:
    original_length = len(payload.content)
    summary = _extractive_summary(payload.content)
    words = payload.content.split()
    word_count = len(words)
    reading_time = max(round(word_count / 200, 1), 0.1)
    sentiment_label, sentiment_score = _simple_sentiment(payload.content)
    category_suggestions = _suggest_categories(payload.content)

    return SummarizeResponse(
        summary=summary,
        original_length=original_length,
        summary_length=len(summary),
        word_count=word_count,
        reading_time_minutes=reading_time,
        sentiment=sentiment_label,
        sentiment_score=sentiment_score,
        category_suggestions=category_suggestions,
    )
