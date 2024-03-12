from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy import ForeignKey
from models.essayBase import Essay
from models.userBase import User
from datetime import datetime
# 导入sqlalchemy的mysql配置
from database.mysql import Base


class Relation(Base):
    __tablename__ = 'relation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    essay_id = Column(Integer, ForeignKey('essay.id'))
    objects = Column(String)
    relation = Column(String)
    subject = Column(String)