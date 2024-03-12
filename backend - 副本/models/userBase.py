from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime
# 导入sqlalchemy的mysql配置
from database.mysql import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    password = Column(String)
    avatar = Column(String)
    profile = Column(String)
    tags = Column(String)
    role = Column(String, default="user")
    create_time = Column(DateTime)
    update_time = Column(DateTime)
