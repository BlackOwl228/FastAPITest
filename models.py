from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Table, Boolean, Text, Index, func

engine = create_engine('postgresql://fastapi:fastapi@localhost:5432/photos')

Base = declarative_base()

tags_of_photos = Table(
    "tags_of_photos",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photos.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    filename = Column(String(40), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    size = Column(Integer) #bytes
    mime_type = Column(String(50))

    tags = relationship("Tag", secondary=tags_of_photos, back_populates="photos")
    creator = relationship("User", back_populates="photos")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)

    photos = relationship("Photo", secondary=tags_of_photos, back_populates="tags")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    sessions = relationship("Session", back_populates="user")
    photos = relationship("Photo", back_populates="creator")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="sessions")

Index("ix_tags_of_photos_tag_id", tags_of_photos.c.tag_id)