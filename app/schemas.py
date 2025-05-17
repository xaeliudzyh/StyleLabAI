from pydantic import BaseModel
from .models import (
    AgeGroup, FaceShape, HairTexture, HairDensity, HairLength, HairColor,
    StylingTime, Lifestyle, StyleCharacter, BodyType, ClothingStyle,
    StylingType, HairstyleName
)


class ClientCreate(BaseModel):
    age_group:      AgeGroup
    face_shape:     FaceShape
    hair_texture:   HairTexture
    hair_density:   HairDensity
    hair_length:    HairLength
    hair_color:     HairColor
    styling_time:   StylingTime
    lifestyle:      Lifestyle
    style_char:     StyleCharacter
    body_type:      BodyType
    clothing_style: ClothingStyle
    uses_products:  bool
    styling_type:   StylingType
    uses_hairdryer: bool


class ClientOut(ClientCreate):
    id: int

    class Config:
        orm_mode = True


class HairstyleOut(BaseModel):
    id: int
    name: HairstyleName
    image_url: str
    tags: list[str] = []

    class Config:
        orm_mode = True
