# 导入sqlalchemy相关包
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# -----------------------数据库配置-----------------------------------
USER='root'
PWD='123456'
DB_NAME='practice'

# 初始化数据库连接
SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{USER}:{PWD}@localhost:3306/{DB_NAME}?charset=utf8'#mysql
# SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,pool_pre_ping=True,echo=True
)
SessionLocal = sessionmaker(autocommit=False, bind=engine)

Base = declarative_base()