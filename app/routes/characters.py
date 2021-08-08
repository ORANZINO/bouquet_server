from typing import List, Optional
from collections import defaultdict
from uuid import uuid4

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database.conn import db
from app.database.schema import Users, Characters, CharacterHates, CharacterLikes
from app import models as m
from app.errors import exceptions as ex
import string
import base64
import secrets

from app.models import CharacterUpdate, CharacterMe, CharacterRow, CharacterOther, UserMe

router = APIRouter(prefix='/character')


@router.post('/me', status_code=201, response_model=CharacterMe)
async def create_my_character(request: Request, character: CharacterMe, session: Session = Depends(db.session)):
    user = request.state.user
    character = dict(character)
    character["user_id"] = user.id
    new_character = Characters.create(session, True, **character)
    character_id = CharacterRow.from_orm(new_character).dict()['id']
    for like in character['likes']:
        CharacterLikes.create(session, True, like=like, character_id=character_id)
    for hate in character['hates']:
        CharacterHates.create(session, True, hate=hate, character_id=character_id)
    return JSONResponse(status_code=200, content=dict(msg="CREATE_CHARACTER_SUCCESS", id=character_id))


@router.get('/me')
async def get_my_character(request: Request, character_id: int = Header(None), session: Session = Depends(db.session)):
    user = request.state.user
    character = Characters.get(session, id=character_id)
    likes = CharacterLikes.filter(session, character_id=character_id).all()
    hates = CharacterHates.filter(session, character_id=character_id).all()
    likes = [like.like for like in likes]
    hates = [hate.hate for hate in hates]
    setattr(character, 'likes', likes)
    setattr(character, 'hates', hates)
    character = CharacterUpdate.from_orm(character).dict()
    return character


@router.put('/me')
async def put_my_character(request: Request, character: CharacterUpdate, session: Session = Depends(db.session)):
    user = request.state.user
    old_character = Characters.get(session, id=character.id)
    if old_character.user_id != user.id:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_USER"))
    character = dict(character)
    character_row = {k: character[k] for k in character.keys() - ['likes', 'hates']}
    Characters.filter(session, id=character['id']).update(True, **character_row)
    CharacterLikes.filter(session, character_id=character['id']).delete(auto_commit=True)
    CharacterHates.filter(session, character_id=character['id']).delete(auto_commit=True)
    for like in character['likes']:
        CharacterLikes.create(session, True, like=like, character_id=character['id'])
    for hate in character['hates']:
        CharacterHates.create(session, True, hate=hate, character_id=character['id'])
    return JSONResponse(status_code=200, content=dict(msg="UPDATE_CHARACTER_SUCCESS"))


@router.delete('/me')
async def delete_my_character(request: Request, character_id: int = Header(None), session: Session = Depends(db.session)):
    user = request.state.user
    character = Characters.get(session, id=character_id)
    if character.user_id != user.id:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_USER"))
    Characters.filter(session, id=character_id, user_id=user.id).delete(auto_commit=True)
    return JSONResponse(status_code=200, content=dict(msg="DELETE_CHARACTER_SUCCESS"))


@router.get('/me/dup_name')
async def check_character_name(request: Request, character_name: str = Header(None), session: Session = Depends(db.session)):
    character = Characters.get(session, name=str(base64.b64decode(character_name.encode()), encoding='utf-8'))
    return JSONResponse(status_code=200, content=dict(msg="CHECK_CHARACTER_NAME_SUCCESS", result=bool(character)))


@router.get('/me/all')
async def get_all_my_characters(request: Request, session: Session = Depends(db.session)):
    user = request.state.user
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
    for i in range(len(characters)):
        setattr(characters[i], 'likes', likes_dict[characters[i].id])
        setattr(characters[i], 'hates', hates_dict[characters[i].id])
    characters = [CharacterUpdate.from_orm(character).dict() for character in characters]
    return characters


@router.get('/another/')
async def get_another_character(request: Request, character_name: str = Header(None), session: Session = Depends(db.session)):
    character = Characters.get(session, name=str(base64.b64decode(character_name.encode()), encoding='utf-8'))
    character = CharacterOther.from_orm(character).dict()
    user = Users.get(session, id=character['user_id'])
    user = UserMe.from_orm(user).dict()
    character['user_name'] = user['name']
    character['user_profile_img'] = user['profile_img']
    del character['user_id']
    return character


@router.get('/another/all')
async def get_all_another_characters(request: Request, user_name: str = Header(None), session: Session = Depends(db.session)):
    user = Users.get(session, name=user_name)
    user = UserMe.from_orm(user).dict()
    characters = Characters.filter(session, user_id=user['id']).all()
    character_ids = [character.id for character in characters]
    likes = CharacterLikes.filter(session, character_id__in=character_ids).all()
    hates = CharacterHates.filter(session, character_id__in=character_ids).all()
    likes_dict = defaultdict(list)
    for like in likes:
        likes_dict[like.character_id].append(like.like)
    hates_dict = defaultdict(list)
    for hate in hates:
        hates_dict[hate.character_id].append(hate.hate)
    for i in range(len(characters)):
        setattr(characters[i], 'likes', likes_dict[characters[i].id])
        setattr(characters[i], 'hates', hates_dict[characters[i].id])
    characters = [CharacterMe.from_orm(character).dict() for character in characters]
    return characters
