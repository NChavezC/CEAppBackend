from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette import status
from uuid import UUID

from database import SessionLocal
from models import User
from routers.auth import get_current_user

router = APIRouter(prefix="/user", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserVerification(BaseModel):
    password: str
    new_password: str

@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(User).filter(User.id == UUID(user.id)).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    return user_model

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(User).filter(User.id == UUID(user.id)).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=404, detail="Error on password change")
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)

    db.add(user_model)
    db.commit()