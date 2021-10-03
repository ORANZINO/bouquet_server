
from fastapi import APIRouter, Depends, Header, Body, Request
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from starlette.responses import JSONResponse
from app.utils.post_utils import process_post, process_comment
from app.database.conn import db
from app.database.schema import Characters, QnASunshines, QnAs, Questions

from app.models import ID, QnA, Message, QnARow, QnAList, Question
from app.utils.examples import get_post_responses, create_post_requests

router = APIRouter(prefix='/qna')


@router.post('', status_code=201, response_model=ID)
async def create_qna(request: Request, qna: QnA, session: Session = Depends(db.session)):
    user = request.state.user
    qna = dict(qna)
    qna['respondent_id'] = user.default_character_id
    new_qna = QnAs.create(session, True, **qna)
    return JSONResponse(status_code=201, content=dict(id=new_qna.id))


@router.get('/{character_name}/{page_num}', status_code=200, response_model=QnAList, responses={
    404: dict(description="No such character", model=Message)
})
async def get_character_qna(character_name: str, page_num: int, session: Session = Depends(db.session)):
    character = Characters.get(session, name=character_name)
    if not character:
        return JSONResponse(status_code=404, content=dict(msg="NO_MATCH_CHARACTER"))
    qnas = session.query(QnAs).filter(QnAs.respondent_id == character.id).order_by(QnAs.created_at.desc()) \
        .offset((page_num - 1) * 10).limit(10).all()
    qnas = [QnARow.from_orm(qna).dict() for qna in qnas]
    for i, qna in enumerate(qnas):
        qnas[i]['liked'] = bool(QnASunshines.get(session, character_id=character.id, qna_id=qna.id))

    return JSONResponse(status_code=201, content=dict(character_name=character.name, profile_img=character.profile_img,
                                                      qnas=qnas))


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


@router.get('/question', status_code=200, response_model=Question)
async def get_question(session: Session = Depends(db.session)):
    question = session.query(Questions).order_by(func.rand()).first()
    return JSONResponse(status_code=200, content=dict(question=question.question))
