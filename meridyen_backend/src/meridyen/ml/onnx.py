"""ONNX Runtime adapter with a safe local fallback and explicit model versioning."""
from __future__ import annotations

from pathlib import Path

from meridyen.domain.models import SignalScores
from .heuristic import HeuristicTurkishMultiTaskModel


class MultiTaskInference:
    def __init__(self, model_path: str | None = None):
        self.fallback = HeuristicTurkishMultiTaskModel()
        self.session = None
        self.tokenizer = None
        self.model_path = model_path
        if model_path and Path(model_path).is_file():
            try:
                import onnxruntime as ort
                from tokenizers import Tokenizer
                self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
                tokenizer_path = Path(model_path).with_name("tokenizer.json")
                self.tokenizer = Tokenizer.from_file(str(tokenizer_path)) if tokenizer_path.is_file() else None
            except (ImportError, RuntimeError, ValueError):
                self.session = None
                self.tokenizer = None

    def predict(self, text: str) -> SignalScores:
        if self.session is not None and self.tokenizer is not None:
            try:
                import math
                import numpy as np
                encoded = self.tokenizer.encode(text)
                ids = (encoded.ids[:256] + [0] * 256)[:256]
                mask = ([1] * min(len(encoded.ids), 256) + [0] * 256)[:256]
                inputs = {"input_ids": np.array([ids], dtype=np.int64), "attention_mask": np.array([mask], dtype=np.int64)}
                names = {node.name for node in self.session.get_inputs()}
                if "token_type_ids" in names:
                    inputs["token_type_ids"] = np.zeros((1, 256), dtype=np.int64)
                values = self.session.run(None, inputs)[0][0].tolist()
                if len(values) != 6:
                    raise ValueError("multitask ONNX output must contain six heads")
                sentiment = math.tanh(float(values[0]))
                probability = lambda v: 1 / (1 + math.exp(-float(v)))
                return SignalScores(sentiment=sentiment, toxicity=probability(values[1]), spam=probability(values[2]),
                    focus_fit=probability(values[3]), learning_fit=probability(values[4]), fun_fit=probability(values[5]),
                    confidence=.90, model_version=f"onnx:{Path(self.model_path or 'model').stem}")
            except Exception:
                # Failing closed preserves moderation availability during a malformed model rollout.
                pass
        return self.fallback.predict(text)
