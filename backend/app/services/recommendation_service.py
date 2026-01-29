"""Service layer for recommendations feature."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recommendation_schemas import (
    AccuracyRating,
    ConfidenceLevel,
    RecommendationHistoryItem,
    RecommendationMetricsResponse,
    RecommendationResponse,
    RecommendationType,
    TimeHorizon,
)


class RecommendationService:
    """Business logic for recommendations."""

    @staticmethod
    def _mock_active_recommendations() -> List[RecommendationResponse]:
        now = datetime.now(tz=timezone.utc)
        return [
            RecommendationResponse(
                id=101,
                commodity_id=1,
                commodity_name="Wheat",
                market_id=11,
                market_name="Delhi",
                recommendation_type=RecommendationType.BUY,
                confidence=ConfidenceLevel.HIGH,
                reasoning="Seasonal demand spike and tightening supply.",
                current_price=2120.5,
                target_price=2285.0,
                expected_change_pct=7.8,
                time_horizon=TimeHorizon.SHORT_TERM,
                created_at=now - timedelta(days=1),
                expires_at=now + timedelta(days=10),
                model_version="v1.0",
                acknowledged=False,
                last_evaluated_at=now - timedelta(hours=3),
            ),
            RecommendationResponse(
                id=102,
                commodity_id=4,
                commodity_name="Onion",
                market_id=14,
                market_name="Mumbai",
                recommendation_type=RecommendationType.STOCK_UP,
                confidence=ConfidenceLevel.MEDIUM,
                reasoning="Transport disruptions expected; buffer stock advised.",
                current_price=1650.0,
                target_price=1780.0,
                expected_change_pct=4.2,
                time_horizon=TimeHorizon.MID_TERM,
                created_at=now - timedelta(hours=6),
                expires_at=now + timedelta(days=14),
                model_version="v1.0",
                acknowledged=True,
                acknowledgement_note="Noted. Aligning procurement.",
                last_evaluated_at=now - timedelta(hours=1),
            ),
        ]

    @staticmethod
    def _mock_history() -> List[RecommendationHistoryItem]:
        now = datetime.now(tz=timezone.utc)
        return [
            RecommendationHistoryItem(
                id=88,
                commodity_name="Tomato",
                recommendation_type=RecommendationType.SELL,
                confidence=ConfidenceLevel.HIGH,
                created_at=now - timedelta(days=14),
                outcome=AccuracyRating.CORRECT,
                actual_change_pct=-6.4,
                roi_pct=5.2,
                note="Price drop matched forecast.",
            ),
            RecommendationHistoryItem(
                id=89,
                commodity_name="Potato",
                recommendation_type=RecommendationType.HOLD,
                confidence=ConfidenceLevel.MEDIUM,
                created_at=now - timedelta(days=10),
                outcome=AccuracyRating.PARTIAL,
                actual_change_pct=1.1,
                roi_pct=0.6,
                note="Minor change, within neutral band.",
            ),
            RecommendationHistoryItem(
                id=90,
                commodity_name="Wheat",
                recommendation_type=RecommendationType.BUY,
                confidence=ConfidenceLevel.LOW,
                created_at=now - timedelta(days=8),
                outcome=AccuracyRating.INCORRECT,
                actual_change_pct=-2.8,
                roi_pct=-1.4,
                note="Unexpected supply release.",
            ),
        ]

    @classmethod
    async def get_active_recommendations(
        cls,
        session: AsyncSession,
        user_id: str,
    ) -> List[RecommendationResponse]:
        """Return active recommendations for a user."""
        logger.info(f"Fetching active recommendations for user {user_id}")
        return cls._mock_active_recommendations()

    @classmethod
    async def get_recommendation_by_id(
        cls,
        session: AsyncSession,
        user_id: str,
        recommendation_id: int,
    ) -> Optional[RecommendationResponse]:
        """Return a single recommendation by id."""
        logger.info(f"Fetching recommendation {recommendation_id} for user {user_id}")
        for rec in cls._mock_active_recommendations():
            if rec.id == recommendation_id:
                return rec
        return None

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
        history = cls._mock_history()
        return history[offset : offset + limit]

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
        return True

    @classmethod
    async def get_accuracy_metrics(
        cls,
        session: AsyncSession,
        user_id: str,
    ) -> RecommendationMetricsResponse:
        """Return summary metrics for recommendations."""
        logger.info(f"Fetching recommendation metrics for user {user_id}")
        history = cls._mock_history()
        correct = sum(1 for item in history if item.outcome == AccuracyRating.CORRECT)
        incorrect = sum(
            1 for item in history if item.outcome == AccuracyRating.INCORRECT
        )
        partial = sum(1 for item in history if item.outcome == AccuracyRating.PARTIAL)
        total = len(history)
        accuracy_rate = correct / total if total else 0.0
        avg_roi = (
            sum(item.roi_pct or 0 for item in history) / total if total else 0.0
        )

        return RecommendationMetricsResponse(
            total_recommendations=total,
            correct_count=correct,
            incorrect_count=incorrect,
            partial_count=partial,
            accuracy_rate=round(accuracy_rate, 2),
            average_roi_pct=round(avg_roi, 2),
            by_type_accuracy={
                RecommendationType.BUY.value: 0.5,
                RecommendationType.SELL.value: 1.0,
                RecommendationType.HOLD.value: 0.5,
                RecommendationType.STOCK_UP.value: 0.75,
                RecommendationType.STOCK_DOWN.value: 0.6,
            },
            generated_at=datetime.now(tz=timezone.utc),
        )
