from typing_extensions import TypedDict
from datetime import datetime
from enum import Enum, IntEnum
from typing import List, Optional, Union
from pydantic import Field, PositiveInt, AnyHttpUrl, conint, constr, StrictBool
from pydantic.main import BaseModel
from pydantic.networks import EmailStr

# For Auth


class Message(BaseModel):
    msg: constr(strict=True)


class Duplicated(BaseModel):
    duplicated: bool


class Email(BaseModel):
    email: EmailStr = Field(..., example='oranz@naver.com')


class UserName(BaseModel):
    user_name: constr(strict=True) = Field(..., example='고팡서')


class CharacterName(BaseModel):
    character_name: constr(strict=True) = Field(..., example='고광남')


class UserLogin(BaseModel):
    email: EmailStr = Field(..., example='oranz@naver.com')
    pw: constr(strict=True) = Field(..., example='12345678')


class UserRegister(UserLogin):
    profile_img: Optional[AnyHttpUrl] = Field(..., example="https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg")
    name: constr(strict=True) = Field(..., example="오란지")


class Token(BaseModel):
    Authorization: constr(strict=True) = None


# For User
class SnsType(str, Enum):
    email: str = "email"
    google: str = "google"
    apple: str = "apple"


class UserMe(BaseModel):
    id: PositiveInt = Field(..., example=1)
    email: EmailStr = Field(..., example="oranz@naver.com")
    name: constr(strict=True) = Field(..., example="오태진")
    profile_img: AnyHttpUrl = Field(..., example="https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg")
    sns_type: SnsType = Field(..., example="email")

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    name: Optional[constr(strict=True)] = Field(None)
    profile_img: Optional[AnyHttpUrl] = Field(None)


class UserMini(BaseModel):
    name: constr(strict=True) = Field(..., example='오태진')
    profile_img: AnyHttpUrl = Field(..., example="https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg")

    class Config:
        orm_mode = True


#  For Character

class ID(BaseModel):
    id: PositiveInt = Field(..., example=1)


class IDWithToken(BaseModel):
    id: PositiveInt = Field(..., example=1)
    Authorization: constr(strict=True) = None


class CharacterMe(BaseModel):
    name: constr(strict=True)
    profile_img: Optional[AnyHttpUrl]
    birth: conint(strict=True, gt=0, lt=100000000)
    job: constr(strict=True)
    nationality: constr(strict=True)
    intro: constr(strict=True)
    tmi: Optional[constr(strict=True)] = None
    likes: List[constr(strict=True)]
    hates: List[constr(strict=True)]

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
    id: PositiveInt = Field(...)
    name: Optional[constr(strict=True)] = Field(None)
    profile_img: Optional[AnyHttpUrl] = Field(None)
    birth: Optional[conint(strict=True, gt=0, lt=100000000)] = None
    job: Optional[constr(strict=True)] = Field(None)
    nationality: Optional[constr(strict=True)] = Field(None)
    intro: Optional[constr(strict=True)] = Field(None)
    tmi: Optional[constr(strict=True)] = Field(None)
    likes: Optional[List[constr(strict=True)]] = Field(None)
    hates: Optional[List[constr(strict=True)]] = Field(None)

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


class CharacterProfile(CharacterMe):
    id: PositiveInt

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
              "likes": [
                "햇빛",
                "비옥한 토양",
                "해변가"
              ],
              "hates": [
                "비오는 곳",
                "낮은 당도",
                "사과(라이벌)"
              ]
            }
        }


class CharacterProfileList(BaseModel):
    characters: List[Optional[CharacterProfile]]


class CharacterInfo(CharacterMe):
    id: PositiveInt
    followed: bool
    num_follows: conint(strict=True, ge=0)
    num_followers: conint(strict=True, ge=0)
    user_info: UserMini

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
              "followed": True,
              "num_follows": 0,
              "num_followers": 1,
              "user_info": {
                  "name": "오태진",
                  "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
              }
            }
        }


class CharacterCard(BaseModel):
    name: constr(strict=True) = Field(..., example='오란지')
    profile_img: AnyHttpUrl = Field(..., example='https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg')
    intro: constr(strict=True) = Field(..., example='상큼합니다.')

    class Config:
        orm_mode = True


class UserInfo(UserMini):
    num_followers: conint(strict=True, ge=0) = Field(..., example=1)
    num_characters: conint(strict=True, ge=0) = Field(..., example=1)


