from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import random

from app.utils.database import engine, Base, get_db
from app.models import Analysis

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- CREATE TABLES ----------------
Base.metadata.create_all(bind=engine)

# ---------------- ANALYZE ----------------
@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    risk_levels = ["Low", "Medium", "High"]
    risk = random.choice(risk_levels)
    confidence = round(random.uniform(0.6, 0.95), 2)

    new_record = Analysis(
        filename=file.filename,
        risk_level=risk,
        confidence=confidence
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return {
        "risk_level": risk,
        "confidence": confidence
    }

# ---------------- ANALYTICS ----------------
@app.get("/analytics/summary")
def get_summary(db: Session = Depends(get_db)):

    total = db.query(Analysis).count()
    high = db.query(Analysis).filter(Analysis.risk_level == "High").count()
    medium = db.query(Analysis).filter(Analysis.risk_level == "Medium").count()
    low = db.query(Analysis).filter(Analysis.risk_level == "Low").count()

    return {
        "total_analyses": total,
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low
    }