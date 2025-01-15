import models
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from pydantic import BaseModel
from typing import List, Optional
from app.routers.auth import authenticate

router = APIRouter(prefix="/users", tags=["users"])


class UserBase(BaseModel):
    username: str
    email: str
    is_active: bool

class User(UserBase):
    id: int
    
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=User)
def create_user(user: UserBase, auth: str = Depends(authenticate), db: Session = Depends(get_db)):
    db_user = models.Usuario(username=user.username, email=user.email, is_active=user.is_active)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, auth: str = Depends(authenticate), db: Session = Depends(get_db)):
    db_user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 10, auth: str = Depends(authenticate), db: Session = Depends(get_db)):
    db_user = db.query(models.Usuario).offset(skip).limit(limit).all()
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, auth: str = Depends(authenticate), db: Session = Depends(get_db)):
    db_user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}

@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user: UserUpdate, auth: str = Depends(authenticate), db: Session = Depends(get_db)):
    db_user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.username:
        db_user.username = user.username
    if user.email:
        db_user.email = user.email
    if not user.is_active is None:
        db_user.is_active = user.is_active

    db.commit()
    db.refresh(db_user)
    return db_user