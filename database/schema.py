from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="student", nullable=False)
    reward_points = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    lost_items = relationship("LostItem", back_populates="user")
    found_items = relationship("FoundItem", back_populates="user")
    rewards = relationship("Reward", back_populates="user")


class LostItem(Base):
    __tablename__ = "lost_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    item_name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    brand = Column(String(100))
    color = Column(String(50))
    description = Column(Text)

    location = Column(String(200), nullable=False)
    lost_at = Column(DateTime, nullable=False)

    image_path = Column(String(500))
    status = Column(String(30), default="LOST", nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="lost_items")


class FoundItem(Base):
    __tablename__ = "found_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    item_name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    brand = Column(String(100))
    color = Column(String(50))
    description = Column(Text)

    location = Column(String(200), nullable=False)
    found_at = Column(DateTime, nullable=False)

    image_path = Column(String(500))
    status = Column(String(30), default="FOUND", nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="found_items")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)

    lost_item_id = Column(
        Integer,
        ForeignKey("lost_items.id"),
        nullable=False
    )

    found_item_id = Column(
        Integer,
        ForeignKey("found_items.id"),
        nullable=False
    )

    image_score = Column(Float, default=0.0)
    text_score = Column(Float, default=0.0)
    location_score = Column(Float, default=0.0)
    time_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)

    status = Column(String(30), default="PENDING", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)

    match_id = Column(
        Integer,
        ForeignKey("matches.id"),
        nullable=False
    )

    status = Column(String(30), default="PENDING", nullable=False)
    notes = Column(Text)

    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class Handover(Base):
    __tablename__ = "handovers"

    id = Column(Integer, primary_key=True, index=True)

    match_id = Column(
        Integer,
        ForeignKey("matches.id"),
        nullable=False
    )

    otp_code = Column(String(10))
    qr_token = Column(String(255), unique=True)

    status = Column(String(30), default="PENDING", nullable=False)
    handed_over_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    match_id = Column(Integer, ForeignKey("matches.id"))

    points = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="rewards")