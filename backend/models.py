from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

Base = declarative_base()

class Memory(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    text = Column(String)
    category = Column(String) # Personal Identity, Interests & Lifestyle, Work & Learning
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    source = Column(String)
    importance_score = Column(Float)

class DecisionLog(Base):
    __tablename__ = "decision_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    prompt = Column(String)
    decision = Column(String) # saved, skipped, merged
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(String) # PERSON, COMPANY, LOCATION, etc.

class Relationship(Base):
    __tablename__ = "relationships"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("entities.id"))
    target_id = Column(Integer, ForeignKey("entities.id"))
    relation_type = Column(String) # WORKS_AT, LIVES_IN, etc.
    memory_id = Column(Integer, ForeignKey("memories.id"))

    source = relationship("Entity", foreign_keys=[source_id])
    target = relationship("Entity", foreign_keys=[target_id])
    memory = relationship("Memory")
