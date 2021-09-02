from collections import defaultdict
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.utils.post_utils import process_post
from app.database.conn import db
from app.database.schema import Posts, Images, Albums, Diaries, Lists, ListComponents, Tracks, Comments, Characters, PostSunshines, CommentSunshines
from datetime import timedelta

from app.models import Post, Image, Diary, Album, List, TemplateType, PostRow, Comment, CharacterMini, CommentMini, ID

router = APIRouter(prefix='/post')

post_keys = ["character_id", "template", "text"]

post_responses = {
    201: {
      "id": 1,
      "created_at": "2021-09-02T15:25:46",
      "updated_at": "2021-09-02T15:25:46",
      "template": {},
      "text": "이것이 포스팅이다.",
      "num_sunshines": 0,
      "character_name": "오란지",
      "character_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
      "liked": False,
      "type": "None",
      "comments": [
        {
          "name": "오란지",
          "profile_img": "https://i.pinimg.com/736x/05/79/5a/05795a16b647118ffb6629390e995adb.jpg",
          "id": 1,
          "created_at": "2021-09-02T15:26:31",
          "updated_at": "2021-09-02T15:26:31",
          "comment": "이 노래를 불러보지만 내 진심이 닿을지 몰라",
          "parent": 0,
          "deleted": False,
          "num_sunshines": 0,
          "liked": False,
          "children": []
        }
      ]
    }
}


@router.post('', status_code=201, response_model=ID)
async def create_post(post: Post, session: Session = Depends(db.session)):
    new_post = Posts.create(session, True, **dict(post))
    return JSONResponse(status_code=201, content=dict(id=new_post.id))


@router.post('/img', status_code=201, response_model=ID)
async def create_image(image: Image, session: Session = Depends(db.session)):
    image = dict(image)
    post = {k: image[k] for k in image if k in post_keys}
    img = image['img']
    new_post = Posts.create(session, True, **dict(post))
    Images.create(session, True, img=img, post_id=new_post.id)
    return JSONResponse(status_code=201, content=dict(id=new_post.id))


@router.post('/diary', status_code=201, response_model=ID)
async def create_diary(diary: Diary, session: Session = Depends(db.session)):
    diary = dict(diary)
    post = {k: diary[k] for k in diary if k in post_keys}
    new_post = Posts.create(session, True, **dict(post))
    diary = {k: diary[k] for k in diary if k not in post_keys}
    diary['post_id'] = new_post.id
    Diaries.create(session, True, **dict(diary))
    return JSONResponse(status_code=201, content=dict(id=new_post.id))


@router.post('/album', status_code=201, response_model=ID)
async def create_album(album: Album, session: Session = Depends(db.session)):
    album = dict(album)
    post = {k: album[k] for k in album if k in post_keys}
    new_post = Posts.create(session, True, **dict(post))
    tracks = album['tracks']
    del album['tracks']
    album['artist'] = Characters.get(session, id=post['character_id']).name
    album = {k: album[k] for k in album if k not in post_keys}
    album['post_id'] = new_post.id
    new_album = Albums.create(session, True, **dict(album))
    for track in tracks:
        track['album_id'] = new_album.id
        Tracks.create(session, True, **dict(track))
    return JSONResponse(status_code=201, content=dict(id=new_post.id))


@router.post('/list', status_code=201, response_model=ID)
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
    return JSONResponse(status_code=201, content=dict(id=new_post.id))


@router.post('/comment', status_code=201, response_model=ID)
async def create_comment(comment: Comment, session: Session = Depends(db.session)):
    new_comment = Comments.create(session, True, **dict(comment))
    return JSONResponse(status_code=201, content=dict(id=new_comment.id))


@router.get('/{post_id}', status_code=200, responses=post_responses)
async def get_post(post_id: int, character_id: int = Header(None), session: Session = Depends(db.session)):
    post = process_post(character_id, Posts.get(session, id=post_id), session)
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
    post['comments'] = parent_comments
    return JSONResponse(status_code=200, content=post)

