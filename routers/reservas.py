from datetime import date, time
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from starlette import status
from uuid import UUID

from database import SessionLocal
from routers.auth import get_current_user
from models import Reserva, Paciente, Profesional, Tratamiento

router = APIRouter(prefix="/reservas", tags=["Reservas"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ReservaRequest(BaseModel):
    paciente_id: str
    profesional_id: str
    tratamiento_id: str
    fecha: date
    hora_inicio: time
    hora_fin: time
    atencion: str
    pago: str

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def get_all(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # Perform explicit joins without modifying the models
    query = (
        db.query(
            Reserva.id,
            Paciente.id.label("paciente_id"),
            Paciente.nombre.label("paciente_nombre"),
            Paciente.apellido.label("paciente_apellido"),
            Profesional.id.label("profesional_id"),
            Profesional.nombre_completo.label("profesional_nombre_completo"),
            Tratamiento.id.label("tratamiento_id"),
            Tratamiento.nombre.label("tratamiento_nombre"),
            Tratamiento.duracion_minutos.label("tratamiento_duracion_minutos"),
            Reserva.fecha,
            Reserva.hora_inicio,
            Reserva.hora_fin,
            Reserva.atencion,
            Reserva.pago
        )
        .join(Paciente, Reserva.paciente_id == Paciente.id)
        .join(Profesional, Reserva.profesional_id == Profesional.id)
        .join(Tratamiento, Reserva.tratamiento_id == Tratamiento.id)
    )

    results = query.all()

    # Convert the result tuples into dictionaries for JSON output
    reservas = [
        {
            "id": r.id,
            "paciente_id": r.paciente_id,
            "paciente_nombre": r.paciente_nombre,
            "paciente_apellido": r.paciente_apellido,
            "profesional_id": r.profesional_id,
            "profesional_nombre_completo": r.profesional_nombre_completo,
            "tratamiento_id": r.tratamiento_id,
            "tratamiento_nombre": r.tratamiento_nombre,
            "tratamiento_duracion_minutos": r.tratamiento_duracion_minutos,
            "fecha": r.fecha,
            "hora_inicio": r.hora_inicio,
            "hora_fin": r.hora_fin,
            "atencion": r.atencion,
            "pago": r.pago
        }
        for r in results
    ]

    return reservas

@router.get("/{reserva_id}", status_code=status.HTTP_200_OK)
async def get_reserva(user: user_dependency, db: db_dependency, reserva_id: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    reserva_model = db.query(Reserva).filter(Reserva.id == UUID(reserva_id)).first()
    if reserva_model is not None:
        raise HTTPException(status_code=404, detail="Reserva not found")
    return reserva_model

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_reserva(user: user_dependency, db: db_dependency, reserva_request: ReservaRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    reserva_model = Reserva()
    reserva_model.paciente_id = UUID(reserva_request.paciente_id)
    reserva_model.profesional_id = UUID(reserva_request.profesional_id)
    reserva_model.tratamiento_id = UUID(reserva_request.tratamiento_id)
    reserva_model.fecha = reserva_request.fecha
    reserva_model.hora_inicio = reserva_request.hora_inicio
    reserva_model.hora_fin = reserva_request.hora_fin
    reserva_model.atencion = reserva_request.atencion
    reserva_model.pago = reserva_request.pago


    db.add(reserva_model)
    db.commit()

@router.put("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_reserva(user: user_dependency, db: db_dependency, reserva_request: ReservaRequest, reserva_id: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    reserva_model = db.query(Reserva).filter(Reserva.id == UUID(reserva_id)).first()
    if reserva_model is None:
        raise HTTPException(status_code=404, detail="Reserva not found")
    reserva_model.paciente_id = UUID(reserva_request.paciente_id)
    reserva_model.profesional_id = UUID(reserva_request.profesional_id)
    reserva_model.tratamiento_id = UUID(reserva_request.tratamiento_id)
    reserva_model.fecha = reserva_request.fecha
    reserva_model.hora_inicio = reserva_request.hora_inicio
    reserva_model.hora_fin = reserva_request.hora_fin
    reserva_model.atencion = reserva_request.atencion
    reserva_model.pago = reserva_request.pago

    db.add(reserva_model)
    db.commit()

@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reserva(user: user_dependency, db: db_dependency, reserva_id: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    reserva_model = db.query(Reserva).filter(Reserva.id == UUID(reserva_id)).first()
    if reserva_model is None:
        raise HTTPException(status_code=404, detail="Reserva not Found")
    
    db.query(Reserva).filter(Reserva.id == reserva_id).delete()
    db.commit()