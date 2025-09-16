from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    characters = relationship("Character", back_populates="user")

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    x = Column(Integer, default=100)
    y = Column(Integer, default=100)
    level = Column(Integer, default=0)
    exp = Column(Integer, default=0)

    # Stats
    hp = Column(Integer, default=50)
    mp = Column(Integer, default=0)
    str = Column(Integer, default=0)
    int = Column(Integer, default=0)
    dex = Column(Integer, default=0)
    vit = Column(Integer, default=0)
    agi = Column(Integer, default=0)
    user = relationship("User", back_populates="characters")
