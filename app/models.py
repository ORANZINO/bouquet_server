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

class TemplateType(str, Enum):
    none: str = "None"
    image: str = "Image"
    diary: str = "Diary"
    list: str = "List"
    album: str = "Album"

class SexType(IntEnum, Enum):
    female: int = 0
    male: int = 1


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


class CharacterMe(BaseModel):
    name: str
    profile_img: str
    birth: int
    job: str
    nationality: str
    intro: str
    tmi: str = None
    likes: List
    hates: List

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "오란지",
                "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
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
    profile_img: str
    birth: int
    job: str
    nationality: str
    intro: str
    tmi: str = None

    class Config:
        orm_mode = True


class CharacterUpdate(CharacterMe):
    id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "오란지",
                "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                "birth": 19990601,
                "job": "과일",
                "nationality": "플로리다",
                "intro": "상큼합니다.",
                "tmi": "당도가 높은 편입니다.",
                "likes": ["햇빛", "비옥한 토양", "해변가"],
                "hates": ["비오는 곳", "낮은 당도", "사과(라이벌)"]
            }
        }


class CharacterOther(BaseModel):
    name: str
    profile_img: str
    birth: int
    job: str
    nationality: str
    intro: str
    tmi: str = None
    user_id: int

    class Config:
        orm_mode = True


class FollowInfo(BaseModel):
    character_id: int
    follower_id: int

    class Config:
        orm_mode = True


class Post(BaseModel):
    character_id: int
    character_name: str
    template: TemplateType = "None"
    text: str

    class Config:
        orm_mode = True


class Image(Post):
    template: TemplateType = "Image"
    img: str

    class Config:
        schema_extra = {
            "example": {
                "character_id": 1,
                "character_name": "오란지",
                "text": "orange pic",
                "template": "Image",
                "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
            }
        }


class Diary(Post):
    template: TemplateType = "Diary"
    title: str
    weather: str
    img: str
    date: int
    content: str

    class Config:
        schema_extra = {
            "example": {
                "character_id": 1,
                "character_name": "오란지",
                "text": "오늘은 일기를 썼다.",
                "template": "Diary",
                "title": "오늘의 일기",
                "weather": "맑음",
                "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                "date": 20210816,
                "content": "오늘은 밥을 먹었다. 참 재미있었다."
            }
        }


class Album(Post):
    template: TemplateType = "Album"
    title: str
    img: str
    release_date: int
    tracks: List

    class Config:
        schema_extra = {
            "example": {
                "character_id": 1,
                "character_name": "오란지",
                "text": "새 앨범이 나왔어용",
                "template": "Album",
                "title": "this is hiphop",
                "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                "release_date": 20210821,
                "tracks": [{"title": "배신의 십자가", "lyric": "으아으아으아으아으아으아"}, {"title": "달콤한 오렌지", "lyric": "우와우와우와우와"}]
            }
        }


class List(Post):
    template: TemplateType = "List"
    title: str
    content: str
    components: List

    class Config:
        schema_extra = {
            "example": {
                "character_id": 1,
                "character_name": "오란지",
                "text": "제가 좋아하는 것들입니당",
                "template": "List",
                "title": "My Favorites",
                "content": "these are what I like",
                "components": [{"title": "Orange", "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg", "content": "오렌지 좋아함 ㅎㅎ"}]
            }
        }


class Comments(BaseModel):
    post_id: int
    character_name: str
    comment: str
    parent: int
