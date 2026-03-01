"""
Pydantic response schemas for the Analytics endpoints.

Provides deterministic, typed models for OpenAPI schema stability.
All fields have explicit types — no untyped 'dict' or 'Any'.
"""

from pydantic import BaseModel


class FeatureImportanceResponse(BaseModel):
    """Response schema for GET /analytics/model-importance."""

    feature_importance: dict[str, float]


class RiskDistribution(BaseModel):
    """
    Breakdown of analyses by risk level.

    Defaults to 0 for all categories so that missing DB rows
    don't produce null/missing keys in the API response.
    """

    Low: int = 0
    Medium: int = 0
    High: int = 0


class AnalyticsSummaryResponse(BaseModel):
    """Response schema for GET /analytics/summary."""

    total_projects: int
    total_analyses: int
    risk_distribution: RiskDistribution
