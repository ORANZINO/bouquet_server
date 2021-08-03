from typing import List, Optional
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

from app.models import MessageOk, UserMe, UserUpdate, CharacterId, CharacterMe, CharacterRow

router = APIRouter(prefix='/user')


@router.get('/me')
async def get_me(request: Request):
    user = request.state.user
    user_info = Users.get(id=user.id)
    return JSONResponse(status_code=200, content=dict(msg="READ_USER_SUCCESS", user=UserMe.from_orm(user_info).dict()))


@router.put('/me')
async def put_me(request: Request, info: UserUpdate, session: Session = Depends(db.session)):
    user = request.state.user
    res = Users.filter(session, id=user.id).update(True, **dict(info))
    return JSONResponse(status_code=200, content=dict(msg="UPDATE_USER_SUCCESS"))


@router.delete('/me', status_code=200)
async def delete_me(request: Request):
    user = request.state.user
    Users.filter(id=user.id).delete(auto_commit=True)
    return JSONResponse(status_code=200, content=dict(msg="DELETE_USER_SUCCESS"))


@router.post('/character', status_code=201, response_model=CharacterMe)
async def create_character(request: Request, character: CharacterMe, session: Session = Depends(db.session)):
    user = request.state.user
    character = dict(character)
    character["user_id"] = user.id
    new_character = Characters.create(session, True, **character)
    character_id = CharacterRow.from_orm(new_character).dict()['id']
    for like in character['likes']:
        CharacterLikes.create(session, True, like=like, character_id=character_id)
    for hate in character['hates']:
        CharacterHates.create(session, True, hate=hate, character_id=character_id)
    return JSONResponse(status_code=200, content=dict(msg="CREATE_CHARACTER_SUCCESS"))


@router.get('/character')
async def get_character(request: Request, character_id: int = Header(None), session: Session = Depends(db.session)):
    user = request.state.user
    character = Characters.get(session, id=character_id)
    if character.user_id != user.id:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_USER"))
    likes = CharacterLikes.filter(session, character_id=character_id).all()
    hates = CharacterHates.filter(session, character_id=character_id).all()
    likes = [like.like for like in likes]
    hates = [hate.hate for hate in hates]
    setattr(character, 'likes', likes)
    setattr(character, 'hates', hates)
    character = CharacterMe.from_orm(character).dict()
    return character


@router.put('/character')
async def put_me(request: Request):
    ...


@router.delete('/character')
async def delete_me(request: Request, character_id: int = Header(None), session: Session = Depends(db.session)):
    user = request.state.user
    Characters.filter(session, id=character_id, user_id=user.id).delete(auto_commit=True)
    return JSONResponse(status_code=200, content=dict(msg="DELETE_CHARACTER_SUCCESS"))


@router.get('/character/dup_name')
async def check_character_name(request: Request, character_name: str = Header(None), english: bool = Header(True), session: Session = Depends(db.session)):
    if not english:
        character = Characters.get(session, name=str(base64.b64decode(character_name.encode()), encoding='utf-8'))
    else:
        character = Characters.get(session, name=character_name)
    return JSONResponse(status_code=200, content=dict(msg="CHECK_CHARACTER_NAME_SUCCESS", result=bool(character)))

