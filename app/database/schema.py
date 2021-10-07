from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Enum,
    Boolean,
    ForeignKey,
    Text
)
from sqlalchemy.orm import Session, relationship

from app.database.conn import Base, db


class BaseMixin:
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

    def __init__(self):
        self._q = None
        self._session = None
        self.served = None

    def all_columns(self):
        return [c for c in self.__table__.columns if c.primary_key is False and c.name != "created_at"]

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def create(cls, session: Session, auto_commit=False, **kwargs):
        """
        테이블 데이터 적재 전용 함수
        :param session:
        :param auto_commit: 자동 커밋 여부
        :param kwargs: 적재 할 데이터
        :return:
        """
        obj = cls()
        for col in obj.all_columns():
            col_name = col.name
            if col_name in kwargs:
                setattr(obj, col_name, kwargs.get(col_name))
        session.add(obj)
        session.flush()
        if auto_commit:
            session.commit()
        return obj

    @classmethod
    def get(cls, session: Session = None, **kwargs):
        """
        Simply get a Row
        :param session:
        :param kwargs:
        :return:
        """
        sess = next(db.session()) if not session else session
        query = sess.query(cls)
        for key, val in kwargs.items():
            col = getattr(cls, key)
            query = query.filter(col == val)

        if query.count() > 1:
            raise Exception("Only one row is supposed to be returned, but got more than one.")
        result = query.first()
        if not session:
            sess.close()
        return result

    @classmethod
    def filter(cls, session: Session = None, **kwargs):
        """
        Simply get a Row
        :param session:
        :param kwargs:
        :return:
        """
        cond = []
        for key, val in kwargs.items():
            key = key.split("__")
            if len(key) > 2:
                raise Exception("No 2 more dunders")
            col = getattr(cls, key[0])
            if len(key) == 1:
                cond.append((col == val))
            elif len(key) == 2 and key[1] == 'gt':
                cond.append((col > val))
            elif len(key) == 2 and key[1] == 'gte':
                cond.append((col >= val))
            elif len(key) == 2 and key[1] == 'lt':
                cond.append((col < val))
            elif len(key) == 2 and key[1] == 'lte':
                cond.append((col <= val))
            elif len(key) == 2 and key[1] == 'in':
                cond.append((col.in_(val)))
        obj = cls()
        if session:
            obj._session = session
            obj.served = True
        else:
            obj._session = next(db.session())
            obj.served = False
        query = obj._session.query(cls)
        query = query.filter(*cond)
        obj._q = query
        return obj

    @classmethod
    def cls_attr(cls, col_name=None):
        if col_name:
            col = getattr(cls, col_name)
            return col
        else:
            return cls

    def order_by(self, *args: str):
        for a in args:
            if a.startswith("-"):
                col_name = a[1:]
                is_asc = False
            else:
                col_name = a
                is_asc = True
            col = self.cls_attr(col_name)
            self._q = self._q.order_by(col.asc()) if is_asc else self._q.order_by(col.desc())
        return self

    def join(self, target, *props, **kwargs):
        self._q = self._q.join(target, *props, **kwargs)
        return self

    def update(self, auto_commit: bool = False, **kwargs):
        print("kwargs: ", kwargs)
        qs = self._q.update(kwargs)
        get_id = self.id
        ret = None

        self._session.flush()
        if qs > 0:
            ret = self._q.first()
        if auto_commit:
            self._session.commit()
        return ret

    def first(self):
        result = self._q.first()
        self.close()
        return result

    def delete(self, auto_commit: bool = False):
        self._q.delete()
        if auto_commit:
            self._session.commit()

    def all(self):
        # print(self.served)
        result = self._q.all()
        self.close()
        return result

    def count(self):
        result = self._q.count()
        self.close()
        return result

    def close(self):
        if not self.served:
            self._session.close()
        else:
            self._session.flush()


class Users(Base, BaseMixin):
    __tablename__ = "users"
    status = Column(Enum("active", "deleted", "blocked"), default="active")
    email = Column(String(length=255), nullable=False)
    pw = Column(String(length=255), nullable=False)
    name = Column(String(length=255), nullable=False)
    profile_img = Column(String(length=255), nullable=True)
    sns_type = Column(Enum("Email", "Google", "Apple"), nullable=False)
    marketing_agree = Column(Boolean, nullable=True, default=True)
    default_character_id = Column(Integer, nullable=True, default=None)
    character = relationship("Characters", backref="characters", cascade="all, delete-orphan")
    pushtoken = relationship("PushTokens", backref="pushtokens", cascade="all, delete-orphan")


class Follows(Base, BaseMixin):
    __tablename__ = "follows"
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="cascade"), nullable=False)
    follower_id = Column(Integer, ForeignKey("characters.id", ondelete="cascade"), nullable=False)


class Posts(Base, BaseMixin):
    __tablename__ = "posts"
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="cascade"), nullable=False)
    template = Column(Enum("None", "Image", "Diary", "List", "Album"), nullable=True)
    text = Column(Text(), nullable=True)
    num_sunshines = Column(Integer, nullable=False, default=0)
    img = relationship("Images", backref="images", cascade="all, delete-orphan")
    list = relationship("Lists", backref="lists", cascade="all, delete-orphan")
    album = relationship("Albums", backref="albums", cascade="all, delete-orphan")
    diary = relationship("Diaries", backref="diaries", cascade="all, delete-orphan")
    comment = relationship("Comments", backref="post_comment", cascade="all, delete-orphan")
    sunshine = relationship("PostSunshines", backref="post_sunshines", cascade="all, delete-orphan")
    comment_sunshine = relationship("CommentSunshines", backref="post_comment_sunshines", cascade="all, delete-orphan")


class Notifications(Base, BaseMixin):
    __tablename__ = "notifications"
    sender_id = Column(Integer, ForeignKey("characters.id", ondelete="cascade"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("characters.id", ondelete="cascade"), nullable=False)
    category = Column(Enum("LikePost", "LikeComment", "Follow", "Comment"), nullable=False)
    post_id = Column(Integer, nullable=True, default=None)


class Characters(Base, BaseMixin):
    __tablename__ = "characters"
    name = Column(String(length=255), unique=True, nullable=False)
    profile_img = Column(String(length=255), nullable=True)
    birth = Column(Integer, nullable=False)
    job = Column(String(length=45), nullable=False)
    nationality = Column(String(length=45), nullable=False)
    intro = Column(String(length=100), nullable=False)
    tmi = Column(String(length=400), nullable=True)
    num_followers = Column(Integer, nullable=False, default=0)
    num_follows = Column(Integer, nullable=False, default=0)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="cascade"), nullable=False)
    like = relationship("CharacterLikes", backref="character_likes", cascade="all, delete-orphan")
    hate = relationship("CharacterHates", backref="character_hates", cascade="all, delete-orphan")
    followee = relationship("Follows", backref="followed", cascade="all, delete-orphan",
                            foreign_keys=[Follows.character_id])
    follower = relationship("Follows", backref="follow", cascade="all, delete-orphan",
                            foreign_keys=[Follows.follower_id])
    post = relationship("Posts", backref="post", cascade="all, delete-orphan")
    qna = relationship("QnAs", backref="qna", cascade="all, delete-orphan")
    comment = relationship("Comments", backref="character_comment", cascade="all, delete-orphan")
    post_sunshine = relationship("PostSunshines", backref="character_post_sunshines", cascade="all, delete-orphan")
    comment_sunshine = relationship("CommentSunshines", backref="character_comment_sunshines",
                                    cascade="all, delete-orphan")
    qna_sunshine = relationship("QnASunshines", backref="character_qna_sunshines",
                                    cascade="all, delete-orphan")
    sender = relationship("Notifications", backref="senders", cascade="all, delete-orphan", foreign_keys=[Notifications.sender_id])
    receiver = relationship("Notifications", backref="receivers", cascade="all, delete-orphan", foreign_keys=[Notifications.receiver_id])


