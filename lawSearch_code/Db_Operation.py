# 载入需要的模块
import sys
import pymysql

# 创建链接数据库的对象并返回
def connect(opt):
    config = {'host': opt['host'] or '127.0.0.1',  # 默认127.0.0.1
              'user': opt['user'] or 'root',
              'password': opt['password'] or 'root',
              'port': opt['port'] or 3306,  # 默认即为3306
              'database': opt['database'] or 'hibernate',
              'charset': opt['charset'] or 'utf8'  # 默认即为utf8
              }
    try:
        # connect方法加载config的配置进行数据库的连接，完成后用db进行接收
        db = pymysql.connect(**config)
    # try有异常的时候才会执行
    except pymysql.err.OperationalError as oe:
        print("mysql连接失败：", oe)
        print("结束程序！")
        sys.exit()
    # try没有异常的时候才会执行
    else:
        print("数据库连接sucessfully!")
        return db

# 增操作 插入，形式如下：
# sql = "INSERT INTO sites (%s, %s) VALUES (%s, %s)"
# val = ("VALUES1", "VALUES2",...)
def Add(mydb, sql, val):
    mycursor = mydb.cursor()
    mycursor.execute(sql, val)
    # 数据表内容有更新，必须使用到该语句
    mydb.commit()
    print(mycursor.rowcount, "记录插入成功。")
    mycursor.close()

# 删操作 删除，形式如下：
# sql = "DELETE FROM sites WHERE name = %s"
def Delete(mydb, sql):
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    mydb.commit()
    print(mycursor.rowcount, " 条记录删除")
    mycursor.close()

# 查操作 查询，形式如下：
# sql="SELECT * FROM sites WhERE name = %s AND name = %s"
def Query(mydb, sql):
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    # 获取所有记录存入列表myresult
    myresult = mycursor.fetchall()
    mycursor.close()

    return myresult

# 改操作 更新，形式如下：
# sql = "UPDATE sites SET name = %s WHERE name = %s"
# val = ("VALUES1", "VALUES2",...)
def Update(mydb, sql, val):
    mycursor = mydb.cursor()
    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, " 条记录被修改")
    mycursor.close()


