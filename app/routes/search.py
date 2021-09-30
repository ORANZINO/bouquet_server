from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database.conn import db
from app.database.schema import Characters, Posts
from app.utils.post_utils import process_post
from app.models import CharacterCard, CharacterList, PostList

router = APIRouter(prefix='/search')


@router.get('/top-characters', status_code=200, response_model=CharacterList)
async def get_top_characters(session: Session = Depends(db.session)):
    top_characters = session.query(Characters).order_by(Characters.num_followers.desc()).limit(5)
    top_characters = [CharacterCard.from_orm(character).dict() for character in top_characters]
    return JSONResponse(status_code=200, content=dict(characters=top_characters))


@router.get('/top-posts', status_code=200, response_model=PostList)
async def get_top_posts(page_num: int = Header(1), character_id: int = Header(None), session: Session = Depends(db.session)):
    top_posts = session.query(Posts).order_by(Posts.num_sunshines.desc()).offset((page_num - 1) * 5).limit(5).all()
    top_posts = [process_post(session, character_id, post) for post in top_posts]
    return JSONResponse(status_code=200, content=dict(posts=top_posts))




