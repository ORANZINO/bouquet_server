from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database.conn import db
from app.database.schema import Posts, Images, Albums, Diaries, Lists, ListComponents, Tracks
from app.errors import exceptions as ex
import string
import base64
import secrets

from app.models import Post, Image, Diary, Album, List

router = APIRouter(prefix='/post')

post_keys = ["character_id", "character_name", "template", "text"]


@router.post('/')
async def create_post(request: Request, post: Post, session: Session = Depends(db.session)):
    new_post = Posts.create(session, True, **dict(post))
    return JSONResponse(status_code=201, content=dict(msg="CREATE_POST_SUCCESS", id=new_post.id))


@router.post('/img')
async def create_image(request: Request, image: Image, session: Session = Depends(db.session)):
    image = dict(image)
    post = {k: image[k] for k in image if k in post_keys}
    img = image['img']
    new_post = Posts.create(session, True, **dict(post))
    Images.create(session, True, img=img, post_id=new_post.id)
    return JSONResponse(status_code=201, content=dict(msg="CREATE_IMAGE_SUCCESS", id=new_post.id))


@router.post('/diary')
async def create_diary(request: Request, diary: Diary, session: Session = Depends(db.session)):
    diary = dict(diary)
    post = {k: diary[k] for k in diary if k in post_keys}
    new_post = Posts.create(session, True, **dict(post))
    diary = {k: diary[k] for k in diary if k not in post_keys}
    diary['post_id'] = new_post.id
    Diaries.create(session, True, **dict(diary))
    return JSONResponse(status_code=201, content=dict(msg="CREATE_DIARY_SUCCESS", id=new_post.id))


@router.post('/album')
async def create_album(request: Request, album: Album, session: Session = Depends(db.session)):
    album = dict(album)
    post = {k: album[k] for k in album if k in post_keys}
    new_post = Posts.create(session, True, **dict(post))
    tracks = album['tracks']
    del album['tracks']
    album['artist'] = album['character_name']
    album = {k: album[k] for k in album if k not in post_keys}
    album['post_id'] = new_post.id
    new_album = Albums.create(session, True, **dict(album))
    for track in tracks:
        track['album_id'] = new_album.id
        Tracks.create(session, True, **dict(track))
    return JSONResponse(status_code=201, content=dict(msg="CREATE_ALBUM_SUCCESS", id=new_post.id))


@router.post('/list')
async def create_list(request: Request, list_: List, session: Session = Depends(db.session)):
    list_ = dict(list_)
    post = {k: list_[k] for k in list_ if k in post_keys}
    new_post = Posts.create(session, True, **dict(post))
    components = list_['components']
    del list_['components']
    list_ = {k: list_[k] for k in list_ if k not in post_keys}
    list_['post_id'] = new_post.id
    new_list = Lists.create(session, True, **dict(list_))
    for component in components:
        component['list_id'] = new_list.id
        ListComponents.create(session, True, **dict(component))
    return JSONResponse(status_code=201, content=dict(msg="CREATE_LIST_SUCCESS", id=new_post.id))

