from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database.conn import db
from app.database.schema import Users

from app.models import UserMe, UserUpdate

router = APIRouter(prefix='/user')


@router.get('/me')
async def get_me(request: Request):
    user = request.state.user
    user_info = Users.get(id=user.id)
    return JSONResponse(status_code=200, content=dict(msg="READ_USER_SUCCESS", user=UserMe.from_orm(user_info).dict()))


@router.put('/me')
async def put_me(request: Request, info: UserUpdate, session: Session = Depends(db.session)):
    user = request.state.user
    res = Users.filter(session, id=user.id).update(True, **dict(info))
    return JSONResponse(status_code=200, content=dict(msg="UPDATE_USER_SUCCESS"))


@router.delete('/me', status_code=200)
async def delete_me(request: Request):
    user = request.state.user
    Users.filter(id=user.id).delete(auto_commit=True)
    return JSONResponse(status_code=200, content=dict(msg="DELETE_USER_SUCCESS"))






