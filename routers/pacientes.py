from datetime import date
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from starlette import status
from uuid import UUID

from database import SessionLocal
from routers.auth import get_current_user
from models import Paciente

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PacienteRequest(BaseModel):
    nombre: str
    apellido: str
    email: Optional[EmailStr]
    telefono: str
    fecha_nacimiento: Optional[date]

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def get_pacientes(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Paciente).all()

@router.get("/{paciente_id}", status_code=status.HTTP_200_OK)
async def get_paciente(user: user_dependency, db: db_dependency, paciente_id: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    paciente_model = db.query(Paciente).filter(Paciente.id == UUID(paciente_id)).first()
    if paciente_model is None:
        raise HTTPException(status_code=404, detail="Paciente not found")
    return paciente_model

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_paciente(user: user_dependency, db: db_dependency, paciente_request: PacienteRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    paciente_model = Paciente(**paciente_request.model_dump())

    db.add(paciente_model)
    db.commit()

@router.put("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_paciente(user: user_dependency, db: db_dependency, paciente_request: PacienteRequest, paciente_id: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    paciente_model = db.query(Paciente).filter(Paciente.id == UUID(paciente_id)).first()
    if paciente_model is None:
        raise HTTPException(status_code=404, detail="Paciente not found")
    paciente_model.nombre = paciente_request.nombre
    paciente_model.apellido = paciente_request.apellido
    paciente_model.email = paciente_request.email
    paciente_model.fecha_nacimiento = paciente_request.fecha_nacimiento

    db.add(paciente_model)
    db.commit()

@router.delete("/paciente/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paciente(user: user_dependency, db: db_dependency, paciente_id: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    paciente_model = db.query(Paciente).filter(Paciente.id == UUID(paciente_id)).first()
    if paciente_model is None:
        raise HTTPException(status_code=404, detail="Paciente not Found")
    
    db.query(Paciente).filter(Paciente.id == UUID(paciente_id)).delete()
    db.commit()