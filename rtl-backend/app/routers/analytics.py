"""
Analytics Router — Production-Grade Analytics & Explainability Endpoints

Endpoints:
    GET /analytics/model-importance — Feature importance from trained model
    GET /analytics/summary          — Aggregate project & analysis statistics

Safety guarantees:
    - SQL-level aggregation only (no ORM object loading, no N+1 risk)
    - DB session try/except with rollback on failure
    - Risk level normalization (case-insensitive, unknown values ignored)
    - Distribution sum validation against total count
    - No internal stack traces exposed to clients
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.analysis import Analysis
from app.models.project import Project
from app.schemas.analytics_schema import (
    AnalyticsSummaryResponse,
    FeatureImportanceResponse,
    RiskDistribution,
)
from app.services.explainability import get_feature_importance

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# ---------------------------------------------------------------------------
# Valid risk levels (canonical title-case)
# ---------------------------------------------------------------------------

VALID_RISK_LEVELS: set[str] = {"Low", "Medium", "High"}


# ---------------------------------------------------------------------------
# DB Dependency
# ---------------------------------------------------------------------------


def get_db():
    """Yield a SQLAlchemy session; always close on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# GET /analytics/model-importance
# ---------------------------------------------------------------------------


@router.get(
    "/model-importance",
    response_model=FeatureImportanceResponse,
    summary="Feature importance from trained ML model",
    description=(
        "Returns the feature importance scores extracted from the trained "
        "RandomForest model, mapped to human-readable feature names and "
        "sorted descending by importance value."
    ),
)
def model_importance():
    """
    Delegates entirely to the explainability service which handles:
    - Lazy model loading / caching
    - Corrupt model protection
    - Feature drift detection
    - NumPy → float conversion
    """
    importance = get_feature_importance()
    return FeatureImportanceResponse(feature_importance=importance)


# ---------------------------------------------------------------------------
# GET /analytics/summary
# ---------------------------------------------------------------------------


@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
    summary="Aggregate analytics summary",
    description=(
        "Returns total project count, total analysis count, and a breakdown "
        "of analyses by risk level (Low / Medium / High)."
    ),
)
def analytics_summary(db: Session = Depends(get_db)):
    """
    Pure SQL-level aggregation — never loads full ORM objects.

    Resilience:
    - Handles empty DB (returns zeros)
    - Normalizes risk levels to title-case ("low" → "Low")
    - Ignores unknown risk levels (e.g. "CRITICAL")
    - Defaults missing categories to 0
    - Validates distribution sum == total_analyses
    - Rolls back DB session on any query failure
    """
    try:
        # --- Scalar counts (SQL-level, no object loading) ---
        total_projects: int = db.query(func.count(Project.id)).scalar() or 0
        total_analyses: int = db.query(func.count(Analysis.id)).scalar() or 0

        # --- Risk distribution via SQL GROUP BY ---
        risk_rows = (
            db.query(Analysis.risk_level, func.count(Analysis.id))
            .group_by(Analysis.risk_level)
            .all()
        )

        # Build distribution with normalization
        distribution: dict[str, int] = {"Low": 0, "Medium": 0, "High": 0}

        for raw_level, count in risk_rows:
            if raw_level is None:
                # NULL risk_level rows — skip them (don't count in distribution)
                continue

            # Normalize: strip whitespace, title-case ("low" → "Low", "HIGH" → "High")
            normalized = raw_level.strip().title()

            if normalized in VALID_RISK_LEVELS:
                distribution[normalized] += count
            else:
                # Unknown risk level (e.g. "Critical") — log and skip
                logger.warning(
                    "Ignoring unknown risk_level '%s' (%d rows) during analytics aggregation.",
                    raw_level,
                    count,
                )

        # --- Distribution sum validation ---
        distribution_sum = sum(distribution.values())
        if distribution_sum != total_analyses:
            # This means there are rows with NULL or unknown risk_level values.
            # Log for observability but do NOT fail the request — the API contract
            # states distribution covers only valid categories.
            logger.warning(
                "Analytics distribution sum (%d) does not match total_analyses (%d). "
                "%d rows have NULL or unrecognized risk_level values.",
                distribution_sum,
                total_analyses,
                total_analyses - distribution_sum,
            )

        return AnalyticsSummaryResponse(
            total_projects=total_projects,
            total_analyses=total_analyses,
            risk_distribution=RiskDistribution(**distribution),
        )

    except HTTPException:
        # Re-raise FastAPI exceptions as-is (don't wrap them)
        raise
    except Exception as exc:
        # --- Transaction state corruption guard ---
        logger.error(
            "Database error during analytics summary: %s: %s",
            type(exc).__name__,
            exc,
        )
        try:
            db.rollback()
        except Exception:
            pass  # rollback itself failed — nothing more we can do
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve analytics summary. Please try again later.",
        )
