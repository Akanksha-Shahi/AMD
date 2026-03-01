from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from app.services.ml_engine import predict_risk
from app.database import get_db
from app.models.analysis import Analysis

router = APIRouter()


@router.post("/analyze/")
async def analyze(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload RTL file, run ML prediction,
    store analysis result in DB
    """

    # ✅ Read file content
    content = await file.read()
    rtl_code = content.decode("utf-8")

    # ✅ Run ML prediction
    result = predict_risk(rtl_code)

    risk = result["risk_level"]
    confidence = result["confidence"]

    # ✅ SAVE ANALYSIS TO DATABASE ⭐⭐⭐
    analysis = Analysis(
        project_id=project_id,
        risk_level=risk,
        confidence=confidence,
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # ✅ Return response (frontend expects this)
    return {
        "risk_level": risk,
        "confidence": confidence,
        "analysis_id": analysis.id,
    }