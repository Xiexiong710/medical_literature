from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Response, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from io import BytesIO
import os
from database.mysql import engine,Base,SessionLocal
from crud import crud
from pdfminer.high_level import extract_text
from utils.response_code import response_200, response_400, response_401
import json
from setting.config import Settings
from jose import JWTError, jwt
import io
import re
from starlette.responses import StreamingResponse
from user.model import TokenData
from CMeKG.model_re.medical_re import config, IterableDataset, Model4s, Model4po, load_schema, load_data, loss_fn, train, extract_spoes, SPO, load_model, get_triples

base_url = 'C:\\Users\\25404\\Desktop\\大学生外服大赛命题-医学文献搜索-测试数据包\\'

# 文件上传路由
files = APIRouter(prefix="/files", tags=["files"])

# txt文件输出路径
output_folder = 'D:/toolsProject/PycharmProject/实训/backend/output'


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


def extract_text_from_binary(binary_data) -> str:
    try:
        # 使用BytesIO将二进制数据转换为文件对象
        binary_stream = BytesIO(binary_data)

        # 使用pdfminer提取文本
        textPDF = extract_text(binary_stream)
        return textPDF
    except Exception as e:
        print(f"Error extracting text from binary data: {e}")
        return None


def remove_spaces_keep_newlines(text):
    # 使用正则表达式替换空格
    cleaned_text = re.sub(r'\s+', '', text)
    return cleaned_text


# 数据库写入三元组
def write_to_db(id: int, res: list):
    for dict in res:
        triples = dict.get('triples')
        if triples is not None:
            for triple in triples:
                crud.create_relation(file_id=id, triple=triple)


@files.get("/get_all")
async def get_all_file(db: Session = Depends(get_db)):
    # 获取所有文件
    all_file = crud.get_all_essay(db=db)
    file_list = [{"essay_id": file_tuple[0], "fileName": file_tuple[1], "create_time": file_tuple[2]} for file_tuple in all_file]
    return response_200(data={'file_list': file_list}, message="success")


@files.post("/upload", name="上传文件")
async def upload_file(file: UploadFile, request: Request, db: Session = Depends(get_db)):
    """
    @description  :
    上传文件前对用户token进行验证，上传完文件后
    @param: File
    """
    # 获取前端头部的token
    jwt_token = request.headers.get('Authorization')
    try:
        # token中的载荷
        playLoad = jwt.decode(jwt_token, Settings.SECRET_KEY, Settings.ALGORITHM)
        username: str = playLoad.get("sub")
        if username is None:
            return response_401(code=401, data=None)
        token_data = TokenData(username=username)
    except JWTError:
        return response_401(code=401, data=None)
    user_id = crud.query_user_by_name(db=db, username=token_data.username)
    if user_id is None:
        return response_401(code=401, data=None)
    contents = await file.read()  # 获取文件内容
    print(type(contents))
    if contents is None:
        return response_400(code=400, message="上传失败")
    file_name = file.filename  # 获取文件名
    file_author_name = file_name.split('.')[0]  # 对文件名进行分割
    last_index = file_author_name.rfind('_')  # 寻找最后一个"_"的字符下标
    file_name = file_author_name[:last_index]  # 再次进行分割
    author_name = file_author_name[last_index+1:]
    crud.create_file(db=db, author=author_name, file_content=contents, fileName=file_name, uploader=user_id[0])  # 创建文件
    # 获取需要进行分词的二进制文件
    file_content = crud.get_max_id_essay(db=db)
    id = file_content[0]
    print('刚才上传的文献', id)
    contents = file_content[1]

    # 提取文本
    text = extract_text_from_binary(contents)
    text = remove_spaces_keep_newlines(text)   # 该文本就是要分词的文本
    """
    现在是分词阶段
    """
    load_schema(config.PATH_SCHEMA)
    model4s, model4po = load_model()

    res = get_triples(text, model4s, model4po)

    # 向数据库中写入三元组
    for dict in res:
        triples = dict.get('triples')
        if triples is not None:
            for triple in triples:
                crud.create_relation(db=db, file_id=id, triple=triple)

    return response_200(message="success")


@files.get("/download", name="下载文件")
async def download_file(file_id: int, db: Session = Depends(get_db)):
    """
    @description  :
    下载文件
    @param: file_id
    """
    db_essay = crud.download_essay(db=db, file_id=file_id)  # 这里的db_essay是sqlalchemy封装好的类 - row
    if not db_essay:
        return response_400(code=400, message="当前服务器繁忙")
    crud.increase_downloads(db=db, file_id=file_id)  # 新增下载
    essay_content = db_essay._data  # 取出essay的实际数据,类型为tuple
    buffer = io.BytesIO(essay_content[0])  # essay_content[0]内容是Blob二进制文件数据流
    return StreamingResponse(content=buffer, status_code=200, media_type="application/octet-stream")  # 适用于以流式方式发送数据，对于大型文件特别有用.FileResponse适合从文件系统钟返回


@files.post("/delete", name="删除文献")
async def delete_file(file_id: int, db:Session = Depends(get_db)):
    crud.delete_essay(db=db, file_id=file_id)   # 删除文件
    return response_200(data=None, message="删除成功")


@files.get("/preview", name="浏览文件")
async def preview_file(file_id: int, db: Session = Depends(get_db)):
    """
    @description  :
    返回浏览器需要的二进制文件数据
    @param: file_id
    """
    db_essay = crud.download_essay(db=db, file_id=file_id)  # 这里的db_essay是sqlalchemy封装好的类 - row
    if not db_essay:
        return response_400(code=400, message="当前服务器繁忙")
    essay_content = db_essay._data  # 取出essay的实际数据,类型为tuple
    print(len(essay_content[0]))
    buffer = io.BytesIO(essay_content[0])  # essay_content[0]内容是Blob二进制文件数据流
    return StreamingResponse(content=buffer, status_code=200, media_type="application/octet-stream")  # 适用于以流式方式发送数据，对于大型文件特别有用.FileResponse适合从文件系统钟返回
