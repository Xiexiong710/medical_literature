from fastapi import APIRouter, Depends, HTTPException, Form
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database.mysql import engine,Base,SessionLocal
from crud import crud
from schemas import userSchema
from fastapi.responses import JSONResponse,ORJSONResponse
from utils.response_code import response_200, response_404, response_400

# 注册注册相关的路由
reg = APIRouter(prefix="/register", tags=["register"])

# 创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"])


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
def get_hashed_password(user_password: str):
    return pwd_context.hash(user_password)


@reg.post("/", summary="用户注册")
async def register(user: userSchema.user_register_form, db: Session = Depends(get_db)):
    """
    @description  :
    注册接口，对传入的账号密码进行注册，并把数据加入数据库，密码哈希一次
    @param  :  请求格式 application/json
    username: 用户名
    password: 密码
    @Returns  :
    -------
    """
    db_user = crud.get_user_by_username(db=db, username=user.username)
    if db_user is not None:
        return response_400(code=400, data=None, message="该账号已被注册，请重新输入")
    user.password = get_hashed_password(user.password)  #hash加密
    crud.create_user(db=db, user=user)
    return response_200(data=None, message="注册成功!")