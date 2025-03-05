from datetime import date
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from starlette import status
from uuid import UUID

from database import SessionLocal
from routers.auth import get_current_user
from models import Profesional

router = APIRouter(prefix="/profesionales", tags=["Profesionales"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProfesionalRequest(BaseModel):
    nombre_completo: str
    tipo: str

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def get_profesionales(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Profesional).all()

@router.get("/{profesional_id}", status_code=status.HTTP_200_OK)
async def get_profesional(user: user_dependency, db: db_dependency, profesional_id: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    profesional_model = db.query(Profesional).filter(Profesional.id == UUID(profesional_id)).first()
    if profesional_model is None:
        raise HTTPException(status_code=404, detail="Profesional not found")
    return profesional_model

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_profesional(user: user_dependency, db: db_dependency, profesional_request: ProfesionalRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    profesional_model = Profesional(**profesional_request.model_dump())
    db.add(profesional_model)
    db.commit()

@router.put("/{profesional_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_profesional(user: user_dependency, db: db_dependency, profesional_request: ProfesionalRequest, profesional_id: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    profesional_model = db.query(Profesional).filter(Profesional.id == UUID(profesional_id)).first()
    if profesional_model is None:
        raise HTTPException(status_code=404, detail="Profesional not found")
    profesional_model.nombre_completo = profesional_request.nombre_completo
    profesional_model.tipo = profesional_request.tipo

    db.add(profesional_model)
    db.commit()

@router.delete("/{profesional_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profesional(user: user_dependency, db: db_dependency, profesional_id: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    profesional_model = db.query(Profesional).filter(Profesional.id == UUID(profesional_id)).first()
    if profesional_model is None:
        raise HTTPException(status_code=404, detail="Profesional not Found")
    
    db.query(Profesional).filter(Profesional.id == UUID(profesional_id)).delete()
    db.commit()