from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import Optional
from starlette.responses import JSONResponse
from app.middlewares.token_validator import token_decode
from app.database.conn import db
from app.database.schema import Characters, Posts, Albums, Images, Diaries, Tracks, Lists, ListComponents
from app.utils.post_utils import process_post
from app.models import CharacterCard, CharacterList, PostList, PostRow
from app.utils.block_utils import block_characters
from datetime import timedelta
from datetime import datetime

router = APIRouter(prefix='/search')


def unpack(arr):
    return [a[0] for a in arr]


@router.get('/posts', status_code=200, response_model=PostList)
async def search(q: str, page_num: int = Header(1), token: Optional[str] = Header(None),
                 session: Session = Depends(db.session)):
    if token is None:
        character_id = None
    else:
        user = await token_decode(access_token=token)
        character_id = user['default_character_id']
    albums = session.query(distinct(Albums.post_id)).outerjoin(Albums.track).filter(Albums.title.ilike(f"%{q}%") |
                                                                                    Albums.artist.ilike(f"%{q}%") |
                                                                                    Albums.description.ilike(f"%{q}%") |
                                                                                    Tracks.lyric.ilike(f"%{q}%") |
                                                                                    Tracks.title.ilike(f"%{q}%")).all()
    lists = session.query(distinct(Lists.post_id)).outerjoin(Lists.component).filter(Lists.title.ilike(f"%{q}%") |
                                                                                     Lists.content.ilike(f"%{q}%") |
                                                                                     ListComponents.title.ilike(
                                                                                         f"%{q}%") |
                                                                                     ListComponents.content.ilike(
                                                                                         f"%{q}%")).all()
    diaries = session.query(distinct(Diaries.post_id)).filter(Diaries.title.ilike(f"%{q}%") |
                                                              Diaries.weather.ilike(f"%{q}%") |
                                                              Diaries.content.ilike(f"%{q}%")).all()
    posts = session.query(distinct(Posts.id)).filter(Posts.text.ilike(f"%{q}%")).all()
    result_ids = sorted(list(set(unpack(albums) + unpack(lists) + unpack(diaries) + unpack(posts))))[
                 (page_num - 1) * 10:page_num * 10]
    result = [process_post(session, character_id, Posts.get(session, id=post_id)) for post_id in result_ids]
    return JSONResponse(status_code=200, content=dict(posts=result))


@router.get('/characters', status_code=200, response_model=CharacterList)
async def search(q: str, page_num: int = Header(1), session: Session = Depends(db.session)):
    result_characters = session.query(Characters).filter(Characters.name.ilike(f"%{q}%") |
                                                         Characters.job.ilike(f"%{q}%") |
                                                         Characters.nationality.ilike(f"%{q}%") |
                                                         Characters.intro.ilike(f"%{q}%") |
                                                         Characters.tmi.ilike(f"%{q}%")) \
        .order_by(Characters.id.asc()).offset((page_num - 1) * 5).limit(5).all()
    result = [CharacterCard.from_orm(character).dict() for character in result_characters]
    return JSONResponse(status_code=200, content=dict(characters=result))


@router.get('/top-posts', status_code=200, response_model=PostList)
async def get_top_posts(page_num: int = Header(1), token: Optional[str] = Header(None), session: Session = Depends(db.session)):
    block_list = []
    if token is None:
        character_id = None
    else:
        user = await token_decode(access_token=token)
        character_id = user['default_character_id']
        block_list = block_characters(user, session)
    top_posts = session.query(Posts).filter(Posts.created_at > (datetime.now() - timedelta(hours=72))).filter(~Posts.character_id.in_(block_list)).order_by(Posts.num_sunshines.desc()).order_by(Posts.id.desc()).offset((page_num - 1) * 5).limit(5).all()
    top_posts = [process_post(session, character_id, post) for post in top_posts]
    return JSONResponse(status_code=200, content=dict(posts=top_posts))


@router.get('/top-characters', status_code=200, response_model=CharacterList)
async def get_top_characters(token: Optional[str] = Header(None), session: Session = Depends(db.session)):
    block_list = []
    if token:
        user = await token_decode(access_token=token)
        block_list = block_characters(user, session)
    top_characters = session.query(Characters).filter(~Characters.id.in_(block_list)).order_by(Characters.num_followers.desc()).limit(5)
    top_characters = [CharacterCard.from_orm(character).dict() for character in top_characters]
    return JSONResponse(status_code=200, content=dict(characters=top_characters))
