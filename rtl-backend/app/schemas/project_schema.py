from pydantic import BaseModel
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    filename: str

class ProjectResponse(BaseModel):
    id: int
    name: str
    filename: str
    risk_level: str | None
    confidence: float | None
    created_at: datetime

    class Config:
        from_attributes = True
