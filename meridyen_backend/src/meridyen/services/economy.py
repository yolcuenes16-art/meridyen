from __future__ import annotations

from meridyen.domain.models import RankedContent, RewardLedgerEntry


class CreatorEconomyService:
    commission_rate = .12

    def distribute(self, pool_amount: float, ranked: list[RankedContent]) -> list[RewardLedgerEntry]:
        eligible = [x for x in ranked if x.scorecard.eligibility and x.content.opted_in_creator_rewards]
        denominator = sum(x.scorecard.visibility_multiplier * max(.01, x.content.engagement_rate) for x in eligible)
        if pool_amount < 0: raise ValueError("pool_amount cannot be negative")
        if not denominator: return []
        entries = []
        for item in eligible:
            share = pool_amount * (item.scorecard.visibility_multiplier * max(.01, item.content.engagement_rate)) / denominator
            commission = round(share * self.commission_rate, 2)
            entries.append(RewardLedgerEntry(content_id=item.content.content_id, creator_id=item.content.creator_id,
                gross_pool_share=round(share, 2), platform_commission=commission, creator_payout=round(share-commission, 2),
                visibility_multiplier=item.scorecard.visibility_multiplier))
        return entries
