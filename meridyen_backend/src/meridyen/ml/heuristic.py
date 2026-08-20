"""Turkish-safe deterministic fallback; ONNX is preferred when provisioned."""
from __future__ import annotations

import re

from meridyen.domain.models import SignalScores

TOXIC = {"aptal", "salak", "nefret", "öldür", "gebert", "hain", "iğrenç"}
SPAM = {"bedava", "çekiliş", "tıkla", "kazan", "kripto", "whatsapp"}
LEARN = {"araştırma", "ders", "nasıl", "rehber", "bilim", "öğren", "veri", "kaynak"}
FOCUS = {"odak", "plan", "sakin", "adım", "verimli", "mola", "dikkat"}
FUN = {"komik", "mizah", "oyun", "eğlence", "gül", "meme"}
POSITIVE = {"teşekkür", "harika", "umut", "destek", "başarı", "paylaş"}
NEGATIVE = {"kötü", "üzgün", "korku", "öfke", "stres"}


def _ratio(tokens: set[str], vocabulary: set[str]) -> float:
    return min(1.0, len(tokens & vocabulary) / 2)


class HeuristicTurkishMultiTaskModel:
    version = "heuristic-tr-multitask-1"

    def predict(self, text: str) -> SignalScores:
        lower = text.lower()
        tokens = set(re.findall(r"[a-zçğıöşü]+", lower))
        links = len(re.findall(r"https?://|www\.", lower))
        repeats = bool(re.search(r"(.)\1{5,}", lower))
        toxic, spam = _ratio(tokens, TOXIC), _ratio(tokens, SPAM)
        spam = min(1.0, spam + .15 * min(links, 3) + (.2 if repeats else 0))
        sentiment = max(-1.0, min(1.0, _ratio(tokens, POSITIVE) - _ratio(tokens, NEGATIVE) - toxic * .5))
        return SignalScores(sentiment=sentiment, toxicity=toxic, spam=spam,
            focus_fit=_ratio(tokens, FOCUS), learning_fit=_ratio(tokens, LEARN), fun_fit=_ratio(tokens, FUN),
            confidence=.62 if len(tokens) > 2 else .40, model_version=self.version)
