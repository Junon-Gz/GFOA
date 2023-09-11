import sqlite3,time
def op_db(sql):
    '''
    sql:sql字符串
    '''
    try:
        conn = sqlite3.connect('mydatabase.db')
        cur = conn.cursor()
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}({time.time()})执行sql:{sql}')
        cur.execute(sql)
        if 'select' in sql.lower():
            res = [x for x in cur.fetchall()]
        else:
            res = True
    except Exception as e:
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}({time.time()}){sql}执行异常：{e}')
        if 'select' in sql.lower():
            res = []
        else:
            res = False
    finally:
        cur.close()
        conn.commit()
        conn.close()
        if 'select' not in sql.lower():
            print(f"执行结果:{res}")
        return res

def create_table():
    create_sql = 'CREATE TABLE IF NOT EXISTS "cookies" (  "cookies" TEXT,  "create_time" TEXT,  "invalid_time" TEXT);'
    op_db(create_sql)

def clear_cookie():
    clear_sql = 'DROP TABLE IF EXISTS "cookies"'
    op_db(clear_sql)