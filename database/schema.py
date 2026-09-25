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


# ============================================================
# USER
# ============================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(150),
        nullable=False,
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = Column(
        String(255),
        nullable=False,
    )

    role = Column(
        String(20),
        nullable=False,
        default="student",
    )

    reward_points = Column(
        Integer,
        nullable=False,
        default=0,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    lost_items = relationship(
        "LostItem",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    found_items = relationship(
        "FoundItem",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    rewards = relationship(
        "Reward",
        back_populates="user",
        cascade="all, delete-orphan",
    )


# ============================================================
# LOST ITEM
# ============================================================

class LostItem(Base):

    __tablename__ = "lost_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    item_name = Column(
        String(150),
        nullable=False,
    )

    category = Column(
        String(100),
        nullable=False,
    )

    brand = Column(
        String(100),
        nullable=True,
    )

    color = Column(
        String(100),
        nullable=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    location = Column(
        String(255),
        nullable=True,
    )

    lost_at = Column(
        DateTime,
        nullable=True,
    )

    image_path = Column(
        String(500),
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="OPEN",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    user = relationship(
        "User",
        back_populates="lost_items",
    )

    matches = relationship(
        "Match",
        back_populates="lost_item",
        cascade="all, delete-orphan",
    )


# ============================================================
# FOUND ITEM
# ============================================================

class FoundItem(Base):

    __tablename__ = "found_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    item_name = Column(
        String(150),
        nullable=False,
    )

    category = Column(
        String(100),
        nullable=False,
    )

    brand = Column(
        String(100),
        nullable=True,
    )

    color = Column(
        String(100),
        nullable=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    location = Column(
        String(255),
        nullable=True,
    )

    found_at = Column(
        DateTime,
        nullable=True,
    )

    image_path = Column(
        String(500),
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="OPEN",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    user = relationship(
        "User",
        back_populates="found_items",
    )

    matches = relationship(
        "Match",
        back_populates="found_item",
        cascade="all, delete-orphan",
    )


# ============================================================
# MATCH
# ============================================================

class Match(Base):

    __tablename__ = "matches"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    lost_item_id = Column(
        Integer,
        ForeignKey("lost_items.id"),
        nullable=False,
        index=True,
    )

    found_item_id = Column(
        Integer,
        ForeignKey("found_items.id"),
        nullable=False,
        index=True,
    )

    image_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    text_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    location_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    time_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    final_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    status = Column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    lost_item = relationship(
        "LostItem",
        back_populates="matches",
    )

    found_item = relationship(
        "FoundItem",
        back_populates="matches",
    )

    verification = relationship(
        "Verification",
        back_populates="match",
        uselist=False,
        cascade="all, delete-orphan",
    )

    handover = relationship(
        "Handover",
        back_populates="match",
        uselist=False,
        cascade="all, delete-orphan",
    )

    rewards = relationship(
        "Reward",
        back_populates="match",
        cascade="all, delete-orphan",
    )


# ============================================================
# VERIFICATION
# ============================================================

class Verification(Base):

    __tablename__ = "verifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    match_id = Column(
        Integer,
        ForeignKey("matches.id"),
        nullable=False,
        index=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    notes = Column(
        Text,
        nullable=True,
    )

    verified_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationship
    # --------------------------------------------------------

    match = relationship(
        "Match",
        back_populates="verification",
    )


# ============================================================
# HANDOVER
# ============================================================

class Handover(Base):

    __tablename__ = "handovers"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    match_id = Column(
        Integer,
        ForeignKey("matches.id"),
        nullable=False,
        index=True,
    )

    otp_code = Column(
        String(10),
        nullable=True,
    )

    qr_token = Column(
        String(255),
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    handed_over_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationship
    # --------------------------------------------------------

    match = relationship(
        "Match",
        back_populates="handover",
    )


# ============================================================
# REWARD
# ============================================================

class Reward(Base):

    __tablename__ = "rewards"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    match_id = Column(
        Integer,
        ForeignKey("matches.id"),
        nullable=True,
        index=True,
    )

    points = Column(
        Integer,
        nullable=False,
        default=0,
    )

    reason = Column(
        String(255),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    user = relationship(
        "User",
        back_populates="rewards",
    )

    match = relationship(
        "Match",
        back_populates="rewards",
    )