from app.database.schema import Characters, PostSunshines, Images, Tracks, Albums, Diaries, Lists, ListComponents
from app.models import TemplateType, PostRow, CharacterMini
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
    post['type'] = post['template']
    post['template'] = dict()
    if post['type'] == TemplateType.image:
        img = Images.get(session, post_id=post['id']).img
        post['template']['img'] = img
    elif post['type'] == TemplateType.diary:
        diary = Diaries.get(session, post_id=post['id'])
        post['template']['title'] = diary.title
        post['template']['weather'] = diary.weather
        post['template']['img'] = diary.img
        post['template']['date'] = diary.date
        post['template']['content'] = diary.content
    elif post['type'] == TemplateType.album:
        album = Albums.get(session, post_id=post['id'])
        post['template']['title'] = album.title
        post['template']['img'] = album.img
        post['template']['artist'] = album.artist
        post['template']['description'] = album.description
        post['template']['release_date'] = album.release_date
        tracks = Tracks.filter(session, album_id=album.id).all()
        post['template']['tracks'] = [{"title": track.title, "lyric": track.lyric} for track in tracks]
    elif post['type'] == TemplateType.list:
        list_ = Lists.get(session, post_id=post['id'])
        post['template']['title'] = list_.title
        post['template']['content'] = list_.content
        post['template']['img'] = list_.img
        list_components = ListComponents.filter(session, list_id=list_.id).all()
        post['template']['components'] = [{"title": component.title, "img": component.img, "content": component.content}
                                          for component in list_components]
    return post
