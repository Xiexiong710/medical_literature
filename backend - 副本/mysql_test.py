import pymysql

db = pymysql.connect(user='root', password='123456', host='127.0.0.1', database='practice')

cursor = db.cursor()

def add_course():
    sql = "INSERT INTO course(id, name, subject) values ('4', '大学高等数学', '高等数学')"
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print(str(e))
        db.rollback()
    db.close()

add_course()