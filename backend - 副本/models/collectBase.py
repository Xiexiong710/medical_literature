
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy import ForeignKey
from essayBase import Essay
from userBase import User
from datetime import datetime
# 导入sqlalchemy的mysql配置
from database.mysql import Base


class Collect(Base):
    __tablename__ = 'collect'

    id = Column(Integer, primary_key=True, autoincrement=True)
    collector = Column(Integer, ForeignKey('User.id'))
    essay = Column(Integer, ForeignKey('Essay.id'))
