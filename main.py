from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, pacientes, users, profesionales, tratamientos, reservas
import models
from database import engine

app = FastAPI()

origins = ["*"]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(pacientes.router)
app.include_router(users.router)
app.include_router(profesionales.router)
app.include_router(tratamientos.router)
app.include_router(reservas.router)