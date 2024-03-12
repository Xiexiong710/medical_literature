from pydantic import BaseModel


class user_login_form(BaseModel):
    username: str #用户账号
    password: str #用户密码


class user_register_form(BaseModel):
    username: str #用户账户
    password: str #用户密码


# 该基础类型是为了防止将密码暴露给请求端
class user_sensitive_form(BaseModel):
    username: str #用户账户