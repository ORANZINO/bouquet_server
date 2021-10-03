
from app.database.conn import db
from app.database.schema import PushTokens
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request
from starlette.responses import JSONResponse
from app.models import ExponentPushToken

router = APIRouter(prefix='/notification')


# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.


@router.post('/token', status_code=201)
async def register_token(request: Request, token: ExponentPushToken, session: Session = Depends(db.session)):
    user = request.state.user
    PushTokens.create(session, True, user_id=user.id, token=token.token)
    return JSONResponse(status_code=201)
