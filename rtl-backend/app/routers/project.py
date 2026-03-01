from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.project import Project
from app.schemas.project_schema import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(
        name=project.name,
        filename=project.filename
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project
