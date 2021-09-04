update_user_requests = {
    "both": {
        "value": {
            "name": "오태진",
            "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
        }
    },
    "name": {
        "value": {
            "name": "오태진"
        }
    },
    "img": {
        "value": {
            "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
        }
    }
}

update_character_requests = {
    "all": {
        "value": {
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
    },
    "part": {
        "value": {
            "id": 1,
            "intro": "상큼합니다.",
            "tmi": "당도가 높은 편입니다.",
            "likes": ["햇빛", "비옥한 토양", "해변가"]
        }
    }
}

create_post_requests = {
    "Plain": {
        "value": {
            "character_id": 1,
            "text": "이것이 포스팅이다.",
            "template": {
                "type": "None"
            }
        }
    },
    "Image": {
        "value": {
                "character_id": 1,
                "text": "orange pic",
                "template": {
                    "type": "Image",
                    "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                }
            }
    },
    "Diary": {
        "value": {
                "character_id": 1,
                "text": "오늘은 일기를 썼다.",
                "template": {
                    "type": "Diary",
                    "title": "오늘의 일기",
                    "weather": "맑음",
                    "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                    "date": 20210816,
                    "content": "오늘은 밥을 먹었다. 참 재미있었다."
                }
            }
    },
    "Album": {
        "value": {
                "character_id": 1,
                "text": "새 앨범이 나왔어용",
                "template": {
                    "type": "Album",
                    "description": "열심히 준비한 앨범입니다!",
                    "title": "this is hiphop",
                    "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
                    "release_date": 20210821,
                    "tracks": [{"title": "배신의 십자가", "lyric": "으아으아으아으아으아으아"}, {"title": "달콤한 오렌지", "lyric": "우와우와우와우와"}]
                }
            }
    },
    "List": {
        "value": {
                "character_id": 1,
                "text": "제가 좋아하는 것들입니당",
                "template": {
                    "type": "List",
                    "title": "My Favorites",
                    "content": "these are what I like",
                    "components": [{"title": "Orange", "img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg", "content": "오렌지 좋아함 ㅎㅎ"}]
                }
            }
    }
}


get_post_responses = {
    200: {
        "content": {
            "application/json": {
                "examples": {
                    "Plain": {
                        "value": {
                            "id": 1,
                            "created_at": "2021-09-02T15:25:46",
                            "updated_at": "2021-09-02T15:25:46",
                            "template": {
                                "type": "None"
                            },
                            "text": "이것이 포스팅이다.",
                            "num_sunshines": 0,
                            "character_info": {
                                "name": "오란지",
                                "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                            },
                            "liked": False,
                            "comments": [
                                {
                                    "id": 1,
                                    "created_at": "2021-09-02T15:26:31",
                                    "updated_at": "2021-09-02T15:26:31",
                                    "comment": "이 노래를 불러보지만 내 진심이 닿을지 몰라",
                                    "parent": 0,
                                    "deleted": False,
                                    "num_sunshines": 0,
                                    "character_info": {
                                        "name": "오란지",
                                        "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                                    },
                                    "liked": False,
                                    "children": [
                                        {
                                            "id": 4,
                                            "created_at": "2021-09-03T20:15:29",
                                            "updated_at": "2021-09-03T20:15:29",
                                            "comment": "Love I want",
                                            "parent": 1,
                                            "deleted": False,
                                            "num_sunshines": 0,
                                            "character_info": {
                                                "name": "오란지",
                                                "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                                            },
                                            "liked": False
                                        }
                                    ]
                                },
                                {
                                    "id": 2,
                                    "created_at": "2021-09-03T14:41:07",
                                    "updated_at": "2021-09-03T14:41:07",
                                    "comment": "이 노래를 불러보지만 내 진심이 닿을지 몰라",
                                    "parent": 0,
                                    "deleted": False,
                                    "num_sunshines": 0,
                                    "character_info": {
                                        "name": "오란지",
                                        "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                                    },
                                    "liked": False,
                                    "children": []
                                },
                                {
                                    "id": 3,
                                    "created_at": "2021-09-03T14:46:25",
                                    "updated_at": "2021-09-03T14:46:25",
                                    "comment": "이 노래를 불러보지만 내 진심이 닿을지 몰라",
                                    "parent": 0,
                                    "deleted": False,
                                    "num_sunshines": 0,
                                    "character_info": {
                                        "name": "오란지",
                                        "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                                    },
                                    "liked": False,
                                    "children": []
                                }
                            ]
                        }
                    },
                    "Image": {
                        "value": {
                            "id": 2,
                            "created_at": "2021-09-02T15:25:58",
                            "updated_at": "2021-09-02T15:25:58",
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
                            "liked": False,
                            "comments": [
                                {
                                    "id": 1,
                                    "created_at": "2021-09-02T15:26:31",
                                    "updated_at": "2021-09-02T15:26:31",
                                    "comment": "이 노래를 불러보지만 내 진심이 닿을지 몰라",
                                    "parent": 0,
                                    "deleted": False,
                                    "num_sunshines": 0,
                                    "character_info": {
                                        "name": "오란지",
                                        "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                                    },
                                    "liked": False,
                                    "children": [
                                        {
                                            "id": 4,
                                            "created_at": "2021-09-03T20:15:29",
                                            "updated_at": "2021-09-03T20:15:29",
                                            "comment": "Love I want",
                                            "parent": 1,
                                            "deleted": False,
                                            "num_sunshines": 0,
                                            "character_info": {
                                                "name": "오란지",
                                                "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg"
                                            },
                                            "liked": False
                                        }
                                    ]
                                }
                            ]
                        }
                    },
                    "Diary": {
                        "value": {
                            "id": 3,
                            "created_at": "2021-09-02T15:26:07",
                            "updated_at": "2021-09-02T15:26:07",
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
                            "liked": False,
                            "comments": []
                        }
                    },
                    "Album": {
                        "value": {
                            "id": 4,
                            "created_at": "2021-09-02T15:26:14",
                            "updated_at": "2021-09-02T15:26:14",
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
                            "liked": False,
                            "comments": []
                        }
                    },
                    "List": {
                        "value": {
                            "id": 5,
                            "created_at": "2021-09-02T15:26:21",
                            "updated_at": "2021-09-02T15:26:21",
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
                            "liked": False,
                            "comments": []
                        }
                    }
                }
            }
        }
    }
}
