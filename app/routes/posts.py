from collections import defaultdict
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database.conn import db
from app.database.schema import Posts, Images, Albums, Diaries, Lists, ListComponents, Tracks, Comments, Characters, PostSunshines, CommentSunshines
from datetime import timedelta
from app.errors import exceptions as ex
import string
import base64
import secrets

from app.models import Post, Image, Diary, Album, List, TemplateType, PostRow, Comment, CharacterRow, CharacterMini, CommentMini

router = APIRouter(prefix='/post')

post_keys = ["character_id", "template", "text"]


@router.post('/')
async def create_post(post: Post, session: Session = Depends(db.session)):
    new_post = Posts.create(session, True, **dict(post))
    return JSONResponse(status_code=201, content=dict(msg="CREATE_POST_SUCCESS", id=new_post.id))


@router.post('/img')
async def create_image(image: Image, session: Session = Depends(db.session)):
    image = dict(image)
    post = {k: image[k] for k in image if k in post_keys}
    img = image['img']
    new_post = Posts.create(session, True, **dict(post))
    Images.create(session, True, img=img, post_id=new_post.id)
    return JSONResponse(status_code=201, content=dict(msg="CREATE_IMAGE_SUCCESS", id=new_post.id))


@router.post('/diary')
async def create_diary(diary: Diary, session: Session = Depends(db.session)):
    diary = dict(diary)
    post = {k: diary[k] for k in diary if k in post_keys}
    new_post = Posts.create(session, True, **dict(post))
    diary = {k: diary[k] for k in diary if k not in post_keys}
    diary['post_id'] = new_post.id
    Diaries.create(session, True, **dict(diary))
    return JSONResponse(status_code=201, content=dict(msg="CREATE_DIARY_SUCCESS", id=new_post.id))


@router.post('/album')
async def create_album(album: Album, session: Session = Depends(db.session)):
    album = dict(album)
    post = {k: album[k] for k in album if k in post_keys}
    new_post = Posts.create(session, True, **dict(post))
    tracks = album['tracks']
    del album['tracks']
    album['artist'] = CharacterRow.from_orm(Characters.get(session, id=post['character_id'])).dict()['name']
    album = {k: album[k] for k in album if k not in post_keys}
    album['post_id'] = new_post.id
    new_album = Albums.create(session, True, **dict(album))
    for track in tracks:
        track['album_id'] = new_album.id
        Tracks.create(session, True, **dict(track))
    return JSONResponse(status_code=201, content=dict(msg="CREATE_ALBUM_SUCCESS", id=new_post.id))


@router.post('/list')
async def create_list(list_: List, session: Session = Depends(db.session)):
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


@router.post('/comment')
async def create_comment(comment: Comment, session: Session = Depends(db.session)):
    new_comment = Comments.create(session, True, **dict(comment))
    return JSONResponse(status_code=201, content=dict(msg="CREATE_COMMENT_SUCCESS", id=new_comment.id))


@router.get('/{post_id}')
async def get_post(post_id: int, character_id: int = Header(None), session: Session = Depends(db.session)):
    post = PostRow.from_orm(Posts.get(session, id=post_id)).dict()
    post['created_at'] = (post['created_at'] + timedelta(hours=9)).isoformat()
    post['updated_at'] = (post['updated_at'] + timedelta(hours=9)).isoformat()
    character_info = CharacterMini.from_orm(Characters.get(session, id=post['character_id'])).dict()
    my_sunshine = bool(PostSunshines.get(session, post_id=post_id, character_id=character_id))
    post['liked'] = my_sunshine
    my_comment_sunshine = CommentSunshines.filter(session, post_id=post_id, character_id=character_id).all()
    my_comment_sunshine = [m.comment_id for m in my_comment_sunshine]
    parent_comments = session.query(Characters, Comments).filter(Comments.post_id == post_id, Comments.parent == 0)\
        .join(Characters.comment).order_by('created_at').all()
    parent_comments = [dict(CharacterMini.from_orm(p[0]).dict(), **CommentMini.from_orm(p[1]).dict())for p in parent_comments]
    parent_ids = list(set(p['id'] for p in parent_comments))
    child_comments = session.query(Characters, Comments).filter(Comments.post_id == post_id, Comments.parent.in_(parent_ids))\
        .join(Characters.comment).order_by('created_at').all()
    child_comments = [dict(CharacterMini.from_orm(c[0]).dict(), **CommentMini.from_orm(c[1]).dict()) for c in child_comments]
    children = defaultdict(list)
    for c in child_comments:
        children[c['parent']].append(c)
    for i, p in enumerate(parent_comments):
        parent_comments[i]['liked'] = True if p['id'] in my_comment_sunshine else False
        parent_comments[i]['created_at'] = (p['created_at'] + timedelta(hours=9)).isoformat()
        parent_comments[i]['updated_at'] = (p['updated_at'] + timedelta(hours=9)).isoformat()
        parent_comments[i]['children'] = children[p['id']]
        for j, c in enumerate(children[p['id']]):
            parent_comments[i]['children'][j]['liked'] = True if c['id'] in my_comment_sunshine else False
            parent_comments[i]['children'][j]['created_at'] = (c['created_at'] + timedelta(hours=9)).isoformat()
            parent_comments[i]['children'][j]['updated_at'] = (c['updated_at'] + timedelta(hours=9)).isoformat()
    del post['character_id']
    if post['template'] == TemplateType.none:
        return JSONResponse(status_code=200, content=dict(msg="GET_POST_SUCCESS", post=post,
                                                          character_info=character_info, comments=parent_comments))
    elif post['template'] == TemplateType.image:
        img = Images.get(session, post_id=post_id).img
        post['img'] = img
        return JSONResponse(status_code=200, content=dict(msg="GET_IMAGE_SUCCESS", post=post,
                                                          character_info=character_info, comments=parent_comments))
    elif post['template'] == TemplateType.diary:
        diary = Diaries.get(session, post_id=post_id)
        post['title'] = diary.title
        post['weather'] = diary.weather
        post['img'] = diary.img
        post['date'] = diary.date
        post['content'] = diary.content
        return JSONResponse(status_code=200, content=dict(msg="GET_DIARY_SUCCESS", post=post,
                                                          character_info=character_info, comments=parent_comments))
    elif post['template'] == TemplateType.album:
        album = Albums.get(session, post_id=post_id)
        post['title'] = album.title
        post['img'] = album.img
        post['artist'] = album.artist
        post['description'] = album.description
        post['release_date'] = album.release_date
        tracks = Tracks.filter(session, album_id=album.id).all()
        post['tracks'] = [{"title": track.title, "lyric": track.lyric} for track in tracks]
        return JSONResponse(status_code=200, content=dict(msg="GET_ALBUM_SUCCESS", post=post,
                                                          character_info=character_info, comments=parent_comments))

    elif post['template'] == TemplateType.list:
        list_ = Lists.get(session, post_id=post_id)
        post['title'] = list_.title
        post['content'] = list_.content
        list_components = ListComponents.filter(session, list_id=list_.id).all()
        post['components'] = [{"title": component.title, "img": component.img, "content": component.content}
                              for component in list_components]
        return JSONResponse(status_code=200, content=dict(msg="GET_LIST_SUCCESS", post=post,
                                                          character_info=character_info, comments=parent_comments))
