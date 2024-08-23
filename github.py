import subprocess

def git_push():
    # 添加文件到暫存區
    subprocess.run(["git", "add", "database.db"])
    
    # 提交更改
    commit_message = "Auto-update database.db"
    subprocess.run(["git", "commit", "-m", commit_message])
    
    # 推送到遠端儲存庫的 main 分支
    subprocess.run(["git", "push", "origin", "main"])

if __name__ == "__main__":
    git_push()
