from collections import defaultdict
from app.database.schema import Characters, PostSunshines, Images, Tracks, Albums, Diaries, Lists, ListComponents, \
    CommentSunshines, Comments
from app.models import PostRow, CharacterMini, CommentMini
from datetime import timedelta


def process_post(session, character_id, post):
    post = PostRow.from_orm(post).dict()
    post['created_at'] = (post['created_at'] + timedelta(hours=9)).isoformat()
    post['updated_at'] = (post['updated_at'] + timedelta(hours=9)).isoformat()
    post['character_info'] = CharacterMini.from_orm(Characters.get(session, id=post['character_id'])).dict()
    my_sunshine = False
    if character_id is not None:
        my_sunshine = bool(PostSunshines.get(session, post_id=post['id'], character_id=character_id))
    post['liked'] = my_sunshine
    template_type = post['template']
    post['template'] = dict()
    post['template']['type'] = template_type
    if template_type == "Image":
        img = Images.get(session, post_id=post['id']).img
        post['template']['img'] = img
    elif template_type == "Diary":
        diary = Diaries.get(session, post_id=post['id'])
        post['template']['title'] = diary.title
        post['template']['weather'] = diary.weather
        post['template']['img'] = diary.img
        post['template']['date'] = diary.date
        post['template']['content'] = diary.content
    elif template_type == "Album":
        album = Albums.get(session, post_id=post['id'])
        post['template']['title'] = album.title
        post['template']['img'] = album.img
        post['template']['artist'] = album.artist
        post['template']['description'] = album.description
        post['template']['release_date'] = album.release_date
        tracks = Tracks.filter(session, album_id=album.id).all()
        post['template']['tracks'] = [{"title": track.title, "lyric": track.lyric} for track in tracks]
    elif template_type == "List":
        list_ = Lists.get(session, post_id=post['id'])
        post['template']['title'] = list_.title
        post['template']['content'] = list_.content
        post['template']['img'] = list_.img
        list_components = ListComponents.filter(session, list_id=list_.id).all()
        post['template']['components'] = [{"title": component.title, "img": component.img, "content": component.content}
                                          for component in list_components]
    return post


def process_comment(session, post_id, character_id):
    my_comment_sunshine = CommentSunshines.filter(session, post_id=post_id, character_id=character_id).all()
    my_comment_sunshine = [m.comment_id for m in my_comment_sunshine]
    parent_comments = session.query(Characters, Comments).filter(Comments.post_id == post_id, Comments.parent == 0) \
        .join(Characters.comment).order_by('created_at').all()
    parent_comments = [dict(CommentMini.from_orm(p[1]).dict(), character_info=CharacterMini.from_orm(p[0]).dict()) for p in
                       parent_comments]
    parent_ids = list(set(p['id'] for p in parent_comments))

    child_comments = session.query(Characters, Comments).filter(Comments.post_id == post_id,
                                                                Comments.parent.in_(parent_ids)) \
        .join(Characters.comment).order_by('created_at').all()
    child_comments = [dict(CommentMini.from_orm(c[1]).dict(), character_info=CharacterMini.from_orm(c[0]).dict()) for c in
                      child_comments]
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

    return parent_comments

