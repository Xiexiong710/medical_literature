from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from fastapi.responses import FileResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database.db import get_db
from jose import JWTError, jwt
from setting.config import settings
from database.mysql import engine,Base,SessionLocal
from crud import crud
from utils.response_code import response_200, response_400

# 创建用户管理路由
user_router = APIRouter()


@user_router.get('/user_info', name="获取当前用户详细信息")
async def get_current_user(token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    # 对当前用户的token进行解码，并取出其中的sub字段
    play_load = jwt.decode(token.split('.')[1], settings.SECRET_KEY)
    username = play_load.get("sub")
    user = crud.get_user_by_username(db=db, username=username)
    if not user:
        return response_400(code=400, message="没有当前用户信息")
    return response_200(data=user, message="success")


# @user_router.post('/update_user', name="修改当前用户个人信息")
# async def update_user()