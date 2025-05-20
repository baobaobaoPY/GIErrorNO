import sqlite3
import subprocess
from datetime import datetime


class FirewallRuleManager:
    def __init__(self, db_name='ResourceFolders/WindowsFirewall_EZYES.db'):
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

        ps_command = (
            f'New-NetFirewallRule -DisplayName "{rule_name}" -Direction Outbound '
            f'-Program "{program_path}" -Action Block'
        )

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

    def delete_firewall_rule(self, rule_name="RawYuanShen"):
        """删除特定的防火墙规则"""
        check_command = f'Get-NetFirewallRule -DisplayName "{rule_name}" 2>&1 | Out-Null'
        try:
            subprocess.run(
                ['powershell', '-Command', check_command],
                check=True,
                shell=True,
                capture_output=True,
                text=True
            )
            delete_command = f'Remove-NetFirewallRule -DisplayName "{rule_name}"'
            result = subprocess.run(
                ['powershell', '-Command', delete_command],
                check=True,
                shell=True,
                capture_output=True,
                text=True
            )
            return {"success": True, "output": result.stdout}
        except subprocess.CalledProcessError as e:
            if "not found" in e.stderr.lower():
                return {"success": False, "error": f"未找到名为 {rule_name} 的防火墙规则！"}
            return {"success": False, "error": f"删除失败或未存在相关规则"}
        except Exception as e:
            return {"success": False, "error": f"删除失败或未存在相关规则"}
