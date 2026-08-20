from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from math import exp


@dataclass(frozen=True)
class DifferentialPrivacyAggregator:
    epsilon: float = 1.0
    sensitivity: float = 1.0

    def noisy_count(self, count: int, release_key: str) -> int:
        """Deterministic two-sided geometric mechanism: reproducible, no raw identities."""
        if self.epsilon <= 0:
            raise ValueError("epsilon must be positive")
        seed = int.from_bytes(hashlib.sha256(release_key.encode()).digest()[:8], "big")
        rng = random.Random(seed)
        alpha = exp(-self.epsilon / self.sensitivity)
        magnitude = 0
        while rng.random() < alpha:
            magnitude += 1
        noise = magnitude * (-1 if rng.random() < .5 else 1)
        return max(0, count + noise)
