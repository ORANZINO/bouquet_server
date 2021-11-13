from datetime import datetime
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from starlette.responses import Response, JSONResponse
from datetime import timedelta
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from starlette.requests import Request
from typing import Optional
from app.database.conn import db
from app.database.schema import Posts, Follows, PushTokens
from app.utils.post_utils import process_post
from app.utils.notification_utils import send_notification
from app.models import PostList
from app.middlewares.token_validator import token_decode

router = APIRouter()


@router.get("/", status_code=200, response_model=PostList)
async def index(page_num: Optional[int] = Header(1), token: Optional[str] = Header(None),
                session: Session = Depends(db.session)):
    if token is None:
        posts = session.query(Posts).filter(Posts.created_at > (datetime.now() - timedelta(hours=72)))\
            .order_by(Posts.num_sunshines.desc()).offset((page_num - 1) * 10).limit(10).all()
        character_id = None
    else:
        user = await token_decode(access_token=token)
        character_id = user['default_character_id']
        followees = Follows.filter(session, follower_id=character_id).all()
        followees = [f.character_id for f in followees]
        posts = session.query(Posts).filter(Posts.created_at > (datetime.now() - timedelta(hours=72)))\
            .filter(Posts.character_id.in_(followees)).order_by(Posts.created_at.desc()).offset((page_num - 1) * 10).limit(10).all()

        if len(posts) < 10:
            posts += session.query(Posts).filter(Posts.created_at > (datetime.now() - timedelta(hours=72)))\
                .filter(Posts.character_id.not_in(followees)).order_by(Posts.created_at.desc())\
                .offset((page_num - 1) * 10).limit(10 - len(posts)).all()

    posts = [process_post(session, character_id, post) for post in posts]

    return JSONResponse(status_code=200, content=dict(posts=posts))


@router.get("/test")
async def test(request: Request, session: Session = Depends(db.session)):
    tokens = [row.token for row in session.query(PushTokens).filter_by(user_id=1).all() if row.token]
    print(tokens)
    result = {'to': 'ExponentPushToken[2EqNf0ESFxv_Iq3-nvM2nU]', 'sound': 'default', 'category': 'all', 'title': 'Today’s Bouquet 인터뷰',
              'body': 'Bouquet에서 부캐들을 인터뷰하고 싶어해요! 나의 부캐에 대해 알려주세요!',
              'data': {'link': 'https://forms.gle/d7eYq4y6pMXjBFd6A'
                       }
              }
    print(result)
    response = PushClient().publish(PushMessage(**result))
    response.validate_response()
