from sqlalchemy import Column, String, DateTime, Integer, LargeBinary
from datetime import datetime
# 导入sqlalchemy的mysql配置
from database.mysql import Base
from sqlalchemy import ForeignKey
from models.userBase import User


class Essay(Base):
    __tablename__ = 'essay'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    author = Column(String)
    contents = Column(LargeBinary)
    tags = Column(String)
    create_time = Column(DateTime)
    stars = Column(Integer, default=0)
    fileName = Column(String)
    uploader = Column(Integer, ForeignKey('user.id'))
    downloads = Column(Integer, default=0)
    secret = Column(Integer, default=0)
    views = Column(Integer, default=0)
