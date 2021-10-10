from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from requests.exceptions import ConnectionError, HTTPError
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.database.conn import db
from app.database.schema import Notifications, Characters, PushTokens
from datetime import timedelta


def generate_message(token, sender, receiver, category, created_at, post_id=None):
    result = {
        'to': token,
        'sound': 'default',
        'category': category[0].lower() + category[1:]
    }
    if category == "LikePost":
        result['body'] = f'{sender.name}님이 {receiver.name}님의 게시글을 좋아해요.'
        result['data'] = {'screen': 'NotiTabPostStack',
                          'params': sender.name,
                          'created_at': created_at,
                          'from': {'name': sender.name, 'profile_img': sender.profile_img}}
    elif category == "LikeComment":
        result['body'] = f'{sender.name}님이 {receiver.name}님의 댓글을 좋아해요.'
        result['data'] = {'screen': 'NotiTabPostStack',
                          'params': post_id,
                          'created_at': created_at,
                          'from': {'name': sender.name, 'profile_img': sender.profile_img}}
    elif category == "Comment":
        result['body'] = f'{sender.name}님이 {receiver.name}님의 게시글에 댓글을 달았어요.'
        result['data'] = {'screen': 'NotiTabPostStack',
                          'params': post_id,
                          'created_at': created_at,
                          'from': {'name': sender.name, 'profile_img': sender.profile_img}}
    elif category == "Follow":
        result['body'] = f'{sender.name}님이 {receiver.name}님을 팔로우해요.'
        result['data'] = {'screen': 'NotiTabProfileDetailStack',
                          'params': post_id,
                          'created_at': created_at,
                          'from': {'name': sender.name, 'profile_img': sender.profile_img}}

    return result


def send_notification(sender_id: int, receiver_id: int, category: str, post_id: Optional[int] = None,
                      session: Session = Depends(db.session)):
    if sender_id != receiver_id:
        sender, receiver = Characters.get(session, id=sender_id), Characters.get(session, id=receiver_id)
        token = PushTokens.get(session, user_id=receiver.user_id).token
        new_notification = Notifications.create(session, True, sender_id=sender_id, receiver_id=receiver_id, category=category, post_id=post_id)
        if token:
            response = PushClient().publish(
                PushMessage(**generate_message(
                    token, sender, receiver, category, (new_notification.created_at + timedelta(hours=9)).isoformat(), post_id)))
            response.validate_response()


