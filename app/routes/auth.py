from datetime import datetime, timedelta

import bcrypt
import boto3
from os import environ
import jwt
from fastapi import APIRouter, Depends, Header, Body

from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from botocore.exceptions import ClientError
from app.common.consts import JWT_SECRET, JWT_ALGORITHM
from app.database.conn import db
from app.database.schema import Users, Characters
from app.models import SnsType, Token, UserToken, UserRegister, UserLogin, Email, UserName, CharacterName, Duplicated, \
    Message, VerificationCode, EmailWithPW
from random import randint

"""
1. 구글 로그인을 위한 구글 앱 준비 (구글 개발자 도구)
2. FB 로그인을 위한 FB 앱 준비 (FB 개발자 도구)
3. 카카오 로그인을 위한 카카오 앱준비( 카카오 개발자 도구)
4. 이메일, 비밀번호로 가입 (v)
5. 가입된 이메일, 비밀번호로 로그인, (v)
6. JWT 발급 (v)

7. 이메일 인증 실패시 이메일 변경
8. 이메일 인증 메일 발송
9. 각 SNS 에서 Unlink 
10. 회원 탈퇴
11. 탈퇴 회원 정보 저장 기간 동안 보유(법적 최대 한도 내에서, 가입 때 약관 동의 받아야 함, 재가입 방지 용도로 사용하면 가능)

400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
405 Method not allowed
500 Internal Error
502 Bad Gateway 
504 Timeout
200 OK
201 Created

"""

router = APIRouter(prefix="/auth")


@router.post("/email", status_code=200, response_model=VerificationCode, responses={
    202: dict(description="Given email is already being used.", model=Message),
    500: dict(description="Failed sending the email.", model=Message)
})
async def verify_email(recipient: Email = Body(...), session: Session = Depends(db.session)):
    user = Users.get(session, email=recipient.email)
    if user:
        return JSONResponse(status_code=202, content=dict(msg="EMAIL_EXISTS"))
    sender = "Bouquet <noreply@bouquet.ooo>"
    title = "Bouquet 서비스에 가입하기 위한 이메일 인증 메일입니다."
    charset = "UTF-8"
    verification_num = randint(0, 999999)
    verification_code = str(verification_num)
    verification_code = '0' * (6 - len(verification_code)) + verification_code
    client = boto3.client(service_name='ses',
                          region_name=environ.get("SES_REGION"),
                          aws_access_key_id=environ.get('SES_ACCESS_KEY_ID'),
                          aws_secret_access_key=environ.get('SES_ACCESS_KEY'))
    body_html = f"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
      <title>Email from Bouquet</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    </head>
    <body>
      <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#ffffff">
        <tr>
          <td style="padding-top:40px; padding-bottom:0; padding-left: 20px; padding-right: 0">
            <img src="https://bouquet-storage.s3.ap-northeast-2.amazonaws.com/c535fa74-239d-11ec-8f8a-0242ac110002.png" alt="Bouquet Logo" width="40" height="40" />
          </td>
        </tr>
        <tr>
          <td style="padding-left:20px; padding-right:0; padding-top:60px; padding-bottom:0; font-size:32px;">
            메일 인증
          </td>
        </tr>
        <tr>
          <td style="padding-left:20px; padding-right:0; padding-top:40px; padding-bottom:0; font-size:16px; color: #3c3c3c">
            안녕하세요. Bouquet에서 새로운 모습을 꽃피우고 계시군요!<br />
            <br />
            인증 번호는 <b>{verification_code}</b>입니다.<br />
            인증 번호를 입력해서 회원가입을 계속 진행해 보세요.<br />
            <br />
            Bouquet를 이용해 주셔서 감사합니다.<br />
            문제나 궁금한 점, 피드백 등은 언제나 Bouquet 팀으로 연락 주세요.<br />
            <br/>
            <b>Bouquet</b> 드림<br />
            support@bouquet.ooo
          </td>
        </tr>
        <tr>
          <td style="padding-left:20px; padding-right:0; padding-top:40px; padding-bottom:0;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#ffffff" style="padding-top:40px; padding-bottom:0; padding-left:0; padding-right:0; border-top-style:solid;border-top-color:#ebeaef;border-width:1px">
              <tr style="color:#999999; font-size:14px;">
                <td>
                  이 메일은 Bouquet 가입 과정에서 메일 인증을 위해 발송되었습니다.<br />
                  메일 인증 요청을 보낸 적이 없다면, 이 메일을 무시해 주세요.
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [recipient.email]
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': body_html,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': title,
                },
            },
            Source=sender,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return JSONResponse(status_code=500, content=dict(msg="FAILED_SENDING_EMAIL"))
    else:
        print(f"Email sent! Message ID: {response['MessageId']}")
        return JSONResponse(status_code=200, content=dict(verification_code=verification_code))


