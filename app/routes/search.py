from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database.conn import db
from app.database.schema import Users, Characters

from app.models import CharacterCard

router = APIRouter(prefix='/search')


@router.get('/top_characters')
async def get_top_characters(session: Session = Depends(db.session)):
    top_characters = session.query(Characters).order_by(Characters.num_followers.desc()).limit(5)
    top_characters = [CharacterCard.from_orm(character).dict() for character in top_characters]
    return JSONResponse(status_code=200, content=dict(msg="GET_TOP_CHARACTERS_SUCCESS", characters=top_characters))