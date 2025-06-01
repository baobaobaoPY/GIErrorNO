import sqlite3
import subprocess
import os
import ctypes
from datetime import datetime


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


class FirewallRuleManager:
    def __init__(self, db_name='./ResourceFolders/WindowsFirewall_EZYES.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.create_table()

        # 获取 netsh.exe 的正确路径（处理 32/64 位系统重定向）
        self.netsh_path = self.get_netsh_path()

    def get_netsh_path(self):
        """获取 netsh.exe 的正确路径"""
        system32 = os.path.join(os.environ['WINDIR'], 'System32')
        netsh_path = os.path.join(system32, 'netsh.exe')

        # 处理 32 位 Python 在 64 位系统上的路径重定向
        if not os.path.exists(netsh_path):
            syswow64 = os.path.join(os.environ['WINDIR'], 'SysWOW64')
            wow64_netsh = os.path.join(syswow64, 'netsh.exe')
            if os.path.exists(wow64_netsh):
                return wow64_netsh
        return netsh_path

    def create_table(self):
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
        if not is_admin():
            return {"success": False, "error": "需要管理员权限！请以管理员身份运行此程序"}

        program_path = self.get_latest_path()
        if not program_path:
            raise ValueError("未找到可执行文件路径！")

        # 使用完整路径的 netsh 命令
        cmd = (
            f'"{self.netsh_path}" advfirewall firewall add rule '
            f'name="{rule_name}" '
            f'dir=out '
            f'program="{program_path}" '
            f'action=block'
        )

        try:
            result = subprocess.run(
                cmd,
                check=True,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            return {"success": True, "output": result.stdout}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"创建防火墙规则失败！错误信息：{e.stderr}"}
        except Exception as e:
            return {"success": False, "error": f"创建防火墙规则失败！错误信息：{str(e)}"}

    def delete_firewall_rule(self, rule_name="RawYuanShen"):
        if not is_admin():
            return {"success": False, "error": "需要管理员权限！请以管理员身份运行此程序"}

        # 使用完整路径的 netsh 命令
        cmd = f'"{self.netsh_path}" advfirewall firewall delete rule name="{rule_name}"'

        try:
            result = subprocess.run(
                cmd,
                check=True,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            return {"success": True, "output": result.stdout}
        except subprocess.CalledProcessError as e:
            if "找不到指定的规则" in e.stderr or "No rules match" in e.stderr:
                return {"success": False, "error": f"未找到名为 {rule_name} 的防火墙规则！"}
            return {"success": False, "error": f"删除失败：{e.stderr}"}
        except Exception as e:
            return {"success": False, "error": f"删除失败：{str(e)}"}
