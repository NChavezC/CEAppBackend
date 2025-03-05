from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from uuid import UUID

from database import SessionLocal
from routers.auth import get_current_user
from models import Tratamiento


router = APIRouter(prefix="/tratamientos", tags=["Tratamientos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TratamientoRequest(BaseModel):
    nombre: str
    descripcion: Optional[str]
    duracion_minutos: int
    precio: int

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def get_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Tratamiento).all()

@router.get("/{tratamiento_id}", status_code=status.HTTP_200_OK)
async def get_tratamiento(user: user_dependency, db: db_dependency, tratamiento_id: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    tratamiento_model = db.query(Tratamiento).filter(Tratamiento.id == UUID(tratamiento_id)).first()
    if tratamiento_model is not None:
        raise HTTPException(status_code=404, detail="Tratamiento not found")
    return tratamiento_model

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_tratamiento(user: user_dependency, db: db_dependency, tratamiento_request: TratamientoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    tratamiento_model = Tratamiento(**tratamiento_request.model_dump())
    db.add(tratamiento_model)
    db.commit()

@router.put("/{tratamiento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_tratamiento(user: user_dependency, db: db_dependency, tratamiento_request: TratamientoRequest, tratamiento_id: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    tratamiento_model = db.query(Tratamiento).filter(Tratamiento.id == UUID(tratamiento_id)).first()
    if tratamiento_model is None:
        raise HTTPException(status_code=404, detail="Tratamiento not found")
    tratamiento_model.nombre = tratamiento_request.nombre
    tratamiento_model.descripcion = tratamiento_request.descripcion
    tratamiento_model.duracion_minutos = tratamiento_request.duracion_minutos
    tratamiento_model.precio = tratamiento_request.precio

    db.add(tratamiento_model)
    db.commit()

@router.delete("/{tratamiento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tratamiento(user: user_dependency, db: db_dependency, tratamiento_id: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    tratamiento_model = db.query(Tratamiento).filter(Tratamiento.id == UUID(tratamiento_id)).first()
    if tratamiento_model is None:
        raise HTTPException(status_code=404, detail="Tratamiento not Found")
    
    db.query(Tratamiento).filter(Tratamiento.id == UUID(tratamiento_id)).delete()
    db.commit()