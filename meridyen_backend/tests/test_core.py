from datetime import datetime, timezone
from uuid import uuid4

from meridyen.domain.math import visibility_multiplier, wellbeing
from meridyen.domain.models import ContentInput, Mode
from meridyen.ml.heuristic import HeuristicTurkishMultiTaskModel
from meridyen.privacy.dp import DifferentialPrivacyAggregator
from meridyen.services.economy import CreatorEconomyService
from meridyen.services.ranking import RankingService


def item(text: str, followers: int = 10) -> ContentInput:
    return ContentInput(creator_id=uuid4(), text=text, creator_followers=followers, engagement_rate=.2, published_at=datetime.now(timezone.utc))


def test_harmful_content_is_not_reward_eligible():
    rows = RankingService(HeuristicTurkishMultiTaskModel()).rank([item("Sen aptal hain, öldür")], Mode.FOCUS)
    assert rows[0].scorecard.eligibility is False
    assert CreatorEconomyService().distribute(100, rows) == []


def test_smaller_creator_receives_larger_visibility_multiplier_at_same_quality():
    signal = HeuristicTurkishMultiTaskModel().predict("Bilim araştırma rehber plan sakin destek")
    assert wellbeing(signal) > 0
    assert visibility_multiplier(signal, 100) > visibility_multiplier(signal, 1_000_000)


def test_dp_release_is_reproducible_and_nonnegative():
    dp = DifferentialPrivacyAggregator(epsilon=1)
    assert dp.noisy_count(3, "daily.active") == dp.noisy_count(3, "daily.active")
    assert dp.noisy_count(0, "daily.active") >= 0