class UserCharacters(BaseModel):
    user_info: UserInfo
    characters: List[Optional[CharacterCard]]

    class Config:
        orm_mode = True


# For Post
class NoTemplate(BaseModel):
    type: str = Field("None", const=True)


class ImageTemplate(BaseModel):
    type: str = Field("Image", const=True)
    img: AnyHttpUrl


class DiaryTemplate(BaseModel):
    type: str = Field("Diary", const=True)
    title: constr(strict=True)
    weather: constr(strict=True)
    img: Optional[AnyHttpUrl]
    date: conint(strict=True, gt=0, lt=100000000)
    content: constr(strict=True)


class AlbumTrack(TypedDict):
    title: str
    lyric: Optional[str]


class AlbumTemplate(BaseModel):
    type: str = Field("Album", const=True)
    title: constr(strict=True)
    img: AnyHttpUrl
    description: Optional[constr(strict=True)]
    release_date: conint(strict=True, gt=0, lt=100000000)
    tracks: List[AlbumTrack]


class ListComponent(TypedDict):
    title: str
    img: Optional[AnyHttpUrl]
    content: Optional[str]


class ListTemplate(BaseModel):
    type: str = Field("List", const=True)
    title: constr(strict=True)
    content: Optional[constr(strict=True)]
    img: Optional[AnyHttpUrl]
    components: List[ListComponent]


class Post(BaseModel):
    text: Optional[constr(strict=True)] = Field(None, example='ㅎㅇ')
    template: Union[NoTemplate, ImageTemplate, DiaryTemplate, AlbumTemplate, ListTemplate]

    class Config:
        orm_mode = True


class Comment(BaseModel):
    post_id: PositiveInt
    comment: constr(strict=True)
    parent: conint(strict=True, ge=0)

    class Config:
        schema_extra = {
            "example": {
                "post_id": 1,
                "comment": "이 노래를 불러보지만 내 진심이 닿을지 몰라",
                "parent": 0
            }
        }


class CharacterMini(BaseModel):
    name: constr(strict=True)
    profile_img: AnyHttpUrl

    class Config:
        orm_mode = True


class ChildComment(BaseModel):
    character_info: CharacterMini
    id: PositiveInt
    created_at: constr(strict=True)
    updated_at: constr(strict=True)
    comment: constr(strict=True)
    parent: conint(strict=True, ge=0)
    deleted: bool
    num_sunshines: conint(strict=True, ge=0)
    liked: bool


class ParentComment(ChildComment):
    children: List[Optional[ChildComment]]


class PostResponse(BaseModel):
    id: PositiveInt
    created_at: constr(strict=True)
    updated_at: constr(strict=True)
    text: Optional[constr(strict=True)]
    num_sunshines: conint(strict=True, ge=0)
    liked: bool
    character_info: CharacterMini
    template: Union[NoTemplate, ImageTemplate, DiaryTemplate, AlbumTemplate, ListTemplate]


class PostResponseWithComments(PostResponse):
    comments: List[Optional[ParentComment]]


class PostRow(BaseModel):
    id: PositiveInt
    created_at: datetime
    updated_at: datetime
    character_id: PositiveInt
    template: constr(strict=True)
    text: constr(strict=True)
    num_sunshines: conint(strict=True, ge=0)

    class Config:
        orm_mode = True


class CommentMini(BaseModel):
    id: PositiveInt
    created_at: datetime
    updated_at: datetime
    comment: constr(strict=True)
    parent: conint(strict=True, ge=0)
    deleted: bool
    num_sunshines: conint(strict=True, ge=0)

    class Config:
        orm_mode = True


# For QnAs

class Question(BaseModel):
    question: constr(strict=True) = Field(..., example="제일 좋아하는 과일은?")


class QnA(Question):
    answer: constr(strict=True) = Field(..., example="오렌지.")


class QnARow(QnA):
    id: PositiveInt
    num_sunshines: conint(strict=True, ge=0)


class QnARowWithLike(QnARow):
    liked: bool


class QnAList(BaseModel):
    character_name: constr(strict=True)
    profile_img: AnyHttpUrl
    qnas: List[Optional[QnARowWithLike]]


# For Notification

class ExponentPushToken(BaseModel):
    token: constr(strict=True) = Field(..., example='ExponentPushToken[ao8g3tHL8052V33aI9hREo]')


