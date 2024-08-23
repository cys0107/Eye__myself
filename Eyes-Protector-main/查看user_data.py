import sqlite3

def get_all_tables(db_path):
    """ 獲取數據庫中的所有表名 """
    con = sqlite3.connect(db_path)
    cursorObj = con.cursor()
    cursorObj.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursorObj.fetchall()
    con.close()
    return [table[0] for table in tables]

def get_table_columns(db_path, table_name):
    """ 獲取指定表的所有欄位名稱 """
    con = sqlite3.connect(db_path)
    cursorObj = con.cursor()
    cursorObj.execute(f'PRAGMA table_info({table_name})')
    columns = cursorObj.fetchall()
    con.close()
    return [column[1] for column in columns]

def get_all_table_data(db_path, table_name):
    """ 獲取指定表中的所有數據 """
    con = sqlite3.connect(db_path)
    cursorObj = con.cursor()

    query = f'SELECT * FROM {table_name}'
    
    print(f"Executing query: {query}")  # 打印查詢語句
    cursorObj.execute(query)
    rows = cursorObj.fetchall()
    con.close()
    return rows

def main():
    db_path = "D:\東吳\畢業專題\database.db"
    
    # 這裡輸入您想要查看的特定表名稱
    table_name = 'test'  # 請替換為您的表名
    
    # 獲取並顯示特定表的所有數據
    table_data = get_all_table_data(db_path, table_name)
    
    print(f"{table_name} 表的所有數據:")
    for row in table_data:
        print(row)
    print()  # 空行分隔數據

if __name__ == "__main__":
    main()
