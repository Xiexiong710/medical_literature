from fastapi import APIRouter, Depends, HTTPException, Form
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database.mysql import engine, Base, SessionLocal
from crud import crud
from schemas import userSchema
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from setting.config import settings
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from user.model import Token
from utils.response_code import response_200, response_400, response_401

# 引入login路由
log = APIRouter()

# 创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"])

# 指定用户从哪个路径能获得登录的token
oauth_schema = OAuth2PasswordBearer(tokenUrl="/login")


def get_db():
    """
    @description  :
    底层依赖，每个接口都会调用该函数，打开会话，然后关闭会话，由depends导入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 对客户端传来的密码进行hash
def get_hashed_password(password: str):
    return pwd_context.hash(password)


# 验证用户传入的密码是否正确
def verify_password(db_password: str, password: str):
    return pwd_context.verify(password, db_password)


# 获取用户
def get_user(username: str):
    db = SessionLocal()
    db_user = crud.get_user_by_username(db=db, username=username)
    return db_user


def authenticate_user(username: str, password: str):
    """
    @description  :
    对用户身份进行校验，返回用户对象或者False
    """
    user = get_user(username)
    if not user:
        return False
    if not verify_password(user.password, password):
        return False
    return user


def create_access_token(data: dict):
    """
    @description  :
    创建json web token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_token = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_token


@log.post("/login", summary="登录接口")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    @description  :
    用户登录并获取token
    @param  :  请求格式 application/form-data
    username: 用户名
    password: 密码
    @Returns  : json web token
    -------
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        return response_401(code=401, data=None, message='用户名或密码错误')
    # 用户通过验证，开始获取token
    access_token = create_access_token(data={"sub": user.username})
    data = {"access_token": access_token, "token_type": "bearer"}
    return response_200(data=data, message="登录成功")


@log.post("/logout", name="用户登出")
def logout():
    return response_200(data=None, message="已登出")