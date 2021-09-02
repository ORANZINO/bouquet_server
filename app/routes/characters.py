from typing import List, Optional
from collections import defaultdict
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, Body, Query
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database.conn import db
from app.database.schema import Users, Characters, CharacterHates, CharacterLikes, Follows
from app import models as m
from app.errors import exceptions as ex
import string
import base64
import secrets

from app.models import CharacterList, CharacterUpdate, CharacterMe, ID, FollowInfo, Message

router = APIRouter(prefix='/character')


update_examples = {
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


@router.post('', status_code=201, response_model=ID, responses={
    202: dict(description="Given character name already exists", model=Message)
})
async def create_my_character(request: Request, character: CharacterMe, session: Session = Depends(db.session)):
    user = request.state.user
    is_exist = bool(Characters.get(session, name=character.name))
    if is_exist:
        return JSONResponse(status_code=202, content=dict(msg="CHARACTER_NAME_EXISTS"))
    character = dict(character)
    character["user_id"] = user.id
    character["num_follows"] = 0
    character["num_followers"] = 0
    new_character = Characters.create(session, True, **character)
    character_id = new_character.id
    for like in character['likes']:
        CharacterLikes.create(session, True, like=like, character_id=character_id)
    for hate in character['hates']:
        CharacterHates.create(session, True, hate=hate, character_id=character_id)
    return JSONResponse(status_code=201, content=dict(id=character_id))


@router.get('/user/{user_name}', status_code=200, response_model=CharacterList, responses={
    404: dict(description="No such user", model=Message)
})
async def get_user_characters(user_name: str, session: Session = Depends(db.session)):
    user = Users.get(session, name=user_name)
    if not user:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_USER_NAME"))
    characters = Characters.filter(session, user_id=user.id).all()
    character_ids = [character.id for character in characters]
    likes = CharacterLikes.filter(session, character_id__in=character_ids).all()
    hates = CharacterHates.filter(session, character_id__in=character_ids).all()
    likes_dict = defaultdict(list)
    for like in likes:
        likes_dict[like.character_id].append(like.like)
    hates_dict = defaultdict(list)
    for hate in hates:
        hates_dict[hate.character_id].append(hate.hate)
    for i, character in enumerate(characters):
        setattr(characters[i], 'likes', likes_dict[character.id])
        setattr(characters[i], 'hates', hates_dict[character.id])
    characters = [CharacterUpdate.from_orm(character).dict() for character in characters]
    return JSONResponse(status_code=200, content=dict(characters=characters))


@router.get('/{character_name}', status_code=200, response_model=CharacterUpdate, responses={
    404: dict(description="No such character", model=Message)
})
async def get_character(character_name: str, session: Session = Depends(db.session)):
    character = Characters.get(session, name=character_name)
    if not character:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_CHARACTER_NAME"))
    likes = CharacterLikes.filter(session, character_id=character.id).all()
    hates = CharacterHates.filter(session, character_id=character.id).all()
    setattr(character, 'likes', [like.like for like in likes])
    setattr(character, 'hates', [hate.hate for hate in hates])
    character = CharacterUpdate.from_orm(character).dict()
    return JSONResponse(status_code=200, content=character)


@router.patch('', status_code=204, responses={
    400: dict(description="Given character doesn't belong to you", model=Message)
})
async def update_my_character(request: Request, character: CharacterUpdate = Body(..., examples=update_examples), session: Session = Depends(db.session)):
    user = request.state.user
    old_character = Characters.get(session, id=character.id)
    if old_character.user_id != user.id:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_USER"))
    character = dict(character)
    character = {key: character[key] for key in character if character[key] is not None}
    character_row = {k: character[k] for k in character.keys() - ['likes', 'hates']}
    Characters.filter(session, id=character['id']).update(True, **character_row)
    if 'likes' in character:
        CharacterLikes.filter(session, character_id=character['id']).delete(auto_commit=True)
        for like in character['likes']:
            CharacterLikes.create(session, True, like=like, character_id=character['id'])
    if 'hates' in character:
        CharacterHates.filter(session, character_id=character['id']).delete(auto_commit=True)
        for hate in character['hates']:
            CharacterHates.create(session, True, hate=hate, character_id=character['id'])
    return JSONResponse(status_code=204)


@router.delete('/{character_name}', status_code=204, responses={
    400: dict(description="Given character doesn't belong to you", model=Message),
    404: dict(description="No such character", model=Message)
})
async def delete_my_character(request: Request, character_name: str, session: Session = Depends(db.session)):
    user = request.state.user
    character = Characters.get(session, name=character_name)
    if not character:
        return JSONResponse(status_code=404, content=dict(msg="WRONG_CHARACTER_NAME"))
    if character.user_id != user.id:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_USER"))
    Characters.filter(session, id=character.id, user_id=user.id).delete(auto_commit=True)
    return JSONResponse(status_code=204)


@router.post('/follow', status_code=200, response_model=Message, responses={
    400: dict(description="Given character doesn't belong to you", model=Message),
    404: dict(description="No such character", model=Message)
})
async def follow(request: Request, follow_info: FollowInfo, session: Session = Depends(db.session)):
    user = request.state.user
    follower = Characters.get(session, id=follow_info.follower_id)
    followee = Characters.get(session, id=follow_info.character_id)
    if not follower or not followee:
        return JSONResponse(status_code=404, content=dict(msg="WRONG_CHARACTER_ID"))
    if follower.user_id != user.id:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_USER"))
    follow_exists = Follows.get(session, character_id=follow_info.character_id, follower_id=follow_info.follower_id)
    if follow_exists:
        session.query(Characters).filter_by(id=follow_info.character_id)\
            .update({Characters.num_followers: Characters.num_followers - 1})
        session.query(Characters).filter_by(id=follow_info.follower_id) \
            .update({Characters.num_follows: Characters.num_follows - 1})
        session.commit()
        session.flush()
        Follows.filter(session, character_id=follow_info.character_id, follower_id=follow_info.follower_id).delete(True)
        return JSONResponse(status_code=200, content=dict(msg="UNFOLLOW_SUCCESS"))
    else:
        session.query(Characters).filter_by(id=follow_info.character_id) \
            .update({Characters.num_followers: Characters.num_followers + 1})
        session.query(Characters).filter_by(id=follow_info.follower_id) \
            .update({Characters.num_follows: Characters.num_follows + 1})
        session.commit()
        session.flush()
        Follows.create(session, True, character_id=follow_info.character_id, follower_id=follow_info.follower_id)
        return JSONResponse(status_code=200, content=dict(msg="FOLLOW_SUCCESS"))




