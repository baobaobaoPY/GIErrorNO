import sqlite3
import subprocess
from datetime import datetime


class FirewallRuleManager:
    def __init__(self, db_name='WindowsFirewall_EZYES.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.create_table()

    def create_table(self):
        """创建存储可执行文件路径的数据库表"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS executable_paths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE,
                timestamp DATETIME
            )
        ''')
        self.conn.commit()

    def save_path(self, path):
        """保存可执行文件路径到数据库"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO executable_paths (path, timestamp)
                VALUES (?, ?)
            ''', (path, datetime.now().isoformat()))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            return False

    def get_latest_path(self):
        """获取最近添加的可执行文件路径并处理为 Windows 支持的路径格式"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT path FROM executable_paths 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''')
            result = cursor.fetchone()
            if result:
                # 将路径转换成 Windows 支持的格式
                return result[0].replace('/', '\\')
            return None
        except sqlite3.Error as e:
            print(f"数据库查询错误: {str(e)}")
            return None

    def create_firewall_rule(self, rule_name="RawYuanShen"):
        """从数据库获取路径并创建防火墙规则"""
        program_path = self.get_latest_path()
        if not program_path:
            raise ValueError("未找到可执行文件路径！")

        # 构造PowerShell命令，使用单引号来包围路径以避免转义问题
        ps_command = (
            f'New-NetFirewallRule -DisplayName "{rule_name}" -Direction Outbound '
            f'-Program "{program_path}" -Action Block'
        )

        # 调用PowerShell执行命令
        try:
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                check=True,
                shell=True,
                capture_output=True,
                text=True
            )
            return {"success": True, "output": result.stdout}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"创建防火墙规则失败！错误信息：{e.stderr}"}
        except Exception as e:
            return {"success": False, "error": f"创建防火墙规则失败！错误信息：{str(e)}"}


# 当这个模块被直接运行时，创建一个防火墙规则
if __name__ == '__main__':
    firewall_manager = FirewallRuleManager()
    result = firewall_manager.create_firewall_rule()
    if result["success"]:
        print(result["output"])
    else:
        print("\x1b[91m错误:\x1b[0m", result["error"])
