from database import Base
from sqlalchemy import Column, Integer, DECIMAL, String, Boolean, ForeignKey, Enum, TIMESTAMP, Date, Time, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum("admin", "recepcionista", name="user_roles"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Profesional(Base):
    __tablename__ = "profesionales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_completo = Column(String, nullable=False)
    tipo = Column(Enum("enfermera", "ayudante", name="profesional_tipo"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Tratamiento(Base):
    __tablename__ = "tratamientos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String, unique=True, nullable=False)
    descripcion = Column(String)
    duracion_minutos = Column(Integer, nullable=False)
    precio = Column(DECIMAL(10,2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    email = Column(String, unique=True)
    telefono = Column(String, nullable=False)
    fecha_nacimiento = Column(Date)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    atencion = Column(Enum("agendada", "confirmada", "espera", "atendida", name="reservas_atencion"), nullable=False, default="confirmada")
    pago = Column(Enum("listo", "pendiente", name="reservas_pago"), nullable=False, default="pendiente")
    created_at = Column(TIMESTAMP, server_default=func.now())

    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False)
    profesional_id = Column(UUID(as_uuid=True), ForeignKey("profesionales.id", ondelete="CASCADE"), nullable=False)
    tratamiento_id = Column(UUID(as_uuid=True), ForeignKey("tratamientos.id", ondelete="CASCADE"), nullable=False)
