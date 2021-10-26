from typing import List, Optional
from collections import defaultdict
from uuid import uuid4
from fastapi import APIRouter, Depends, Header, Body, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import insert, and_, or_
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.database.conn import db
from app.database.schema import Users, Characters, CharacterHates, CharacterLikes, Follows, CharacterBlocks, UserBlocks
from app.routes.auth import create_access_token
from app.models import CharacterMe, IDWithToken, UserToken, Message, CharacterCard, CharacterInfo, UserMini, \
    UserCharacters, CharacterUpdate, ID, Token, CharacterName
from app.utils.examples import update_character_requests
from app.middlewares.token_validator import token_decode
from app.utils.notification_utils import send_notification
from app.errors.exceptions import APIException

router = APIRouter(prefix='/character')


@router.post('/change', status_code=200, response_model=Token, responses={
    400: dict(description="Given character doesn't belong to you", model=Message),
    404: dict(description="Given character doesn't exist", model=Message)
})
async def change_my_character(request: Request, character_id: int, session: Session = Depends(db.session)):
    user = request.state.user
    character = Characters.get(session, id=character_id)
    if not character:
        return JSONResponse(status_code=404, content=dict(msg="NO_MATCH_CHARACTER"))
    elif character.user_id != user.id:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_CHARACTER_ID"))
    else:
        user.default_character_id = character_id
        token = f"Bearer {create_access_token(data=dict(user))}"

    return JSONResponse(status_code=201, content=dict(Authorization=token))


