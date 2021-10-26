from dataclasses import asdict

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.database.conn import db
from app.common.config import conf
from app.middlewares.token_validator import access_control
from app.middlewares.trusted_hosts import TrustedHostMiddleware
from app.routes import index, auth, users, imgs, characters, posts, search, qnas, notification

API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)


def create_app():
    """
    앱 함수 실행
    :return:
    """
    c = conf()
    app = FastAPI(title="Bouquet")
    conf_dict = asdict(c)
    db.init_app(app, **conf_dict)

    # 미들웨어 정의
    app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=access_control)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=conf().ALLOW_SITE,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=conf().TRUSTED_HOSTS, except_path=["/health"])

    # 라우터 정의
    app.include_router(index.router, tags=["Home"])
    app.include_router(auth.router, tags=["Authentication"])
    app.include_router(search.router, tags=["Search"])
    if conf().DEBUG:
        app.include_router(imgs.router, tags=["Images"], dependencies=[Depends(API_KEY_HEADER)])
    else:
        app.include_router(imgs.router, tags=["Images"])
    app.include_router(users.router, tags=["Users"], dependencies=[Depends(API_KEY_HEADER)])
    app.include_router(characters.router, tags=["Characters"], dependencies=[Depends(API_KEY_HEADER)])
    app.include_router(posts.router, tags=["Posts"], dependencies=[Depends(API_KEY_HEADER)])
    app.include_router(qnas.router, tags=["Q&As"], dependencies=[Depends(API_KEY_HEADER)])
    app.include_router(notification.router, tags=["Notification"], dependencies=[Depends(API_KEY_HEADER)])
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
