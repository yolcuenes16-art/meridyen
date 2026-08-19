import re

from backend.app.schemas.analysis import ContentAnalysis


class ContentAnalysisService:

    def analyze(
        self,
        title: str,
        description: str,
        category: str,
    ) -> ContentAnalysis:

        text = f"{title} {description}".strip()
        word_count = len(text.split())

        quality_score = self._quality_score(text, word_count)
        educational_score = self._educational_score(text, category)
        safety_score = self._safety_score(text)
        spam_score = self._spam_score(text)

        wellbeing_score = (
            quality_score * 0.30
            + educational_score * 0.25
            + safety_score * 0.30
            + (100 - spam_score) * 0.15
        )

        overall_score = (
            quality_score * 0.25
            + educational_score * 0.25
            + safety_score * 0.25
            + wellbeing_score * 0.25
        )

        return ContentAnalysis(
            quality_score=round(quality_score, 2),
            educational_score=round(educational_score, 2),
            safety_score=round(safety_score, 2),
            spam_score=round(spam_score, 2),
            wellbeing_score=round(wellbeing_score, 2),
            overall_score=round(overall_score, 2),
        )

    def _quality_score(self, text: str, word_count: int) -> float:
        score = 50.0

        if word_count >= 10:
            score += 15

        if word_count >= 20:
            score += 10

        if len(text) >= 100:
            score += 10

        if re.search(r"[.!?]", text):
            score += 5

        return min(score, 100)

    def _educational_score(self, text: str, category: str) -> float:
        score = 40.0

        educational_keywords = {
            "öğren",
            "eğitim",
            "bilgi",
            "yapay zeka",
            "teknoloji",
            "bilim",
            "araştır",
            "geliştir",
            "verimli",
            "öğret",
        }

        normalized_text = text.lower()

        matches = sum(
            1
            for keyword in educational_keywords
            if keyword in normalized_text
        )

        score += min(matches * 8, 50)

        if category.lower() in {"eğitim", "bilim", "teknoloji"}:
            score += 10

        return min(score, 100)

    def _safety_score(self, text: str) -> float:
        unsafe_keywords = {
            "şiddet",
            "nefret",
            "tehdit",
            "zarar ver",
            "öldür",
        }

        normalized_text = text.lower()

        matches = sum(
            1
            for keyword in unsafe_keywords
            if keyword in normalized_text
        )

        return max(100 - matches * 25, 0)

    def _spam_score(self, text: str) -> float:
        score = 0.0

        if text.count("!") >= 3:
            score += 20

        if text.isupper() and len(text) > 20:
            score += 30

        spam_keywords = {
            "bedava",
            "hemen kazan",
            "tıkla",
            "inanılmaz fırsat",
            "garanti kazanç",
        }

        normalized_text = text.lower()

        matches = sum(
            1
            for keyword in spam_keywords
            if keyword in normalized_text
        )

        score += matches * 20

        return min(score, 100)


content_analysis_service = ContentAnalysisService()