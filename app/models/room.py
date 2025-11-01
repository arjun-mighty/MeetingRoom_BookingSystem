from sqlalchemy import Column, Integer, String
from app.db import Base

class Room(Base):
    """rooms table"""
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    capacity = Column(Integer, nullable=False, default=1)


