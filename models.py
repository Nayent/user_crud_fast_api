from sqlalchemy import Boolean, Column, Integer, String
from database import Base


class Usuario(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=False, index=True)
    email = Column(String, unique=False, index=True)
    is_active = Column(Boolean, default=True)