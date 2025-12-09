from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Table, Boolean, Text, Index, func, UniqueConstraint

engine = create_engine('postgresql://fastapi:fastapi@localhost:5432/photos')
Base = declarative_base()

tags_of_photos = Table(
    "tags_of_photos",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photos.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
Index("ix_tags_of_photos_tag_id", tags_of_photos.c.tag_id)

likes = Table(
    "likes",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photos.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime(timezone=True), default=func.now())
)
#Index("ix_likes_user_id", likes.c.user_id)

album_photos = Table(
    'album_photos', Base.metadata,
    Column('album_id', ForeignKey('albums.id', ondelete="CASCADE"), primary_key=True),
    Column('photo_id', ForeignKey('photos.id', ondelete="CASCADE"), primary_key=True)
)
#Index("ix_album_photos_photo_id", album_photos.c.photo_id)

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    filename = Column(String(40), unique=True, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_public = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    size = Column(Integer) #bytes
    mime_type = Column(String(50))

    tags = relationship("Tag", secondary=tags_of_photos, back_populates="photos")
    creator = relationship("User", back_populates="photos")
    albums = relationship("Album", secondary=album_photos, back_populates="photos")
    liked_by = relationship("User", secondary=likes, back_populates="likes")

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
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    sessions = relationship("UserSession", back_populates="user")
    photos = relationship("Photo", back_populates="creator")
    albums = relationship("Album", back_populates="creator")
    likes = relationship("Photo", secondary=likes, back_populates="liked_by")

class UserSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(64), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="sessions")

class Album(Base):
    __tablename__ = "albums"
    __table_args__ = (UniqueConstraint('creator_id', 'title', name='uq_user_album_title'),)

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_public = Column(Boolean, default=True, nullable=False)
    position = Column(Integer, default=1, nullable=False) #ХУЕТА ПОЛНАЯ
    photo_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("User", back_populates="albums")
    photos = relationship("Photo", secondary=album_photos, back_populates="albums")