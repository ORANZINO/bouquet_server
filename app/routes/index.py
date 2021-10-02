from datetime import datetime

from starlette.responses import Response, JSONResponse
from inspect import currentframe as frame
from fastapi import APIRouter, Depends, Header, Path
from sqlalchemy.orm import Session
from starlette.requests import Request
from typing import Optional
from app.database.conn import db
from app.database.schema import Posts, Follows
from app.utils.post_utils import process_post
from app.models import PostList
from app.middlewares.token_validator import token_decode

router = APIRouter()


@router.get("/", status_code=200, response_model=PostList)
async def index(page_num: Optional[int] = Header(1), token: Optional[str] = Header(None), session: Session = Depends(db.session)):
    if token is None:
        posts = session.query(Posts).order_by(Posts.num_sunshines.desc()).offset((page_num - 1) * 10).limit(10).all()
        character_id = None
    else:
        user = await token_decode(access_token=token)
        character_id = user['default_character_id']
        followees = Follows.filter(session, follower_id=character_id).all()
        followees = [f.character_id for f in followees]
        posts = session.query(Posts).filter(Posts.character_id.in_(followees)).order_by(Posts.created_at.desc())\
            .offset((page_num - 1) * 10).limit(10).all()

    posts = [process_post(session, character_id, post) for post in posts]

    return JSONResponse(status_code=200, content=dict(posts=posts))


@router.get("/test")
async def test(request: Request):
    """
    ELB 상태 체크용 API
    :return:
    """
    print("state.user", request.state.user)
    try:
        a = 1/0
    except Exception as e:
        request.state.inspect = frame()
        raise e
    current_time = datetime.utcnow()
    return Response(f"Notification API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")
