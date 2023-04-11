import pymysql
import pandas as pd

def connect():
    connection = pymysql.connect(host="",port=3306,database="",user="",password="")
    return connection
    
def exec(sql,conn):
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)
def exec_select(sql,conn):
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        res = cursor.fetchall()
        return res
    except Exception as e:
        print(e)
        return None

########test
# conn = connect()
# sql = '''
# select * from t_kline_day_0 limit 10
# '''

# res = exec_select(sql,conn)
# print(pd.DataFrame(res))