@router.post("/email/check", status_code=200, response_model=Duplicated)
async def check_email(email: Email = Body(...), session: Session = Depends(db.session)):
    user = Users.get(session, email=email.email)
    return {"duplicated": bool(user)}


@router.post('/user/check', status_code=200, response_model=Duplicated)
async def check_user_name(user_name: UserName = Body(...), session: Session = Depends(db.session)):
    user = Users.get(session, name=user_name.user_name)
    return {"duplicated": bool(user)}


@router.post('/character/check', status_code=200, response_model=Duplicated)
async def check_character_name(character_name: CharacterName = Body(...), session: Session = Depends(db.session)):
    character = Characters.get(session, name=character_name.character_name)
    return {"duplicated": bool(character)}


@router.post("/user/email", status_code=200, response_model=VerificationCode, responses={
    404: dict(description="Given email doesn't exist.", model=Message),
    500: dict(description="Failed sending the email.", model=Message)
})
async def verify_user_email(recipient: Email = Body(...), session: Session = Depends(db.session)):
    user = Users.get(session, email=recipient.email)
    if not user:
        return JSONResponse(status_code=404, content=dict(msg="NO_MATCH_EMAIL"))
    sender = "Bouquet <noreply@bouquet.ooo>"
    title = "Bouquet 서비스에서 비밀번호 변경을 위한 이메일 인증 메일입니다."
    charset = "UTF-8"
    verification_num = randint(0, 999999)
    verification_code = str(verification_num)
    verification_code = '0' * (6 - len(verification_code)) + verification_code
    client = boto3.client(service_name='ses',
                          region_name=environ.get("SES_REGION"),
                          aws_access_key_id=environ.get('SES_ACCESS_KEY_ID'),
                          aws_secret_access_key=environ.get('SES_ACCESS_KEY'))
    body_html = f"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
      <title>Email from Bouquet</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    </head>
    <body>
      <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#ffffff">
        <tr>
          <td style="padding-top:40px; padding-bottom:0; padding-left: 20px; padding-right: 0">
            <img src="https://bouquet-storage.s3.ap-northeast-2.amazonaws.com/c535fa74-239d-11ec-8f8a-0242ac110002.png" alt="Bouquet Logo" width="40" height="40" />
          </td>
        </tr>
        <tr>
          <td style="padding-left:20px; padding-right:0; padding-top:60px; padding-bottom:0; font-size:32px;">
            메일 인증
          </td>
        </tr>
        <tr>
          <td style="padding-left:20px; padding-right:0; padding-top:40px; padding-bottom:0; font-size:16px; color: #3c3c3c">
            안녕하세요. 비밀번호를 잊으셔서 재미있는 Bouquet를 이용하지 못하고 계시단 소식을 듣고 달려왔습니다!<br />
            <br />
            인증 번호는 <b>{verification_code}</b>입니다.<br />
            인증 번호를 입력해서 비밀번호 변경을 진행해 보세요.<br />
            <br />
            Bouquet를 이용해 주셔서 감사합니다.<br />
            문제나 궁금한 점, 피드백 등은 언제나 Bouquet 팀으로 연락 주세요.<br />
            <br/>
            <b>Bouquet</b> 드림<br />
            noreply@bouquet.ooo
          </td>
        </tr>
        <tr>
          <td style="padding-left:20px; padding-right:0; padding-top:40px; padding-bottom:0;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#ffffff" style="padding-top:40px; padding-bottom:0; padding-left:0; padding-right:0; border-top-style:solid;border-top-color:#ebeaef;border-width:1px">
              <tr style="color:#999999; font-size:14px;">
                <td>
                  이 메일은 Bouquet 가입 과정에서 메일 인증을 위해 발송되었습니다.<br />
                  메일 인증 요청을 보낸 적이 없다면, 이 메일을 무시해 주세요.
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [recipient.email]
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': body_html,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': title,
                },
            },
            Source=sender,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return JSONResponse(status_code=500, content=dict(msg="FAILED_SENDING_EMAIL"))
    else:
        print(f"Email sent! Message ID: {response['MessageId']}")
        return JSONResponse(status_code=200, content=dict(verification_code=verification_code))


