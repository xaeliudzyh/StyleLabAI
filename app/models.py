from sqlalchemy import (
    Column, Integer, Enum, Boolean, String, DateTime, func, ForeignKey, ARRAY
)
from sqlalchemy.orm import relationship
from .db import Base
import enum


# ─── ENUMs (из Google Forms) ──────────────────────────────────────────────────
class AgeGroup(str, enum.Enum):
    age_0_12  = "0-12"
    age_13_18 = "13-18"
    age_19_28 = "19-28"
    age_29_45 = "29-45"
    age_46_plus = "46+"

class FaceShape(str, enum.Enum):
    oval        = "oval"
    round       = "round"
    square      = "square"
    diamond     = "diamond"
    rectangular = "rectangular"
    triangular  = "triangular"

class HairTexture(str, enum.Enum):
    straight = "straight"
    wavy     = "wavy"
    curly    = "curly"
    spiral   = "spiral"

class HairDensity(str, enum.Enum):
    low    = "low"
    medium = "medium"
    high   = "high"

class HairLength(str, enum.Enum):
    short  = "short"
    medium = "medium"
    long   = "long"

class HairColor(str, enum.Enum):
    blond   = "blond"
    chestnut = "chestnut"   # «шатен»
    brunette = "brunette"
    red     = "red"
    grey    = "grey"
    other   = "other"

class StylingTime(str, enum.Enum):
    none        = "0"
    up_to_10    = "1-10"
    up_to_30    = "10-30"
    over_30     = "30+"

class Lifestyle(str, enum.Enum):
    active     = "active"
    business   = "business"
    calm       = "calm"
    creative   = "creative"

class StyleCharacter(str, enum.Enum):
    experimental = "experimental"
    minimalist   = "minimalist"
    mixed        = "mixed"

class BodyType(str, enum.Enum):
    athletic = "athletic"
    slim     = "slim"
    average  = "average"
    stocky   = "stocky"

class ClothingStyle(str, enum.Enum):
    casual    = "casual"
    sport     = "sport"
    street    = "street"
    business  = "business"
    other     = "other"

class StylingType(str, enum.Enum):
    neat        = "neat"
    messy       = "messy"
    natural     = "natural"
    other       = "other"

class HairstyleName(str, enum.Enum):
    classic      = "classic"
    buzz_cut     = "buzz-cut"
    crew_cut     = "crew-cut"
    french_crop  = "french crop"
    curtains     = "curtains"
    pompadour    = "pompadour"
    mullet       = "mullet"
    undercut     = "undercut"
    cascade      = "cascade"
    man_bun      = "man-bun"
    surfer       = "surfer"
    shag         = "shag"


# ─── Tables ───────────────────────────────────────────────────────────────────
class Clients(Base):
    __tablename__ = "clients"

    id              = Column(Integer, primary_key=True)
    age_group       = Column(Enum(AgeGroup),       nullable=False)
    face_shape      = Column(Enum(FaceShape),      nullable=False)
    hair_texture    = Column(Enum(HairTexture),    nullable=False)
    hair_density    = Column(Enum(HairDensity),    nullable=False)
    hair_length     = Column(Enum(HairLength),     nullable=False)
    hair_color      = Column(Enum(HairColor),      nullable=False)
    styling_time    = Column(Enum(StylingTime),    nullable=False)
    lifestyle       = Column(Enum(Lifestyle),      nullable=False)
    style_char      = Column(Enum(StyleCharacter), nullable=False)
    body_type       = Column(Enum(BodyType),       nullable=False)
    clothing_style  = Column(Enum(ClothingStyle),  nullable=False)
    uses_products   = Column(Boolean,              nullable=False)
    styling_type    = Column(Enum(StylingType),    nullable=False)
    uses_hairdryer  = Column(Boolean,              nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    recommendations = relationship("Recommendations", back_populates="client")


class Hairstyles(Base):
    __tablename__ = "hairstyles"

    id        = Column(Integer, primary_key=True)
    name      = Column(Enum(HairstyleName), nullable=False, unique=True)
    image_url = Column(String, nullable=False)
    tags      = Column(ARRAY(String), default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recommendations = relationship("Recommendations", back_populates="hairstyle")


class Recommendations(Base):
    __tablename__ = "recommendations"

    id            = Column(Integer, primary_key=True)
    client_id     = Column(Integer, ForeignKey("clients.id",      ondelete="CASCADE"))
    hairstyle_id  = Column(Integer, ForeignKey("hairstyles.id",   ondelete="CASCADE"))
    model_version = Column(String, nullable=True)
    rating        = Column(Integer)                       # 1‑5, nullable — пока нет фидбэка
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    client    = relationship("Clients",    back_populates="recommendations")
    hairstyle = relationship("Hairstyles", back_populates="recommendations")
