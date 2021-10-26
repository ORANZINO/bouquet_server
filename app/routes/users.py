from fastapi import APIRouter, Depends, Body
from sqlalchemy import or_
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database.conn import db
from app.database.schema import Users, Characters, CharacterHates, CharacterLikes, UserBlocks, Follows

from app.models import UserMe, UserUpdate, Message, CharacterProfile, CharacterProfileList, ID, UserName
from app.utils.examples import update_user_requests

router = APIRouter(prefix='/user')


@router.get('', status_code=200, response_model=UserMe, responses={
    404: dict(description="No such user", model=Message)
})
async def get_me(request: Request, session: Session = Depends(db.session)):
    user = request.state.user
    user_info = Users.get(session, id=user.id)
    setattr(user_info, 'sns_type', user_info.sns_type.lower())
    user_info = UserMe.from_orm(user_info).dict()

    if not user_info:
        return JSONResponse(status_code=404, content=dict(msg="NO_MATCH_USER"))
    return JSONResponse(status_code=200, content=user_info)


@router.patch('', status_code=204, description="Successfully updated user")
async def update_me(request: Request, info: UserUpdate = Body(..., examples=update_user_requests), session: Session = Depends(db.session)):
    user = request.state.user
    info = dict(info)
    info = {key: info[key] for key in info if info[key] is not None}
    Users.filter(session, id=user.id).update(True, **dict(info))
    return JSONResponse(status_code=204)


@router.delete('', status_code=204, description="Successfully deleted user")
async def delete_me(request: Request, session: Session = Depends(db.session)):
    user = request.state.user
    Users.filter(session, id=user.id).delete(auto_commit=True)
    return JSONResponse(status_code=204)


@router.post('/block', status_code=201, description="Successfully blocked user", responses={
    400: dict(description="You can't block yourself", model=Message),
    404: dict(description="Given character doesn't exist", model=Message),
    500: dict(description="Something went wrong with the database", model=Message)
})
async def block(request: Request, block_name: UserName, session: Session = Depends(db.session)):
    user = request.state.user
    block_user = Users.get(session, name=block_name.user_name)
    if not block_user:
        return JSONResponse(status_code=404, content=dict(msg="NO_MATCH_CHARACTER"))
    elif block_user.id == user.id:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_USER_ID"))
    try:
        UserBlocks.create(session, False, user_id=user.id, blocked_id=block_user.id)
        # block_characters = Characters.filter(session, user_id__in=[block_id, user.id]).all()
        # block_characters = [character.id for character in block_characters if character.user_id == block_id]
        # my_characters = [character.id for character in block_characters if character.user_id == user.id]
        # session.query(Follows).filter(or_((Follows.character_id.in_(block_characters), Follows.follower_id.in_(my_characters)),
        #                                   (Follows.character_id.in_(my_characters), Follows.follower_id.in_(block_characters)))).delete()
        session.commit()
        return JSONResponse(status_code=201)
    except:
        session.rollback()
        return JSONResponse(status_code=500, content=dict(msg="DB_PROBLEM"))



@router.get('/character', status_code=200, response_model=CharacterProfileList, responses={
    404: dict(description="No such user", model=Message)
})
async def get_my_characters(request: Request, session: Session = Depends(db.session)):
    user = request.state.user
    characters = session.query(Characters).filter(Users.id == user.id).join(Users.character).all()
    if not characters:
        user = Users.get(session, id=user.id)
        if not user:
            return JSONResponse(status_code=400, content=dict(msg="WRONG_USER_ID"))
        else:
            result = dict(characters=[])
    else:
        for i, character in enumerate(characters):
            likes = CharacterLikes.filter(session, character_id=character.id).all()
            hates = CharacterHates.filter(session, character_id=character.id).all()
            setattr(characters[i], 'likes', [like.like for like in likes])
            setattr(characters[i], 'hates', [hate.hate for hate in hates])
        result = dict(characters=[CharacterProfile.from_orm(character).dict() for character in characters])

    return JSONResponse(status_code=200, content=result)

