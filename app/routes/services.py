import json
import os
from time import time, sleep

from fastapi import APIRouter
from fastapi.logger import logger
from starlette.background import BackgroundTasks
from starlette.requests import Request

from app.errors import exceptions as ex

router = APIRouter(prefix='/services')


@router.get('')
async def get_all_services(request: Request):
    return dict(your_email=request.state.user.email)
