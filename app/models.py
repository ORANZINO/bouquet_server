from datetime import datetime
from enum import Enum, IntEnum
from typing import List, Optional
from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import EmailStr, IPvAnyAddress

# For Auth


class Message(BaseModel):
    msg: str


class Duplicated(BaseModel):
    duplicated: bool


class Email(BaseModel):
    email: EmailStr = Field(..., example='oranz@naver.com')


class UserName(BaseModel):
    user_name: str = Field(..., example='고팡서')


class CharacterName(BaseModel):
    character_name: str = Field(..., example='고광남')


class UserLogin(BaseModel):
    email: EmailStr = Field(..., example='oranz@naver.com')
    pw: str = Field(..., example='12345678')


class UserRegister(UserLogin):
    profile_img: str = Field(..., example="https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg")
    name: str = Field(..., example="오란지")


class Token(BaseModel):
    Authorization: str = None


# For User


class UserMe(BaseModel):
    id: int = Field(..., example=1)
    email: EmailStr = Field(..., example="oranz@naver.com")
    name: str = Field(..., example="오태진")
    profile_img: str = Field(..., example="https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg")
    sns_type: str = Field(..., example="Email")

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None)
    profile_img: Optional[str] = Field(None)


class SnsType(str, Enum):
    email: str = "email"
    google: str = "google"
    apple: str = "apple"


#  For Character


class ID(BaseModel):
    id: int = Field(..., example=1)


class CharacterMe(BaseModel):
    name: str
    profile_img: str
    birth: int
    job: str
    nationality: str
    intro: str
    tmi: Optional[str] = None
    likes: List[str]
    hates: List[str]

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


class CharacterUpdate(BaseModel):
    id: int = Field(...)
    name: Optional[str] = Field(None)
    profile_img: Optional[str] = Field(None)
    birth: Optional[int] = Field(None)
    job: Optional[str] = Field(None)
    nationality: Optional[str] = Field(None)
    intro: Optional[str] = Field(None)
    tmi: Optional[str] = Field(None)
    likes: Optional[List[str]] = Field(None)
    hates: Optional[List[str]] = Field(None)

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


class CharacterInfo(CharacterMe):
    id: int
    num_follows: int
    num_followers: int
    user_id: int

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
              "likes": [
                "햇빛",
                "비옥한 토양",
                "해변가"
              ],
              "hates": [
                "비오는 곳",
                "낮은 당도",
                "사과(라이벌)"
              ],
              "id": 1,
              "num_follows": 0,
              "num_followers": 1,
              "user_id": 1
            }
        }


class CharacterList(BaseModel):
    characters: List[CharacterInfo] = Field(...)


class FollowInfo(BaseModel):
    character_id: int = Field(..., example=1)
    follower_id: int = Field(..., example=3)

    class Config:
        orm_mode = True


# For Post


class TemplateType(str, Enum):
    none: str = "None"
    image: str = "Image"
    diary: str = "Diary"
    list: str = "List"
    album: str = "Album"


class Post(BaseModel):
    character_id: int
    template: TemplateType = "None"
    text: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "character_id": 1,
                "template": "None",
                "text": "이것이 포스팅이다.",
            }
        }


class Image(Post):
    template: TemplateType = "Image"
    img: str

    class Config:
        schema_extra = {
            "example": {
                "character_id": 1,
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
                "text": "새 앨범이 나왔어용",
                "template": "Album",
                "description": "열심히 준비한 앨범입니다!",
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
                "text": "제가 좋아하는 것들입니당",
                "template": "List",
                "title": "My Favorites",
                "content": "these are what I like",
                "components": [{"title": "Orange", "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg", "content": "오렌지 좋아함 ㅎㅎ"}]
            }
        }


class Comment(BaseModel):
    post_id: int
    character_id: int
    comment: str
    parent: int

    class Config:
        schema_extra = {
            "example": {
                "post_id": 1,
                "character_id": 1,
                "comment": "이 노래를 불러보지만 내 진심이 닿을지 몰라",
                "parent": 0
            }
        }


class PostRow(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    character_id: int
    template: TemplateType
    text: str
    num_sunshines: int

    class Config:
        orm_mode = True


class CharacterMini(BaseModel):
    name: str
    profile_img: str

    class Config:
        orm_mode = True


class CharacterCard(BaseModel):
    name: str
    profile_img: str
    intro: str

    class Config:
        orm_mode = True


class CommentMini(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    comment: str
    parent: int
    deleted: bool
    num_sunshines: int

    class Config:
        orm_mode = True

# For Imgs


class SexType(IntEnum, Enum):
    female: int = 0
    male: int = 1

# For Auth


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


