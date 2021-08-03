from datetime import datetime
from enum import Enum, IntEnum
from typing import List

from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import EmailStr, IPvAnyAddress


class UserLogin(BaseModel):
    email: EmailStr = None
    pw: str = None

    class Config:
        schema_extra = {
            "example": {
                "email": "oranz@naver.com",
                "pw": "1234",
            }
        }


class UserRegister(UserLogin):
    profile_img: str
    name: str

    class Config:
        schema_extra = {
            "example": {
                "email": "oranz@naver.com",
                "pw": "1234",
                "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                "name": "오란지"
            }
        }


class SnsType(str, Enum):
    email: str = "Email"
    google: str = "Google"
    apple: str = "Apple"


class SexType(IntEnum, Enum):
    male: int = 1
    female: int = 0


class Token(BaseModel):
    Authorization: str = None


class MessageOk(BaseModel):
    message: str = Field(default="OK")


class UserToken(BaseModel):
    id: int
    email: EmailStr = None
    name: str = None
    profile_img: str = None
    sns_type: str = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "email": "oranz@naver.com",
                "name": "오란지",
                "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                "sns_type": "Email"
            }
        }


class UserMe(BaseModel):
    id: int
    email: EmailStr = None
    name: str = None
    profile_img: str = None
    sns_type: str = None

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    name: str = None
    profile_img: str = None

    class Config:
        schema_extra = {
            "example": {
                "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                "name": "오태진"
            }
        }


class CharacterId(BaseModel):
    id: int


class CharacterMe(BaseModel):
    name: str
    birth: int
    job: str
    nationality: str
    intro: str
    tmi: str
    likes: List
    hates: List

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "오란지",
                "birth": 19990601,
                "job": "과일",
                "nationality": "플로리다",
                "intro": "상큼합니다.",
                "tmi": "당도가 높은 편입니다.",
                "likes": ["햇빛", "비옥한 토양", "해변가"],
                "hates": ["비오는 곳", "낮은 당도", "사과(라이벌)"]
            }
        }


class CharacterRow(BaseModel):
    id: int
    name: str
    birth: int
    job: str
    nationality: str
    intro: str
    tmi: str

    class Config:
        orm_mode = True


