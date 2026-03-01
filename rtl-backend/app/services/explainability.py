"""
Explainability Service — Production-Grade Model Feature Importance Extraction

Provides a crash-safe, singleton-cached interface to extract and serve
feature importance values from the trained RandomForest model.

Safety guarantees:
- Lazy singleton loader: model loaded at most once per process
- Broad exception handling on load (corrupt file, version mismatch, truncation)
- Feature drift detection: validates importance count matches expected schema
- NumPy → native float conversion for JSON serialization safety
- No internal stack traces exposed to clients
"""

import logging
import os
from typing import Optional

import joblib
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "classical_model.pkl")

# Canonical feature names — must match the order used during training.
# Source of truth: app/services/ml_engine.py → feature_order
FEATURE_NAMES: list[str] = [
    "num_modules",
    "num_always_blocks",
    "num_if",
    "num_case",
    "num_loops",
    "num_assignments",
    "code_length",
]

# ---------------------------------------------------------------------------
# Singleton Model Cache
# ---------------------------------------------------------------------------

_model_cache: Optional[object] = None
_model_load_attempted: bool = False


def _load_model() -> object:
    """
    Lazy-load the trained model exactly once per process lifetime.

    On failure (corrupt file, missing file, version mismatch, wrong object type),
    logs the internal error and raises an HTTPException with a safe external message.
    The failure is sticky — once a load fails, subsequent calls will not retry
    until the process is restarted, preventing repeated disk I/O on a known-bad file.
    """
    global _model_cache, _model_load_attempted

    # Fast path — already loaded successfully
    if _model_cache is not None:
        return _model_cache

    # Sticky failure — don't retry a known-bad file within the same process
    if _model_load_attempted:
        raise HTTPException(
            status_code=500,
            detail="ML model is unavailable. Please contact the administrator.",
        )

    _model_load_attempted = True

    # --- Guard: file existence ---
    if not os.path.isfile(MODEL_PATH):
        logger.error("Model file not found at %s", MODEL_PATH)
        raise HTTPException(
            status_code=500,
            detail="ML model is unavailable. Please contact the administrator.",
        )

    # --- Attempt load ---
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as exc:
        # Catches: EOFError, ValueError, pickle.UnpicklingError,
        # sklearn version mismatch, truncated file, etc.
        logger.error(
            "Failed to load ML model from %s: %s: %s",
            MODEL_PATH,
            type(exc).__name__,
            exc,
        )
        raise HTTPException(
            status_code=500,
            detail="ML model is unavailable. Please contact the administrator.",
        )

    # --- Guard: model structure ---
    if not hasattr(model, "feature_importances_"):
        logger.error(
            "Loaded object from %s does not have 'feature_importances_' attribute. "
            "Type: %s",
            MODEL_PATH,
            type(model).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail="ML model is unavailable. Please contact the administrator.",
        )

    _model_cache = model
    logger.info("ML model loaded successfully from %s", MODEL_PATH)
    return _model_cache


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_feature_importance() -> dict[str, float]:
    """
    Return feature importance scores mapped to human-readable feature names,
    sorted descending by importance value.

    Raises:
        HTTPException 500 — if model cannot be loaded or feature schema has drifted.

    Returns:
        dict[str, float]: e.g. {"num_modules": 0.24, "num_loops": 0.19, ...}
    """
    model = _load_model()

    importances = model.feature_importances_

    # --- Feature drift guard ---
    if len(importances) != len(FEATURE_NAMES):
        logger.error(
            "Feature schema mismatch between trained model and explainability mapping. "
            "Model has %d features, expected %d.",
            len(importances),
            len(FEATURE_NAMES),
        )
        raise HTTPException(
            status_code=500,
            detail=(
                "Model feature schema mismatch detected. "
                "Please contact the administrator."
            ),
        )

    # --- Build mapping with native float conversion (prevents JSON serialization failures) ---
    importance_map: dict[str, float] = {
        name: float(value) for name, value in zip(FEATURE_NAMES, importances)
    }

    # --- Sort descending by importance ---
    sorted_importance: dict[str, float] = dict(
        sorted(importance_map.items(), key=lambda item: item[1], reverse=True)
    )

    return sorted_importance
