from backend.app.schemas.post import RankBreakdownItem

MODE_WEIGHTS = {
    "odak": (
        ("Refah", "wellbeing_score", 0.36),
        ("Güvenlik", "safety_score", 0.24),
        ("Odak uyumu", "focus_fit", 0.28),
        ("Kalite", "quality_score", 0.12),
    ),
    "ogrenme": (
        ("Eğiticilik", "educational_score", 0.34),
        ("Öğrenme uyumu", "learn_fit", 0.28),
        ("Refah", "wellbeing_score", 0.22),
        ("Güvenlik", "safety_score", 0.16),
    ),
    "eglence": (
        ("Eğlence uyumu", "fun_fit", 0.34),
        ("Refah", "wellbeing_score", 0.24),
        ("Kalite", "quality_score", 0.22),
        ("Güvenlik", "safety_score", 0.20),
    ),
}

MODE_LABELS = {
    "odak": "Odak",
    "ogrenme": "Öğrenme",
    "eglence": "Eğlence",
}


def normalize_mode(mode: str | None) -> str:
    value = (mode or "odak").strip().lower()
    aliases = {
        "focus": "odak",
        "learn": "ogrenme",
        "öğrenme": "ogrenme",
        "fun": "eglence",
        "eğlence": "eglence",
    }
    value = aliases.get(value, value)
    if value not in MODE_WEIGHTS:
        return "odak"
    return value


def rank_content(analysis_like: object, mode: str) -> dict:
    mode_key = normalize_mode(mode)
    weights = MODE_WEIGHTS[mode_key]
    spam_score = float(getattr(analysis_like, "spam_score", 0))

    breakdown: list[RankBreakdownItem] = []
    rank_score = 0.0

    for label, field, weight in weights:
        value = float(getattr(analysis_like, field, 0))
        contribution = value * weight
        rank_score += contribution
        breakdown.append(
            RankBreakdownItem(
                label=label,
                weight=weight,
                value=round(value, 2),
                contribution=round(contribution, 2),
            )
        )

    rank_score -= min(spam_score * 0.35, 28)
    if not bool(getattr(analysis_like, "is_publishable", True)):
        rank_score = min(rank_score, 10)
    rank_score = min(max(rank_score, 0), 100)

    reasons = list(getattr(analysis_like, "reasons", []) or [])
    mode_fit_field = {
        "odak": "focus_fit",
        "ogrenme": "learn_fit",
        "eglence": "fun_fit",
    }[mode_key]
    mode_fit = float(getattr(analysis_like, mode_fit_field, 0))
    reasons = [
        f"Mod uyumu: {mode_fit:.0f}/100.",
        *reasons,
    ]

    return {
        "rank_score": round(rank_score, 2),
        "rank_breakdown": breakdown,
        "rank_reasons": reasons[:5],
        "active_mode": mode_key,
    }
