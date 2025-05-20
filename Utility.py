import os
import sqlite3


class PathManager:
    def __init__(self, db_name='ResourceFolders/WindowsFirewall_EZYES.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)

    def get_latest_program_path(self):
        """从数据库中获取最新的程序路径"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT path FROM executable_paths 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''')
            result = cursor.fetchone()
            return result[0].replace('\\', '/') if result else None  # 统一替换为 /
        except sqlite3.Error as e:
            pass
            return None

    def clean_persistent_log(self):
        """清理 Persistent 目录中的指定日志文件"""
        program_path = self.get_latest_program_path()
        if not program_path:
            pass
            return

        try:
            # 获取程序目录
            program_dir = os.path.dirname(program_path).replace('\\', '/')  # 统一替换为 /
            # 构建 Persistent 目录路径
            persistent_dir = f"{program_dir}/YuanShen_Data"

            # 定义要删除的文件列表
            files_to_delete = [
                "DownloadError.log",
                "upload_err.log",
                "DownloadError.log.bak"
            ]

            # 遍历并删除文件
            for file_name in files_to_delete:
                log_file_path = f"{persistent_dir}/{file_name}"
                if os.path.exists(log_file_path):
                    os.remove(log_file_path)
                # 添加异常处理确保程序正常运行
                try:
                    if os.path.exists(log_file_path):
                        os.remove(log_file_path)
                    else:
                        pass
                except Exception as e:
                    pass

        except Exception as e:
            pass


if __name__ == "__main__":
    manager = PathManager()
    manager.clean_persistent_log()