class NotificationRow(BaseModel):
    id: PositiveInt
    created_at: str
    sender_name: constr(strict=True)
    sender_profile_img: AnyHttpUrl
    category: constr(strict=True)
    post_id: Optional[PositiveInt]

    class Config:
        orm_mode = True


class NotificationList(BaseModel):
    notifications: List[Optional[NotificationRow]]

    class Config:
        schema_extra = {
            "example": {
              "notifications": [
                {
                  "id": 64,
                  "created_at": "2021-10-03T21:22:34",
                  "sender_name": "C JAMM",
                  "sender_profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                  "category": "LikeComment",
                  "post_id": 1
                },
                {
                  "id": 63,
                  "created_at": "2021-10-03T21:22:33",
                  "sender_name": "C JAMM",
                  "sender_profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                  "category": "LikeComment",
                  "post_id": 1
                }
              ]
            }
        }


# For Imgs


class SexType(IntEnum, Enum):
    female: int = 0
    male: int = 1

# For Auth


class UserToken(BaseModel):
    id: PositiveInt
    email: EmailStr = None
    name: constr(strict=True) = None
    profile_img: AnyHttpUrl = None
    sns_type: constr(strict=True) = None
    default_character_id: Optional[PositiveInt] = None

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


# For Search

class CharacterList(BaseModel):
    characters: List[Optional[CharacterCard]]

    class Config:
        schema_extra = {
            "example": {
                "characters": [
                    {
                        "name": "오란지",
                        "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                        "intro": "상큼합니다."
                    },
                    {
                        "name": "두리안",
                        "profile_img": "https://img3.daumcdn.net/thumb/R658x0.q70/?fname=https://t1.daumcdn.net/news/202105/21/dailylife/20210521214351768duii.jpg",
                        "intro": "내 매력의 출구는 없다."
                    },
                    {
                        "name": "폭스",
                        "profile_img": "https://img.dmitory.com/img/202104/cBS/EJy/cBSEJyPITSwsos0Iy4YuO.jpg",
                        "intro": "비스트 걸스 폭스에요*^^*"
                    },
                    {
                        "name": "내일의 아스카",
                        "profile_img": "https://mblogthumb-phinf.pstatic.net/20160120_261/cyc085_1453276292281BRcsj_JPEG/%B8%DE%C0%CE_%C0%CC%B9%CC%C1%F6.jpg?type=w2",
                        "intro": "시간은 영원할까?"
                    }
                ]
            }
        }


