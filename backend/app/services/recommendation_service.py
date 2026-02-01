"""Service layer for recommendations feature."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from loguru import logger
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Recommendation
from app.models.recommendation_schemas import (
    AccuracyRating,
    RecommendationHistoryItem,
    RecommendationMetricsResponse,
    RecommendationResponse,
    RecommendationType,
)


class RecommendationService:
    """Business logic for recommendations."""

    @staticmethod
    def _to_response(rec: Recommendation) -> RecommendationResponse:
        return RecommendationResponse(
            id=rec.id,
            commodity_id=rec.commodity_id,
            commodity_name=rec.commodity_name,
            market_id=rec.market_id,
            market_name=rec.market_name,
            recommendation_type=rec.recommendation_type,
            confidence=rec.confidence,
            reasoning=rec.reasoning,
            current_price=rec.current_price,
            target_price=rec.target_price,
            expected_change_pct=rec.expected_change_pct,
            time_horizon=rec.time_horizon,
            created_at=rec.created_at,
            expires_at=rec.expires_at,
            model_version=rec.model_version,
            acknowledged=rec.acknowledged,
            acknowledgement_note=rec.acknowledgement_note,
            last_evaluated_at=rec.last_evaluated_at,
        )

    @classmethod
    async def get_active_recommendations(
        cls,
        session: AsyncSession,
        user_id: str,
    ) -> List[RecommendationResponse]:
        """Return active recommendations for a user."""
        logger.info(f"Fetching active recommendations for user {user_id}")
        now = datetime.utcnow()
        query = (
            select(Recommendation)
            .where(
                Recommendation.user_id == user_id,
                Recommendation.status == "ACTIVE",
                or_(Recommendation.expires_at.is_(None), Recommendation.expires_at >= now),
            )
            .order_by(desc(Recommendation.created_at))
        )
        result = await session.execute(query)
        rows = result.scalars().all()
        return [cls._to_response(rec) for rec in rows]

    @classmethod
    async def get_recommendation_by_id(
        cls,
        session: AsyncSession,
        user_id: str,
        recommendation_id: int,
    ) -> Optional[RecommendationResponse]:
        """Return a single recommendation by id."""
        logger.info(f"Fetching recommendation {recommendation_id} for user {user_id}")
        query = select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == user_id,
        )
        result = await session.execute(query)
        rec = result.scalar_one_or_none()
        return cls._to_response(rec) if rec else None

    @classmethod
    async def get_recommendation_history(
        cls,
        session: AsyncSession,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[RecommendationHistoryItem]:
        """Return recommendation history for a user."""
        logger.info(f"Fetching recommendation history for user {user_id}")
        query = (
            select(Recommendation)
            .where(
                Recommendation.user_id == user_id,
                Recommendation.outcome.is_not(None),
            )
            .order_by(desc(Recommendation.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(query)
        rows = result.scalars().all()
        return [
            RecommendationHistoryItem(
                id=rec.id,
                commodity_name=rec.commodity_name,
                recommendation_type=rec.recommendation_type,
                confidence=rec.confidence,
                created_at=rec.created_at,
                outcome=rec.outcome,
                actual_change_pct=rec.actual_change_pct,
                roi_pct=rec.roi_pct,
                note=rec.note,
            )
            for rec in rows
        ]

    @classmethod
    async def acknowledge_recommendation(
        cls,
        session: AsyncSession,
        user_id: str,
        recommendation_id: int,
        note: Optional[str] = None,
    ) -> bool:
        """Acknowledge a recommendation."""
        logger.info(
            "Acknowledging recommendation %s for user %s", recommendation_id, user_id
        )
        query = select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == user_id,
        )
        result = await session.execute(query)
        rec = result.scalar_one_or_none()
        if not rec:
            return False
        rec.acknowledged = True
        rec.acknowledgement_note = note
        rec.last_evaluated_at = datetime.utcnow()
        await session.commit()
        return True

    @classmethod
    async def record_recommendation_accuracy(
        cls,
        session: AsyncSession,
        user_id: str,
        recommendation_id: int,
        outcome: AccuracyRating,
        actual_change_pct: Optional[float] = None,
        roi_pct: Optional[float] = None,
        note: Optional[str] = None,
    ) -> bool:
        """Record accuracy of a recommendation."""
        logger.info(
            "Recording accuracy for recommendation %s user %s outcome %s",
            recommendation_id,
            user_id,
            outcome,
        )
        query = select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == user_id,
        )
        result = await session.execute(query)
        rec = result.scalar_one_or_none()
        if not rec:
            return False
        rec.outcome = outcome.value
        rec.actual_change_pct = actual_change_pct
        rec.roi_pct = roi_pct
        rec.note = note
        rec.last_evaluated_at = datetime.utcnow()
        rec.status = "ARCHIVED"
        await session.commit()
        return True

    @classmethod
    async def get_accuracy_metrics(
        cls,
        session: AsyncSession,
        user_id: str,
    ) -> RecommendationMetricsResponse:
        """Return summary metrics for recommendations."""
        logger.info(f"Fetching recommendation metrics for user {user_id}")
        query = select(Recommendation).where(
            Recommendation.user_id == user_id,
            Recommendation.outcome.is_not(None),
        )
        result = await session.execute(query)
        history = result.scalars().all()

        def _outcome_value(value: Optional[object]) -> str:
            if isinstance(value, AccuracyRating):
                return value.value
            return str(value) if value is not None else ""

        correct = sum(
            1 for item in history if _outcome_value(item.outcome) == AccuracyRating.CORRECT.value
        )
        incorrect = sum(
            1 for item in history if _outcome_value(item.outcome) == AccuracyRating.INCORRECT.value
        )
        partial = sum(
            1 for item in history if _outcome_value(item.outcome) == AccuracyRating.PARTIAL.value
        )
        total = len(history)
        accuracy_rate = correct / total if total else 0.0
        avg_roi = sum(item.roi_pct or 0 for item in history) / total if total else 0.0

        by_type_totals: dict[str, int] = {}
        by_type_correct: dict[str, int] = {}
        for item in history:
            rec_type = item.recommendation_type
            rec_type_value = rec_type.value if isinstance(rec_type, RecommendationType) else str(rec_type)
            by_type_totals[rec_type_value] = by_type_totals.get(rec_type_value, 0) + 1
            if _outcome_value(item.outcome) == AccuracyRating.CORRECT.value:
                by_type_correct[rec_type_value] = by_type_correct.get(rec_type_value, 0) + 1

        by_type_accuracy = {
            rec_type: (by_type_correct.get(rec_type, 0) / total_count)
            for rec_type, total_count in by_type_totals.items()
            if total_count
        }

        return RecommendationMetricsResponse(
            total_recommendations=total,
            correct_count=correct,
            incorrect_count=incorrect,
            partial_count=partial,
            accuracy_rate=round(accuracy_rate, 2),
            average_roi_pct=round(avg_roi, 2),
            by_type_accuracy=by_type_accuracy,
            generated_at=datetime.utcnow(),
        )