@router.patch('/user/change-pw', status_code=204, description="Successfully changed password", responses={
    404: dict(description="User with given E-mail doesn't exist", model=Message)
})
async def change_password(info: EmailWithPW, session: Session = Depends(db.session)):
    user = Users.get(session, email=info.email)
    if not user:
        return JSONResponse(status_code=404, content=dict(msg="NO_MATCH_USER"))
    new_pw = bcrypt.hashpw(info.pw.encode("utf-8"), bcrypt.gensalt())
    Users.filter(session, email=info.email).update(True, pw=new_pw)
    return JSONResponse(status_code=204)


@router.post("/register/{sns_type}", status_code=201, response_model=Token, responses={
    202: dict(description="Given E-mail already exists", model=Message),
    404: dict(description="Given SNS type is not supported", model=Message)
})
async def register(sns_type: SnsType, reg_info: UserRegister, session: Session = Depends(db.session)):
    """
    `회원가입 API`\n
    :param sns_type:
    :param reg_info:
    :param session:
    :return:
    """
    if sns_type == SnsType.email:
        is_exist = await is_email_exist(reg_info.email)
        if is_exist:
            return JSONResponse(status_code=202, content=dict(msg="EMAIL_EXISTS"))
        hash_pw = bcrypt.hashpw(reg_info.pw.encode("utf-8"), bcrypt.gensalt())
        new_user = Users.create(session, auto_commit=True, pw=hash_pw, email=reg_info.email, name=reg_info.name,
                                profile_img=reg_info.profile_img, sns_type='Email')
        token = f"Bearer {create_access_token(data=UserToken.from_orm(new_user).dict(exclude={'pw', 'marketing_agree'}), )}"
        return dict(Authorization=token)
    return JSONResponse(status_code=404, content=dict(msg="NOT_SUPPORTED"))


@router.post("/login/{sns_type}", status_code=200, response_model=Token, responses={
    400: dict(description="Wrong ID or PW", model=Message),
    404: dict(description="Given SNS type is not supported", model=Message)
})
async def login(sns_type: SnsType, user_info: UserLogin = Body(...)):
    if sns_type == SnsType.email:
        is_exist = await is_email_exist(user_info.email)
        if not is_exist:
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))
        user = Users.get(email=user_info.email)
        is_verified = bcrypt.checkpw(user_info.pw.encode("utf-8"), user.pw.encode("utf-8"))
        if not is_verified:
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))
        token = dict(
            Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(user).dict(exclude={'pw', 'marketing_agree'}))}")
        return token
    return JSONResponse(status_code=400, content=dict(msg="NOT_SUPPORTED"))


async def is_email_exist(email: str):
    get_email = Users.get(email=email)
    if get_email:
        return True
    return False


def create_access_token(*, data: dict = None, expires_delta: int = None):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt
