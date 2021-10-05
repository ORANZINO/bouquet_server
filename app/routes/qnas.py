
from fastapi import APIRouter, Depends, Header, Body, Request
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from starlette.responses import JSONResponse
from app.utils.post_utils import process_post, process_comment
from app.database.conn import db
from app.database.schema import Characters, QnASunshines, QnAs, Questions
from typing import Optional
from app.models import ID, QnA, Message, QnARow, QnAList, Question
from app.utils.notification_utils import send_notification
from app.middlewares.token_validator import token_decode

router = APIRouter(prefix='/qna')


@router.post('', status_code=201, response_model=ID)
async def create_qna(request: Request, qna: QnA, session: Session = Depends(db.session)):
    user = request.state.user
    qna = dict(qna)
    qna['respondent_id'] = user.default_character_id
    new_qna = QnAs.create(session, True, **qna)
    return JSONResponse(status_code=201, content=dict(id=new_qna.id))


@router.get('/{character_name}', status_code=200, response_model=QnAList, responses={
    404: dict(description="No such character", model=Message)
})
async def get_character_qna(character_name: str, token: Optional[str] = Header(None), page_num: int = Header(1), session: Session = Depends(db.session)):
    character = Characters.get(session, name=character_name)
    if not character:
        return JSONResponse(status_code=404, content=dict(msg="NO_MATCH_CHARACTER"))
    qnas = session.query(QnAs).filter(QnAs.respondent_id == character.id).order_by(QnAs.created_at.desc()) \
        .offset((page_num - 1) * 10).limit(10).all()
    qnas = [QnARow.from_orm(qna).dict() for qna in qnas]
    if token is not None:
        user = await token_decode(access_token=token)
        character_id = user['default_character_id']
        for i, qna in enumerate(qnas):
            qnas[i]['liked'] = bool(QnASunshines.get(session, character_id=character_id, qna_id=qna['id']))
    else:
        for i, qna in enumerate(qnas):
            qnas[i]['liked'] = False

    return JSONResponse(status_code=200, content=dict(character_name=character.name, profile_img=character.profile_img,
                                                      qnas=qnas))


@router.post('/like/{qna_id}', status_code=200, response_model=Message, responses={
    400: dict(description="You should have character to like", model=Message),
    404: dict(description="No such Q&A", model=Message)
})
async def like_qna(request: Request, qna_id: int, session: Session = Depends(db.session)):
    user = request.state.user
    if user.default_character_id is None:
        return JSONResponse(status_code=400, content=dict(msg="NO_GIVEN_CHARACTER"))
    qna = QnAs.get(session, id=qna_id)
    if not qna:
        return JSONResponse(status_code=404, content=dict(msg="NO_MATCH_Q&A"))
    like_exists = QnASunshines.get(session, character_id=user.default_character_id, qna_id=qna_id)
    if like_exists:
        session.query(QnAs).filter_by(id=qna_id).update({QnAs.num_sunshines: QnAs.num_sunshines - 1})
        session.commit()
        session.flush()
        QnASunshines.filter(session, character_id=user.default_character_id, qna_id=qna.id).delete(True)
        return JSONResponse(status_code=200, content=dict(msg="UNLIKE_SUCCESS"))
    else:
        session.query(QnAs).filter_by(id=qna_id).update({QnAs.num_sunshines: QnAs.num_sunshines + 1})
        session.commit()
        session.flush()
        QnASunshines.create(session, True, character_id=user.default_character_id, qna_id=qna.id)
        return JSONResponse(status_code=200, content=dict(msg="LIKE_SUCCESS"))


@router.delete('', status_code=204, responses={
    400: dict(description="Not your Q&A", model=Message)
})
async def delete_qna(request: Request, qna_id: int, session: Session = Depends(db.session)):
    user = request.state.user
    qna = QnAs.get(session, id=qna_id)
    if qna.respondent_id == user.default_character_id:
        QnAs.filter(session, id=qna_id).delete(True)
    else:
        return JSONResponse(status_code=400, content=dict(msg="WRONG_CHARACTER"))
    return JSONResponse(status_code=204)


@router.post('/question', status_code=201, response_model=ID)
async def create_question(question: Question, session: Session = Depends(db.session)):
    new_qna = Questions.create(session, True, question=question.question)
    return JSONResponse(status_code=201, content=dict(id=new_qna.id))


@router.get('/question/new', status_code=200, response_model=Question)
async def get_question(session: Session = Depends(db.session)):
    question = session.query(Questions).order_by(func.rand()).first()
    return JSONResponse(status_code=200, content=dict(question=question.question))