class CharacterLikes(Base, BaseMixin):
    __tablename__ = "character_likes"
    like = Column(String(length=20), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="cascade"), nullable=False)


class CharacterHates(Base, BaseMixin):
    __tablename__ = "character_hates"
    hate = Column(String(length=20), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="cascade"), nullable=False)


class PostSunshines(Base, BaseMixin):
    __tablename__ = "post_sunshines"
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="cascade"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="cascade"), nullable=False)


class CommentSunshines(Base, BaseMixin):
    __tablename__ = "comment_sunshines"
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="cascade"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="cascade"), nullable=False)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="cascade"), nullable=False)


class Comments(Base, BaseMixin):
    __tablename__ = "comments"
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="cascade"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="cascade"), nullable=False)
    comment = Column(String(length=255), nullable=False)
    parent = Column(Integer, nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)
    num_sunshines = Column(Integer, nullable=False, default=0)
    sunshine = relationship("CommentSunshines", backref="comment_sunshines", cascade="all, delete-orphan")


class Images(Base, BaseMixin):
    __tablename__ = "images"
    img = Column(String(length=255), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="cascade"), nullable=False)


class Lists(Base, BaseMixin):
    __tablename__ = "lists"
    title = Column(String(length=255), nullable=False)
    content = Column(String(length=255), nullable=True)
    img = Column(String(length=255), nullable=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="cascade"), nullable=False)
    component = relationship("ListComponents", backref="components", cascade="all, delete-orphan")


class ListComponents(Base, BaseMixin):
    __tablename__ = "list_components"
    title = Column(String(length=255), nullable=False)
    img = Column(String(length=255), nullable=True)
    content = Column(String(length=255), nullable=True)
    list_id = Column(Integer, ForeignKey("lists.id", ondelete="cascade"), nullable=False)


class Diaries(Base, BaseMixin):
    __tablename__ = "diaries"
    title = Column(String(length=255), nullable=False)
    weather = Column(String(length=32), nullable=True)
    img = Column(String(length=255), nullable=True)
    date = Column(String(length=8), nullable=False)
    content = Column(Text(), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="cascade"), nullable=False)


class Albums(Base, BaseMixin):
    __tablename__ = "albums"
    title = Column(String(length=255), nullable=False)
    img = Column(String(length=255), nullable=True)
    artist = Column(String(length=255), nullable=False)
    description = Column(Text(), nullable=True)
    release_date = Column(String(length=8), nullable=False)
    track = relationship("Tracks", backref="tracks", cascade="all, delete-orphan")
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="cascade"), nullable=False)


class Tracks(Base, BaseMixin):
    __tablename__ = "tracks"
    album_id = Column(Integer, ForeignKey("albums.id", ondelete="cascade"), nullable=False)
    title = Column(String(length=255), nullable=False)
    lyric = Column(Text(), nullable=True)


class QnASunshines(Base, BaseMixin):
    __tablename__ = "qna_sunshines"
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="cascade"), nullable=False)
    qna_id = Column(Integer, ForeignKey("qnas.id", ondelete="cascade"), nullable=False)


class QnAs(Base, BaseMixin):
    __tablename__ = "qnas"
    respondent_id = Column(Integer, ForeignKey("characters.id", ondelete="cascade"), nullable=False)
    question = Column(String(length=255), nullable=False)
    answer = Column(String(length=255), nullable=True)
    num_sunshines = Column(Integer, nullable=False, default=0)
    sunshine = relationship("QnASunshines", backref="qna_sunshines", cascade="all, delete-orphan")


class Questions(Base, BaseMixin):
    __tablename__ = "questions"
    question = Column(String(length=255), nullable=False)


class PushTokens(Base, BaseMixin):
    __tablename__ = "push_tokens"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="cascade"), nullable=False)
    token = Column(String(length=255), nullable=False)