class PostList(BaseModel):
    posts: List[Optional[PostResponse]]

    class Config:
        schema_extra = {
            "example": {
                "posts": [
                    {
                        "id": 1,
                        "created_at": "2021-09-02T15:25:46",
                        "updated_at": "2021-09-02T15:25:46",
                        "character_id": 1,
                        "template": {
                            "type": "None"
                        },
                        "text": "이것이 포스팅이다.",
                        "num_sunshines": 0,
                        "character_info": {
                            "name": "오란지",
                            "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                        },
                        "liked": False
                    },
                    {
                        "id": 2,
                        "created_at": "2021-09-02T15:25:58",
                        "updated_at": "2021-09-02T15:25:58",
                        "character_id": 1,
                        "template": {
                            "type": "Image",
                            "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                        },
                        "text": "orange pic",
                        "num_sunshines": 0,
                        "character_info": {
                            "name": "오란지",
                            "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                        },
                        "liked": False
                    },
                    {
                        "id": 3,
                        "created_at": "2021-09-02T15:26:07",
                        "updated_at": "2021-09-02T15:26:07",
                        "character_id": 1,
                        "template": {
                            "type": "Diary",
                            "title": "오늘의 일기",
                            "weather": "맑음",
                            "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                            "date": 20210816,
                            "content": "오늘은 밥을 먹었다. 참 재미있었다."
                        },
                        "text": "오늘은 일기를 썼다.",
                        "num_sunshines": 0,
                        "character_info": {
                            "name": "오란지",
                            "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                        },
                        "liked": False
                    },
                    {
                        "id": 4,
                        "created_at": "2021-09-02T15:26:14",
                        "updated_at": "2021-09-02T15:26:14",
                        "character_id": 1,
                        "template": {
                            "type": "Album",
                            "title": "this is hiphop",
                            "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                            "artist": "오란지",
                            "description": None,
                            "release_date": 20210821,
                            "tracks": [
                                {
                                    "title": "배신의 십자가",
                                    "lyric": "으아으아으아으아으아으아"
                                },
                                {
                                    "title": "달콤한 오렌지",
                                    "lyric": "우와우와우와우와"
                                }
                            ]
                        },
                        "text": "새 앨범이 나왔어용",
                        "num_sunshines": 0,
                        "character_info": {
                            "name": "오란지",
                            "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                        },
                        "liked": False
                    },
                    {
                        "id": 5,
                        "created_at": "2021-09-02T15:26:21",
                        "updated_at": "2021-09-02T15:26:21",
                        "character_id": 1,
                        "template": {
                            "type": "List",
                            "title": "My Favorites",
                            "content": "these are what I like",
                            "img": None,
                            "components": [
                                {
                                    "title": "Orange",
                                    "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                                    "content": "오렌지 좋아함 ㅎㅎ"
                                }
                            ]
                        },
                        "text": "제가 좋아하는 것들입니당",
                        "num_sunshines": 0,
                        "character_info": {
                            "name": "오란지",
                            "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                        },
                        "liked": False
                    }
                ]
            }
        }


class PostListWithNum(PostList):
    total_post_num: conint(strict=True, ge=0) = Field(..., example=15)

    class Config:
        schema_extra = {
            "example": {
                "posts": [
                    {
                        "id": 1,
                        "created_at": "2021-09-02T15:25:46",
                        "updated_at": "2021-09-02T15:25:46",
                        "character_id": 1,
                        "template": {
                            "type": "None"
                        },
                        "text": "이것이 포스팅이다.",
                        "num_sunshines": 0,
                        "character_info": {
                            "name": "오란지",
                            "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                        },
                        "liked": False
                    },
                    {
                        "id": 2,
                        "created_at": "2021-09-02T15:25:58",
                        "updated_at": "2021-09-02T15:25:58",
                        "character_id": 1,
                        "template": {
                            "type": "Image",
                            "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                        },
                        "text": "orange pic",
                        "num_sunshines": 0,
                        "character_info": {
                            "name": "오란지",
                            "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                        },
                        "liked": False
                    },
                    {
                        "id": 3,
                        "created_at": "2021-09-02T15:26:07",
                        "updated_at": "2021-09-02T15:26:07",
                        "character_id": 1,
                        "template": {
                            "type": "Diary",
                            "title": "오늘의 일기",
                            "weather": "맑음",
                            "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                            "date": 20210816,
                            "content": "오늘은 밥을 먹었다. 참 재미있었다."
                        },
                        "text": "오늘은 일기를 썼다.",
                        "num_sunshines": 0,
                        "character_info": {
                            "name": "오란지",
                            "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                        },
                        "liked": False
                    },
                    {
                        "id": 4,
                        "created_at": "2021-09-02T15:26:14",
                        "updated_at": "2021-09-02T15:26:14",
                        "character_id": 1,
                        "template": {
                            "type": "Album",
                            "title": "this is hiphop",
                            "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                            "artist": "오란지",
                            "description": None,
                            "release_date": 20210821,
                            "tracks": [
                                {
                                    "title": "배신의 십자가",
                                    "lyric": "으아으아으아으아으아으아"
                                },
                                {
                                    "title": "달콤한 오렌지",
                                    "lyric": "우와우와우와우와"
                                }
                            ]
                        },
                        "text": "새 앨범이 나왔어용",
                        "num_sunshines": 0,
                        "character_info": {
                            "name": "오란지",
                            "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                        },
                        "liked": False
                    },
                    {
                        "id": 5,
                        "created_at": "2021-09-02T15:26:21",
                        "updated_at": "2021-09-02T15:26:21",
                        "character_id": 1,
                        "template": {
                            "type": "List",
                            "title": "My Favorites",
                            "content": "these are what I like",
                            "img": None,
                            "components": [
                                {
                                    "title": "Orange",
                                    "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                                    "content": "오렌지 좋아함 ㅎㅎ"
                                }
                            ]
                        },
                        "text": "제가 좋아하는 것들입니당",
                        "num_sunshines": 0,
                        "character_info": {
                            "name": "오란지",
                            "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                        },
                        "liked": False
                    }
                ],
                "total_post_num": 15
            }
        }


