
from fastapi import APIRouter, Depends, Header, Body, Request
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from app.utils.post_utils import process_post, process_comment
from app.database.conn import db
from app.database.schema import Characters, QnASunshines, QnAs

from app.models import ID, QnA, Message, QnARow, QnAList
from app.utils.examples import get_post_responses, create_post_requests

router = APIRouter(prefix='/qna')


@router.post('', status_code=201, response_model=ID)
async def create_qna(request: Request, qna: QnA, session: Session = Depends(db.session)):
    user = request.state.user
    qna.respondent_id = user.default_character_id
    new_qna = QnAs.create(session, True, **dict(qna))
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