@router.post('', status_code=201, response_model=IDWithToken, responses={
    202: dict(description="Given character name already exists", model=Message),
    500: dict(description="Something went wrong with the database", model=Message)
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
    likes = character.pop('likes')
    hates = character.pop('hates')
    character = Characters(**character)
    try:
        session.add(character)
        session.flush()
        character_id = character.id
        session.bulk_insert_mappings(CharacterLikes, [{'like': like, 'character_id': character_id} for like in likes])
        session.bulk_insert_mappings(CharacterHates, [{'hate': hate, 'character_id': character_id} for hate in hates])
        session.query(Users).filter_by(id=user.id).update({'default_character_id': character_id})
        session.flush()
        session.commit()
    except:
        session.rollback()
        return JSONResponse(status_code=500, content=dict(msg="DB_PROBLEM"))
    user.default_character_id = character_id
    token = f"Bearer {create_access_token(data=UserToken.from_orm(user).dict(exclude={'pw', 'marketing_agree'}))}"
    return JSONResponse(status_code=201, content=dict(id=character_id, Authorization=token))


@router.get('/user/{user_name}', status_code=200, response_model=UserCharacters, responses={
    400: dict(description="Blocked user", model=Message),
    404: dict(description="No such user", model=Message)
})
async def get_user_characters(user_name: str, token: Optional[str] = Header(None),
                              session: Session = Depends(db.session)):
    target = Users.get(session, name=user_name)
    if not target:
        return JSONResponse(status_code=404, content=dict(msg="NO_MATCH_USER"))
    if token:
        user = await token_decode(access_token=token)
        user_blocks = session.query(UserBlocks).filter(
            or_(and_(UserBlocks.user_id == user['id'], UserBlocks.blocked_id == target.id),
                and_(UserBlocks.user_id == target.id, UserBlocks.blocked_id == user['id']))).all()
        if user_blocks:
            return JSONResponse(status_code=400, content=dict(msg="BLOCKED_USER"))
        character_blocks = session.query(CharacterBlocks).filter(
            or_(CharacterBlocks.character_id == user['default_character_id'],
                CharacterBlocks.blocked_id == user['default_character_id'])).all()
        blocked_characters = []
        for block in character_blocks:
            if block.character_id == user['default_character_id']:
                blocked_characters.append(block.blocked_id)
            else:
                blocked_characters.append(block.character_id)
        user_characters = session.query(Users, Characters).filter(Users.name == user_name,
                                                                  Characters.id.in_(blocked_characters)).join(
            Users.character).all()
    else:
        user_characters = session.query(Users, Characters).filter(Users.name == user_name).join(Users.character).all()
    if not user_characters:
        user_info = UserMini.from_orm(target).dict()
        user_info['num_followers'] = 0
        user_info['num_characters'] = 0
        result = dict(user_info=user_info, characters=[])
    else:
        user_info = UserMini.from_orm(user_characters[0][0]).dict()
        user_info['num_followers'] = sum(character[1].num_followers for character in user_characters)
        user_info['num_characters'] = len(user_characters)
        result = dict(user_info=user_info,
                      characters=[CharacterCard.from_orm(character[1]).dict() for character in user_characters])

    return JSONResponse(status_code=200, content=result)


@router.post('/me', status_code=200, response_model=ID, responses={
    404: dict(description="No such character", model=Message)
})
async def who_am_i(request: Request, session: Session = Depends(db.session)):
    user = request.state.user
    character = Characters.get(session, id=user.default_character_id)
    if not character:
        return JSONResponse(status_code=404, content=dict(msg="WRONG_CHARACTER_ID"))
    return JSONResponse(status_code=200, content=dict(id=character.id))


@router.post('/block', status_code=201, description="Successfully blocked character", responses={
    400: dict(description="You can't block yourself", model=Message),
    404: dict(description="Given character doesn't exist", model=Message),
    500: dict(description="Something went wrong with the database", model=Message)
})
async def block(request: Request, block_name: CharacterName, session: Session = Depends(db.session)):
    user = request.state.user
    my_character = Characters.get(session, id=user.default_character_id)
    block_character = Characters.get(session, name=block_name.character_name)
    if not block_character:
        return JSONResponse(status_code=404, content=dict(msg="NO_MATCH_CHARACTER"))
    elif block_character.name == my_character.name:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_CHARACTER_NAME"))
    try:
        CharacterBlocks.create(session, False, character_id=user.default_character_id, blocked_id=block_character.id)
        session.commit()
        return JSONResponse(status_code=201)
    except:
        session.rollback()
        return JSONResponse(status_code=500, content=dict(msg="DB_PROBLEM"))


@router.get('/{character_name}', status_code=200, response_model=CharacterInfo, responses={
    400: dict(description="Blocked", model=Message),
    404: dict(description="No such character", model=Message)
})
async def get_character(character_name: str, token: Optional[str] = Header(None),
                        session: Session = Depends(db.session)):
    target = Characters.get(session, name=character_name)
    if not target:
        return JSONResponse(status_code=404, content=dict(msg="WRONG_CHARACTER_NAME"))
    if token:
        user = await token_decode(access_token=token)
        user_block = session.query(UserBlocks).filter(and_(UserBlocks.user_id == user['id'],
                                                           UserBlocks.blocked_id == target.user_id) |
                                                      and_(UserBlocks.user_id == target.user_id,
                                                           UserBlocks.blocked_id == user['id'])).all()
        if user_block:
            return JSONResponse(status_code=400, content=dict(msg="BLOCKED_USER"))
        character_block = session.query(CharacterBlocks).filter(
            and_(CharacterBlocks.character_id == user['default_character_id'],
                 CharacterBlocks.blocked_id == target.id) | and_(
                CharacterBlocks.blocked_id == user['default_character_id'],
                CharacterBlocks.character_id == target.id)).all()
        if character_block:
            return JSONResponse(status_code=400, content=dict(msg="BLOCKED_CHARACTER"))
    setattr(target, 'user_info', UserMini.from_orm(Users.get(session, id=target.user_id)).dict())
    character = target
    likes = CharacterLikes.filter(session, character_id=character.id).all()
    hates = CharacterHates.filter(session, character_id=character.id).all()
    setattr(character, 'likes', [like.like for like in likes])
    setattr(character, 'hates', [hate.hate for hate in hates])

    if token is None:
        setattr(character, 'followed', False)
    else:
        follower_id = user['default_character_id']
        setattr(character, 'followed', bool(Follows.get(session, character_id=character.id, follower_id=follower_id)))

    character = CharacterInfo.from_orm(character).dict()
    return JSONResponse(status_code=200, content=character)


@router.patch('', status_code=204, responses={
    400: dict(description="Given character doesn't belong to you", model=Message),
    500: dict(description="Something went wrong with the database", model=Message)
})
async def update_my_character(request: Request,
                              character: CharacterUpdate = Body(..., examples=update_character_requests),
                              session: Session = Depends(db.session)):
    user = request.state.user
    old_character = Characters.get(session, id=user.default_character_id)
    if old_character.user_id != user.id:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_USER"))
    character = dict(character)
    character = {key: character[key] for key in character if character[key] is not None}
    character_row = {k: character[k] for k in character.keys() - ['likes', 'hates']}
    Characters.filter(session, id=character['id']).update(True, **character_row)
    try:
        session.query(Characters).filter_by(id=character['id']).update(character_row)
        if 'likes' in character:
            session.query(CharacterLikes).filter_by(character_id=character['id']).delete()
            session.bulk_insert_mappings(CharacterLikes, [{'like': like, 'character_id': character['id']} for like in
                                                          character['likes']])
        if 'hates' in character:
            session.query(CharacterHates).filter_by(character_id=character['id']).delete()
            session.bulk_insert_mappings(CharacterHates, [{'hate': hate, 'character_id': character['id']} for hate in
                                                          character['hates']])
        session.flush()
        session.commit()
        return JSONResponse(status_code=204)
    except:
        session.rollback()
        return JSONResponse(status_code=500, content=dict(msg="DB_PROBLEM"))


@router.delete('/{character_name}', status_code=204, responses={
    400: dict(description="Given character doesn't belong to you", model=Message),
    404: dict(description="No such character", model=Message),
    500: dict(description="Something went wrong with the database", model=Message)
})
async def delete_my_character(request: Request, character_name: str, session: Session = Depends(db.session)):
    user = request.state.user
    character = Characters.get(session, name=character_name)
    if not character:
        return JSONResponse(status_code=404, content=dict(msg="WRONG_CHARACTER_NAME"))
    if character.user_id != user.id:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_USER"))
    try:
        Characters.filter(session, id=character.id, user_id=user.id).delete(auto_commit=True)
        return JSONResponse(status_code=204)
    except:
        session.rollback()
        return JSONResponse(status_code=500, content=dict(msg="DB_PROBLEM"))


@router.post('/follow', status_code=200, response_model=Message, responses={
    400: dict(description="Given character doesn't belong to you", model=Message),
    404: dict(description="No such character", model=Message),
    500: dict(description="Something went wrong with the database", model=Message)
})
async def follow(request: Request, character_id: ID, background_tasks: BackgroundTasks,
                 session: Session = Depends(db.session)):
    user = request.state.user
    follower = Characters.get(session, id=user.default_character_id)
    followee = Characters.get(session, id=character_id.id)
    if not follower or not followee:
        return JSONResponse(status_code=404, content=dict(msg="WRONG_CHARACTER_ID"))
    if follower.user_id != user.id:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_USER"))
    follow_exists = Follows.get(session, character_id=followee.id, follower_id=follower.id)

    try:
        if follow_exists:
            session.query(Characters).filter_by(id=followee.id) \
                .update({Characters.num_followers: Characters.num_followers - 1})
            session.query(Characters).filter_by(id=follower.id) \
                .update({Characters.num_follows: Characters.num_follows - 1})
            session.query(Follows).filter_by(character_id=followee.id, follower_id=follower.id).delete()
            session.flush()
            session.commit()
            return JSONResponse(status_code=200, content=dict(msg="UNFOLLOW_SUCCESS"))
        else:
            session.query(Characters).filter_by(id=followee.id) \
                .update({Characters.num_followers: Characters.num_followers + 1})
            session.query(Characters).filter_by(id=follower.id) \
                .update({Characters.num_follows: Characters.num_follows + 1})
            session.execute(insert(Follows).values(character_id=followee.id, follower_id=follower.id))
            session.flush()
            session.commit()
            background_tasks.add_task(send_notification, follower.id, followee.id, 'Follow', session=session)
            return JSONResponse(status_code=200, content=dict(msg="FOLLOW_SUCCESS"))
    except:
        session.rollback()
        return JSONResponse(status_code=500, content=dict(msg="DB_PROBLEM"))
