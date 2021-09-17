
from fastapi import APIRouter, Depends, Header, Body
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from app.utils.post_utils import process_post, process_comment
from app.database.conn import db
from app.database.schema import Posts, Images, Albums, Diaries, Lists, ListComponents, Tracks, Comments, Characters

from app.models import Post, Comment, PostResponseWithComments, ID, Message, PostList
from app.utils.examples import get_post_responses, create_post_requests

router = APIRouter(prefix='/post')

post_keys = ["character_id", "template", "text"]


@router.post('', status_code=201, response_model=ID)
async def create_post(post: Post = Body(..., examples=create_post_requests), session: Session = Depends(db.session)):
    post_args = {
        "character_id": post.character_id,
        "text": post.text,
        "template": "None" if post.template is None else post.template.type
    }
    new_post = Posts.create(session, True, **dict(post_args))
    if post.template is not None:
        template_type = post.template.type
        template = dict(post.template)
        template['post_id'] = new_post.id
        del template['type']
        if template_type == "Image":
            Images.create(session, True, **template)
        elif template_type == "Diary":
            Diaries.create(session, True, **template)
        elif template_type == "Album":
            tracks = template['tracks']
            del template['tracks']
            template['artist'] = Characters.get(session, id=post.character_id).name
            new_album = Albums.create(session, True, **template)
            for track in tracks:
                track['album_id'] = new_album.id
                Tracks.create(session, True, **track)
        elif template_type == "List":
            components = template['components']
            del template['components']
            new_list = Lists.create(session, True, **template)
            for component in components:
                component['list_id'] = new_list.id
                ListComponents.create(session, True, **component)

    return JSONResponse(status_code=201, content=dict(id=new_post.id))


@router.post('/comment', status_code=201, response_model=ID)
async def create_comment(comment: Comment, session: Session = Depends(db.session)):
    new_comment = Comments.create(session, True, **dict(comment))
    return JSONResponse(status_code=201, content=dict(id=new_comment.id))


@router.delete('/comment/{comment_id}', status_code=204, responses={
    400: dict(description="Not your comment", model=Message)
})
async def delete_comment(comment_id: int, session: Session = Depends(db.session)):
    Comments.filter(session, id=comment_id).delete(auto_commit=True)
    Comments.filter(session, parent=comment_id).delete(auto_commit=True)
    return JSONResponse(status_code=204)


@router.get('/{post_id}', status_code=200, response_model=PostResponseWithComments, responses=get_post_responses)
async def get_post(post_id: int, character_id: int = Header(None), session: Session = Depends(db.session)):
    post = process_post(session, character_id, Posts.get(session, id=post_id))
    post['comments'] = process_comment(session, post_id, character_id)
    return JSONResponse(status_code=200, content=post)


@router.get('/character/{character_name}/{page_num}', status_code=200, response_model=PostList, responses={
    404: dict(description="No such character", model=Message)
})
async def get_character_posts(character_name: str, page_num: int, session: Session = Depends(db.session)):
    character = Characters.get(session, name=character_name)
    if character_name is None or not character:
        return JSONResponse(status_code=404, content=dict(msg="WRONG_CHARACTER_NAME"))
    posts = session.query(Posts).filter(Posts.character_id == character.id).order_by(Posts.created_at.desc()) \
        .offset((page_num - 1) * 10).limit(10).all()
    posts = [process_post(session, character.id, post) for post in posts]
    return JSONResponse(status_code=200, content=posts)






