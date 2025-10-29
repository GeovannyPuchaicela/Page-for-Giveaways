from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Tabla de participantes (many-to-many)
participants = Table(
    'participants',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('giveaway_id', Integer, ForeignKey('giveaways.id'), primary_key=True),
    Column('joined_at', DateTime, default=datetime.utcnow)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    giveaways = relationship("Giveaway", back_populates="creator", foreign_keys="[Giveaway.creator_id]")
    participating_in = relationship("Giveaway", secondary=participants, back_populates="participants")
    won_giveaways = relationship("Giveaway", back_populates="winner", foreign_keys="[Giveaway.winner_id]")


class Giveaway(Base):
    __tablename__ = "giveaways"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    prize = Column(String)
    image_url = Column(String, nullable=True)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    creator_id = Column(Integer, ForeignKey("users.id"))
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    drawn_at = Column(DateTime, nullable=True)

    creator = relationship("User", back_populates="giveaways", foreign_keys=[creator_id])
    winner = relationship("User", back_populates="won_giveaways", foreign_keys=[winner_id])
    participants = relationship("User", secondary=participants, back_populates="participating_in")
