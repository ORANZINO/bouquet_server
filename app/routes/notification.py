
from app.database.conn import db
from app.database.schema import PushTokens, Notifications, Characters
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request, Header
from starlette.responses import JSONResponse
from app.models import ExponentPushToken, NotificationList, NotificationRow, Message, Count
from typing import Optional
from datetime import timedelta

router = APIRouter(prefix='/notification')


@router.get('/count', status_code=200, response_model=Count, responses={
    400: dict(description="You should have character", model=Message),
})
async def count_my_notifications(request: Request, session: Session = Depends(db.session)):
    user = request.state.user

    if user.default_character_id is None:
        return JSONResponse(status_code=400, content=dict(msg="NO_GIVEN_CHARACTER"))
    character_id = user.default_character_id
    return JSONResponse(status_code=200, content=dict(count=Notifications.filter(session, receiver_id=character_id).count()))


@router.get('', status_code=200, response_model=NotificationList, responses={
    400: dict(description="You should have character", model=Message),
})
async def get_my_notifications(request: Request, page_num: Optional[int] = Header(1), session: Session = Depends(db.session)):
    user = request.state.user
    if user.default_character_id is None:
        return JSONResponse(status_code=400, content=dict(msg="NO_GIVEN_CHARACTER"))

    notifications = session.query(Notifications, Characters).filter(Notifications.receiver_id == user.default_character_id)\
        .join(Characters.sender).order_by(Notifications.created_at.desc()).offset((page_num - 1) * 15).limit(15).all()
    for i, notification in enumerate(notifications):
        notification[0].created_at = (notification[0].created_at + timedelta(hours=9)).isoformat()
        notification[0].sender_name = notification[1].name
        notification[0].sender_profile_img = notification[1].profile_img
        notifications[i] = notification[0]
    notifications = [NotificationRow.from_orm(notification).dict() for notification in notifications]

    return JSONResponse(status_code=200, content=dict(notifications=notifications))


@router.delete('', status_code=204, responses={
    400: dict(description="Not your notification", model=Message)
})
async def delete_notification(request: Request, notification_id: int, session: Session = Depends(db.session)):
    user = request.state.user
    notification = Notifications.get(session, id=notification_id)
    if notification.receiver_id == user.default_character_id:
        Notifications.filter(session, id=notification_id).delete(True)
    else:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_CHARACTER"))
    return JSONResponse(status_code=204)


@router.post('/token', status_code=201)
async def register_token(request: Request, token: ExponentPushToken, session: Session = Depends(db.session)):
    user = request.state.user
    old_token = PushTokens.get(session, user_id=user.id)
    if old_token:
        PushTokens.filter(session, user_id=user.id).update(True, token=token.token)
    else:
        PushTokens.create(session, True, user_id=user.id, token=token.token)
    return JSONResponse(status_code=201)
