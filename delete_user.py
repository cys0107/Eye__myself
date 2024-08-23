import sqlite3

def delete_user_and_related_table(db_path, username):
    """刪除 threshold 表中的使用者資料，並刪除與該使用者相關的數據表"""
    try:
        con = sqlite3.connect(db_path)
        cursorObj = con.cursor()

        # 1. 刪除 threshold 表中的使用者資料
        query = "DELETE FROM threshold WHERE user = ?"
        cursorObj.execute(query, (username,))
        print(f"使用者 {username} 的資料已從 threshold 表中刪除。")
        
        # 2. 刪除與該使用者相關的數據表（假設表名與使用者名稱相同）
        related_table_name = username  # 假設數據表的名稱與使用者名稱一致
        
        # 檢查該表是否存在
        cursorObj.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (related_table_name,))
        table_exists = cursorObj.fetchone()
        
        if table_exists:
            cursorObj.execute(f"DROP TABLE IF EXISTS {related_table_name}")
            print(f"數據表 {related_table_name} 已刪除。")
        else:
            print(f"數據表 {related_table_name} 不存在，無需刪除。")
        
        con.commit()  # 提交更改
        
    except sqlite3.Error as e:
        print(f"刪除使用者或相關表時發生錯誤: {e}")
    finally:
        if con:
            con.close()

def main():
    db_path = 'C:/Users/ryan9/database.db'  # 資料庫路徑
    username = 'vSj2J7iH0T4aKlhNKFqIOgkwb6vuR9aXiuKglF2bRKz'  # 替換為您要刪除的使用者名稱
    
    delete_user_and_related_table(db_path, username)

if __name__ == "__main__":
    main()
