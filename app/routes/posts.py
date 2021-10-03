
from fastapi import APIRouter, Depends, Header, Body, Request
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from app.utils.post_utils import process_post, process_comment
from app.database.conn import db
from app.database.schema import Posts, Images, Albums, Diaries, Lists, ListComponents, Tracks, Comments, Characters, PostSunshines
from typing import Optional
from app.models import Post, Comment, PostResponseWithComments, Message, ID, PostListWithNum
from app.utils.examples import get_post_responses, create_post_requests
from app.middlewares.token_validator import token_decode

router = APIRouter(prefix='/post')

post_keys = ["character_id", "template", "text"]


@router.post('', status_code=201, response_model=ID, responses={
    400: dict(description="You need to login as a character", model=Message),
    404: dict(description="No such character", model=Message)
})
async def create_post(request: Request, post: Post = Body(..., examples=create_post_requests), session: Session = Depends(db.session)):
    user = request.state.user
    if user.default_character_id is None:
        return JSONResponse(status_code=400, content=dict(msg="NO_CHARACTER_ID"))
    character = Characters.get(session, id=user.default_character_id)
    if not character:
        return JSONResponse(status_code=404, content=dict(msg="NO_MATCH_CHARACTER"))
    post_args = {
        "character_id": user.default_character_id,
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


@router.delete('', status_code=204, responses={
    400: dict(description="Not your post", model=Message),
    404: dict(description="No such post", model=Message)
})
async def delete_post(request: Request, post_id: int, session: Session = Depends(db.session)):
    user = request.state.user
    post = Posts.get(session, id=post_id)
    if not post:
        return JSONResponse(status_code=404, content=dict(msg="NO_MATCH_POST"))
    elif user.default_character_id != post.character_id:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_CHARACTER_ID"))
    Posts.filter(session, id=post_id).delete(auto_commit=True)
    return JSONResponse(status_code=204)


@router.post('/comment', status_code=201, response_model=ID)
async def create_comment(request: Request, comment: Comment, session: Session = Depends(db.session)):
    user = request.state.user
    comment = dict(comment)
    comment['character_id'] = user.default_character_id
    new_comment = Comments.create(session, True, **dict(comment))
    return JSONResponse(status_code=201, content=dict(id=new_comment.id))


@router.delete('/comment/{comment_id}', status_code=204, responses={
    400: dict(description="Not your comment", model=Message)
})
async def delete_comment(request: Request, comment_id: int, session: Session = Depends(db.session)):
    user = request.state.user
    comment = Comments.get(session, id=comment_id)
    if comment.character_id == user.default_character_id:
        Comments.filter(session, id=comment_id).delete(auto_commit=True)
        Comments.filter(session, parent=comment_id).delete(auto_commit=True)
    else:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_CHARACTER"))
    return JSONResponse(status_code=204)


@router.get('/{post_id}', status_code=200, response_model=PostResponseWithComments, responses=get_post_responses)
async def get_post(post_id: int, token: Optional[str] = Header(None), session: Session = Depends(db.session)):
    post = Posts.get(session, id=post_id)
    if post is None:
        return JSONResponse(status_code=404, content=dict(msg="NO_MATCH_POST"))
    elif token is None:
        character_id = None
    else:
        user = await token_decode(access_token=token)
        character_id = user['default_character_id']
    post = process_post(session, character_id, post)
    post['comments'] = process_comment(session, post_id, character_id)
    return JSONResponse(status_code=200, content=post)


@router.get('/character/{character_name}/{page_num}', status_code=200, response_model=PostListWithNum, responses={
    404: dict(description="No such character", model=Message)
})
async def get_character_posts(character_name: str, page_num: int, session: Session = Depends(db.session)):
    character = Characters.get(session, name=character_name)
    if character_name is None or not character:
        return JSONResponse(status_code=404, content=dict(msg="WRONG_CHARACTER_NAME"))
    posts = session.query(Posts).filter(Posts.character_id == character.id).order_by(Posts.created_at.desc()) \
        .offset((page_num - 1) * 10).limit(10).all()
    posts = [process_post(session, character.id, post) for post in posts]
    total_post_num = Posts.filter(session, character_id=character.id).count()
    return JSONResponse(status_code=200, content=dict(posts=posts, total_post_num=total_post_num))


@router.post('/like/{post_id}', status_code=200, responses={
    404: dict(description="No such post", model=Message)
})
async def like(request: Request, post_id: int, session: Session = Depends(db.session)):
    user = request.state.user
    post = Posts.get(session, id=post_id)
    if not post:
        return JSONResponse(status_code=404, content=dict(msg="WRONG_POST_ID"))
    like_exists = PostSunshines.get(session, character_id=user.default_character_id, post_id=post_id)
    if like_exists:
        session.query(Posts).filter_by(id=post_id).update({Posts.num_sunshines: Posts.num_sunshines - 1})
        session.commit()
        session.flush()
        PostSunshines.filter(session, character_id=user.default_character_id, post_id=post.id).delete(True)
        return JSONResponse(status_code=200, content=dict(msg="UNLIKE_SUCCESS"))
    else:
        session.query(Posts).filter_by(id=post_id).update({Posts.num_sunshines: Posts.num_sunshines - 1})
        session.commit()
        session.flush()
        PostSunshines.create(session, True, character_id=user.default_character_id, post_id=post.id)
        return JSONResponse(status_code=200, content=dict(msg="LIKE_SUCCESS"))







