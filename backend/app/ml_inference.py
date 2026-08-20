"""ONNX multi-task inference for Meridyen content analysis.

Loads trained TF-IDF + Logistic Regression models exported as ONNX.
Falls back to lexicon-based heuristic if models are unavailable.
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent / "ml_models"


class MeridyenMLInference:
    """Multi-task ONNX inference with heuristic fallback."""

    def __init__(self) -> None:
        self._ready = False
        self._vectorizer = None
        self._sessions: dict = {}
        self._config: dict = {}
        self._load()

    def _load(self) -> None:
        vec_path = MODELS_DIR / "vectorizer.pkl"
        config_path = MODELS_DIR / "model_config.json"

        if not vec_path.exists() or not config_path.exists():
            logger.warning("ML models not found at %s — using heuristic fallback", MODELS_DIR)
            return

        try:
            import json
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)

            with open(vec_path, "rb") as f:
                self._vectorizer = pickle.load(f)

            import onnxruntime as ort
            for name in ("toxicity", "spam", "sentiment", "mode_fit"):
                onnx_path = MODELS_DIR / f"{name}.onnx"
                if onnx_path.exists():
                    self._sessions[name] = ort.InferenceSession(
                        str(onnx_path), providers=["CPUExecutionProvider"]
                    )

            if len(self._sessions) == 4:
                self._ready = True
                metrics = self._config.get("metrics", {})
                logger.info(
                    "ML models loaded (v%s) — toxicity=%.1f%% spam=%.1f%% sentiment=%.1f%% mode=%.1f%%",
                    self._config.get("model_version", "?"),
                    metrics.get("toxicity_acc", 0) * 100,
                    metrics.get("spam_acc", 0) * 100,
                    metrics.get("sentiment_acc", 0) * 100,
                    metrics.get("mode_acc", 0) * 100,
                )
            else:
                logger.warning("Only %d/4 ONNX models loaded — falling back to heuristic", len(self._sessions))
                self._sessions.clear()

        except Exception as exc:
            logger.warning("Failed to load ML models: %s — using heuristic fallback", exc)
            self._sessions.clear()
            self._vectorizer = None

    @property
    def ready(self) -> bool:
        return self._ready

    @property
    def model_version(self) -> str:
        return self._config.get("model_version", "heuristic-v1")

    @property
    def metrics(self) -> dict:
        return self._config.get("metrics", {})

    def predict(self, text: str) -> dict:
        """Predict toxicity, spam, sentiment, and mode fit scores.

        Returns dict with keys: toxicity, spam, sentiment, focus_fit, learn_fit, fun_fit, confidence.
        Values are floats in [0,1] (sentiment in [-1,1]).
        """
        if not self._ready:
            return self._heuristic_predict(text)

        try:
            X = self._vectorizer.transform([text])
            X_dense = X.astype(np.float32).toarray()

            # Toxicity
            _, prob_dict = self._sessions["toxicity"].run(None, {"input": X_dense})
            toxicity = float(prob_dict[0].get(1, 0))

            # Spam
            _, prob_dict = self._sessions["spam"].run(None, {"input": X_dense})
            spam = float(prob_dict[0].get(1, 0))

            # Sentiment
            _, prob_dict = self._sessions["sentiment"].run(None, {"input": X_dense})
            probs = prob_dict[0]
            sentiment = float(probs.get(1, 0)) - float(probs.get(-1, 0))

            # Mode fit
            _, prob_dict = self._sessions["mode_fit"].run(None, {"input": X_dense})
            probs = prob_dict[0]
            focus_fit = float(probs.get("focus", 0))
            fun_fit = float(probs.get("fun", 0))
            learn_fit = float(probs.get("learn", 0))

            return {
                "toxicity": max(0.0, min(1.0, toxicity)),
                "spam": max(0.0, min(1.0, spam)),
                "sentiment": max(-1.0, min(1.0, sentiment)),
                "focus_fit": max(0.0, min(1.0, focus_fit)),
                "learn_fit": max(0.0, min(1.0, learn_fit)),
                "fun_fit": max(0.0, min(1.0, fun_fit)),
                "confidence": 0.88,
            }

        except Exception as exc:
            logger.warning("ONNX inference failed: %s — falling back to heuristic", exc)
            return self._heuristic_predict(text)

    def _heuristic_predict(self, text: str) -> dict:
        """Lexicon-based fallback when ONNX models are unavailable."""
        import re
        lower = text.lower()
        tokens = set(re.findall(r"[a-zçğıöşü]+", lower))
        word_count = len(tokens)

        toxic_terms = {"aptal", "salak", "nefret", "oldur", "gebert", "hain", "igrenc",
                       "sik", "siktir", "amk", "aq", "mk", "orospu", "pic", "ibne",
                       "yarrak", "got", "kahpe", "pislik", "ezik", "pezevenk",
                       "nefret", "tehdit", "siddet", "hakaret", "irkci"}
        spam_terms = {"bedava", "cekilis", "tikla", "kazan", "kripto", "whatsapp",
                      "hemen kazan", "takip et kazan", "dm at", "link bio"}
        positive = {"tesekkur", "harika", "umut", "destek", "basari", "paylas",
                    "guzel", "iyi", "seviyorum", "mutlu", "keyifli", "eglen"}
        negative = {"kotu", "uzgun", "korku", "ofke", "stres", "kizgin", "sinir"}
        focus_terms = {"odak", "plan", "sakin", "adim", "verimli", "mola", "dikkat",
                       "pomodoro", "rutin", "checklist", "gorev", "calisma"}
        learn_terms = {"ogren", "arastra", "bilim", "model", "veri", "kanit", "ornek",
                       "kaynak", "ders", "kavram", "yontem", "analiz", "nasil", "egitim"}
        fun_terms = {"komik", "mizah", "oyun", "eglen", "gul", "meme", "film",
                     "muzik", "sohbet", "arkadas", "kahve", "yuruyus", "albume"}

        def ratio(vocab):
            return min(1.0, len(tokens & vocab) / 2)

        toxicity = ratio(toxic_terms)
        spam = ratio(spam_terms)
        links = len(re.findall(r"https?://|www\\.", lower))
        spam = min(1.0, spam + 0.15 * min(links, 3))
        sentiment = max(-1.0, min(1.0, ratio(positive) - ratio(negative) - toxicity * 0.5))

        # Fit scores: base score from content quality + keyword boost
        content_quality = min(1.0, word_count / 20)
        base_fit = 0.30 + content_quality * 0.30

        focus_fit = min(1.0, base_fit + ratio(focus_terms) * 0.5)
        learn_fit = min(1.0, base_fit + ratio(learn_terms) * 0.5)
        fun_fit = min(1.0, base_fit + ratio(fun_terms) * 0.5)

        # Positive content gets a small universal boost
        if sentiment > 0.2:
            focus_fit = min(1.0, focus_fit + 0.08)
            learn_fit = min(1.0, learn_fit + 0.08)
            fun_fit = min(1.0, fun_fit + 0.08)

        # Longer content fits more modes
        if word_count >= 10:
            focus_fit = min(1.0, focus_fit + 0.05)
            learn_fit = min(1.0, learn_fit + 0.05)

        return {
            "toxicity": toxicity,
            "spam": spam,
            "sentiment": sentiment,
            "focus_fit": focus_fit,
            "learn_fit": learn_fit,
            "fun_fit": fun_fit,
            "confidence": 0.62 if len(tokens) > 2 else 0.40,
        }


ml_inference = MeridyenMLInference()
