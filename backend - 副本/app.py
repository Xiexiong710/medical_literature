from fastapi import FastAPI
from typing import Annotated
from api.userManage import login, register
from api.fileManage import fileManage
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from api.search import essaySearch
"""
此处应该对跨域进行配置,允许前端9527域发来http请求并响应
"""
app = FastAPI()

origins = [
    "http://localhost:9527"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins, # 允许跨域请求的源
    allow_credentials = True, # 指示跨域请求是否支持 cookies
    allow_methods = ["*"], # 允许请求的HTTP方法
    allow_headers = ["*"] # 允许的请求头部
)
"""
添加注册的路由
"""
app.include_router(register.reg)
"""
添加登录的路由
"""
app.include_router(login.log)
"""
添加文件管理的路由
"""
app.include_router(fileManage.files)
"""
添加文献检索的路由
"""
app.include_router(essaySearch.Search)