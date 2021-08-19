from app.database.schema import Posts, Follows, Characters, PostSunshines, Images, Tracks, Albums, Diaries, Lists, ListComponents
from app.models import Post, Image, Diary, Album, List, TemplateType, PostRow, Comment, CharacterRow, CharacterMini, CommentMini
from datetime import timedelta


def process_post(character_id, post, session):
    post = PostRow.from_orm(post).dict()
    post['created_at'] = (post['created_at'] + timedelta(hours=9)).isoformat()
    post['updated_at'] = (post['updated_at'] + timedelta(hours=9)).isoformat()
    character_info = CharacterMini.from_orm(Characters.get(session, id=post['character_id'])).dict()
    post['character_name'] = character_info['name']
    post['character_img'] = character_info['profile_img']
    my_sunshine = False
    if character_id is not None:
        my_sunshine = bool(PostSunshines.get(session, post_id=post['id'], character_id=character_id))
    post['liked'] = my_sunshine

    if post['template'] == TemplateType.image:
        img = Images.get(session, post_id=post['id']).img
        post['img'] = img
    elif post['template'] == TemplateType.diary:
        diary = Diaries.get(session, post_id=post['id'])
        post['title'] = diary.title
        post['weather'] = diary.weather
        post['img'] = diary.img
        post['date'] = diary.date
        post['content'] = diary.content
    elif post['template'] == TemplateType.album:
        album = Albums.get(session, post_id=post['id'])
        post['title'] = album.title
        post['img'] = album.img
        post['artist'] = album.artist
        post['description'] = album.description
        post['release_date'] = album.release_date
        tracks = Tracks.filter(session, album_id=album.id).all()
        post['tracks'] = [{"title": track.title, "lyric": track.lyric} for track in tracks]
    elif post['template'] == TemplateType.list:
        list_ = Lists.get(session, post_id=post['id'])
        post['title'] = list_.title
        post['content'] = list_.content
        list_components = ListComponents.filter(session, list_id=list_.id).all()
        post['components'] = [{"title": component.title, "img": component.img, "content": component.content}
                              for component in list_components]
    return post

