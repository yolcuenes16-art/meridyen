import re
from dataclasses import dataclass, field


@dataclass
class ModerationResult:
    approved: bool
    toxicity_score: float = 0.0
    spam_score: float = 0.0
    category_appropriate: bool = True
    reasons: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)


LINK_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
REPEATED_CHARS = re.compile(r"(.)\1{3,}")
ALL_CAPS_THRESHOLD = 0.6
MIN_CONTENT_LENGTH = 5

CATEGORY_WHITELIST = {
    "Genel",
    "Teknoloji",
    "Egitim",
    "Saglik",
    "Spor",
    "Sanat",
    "Bilim",
    "Cevre",
    "Ekonomi",
    "Kultur",
    "Eglence",
    "Gundem",
    "Yasam",
}


class ModerationService:
    def check_content(self, content: str, category: str = "Genel") -> ModerationResult:
        reasons: list[str] = []
        flags: list[str] = []
        toxicity = 0.0
        spam = 0.0

        normalized = content.strip()
        word_count = max(len(normalized.split()), 1)
        char_count = max(len(normalized), 1)

        # Toxicity / abuse detection
        lower = normalized.lower()
        toxic_patterns = {
            "salak": 0.6, "ahmak": 0.6, "aptal": 0.5,
            "gerizekali": 0.9, "mal": 0.4, "ochastic": 0.8,
            "kufur": 0.7, "amk": 0.9, "sgt": 0.9,
        }
        for pattern, score in toxic_patterns.items():
            if pattern in lower:
                toxicity = max(toxicity, score)
                if score >= 0.7:
                    flags.append("toksik")
                    reasons.append(f"Zararli kelime algilandi: '{pattern}'.")

        # Spam detection
        link_count = len(LINK_PATTERN.findall(normalized))
        if link_count >= 3:
            spam = max(spam, 0.8)
            reasons.append(f"Cok fazla link algilandi ({link_count}).")
            flags.append("spam_cok_link")
        elif link_count >= 2:
            spam = max(spam, 0.4)
            reasons.append("Birden fazla link iceriyor.")

        # ALL CAPS
        alpha_chars = [c for c in normalized if c.isalpha()]
        if alpha_chars:
            caps_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
            if caps_ratio >= ALL_CAPS_THRESHOLD and word_count > 4:
                spam = max(spam, 0.5)
                reasons.append("Cok buyuk harf kullanimi algilandi.")
                flags.append("caps")

        # Repetitive characters
        repeated_matches = REPEATED_CHARS.findall(normalized)
        if repeated_matches:
            spam = max(spam, 0.3 + 0.1 * len(repeated_matches))
            reasons.append("Tekrarlayan karakterler algilandi.")

        # Very short content
        if word_count < 3:
            spam = max(spam, 0.2)
            reasons.append("Cok kisa icerik.")

        # Category check
        category_ok = True
        if category not in CATEGORY_WHITELIST:
            category_ok = False
            reasons.append(f"Kategori uygun degil: '{category}'.")

        approved = toxicity < 0.7 and spam < 0.7 and category_ok

        return ModerationResult(
            approved=approved,
            toxicity_score=min(toxicity, 1.0),
            spam_score=min(spam, 1.0),
            category_appropriate=category_ok,
            reasons=reasons,
            flags=flags,
        )


moderation_service = ModerationService()
