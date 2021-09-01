from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database.conn import db
from app.database.schema import Users

from app.models import UserMe, UserUpdate, Message

router = APIRouter(prefix='/user')


@router.get('/', status_code=200, response_model=UserMe, responses={
    400: dict(description="Given user doesn't exist", model=Message)
})
async def get_me(request: Request):
    user = request.state.user
    user_info = Users.get(id=user.id)
    if not user_info:
        return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))
    return JSONResponse(status_code=200, content=UserMe.from_orm(user_info).dict())


@router.patch('/', status_code=204, description="Successfully updated user")
async def update_me(request: Request, info: UserUpdate, session: Session = Depends(db.session)):
    user = request.state.user
    res = Users.filter(session, id=user.id).update(True, **dict(info))
    return JSONResponse(status_code=204)


@router.delete('/', status_code=204, description="Successfully deleted user")
async def delete_me(request: Request):
    user = request.state.user
    Users.filter(id=user.id).delete(auto_commit=True)
    return JSONResponse(status_code=204)






