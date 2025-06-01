import datetime
import sqlite3


class DatabaseWindow:
    def __init__(self, db_name='./ResourceFolders/WindowsFirewall_EZYES.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        # 创建 config 表
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"创建 config 表时出错: {e}")

        # 创建 executable_paths 表
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS executable_paths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE,
                    timestamp DATETIME
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"创建 executable_paths 表时出错: {e}")

        # 创建 xxmi_path 表（新增）
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS xxmi_path (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE,
                    timestamp DATETIME
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"创建 XXMI 路径信息表时出错: {e}")

    # 以下是新增的方法用于处理XXMI路径
    def save_xxmi_path(self, path):
        """保存XXMI路径到数据库"""
        try:
            cursor = self.conn.cursor()
            # 检查路径是否存在
            cursor.execute('SELECT id FROM xxmi_path WHERE path = ?', (path,))
            existing = cursor.fetchone()
            if existing:
                # 更新现有记录的timestamp
                cursor.execute('''
                    UPDATE xxmi_path
                    SET timestamp = ?
                    WHERE path = ?
                ''', (datetime.datetime.now().isoformat(), path))
            else:
                # 插入新记录
                cursor.execute('''
                    INSERT INTO xxmi_path (path, timestamp)
                    VALUES (?, ?)
                ''', (path, datetime.datetime.now().isoformat()))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"保存XXMI路径时出错: {e}")
            return False

    def get_latest_xxmi_path(self):
        """获取最新的XXMI路径"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT path FROM xxmi_path 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''')
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"获取XXMI路径时出错: {e}")
            return None

    def update_agreement_config(self, value):
        """保存用户是否同意协议的配置到数据库"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO config (key, value)
            VALUES ('agreement_config', ?)
        ''', (value,))
        self.conn.commit()

    def check_agreement_config(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT value FROM config
            WHERE key = 'agreement_config'
        ''')
        result = cursor.fetchone()
        if result:
            return result[0] == 'True'
        else:
            return False

    def update_config_value(self, key, value):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO config (key, value)
            VALUES (?, ?)
        ''', (key, value))
        self.conn.commit()

    def get_config_value(self, key, default=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT value FROM config
            WHERE key = ?
        ''', (key,))
        result = cursor.fetchone()
        return result[0] if result else default

    def save_path(self, path):
        try:
            cursor = self.conn.cursor()
            # 检查路径是否存在
            cursor.execute('SELECT id FROM executable_paths WHERE path = ?', (path,))
            existing = cursor.fetchone()
            if existing:
                # 更新现有记录的timestamp
                cursor.execute('''
                    UPDATE executable_paths
                    SET timestamp = ?
                    WHERE path = ?
                ''', (datetime.datetime.now().isoformat(), path))
            else:
                # 插入新记录
                cursor.execute('''
                    INSERT INTO executable_paths (path, timestamp)
                    VALUES (?, ?)
                ''', (path, datetime.datetime.now().isoformat()))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"保存路径时出错: {e}")
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
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"获取路径时出错: {e}")
            return None

    def save_firewall_tool(self, tool_name):
        """保存用户选择的防火墙工具到数据库"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO config (key, value)
            VALUES ('firewall_tool', ?)
        ''', (tool_name,))
        self.conn.commit()

    def get_firewall_tool(self):
        """从数据库获取用户选择的防火墙工具"""
        return self.get_config_value('firewall_tool', 'powershell')
