from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Response, Request
from fastapi.responses import FileResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from io import BytesIO
from database.mysql import engine,Base,SessionLocal
from crud import crud
from schemas import userSchema
from utils.response_code import response_200, response_400
import json
import io
from urllib.parse import unquote
from pytrie import StringTrie

# 文件搜索路由
Search = APIRouter()

# 创建一个空的 Trie 树
trie = StringTrie()

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


# 返回要搜索的关键词
def substring_msg(search_msg: str):
    index = search_msg.find("search_msg=")
    index += 11
    return search_msg[index:]


# 生成前端所需要的节点关系图
def generate_graph(object_list: list, subject_list: list, relation_list: list):
    nodes_list = []
    categories = []
    object_length = len(object_list)
    for i, object_tuple in enumerate(object_list):
        nodes_list.append({"name": object_tuple[0], "des": None, "symbolSize": 5, "category": i})
        categories.append({"name": str(i)})
    for j, subject_tuple in enumerate(subject_list):
        nodes_list.append({"name": subject_tuple[0], "des": None, "symbolSize": 6, "category": j+object_length})
        categories.append({"name": str(object_length + j)})
    links_list = [{"source": relation_tuple[0], "target": relation_tuple[1], "name": relation_tuple[2]} for relation_tuple in relation_list]
    return nodes_list, links_list, categories



# @Search.get("/", name="主页面刷新")
# async def get_home(request: Request, db: Session = Depends(get_db)):
#     # 查询所有主客体
#     objects = crud.query_object(db=db)
#     # 查询所有客体
#     subject = crud.query_subject(db=db)
#     return response_200(data={"objects": objects, "subject": subject}, message="success")


@Search.get("/keyWord_search", name="根据关键词信息检索")
async def get_keyword_result(request: Request, db: Session = Depends(get_db)):
    """
    @description  :
    @param  :
    @Returns  : search_box
    -------
    """
    # 前端请求的url地址
    url_str = str(request.url)
    key_word = substring_msg(unquote(url_str))
    essay_list = []
    essay_list_tuple = crud.query_essay_by_keyword(db=db, keyword=key_word)
    for essay_tuple in essay_list_tuple:
        essay_list.append(essay_tuple[0])
    print('文章列表：', essay_list)
    essay_key = ('id', 'title', 'author', 'tags', 'stars', 'fileName', 'uploader', 'downloads', 'secret', 'views')
    results = []
    for essay_id in essay_list:  # 遍历查询出来的List
        essay_info = tuple(crud.get_essay_by_id(db=db, id=essay_id))  # 根据id查询文献信息
        essay_dict = {f'{essay_key[i]}': value for i, value in enumerate(essay_info)}
        # 根据id和关键词查询各文献命中次数, 返回的是查询的list列表
        essay_hits = len(crud.query_essay_by_id(db=db, essay_id=essay_id, keyword=key_word))
        print('命中次数', essay_hits)
        query_score = crud.query_score(db=db, essay_id=essay_id)  # 查询出该文献分数相关的一切信息
        essay_score = essay_hits * 0.5 + query_score.stars * 0.2 + query_score.downloads * 0.2 + query_score.views * 0.1
        query_info = {'essay_info': essay_dict, 'essay_hits': essay_hits, 'essay_score': essay_score}
        results.append(query_info)
    return response_200(data=results, message="success")


# @Search.post("/search_suggest", name="搜索提示")
# async def get_search_suggest(inputStr: str, )

@Search.get("/knowledge_map", name="查询知识图谱关系数据")
async def get_knowledge_map(file_id: int, db: Session = Depends(get_db)):
    """
    @description  :
    根据文献id查询其存在的所有关系实体
    @param  :
    @Returns  : search_box
    -------
    """
    object_list = crud.query_objects_by_id(db=db, essay_id=file_id)
    subject_list = crud.query_subject_by_id(db=db, essay_id=file_id)
    relation_list = crud.query_relation_by_id(db=db, essay_id=file_id)
    nodes_list, links_list, categories = generate_graph(object_list=object_list, subject_list=subject_list, relation_list=relation_list)
    return response_200(data={'nodes_list': nodes_list, 'links_list': links_list, 'categories': categories}, message="success")