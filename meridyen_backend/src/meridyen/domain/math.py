"""Deterministic, bounded welfare and fair-distribution equations."""
from __future__ import annotations

from math import exp, log1p

from .models import Mode, SignalScores


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return min(high, max(low, value))


def wellbeing(signals: SignalScores) -> float:
    """Ws=100*sigma(1.65s+1.15m-2.8t-1.9p), safe bounded score."""
    mode_fit = (signals.focus_fit + signals.learning_fit + signals.fun_fit) / 3
    latent = 1.65 * signals.sentiment + 1.15 * mode_fit - 2.8 * signals.toxicity - 1.9 * signals.spam
    return round(100 / (1 + exp(-latent)), 3)


def mode_fit(signals: SignalScores, mode: Mode) -> float:
    return {Mode.FOCUS: signals.focus_fit, Mode.LEARN: signals.learning_fit, Mode.FUN: signals.fun_fit}[mode]


def safety(signals: SignalScores) -> float:
    return round(100 * (1 - max(signals.toxicity, signals.spam)), 3)


def quality(signals: SignalScores) -> float:
    return round(100 * clamp(.55 * signals.confidence + .25 * (1 - signals.spam) + .20 * (1 - signals.toxicity)), 3)


def rank_weight(signals: SignalScores, mode: Mode, engagement_rate: float, hours_old: float, novelty: float = 1.0) -> float:
    """Rw=100*(.44Ws+.24M+.14Q+.10N+.08E)*freshness, all normalized."""
    ws = wellbeing(signals) / 100
    m = mode_fit(signals, mode)
    q = quality(signals) / 100
    freshness = exp(-max(hours_old, 0) / 36)
    score = .44 * ws + .24 * m + .14 * q + .10 * clamp(novelty) + .08 * clamp(engagement_rate)
    return round(100 * score * (.65 + .35 * freshness), 3)


def visibility_multiplier(signals: SignalScores, creator_followers: int) -> float:
    """Vm=clip(0.7+0.9Ws+0.3Q-0.4log(1+followers)/log(1e6),0.5,1.6)."""
    ws, q = wellbeing(signals) / 100, quality(signals) / 100
    size_penalty = log1p(creator_followers) / log1p(1_000_000)
    return round(clamp(.7 + .9 * ws + .3 * q - .4 * size_penalty, .5, 1.6), 4)
