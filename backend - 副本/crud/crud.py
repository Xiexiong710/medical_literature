from sqlalchemy.orm import Session
from sqlalchemy import LargeBinary
from models.userBase import User
from models.essayBase import Essay
from datetime import datetime
from schemas.userSchema import user_login_form
from schemas.userSchema import user_register_form
from models.relationBase import Relation
from sqlalchemy import or_, and_
from sqlalchemy.sql import func


def get_user_by_id(db: Session, user_id: int):
    """
    @description  :
    通过id查找用户
    @param  :
    -------
    @Returns  :
    -------
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    """
    @description  :
    通过账户查找用户
    """
    return db.query(User).filter(User.username == username).first()


def get_user_no_password(db: Session, username: str):
    """
    @description  :
    返回无密码用户
    """
    return db.query(User.username, User.tags, User.user_avatar).filter(User.username == username).first()


def create_user(db: Session, user: user_register_form):
    """
    @description  :
    创建用户,it's really hash
    @param  :
    -------
    @Returns  :
    -------
    """
    create_time = datetime.now()
    update_time = datetime.now()
    db_user = User(username=user.username, password=user.password, create_time=create_time,
                   update_time=update_time)
    db.add(db_user) #添加该用户
    db.commit() #数据库提交
    db.refresh(db_user) #刷新


def query_user_by_name(db: Session, username: str):
    """
    @description  :
    根据用户名查询用户id
    """
    return db.query(User.id).filter_by(username=username).first()


def update_user(db:Session, username: str):
    """
    @description  :
    修改用户
    """
    return db.execute()


def create_file(db: Session, file_content: LargeBinary, fileName: str, author: str, uploader: int):
    """
    @description  :
    新增文献
    @param  :
    -------
    @Returns  :
    -------
    """
    create_time = datetime.now()
    db_essay = Essay(author=author, contents=file_content, create_time=create_time, fileName=fileName, uploader=uploader)
    db.add(db_essay) #添加该文章
    db.commit() #数据库提交
    db.refresh(db_essay) #刷新


def get_all_essay(db: Session):
    """
    @description  :
    查询所有文献
    @param  :
    -------
    @Returns  :
    -------
    """
    return db.query(Essay.id, Essay.fileName, Essay.create_time).all()


def get_all_essay_content(db: Session):
    """
    @description  :
    查询所有文献
    @param  :
    -------
    @Returns  :
    -------
    """
    return db.query(Essay.id, Essay.contents).all()


def get_max_id_essay(db: Session):
    """
    @description  :
    查询最新入库的文献
    """
    return db.query(Essay.id, Essay.contents).order_by(Essay.id.desc()).first()

def delete_essay(db: Session, file_id: int):
    """
    @description  :
    根据文献id删除文献
    @param  :
    -------
    @Returns  :
    -------
    """
    user_to_delete = db.query(Essay).filter_by(id=file_id).first() #要删除的行
    db.delete(user_to_delete)
    db.commit()


def get_essay_by_id(db: Session, id: int):
    """
    @description  :
    根据文献id查找文献
    @param  :
    -------
    @Returns  :
    -------
    """
    return db.query(Essay.id, Essay.title, Essay.author, Essay.tags, Essay.stars,
                    Essay.fileName, Essay.uploader, Essay.downloads,
                    Essay.secret, Essay.views).filter_by(id=id).first()


def download_essay(db: Session, file_id: int):
    """
    @description  :
    下载文献
    @param  :
    -------
    @Returns  :
    文献数据流
    -------
    """
    return db.query(Essay.contents).filter_by(id=file_id).first()


def increase_downloads(db: Session, file_id: int):
    """
    @description  :
    新增文献下载量
    """
    essay_update = db.query(Essay).filter_by(id=file_id).first()
    essay_update.downloads += 1
    db.commit()  # 数据库提交


def query_essay_by_keyword(db: Session, keyword: str):
    """
    @description  :
    查询有多少篇文献具有object关键词
    """
    return db.query(Relation.essay_id).filter(or_(Relation.objects==keyword,
                                                  Relation.relation==keyword,
                                                  Relation.subject==keyword)).distinct().all()


def query_object(db: Session):
    """
    @description  :
    查询所有主客体
    """
    return db.query(Relation.objects, Relation.subject).distinct().all()


def query_essay_by_id(db:Session, essay_id: int, keyword: str):
    """
    @description  :
    根据文献id查询其关键词命中次数
    """
    return db.query(Relation.essay_id).filter(and_(or_(Relation.objects==keyword,
                                    Relation.relation==keyword,
                                    Relation.subject==keyword),Relation.essay_id==essay_id)).all()


def query_score(db: Session, essay_id: int):
    """
    @description  :
    根据文献id查询其浏览量，下载量，收藏量
    """
    return db.query(Essay.downloads, Essay.stars, Essay.views).filter_by(id=essay_id).first()


def query_objects_by_id(db: Session, essay_id: int):
    """
    @description  :
    根据文献id查找objects字段存在的所有节点
    """
    return db.query(Relation.objects).filter_by(essay_id=essay_id).distinct().all()


def query_subject_by_id(db: Session, essay_id: int):
    """
    @description  :
    根据文献id查找subject字段存在的所有节点
    """
    return db.query(Relation.subject).filter_by(essay_id=essay_id).distinct().all()


def query_relation_by_id(db: Session, essay_id: int):
    """
    @description  :
    根据文献id查找其存在的所有关系
    """
    return db.query(Relation.objects, Relation.subject, Relation.relation).filter_by(essay_id=essay_id).all()


def create_relation(db:Session, file_id: int, triple: tuple):
    """
    @description  :
    插入三元组
    :param db:
    :param file_id:
    :param triples:
    :return:
    """
    relation_base = Relation(essay_id=file_id, objects=triple[0], relation=triple[1], subject=triple[2])
    db.add(relation_base)  # 添加该关系
    db.commit()  # 数据库提交
    db.refresh(relation_base)  # 刷新