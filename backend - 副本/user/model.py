from typing import Union
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel


# 定义用户模型
class User(BaseModel):
    username: str
    password: str
    avatar: str #用户头像
    profile: str #用户简介
    tags: str  #用户所属标签
    role: str  #用户角色，默认'user'
    create_time: datetime  #创建时间
    update_time: datetime  #更新时间


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str

