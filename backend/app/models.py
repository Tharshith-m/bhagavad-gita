# backend/app/models.py
from sqlalchemy import Column, Integer, Text
from .database import Base

class Slokam(Base):
    __tablename__ = "Slokams"
    id = Column(Integer, primary_key=True, index=True)
    chapter = Column(Integer, index=True)
    verse = Column(Integer, index=True)
    verse_text = Column(Text)
    translation = Column(Text)
    purport = Column(Text)
    bhavam = Column(Text)
