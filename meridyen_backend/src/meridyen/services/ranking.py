from __future__ import annotations

from datetime import datetime, timezone

from meridyen.domain.math import mode_fit, quality, rank_weight, safety, visibility_multiplier, wellbeing
from meridyen.domain.models import ContentInput, Mode, RankedContent, ScoreCard
from meridyen.ml.onnx import MultiTaskInference


class RankingService:
    def __init__(self, inference: MultiTaskInference): self.inference = inference

    def rank(self, content: list[ContentInput], mode: Mode) -> list[RankedContent]:
        now = datetime.now(timezone.utc)
        ranked = []
        for item in content:
            sig = self.inference.predict(item.text)
            age = (now - item.published_at).total_seconds() / 3600
            ws, ss, qs = wellbeing(sig), safety(sig), quality(sig)
            eligible = sig.toxicity < .65 and sig.spam < .65
            reasons = [f"refah={ws:.1f}", f"güvenlik={ss:.1f}", f"{mode.value} uyumu={mode_fit(sig, mode):.2f}"]
            card = ScoreCard(wellbeing_score=ws, safety_score=ss, quality_score=qs,
                rank_weight=rank_weight(sig, mode, item.engagement_rate, age), visibility_multiplier=visibility_multiplier(sig, item.creator_followers),
                eligibility=eligible, reasons=reasons)
            ranked.append((item, sig, card))
        ranked.sort(key=lambda row: (row[2].eligibility, row[2].rank_weight), reverse=True)
        return [RankedContent(content=i, signals=s, scorecard=c, position=n) for n, (i,s,c) in enumerate(ranked, 1)]
