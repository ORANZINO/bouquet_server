import json
import boto3
import io
from os import environ
from time import time, sleep

from fastapi import APIRouter, UploadFile, File
from fastapi.logger import logger
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.responses import JSONResponse
from types import SimpleNamespace
from app.stargan.solver import Solver
from app.models import SexType
from PIL import Image
from app.errors import exceptions as ex

router = APIRouter(prefix='/services')

args = SimpleNamespace()
args.img_size = 256
args.num_domains = 2
args.latent_dim = 16
args.style_dim = 64
args.w_hpf = 1
args.wing_path = 'stargan/checkpoints/wing.ckpt'
args.checkpoint_dir = 'stargan/checkpoints'
solver = Solver(args)
bucket = environ.get('S3_BUCKET')
region = environ.get('S3_REGION')
s3_client = boto3.client(service_name='s3', aws_access_key_id=environ.get('S3_ACCESS_KEY_ID'),
                         aws_secret_access_key=environ.get('S3_ACCESS_KEY'))


@router.post('/img/upload', status_code=201)
async def upload_img(request: Request, img: UploadFile = File(...)):
    user = request.state.user
    filename = img.filename
    img = Image.open(img.file).resize((256, 256))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    save_name = f'{user.name} {filename}'
    s3_client.upload_fileobj(buf, bucket, save_name)
    upload_url = f"https://{bucket}.s3.{region}.amazonaws.com/{save_name}"

    return JSONResponse(status_code=201, content=dict(msg="UPLOAD_IMAGE_SUCCESS", url=upload_url))


@router.post('/img/style', status_code=201)
async def style_img(request: Request, target_sex: SexType, img: UploadFile = File(...)):
    user = request.state.user
    filename = img.filename
    img = Image.open(img.file).convert('RGB')
    styled_img = solver.style(img, target_sex)
    buf = io.BytesIO()
    styled_img.save(buf, format='PNG')
    buf.seek(0)
    save_name = f'{user.name} {filename}'
    s3_client.upload_fileobj(buf, bucket, save_name)
    upload_url = f"https://{bucket}.s3.{region}.amazonaws.com/{save_name}"

    return JSONResponse(status_code=201, content=dict(msg="STYLE_IMAGE_SUCCESS", url=upload_url))


@router.post('/img/ref')
async def ref_img(request: Request, target_sex: SexType, src: UploadFile = File(...), ref: UploadFile = File(...)):
    user = request.state.user
    filename = src.filename
    src = Image.open(src.file).convert('RGB')
    ref = Image.open(ref.file).convert('RGB')
    refed_img = solver.ref(ref, src, target_sex)
    buf = io.BytesIO()
    refed_img.save(buf, format='PNG')
    buf.seek(0)
    save_name = f'{user.name} {filename}'
    s3_client.upload_fileobj(buf, bucket, save_name)
    upload_url = f"https://{bucket}.s3.{region}.amazonaws.com/{save_name}"

    return JSONResponse(status_code=201, content=dict(msg="REF_IMAGE_SUCCESS", url=upload_url))
