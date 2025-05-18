import os
import subprocess
import sys
import sqlite3
import multiprocessing
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QDialog, QFormLayout, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase, QIntValidator


class DatabaseWindow:
    def __init__(self, db_name='WindowsFirewall_EZYES.db'):
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

    def update_agreement_config(self, value):
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
            cursor.execute('''
                INSERT OR IGNORE INTO executable_paths (path, timestamp)
                VALUES (?, ?)
            ''', (path, datetime.now().isoformat()))
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_custom_font()
        self.db = DatabaseWindow()
        self.init_ui()
        self.load_history()
        self.center_window()
        self.process = None
        # 检查用户是否同意协议说明
        if not self.db.check_agreement_config():
            self.show_user_agreement()

    def center_window(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        x = screen_geometry.x() + (screen_geometry.width() - window_geometry.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - window_geometry.height()) // 2 - 150
        self.move(x, y)

    def load_history(self):
        latest_path = self.db.get_latest_path()
        if latest_path:
            self.path_display.setText(latest_path)

    def load_custom_font(self):
        font_file = "ResourceFolders/ttf_A/zh-cn.ttf"
        font_id = QFontDatabase.addApplicationFont(font_file)
        if font_id == -1:
            print("\x1b[91m加载字体失败，请检查字体文件路径是否正确\x1b[0m")
        else:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                app_font = QFont(font_families[0], 9)
                app_font.setStyleStrategy(QFont.PreferAntialias)
                app_font.setHintingPreference(QFont.PreferNoHinting)
                QApplication.setFont(app_font)

    def init_ui(self):
        self.setWindowTitle('WindowsFirewall_Proxy V1.0.1')
        self.resize(777, 200)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 5, 10, 5)

        h_container = QWidget()
        h_layout = QHBoxLayout(h_container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(8)

        self.path_display = QLineEdit()
        self.path_display.setAlignment(Qt.AlignLeft)
        self.path_display.setPlaceholderText("添加的YuanShen.exe路径将显示此处")
        self.path_display.setReadOnly(True)
        self.path_display.setStyleSheet('''
            QLineEdit {
                background: #f8f9fa;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
            }
        ''')

        self.select_btn = QPushButton("添加")
        self.select_btn.setFixedWidth(66)
        self.select_btn.setStyleSheet('''
            QPushButton {
                background: #177be5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #146dcc;
            }
        ''')
        self.select_btn.clicked.connect(self.select_executable)

        self.start_btn = QPushButton("开始")
        self.start_btn.setFixedWidth(66)
        self.start_btn.setStyleSheet('''
            QPushButton {
                background: #9140ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #7930e5;
            }
        ''')
        self.start_btn.clicked.connect(self.start_surveillance)

        h_layout.addWidget(self.path_display)
        h_layout.addWidget(self.select_btn)
        h_layout.addWidget(self.start_btn)

        input_container = QWidget()
        input_layout = QFormLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setVerticalSpacing(12)
        input_layout.setHorizontalSpacing(10)
        input_layout.setLabelAlignment(Qt.AlignLeft)

        button_style = '''
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background: #218838;
            }
        '''

        # 启动后禁网时间
        ban_label = QLabel("在启动后禁网时间(秒):")
        ban_label.setStyleSheet("QLabel { color: #444444; font-weight: normal; }")
        self.ban_duration_input = QLineEdit()
        self.ban_duration_input.setPlaceholderText("输入原神启动后禁网时间：")
        self.ban_duration_input.setStyleSheet('''
            QLineEdit {
                background: #f8f9fa;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
            }
        ''')
        self.ban_duration_input.setValidator(QIntValidator(0, 300))
        self.save_ban_btn = QPushButton("保存值")
        self.save_ban_btn.setStyleSheet(button_style)
        self.save_ban_btn.clicked.connect(lambda: self.save_input_value(self.ban_duration_input, "ban_duration"))

        # 中间歇式禁网时间
        intermittent_label = QLabel("游戏中间歇式禁网(秒):")
        intermittent_label.setStyleSheet("QLabel { color: #444444; font-weight: normal; }")
        self.intermittent_input = QLineEdit()
        self.intermittent_input.setPlaceholderText("输入原神断网时间：")
        self.intermittent_input.setStyleSheet('''
            QLineEdit {
                background: #f8f9fa;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
            }
        ''')
        self.intermittent_input.setValidator(QIntValidator(0, 30))
        self.save_intermittent_btn = QPushButton("保存值")
        self.save_intermittent_btn.setStyleSheet(button_style)
        self.save_intermittent_btn.clicked.connect(lambda: self.save_input_value(self.intermittent_input, "intermittent"))

        # 服务器可连接时间
        connect_label = QLabel("服务器可连接时间(秒):")
        connect_label.setStyleSheet("QLabel { color: #444444; font-weight: normal; }")
        self.connect_duration_input = QLineEdit()
        self.connect_duration_input.setPlaceholderText("输入原神联网时间：")
        self.connect_duration_input.setStyleSheet('''
            QLineEdit {
                background: #f8f9fa;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
            }
        ''')
        self.connect_duration_input.setValidator(QIntValidator(5, 120))
        self.save_connect_btn = QPushButton("保存值")
        self.save_connect_btn.setStyleSheet(button_style)
        self.save_connect_btn.clicked.connect(lambda: self.save_input_value(self.connect_duration_input, "connect_duration"))

        # 使用 QHBoxLayout 来布局输入框和按钮
        ban_layout = QHBoxLayout()
        ban_layout.setSpacing(8)
        ban_layout.addWidget(self.ban_duration_input)
        ban_layout.addWidget(self.save_ban_btn)
        input_layout.addRow(ban_label, ban_layout)

        intermittent_layout = QHBoxLayout()
        intermittent_layout.setSpacing(8)
        intermittent_layout.addWidget(self.intermittent_input)
        intermittent_layout.addWidget(self.save_intermittent_btn)
        input_layout.addRow(intermittent_label, intermittent_layout)

        connect_layout = QHBoxLayout()
        connect_layout.setSpacing(8)
        connect_layout.addWidget(self.connect_duration_input)
        connect_layout.addWidget(self.save_connect_btn)
        input_layout.addRow(connect_label, connect_layout)

        main_layout.addWidget(h_container)
        main_layout.addWidget(input_container)
        self.setCentralWidget(main_widget)

        # 加载保存的值
        self.load_saved_values()

    def load_saved_values(self):
        ban_duration = self.db.get_config_value("ban_duration")
        if ban_duration:
            self.ban_duration_input.setText(ban_duration)

        intermittent = self.db.get_config_value("intermittent")
        if intermittent:
            self.intermittent_input.setText(intermittent)

        connect_duration = self.db.get_config_value("connect_duration")
        if connect_duration:
            self.connect_duration_input.setText(connect_duration)

    def get_input_value(self, input_box, min_val, max_val):
        text = input_box.text().strip()
        if not text:
            return None
        try:
            value = int(text)
            if min_val <= value <= max_val:
                return value
            else:
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("输入错误")
                error_msg.setText(f"<font color='#ff5f40'>输入值必须在 {min_val}-{max_val} 之间</font>")
                error_msg.setIcon(QMessageBox.Warning)
                error_msg.addButton("确定", QMessageBox.AcceptRole)
                error_msg.exec()
                return None
        except ValueError:
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("输入错误")
            error_msg.setText("<font color='#ff5f40'>请输入有效的整数</font>")
            error_msg.setIcon(QMessageBox.Warning)
            error_msg.addButton("确定", QMessageBox.AcceptRole)
            error_msg.exec()
            return None

    def save_input_value(self, input_box, key):
        value = input_box.text().strip()
        if not value:
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("输入错误")
            error_msg.setText("<font color='#ff5f40'>输入框不能为空</font>")
            error_msg.setIcon(QMessageBox.Warning)
            error_msg.addButton("确定", QMessageBox.AcceptRole)
            error_msg.exec()
            return

        try:
            int_value = int(value)
            self.db.update_config_value(key, str(int_value))
            success_msg = QMessageBox(self)
            success_msg.setWindowTitle("保存成功")
            success_msg.setText("<font color='#28a745'>值已成功保存！</font>")
            success_msg.setIcon(QMessageBox.Information)
            success_msg.addButton("确定", QMessageBox.AcceptRole)
            success_msg.exec()
        except ValueError:
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("输入错误")
            error_msg.setText("<font color='#ff5f40'>请输入有效的整数</font>")
            error_msg.setIcon(QMessageBox.Warning)
            error_msg.addButton("确定", QMessageBox.AcceptRole)
            error_msg.exec()

    def select_executable(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择YuanShen可执行文件",
            "",
            "YuanShen.exe"
        )
        if file_path:
            self.path_display.setText(file_path)
            if self.db.save_path(file_path):
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("成功添加")
                success_msg.setText("<font color='#28a745'>成功添加路径！</font>")
                success_msg.setIcon(QMessageBox.Information)
                success_msg.addButton("确定", QMessageBox.AcceptRole)
                success_msg.exec()
            else:
                print("\x1b[91m路径保存失败\x1b[0m")

    def show_error_message(self):
        error_msg = QMessageBox(self)
        error_msg.setWindowTitle("错误")
        error_msg.setText("<font color='#ff5f40'>未设置YuanShen.exe路径信息！</font>")
        error_msg.setIcon(QMessageBox.Warning)
        error_msg.addButton("确认", QMessageBox.AcceptRole)
        error_msg.exec()

    def start_surveillance(self):
        latest_path = self.db.get_latest_path()
        if not latest_path:
            self.show_error_message()
            return

        ban_duration = self.get_input_value(self.ban_duration_input, 0, 300)
        intermittent = self.get_input_value(self.intermittent_input, 0, 30)
        connect_duration = self.get_input_value(self.connect_duration_input, 5, 120)

        if ban_duration is None or intermittent is None or connect_duration is None:
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("配置错误")
            error_msg.setText("<font color='#ff5f40'>程序未能找到执行配置，请重试！</font>")
            error_msg.setIcon(QMessageBox.Warning)
            error_msg.addButton("确定", QMessageBox.AcceptRole)
            error_msg.exec()
            return

        # 启动子进程，注意这里传递的参数不能包含 GUI 对象
        self.process = multiprocessing.Process(target=surveillance_worker, args=(latest_path, ban_duration, intermittent, connect_duration))
        self.process.start()

    # 此方法来处理监控进程的退出并显示消息
    def check_surveillance_process(self):
        if self.process and not self.process.is_alive():
            # 显示消息框
            msg = QMessageBox(self)
            msg.setWindowTitle("提示")
            msg.setText("<font color='#14c498'>游戏进程已结束，此次防报错工程已停止，点击确认按钮后退出</font>")
            msg.setIcon(QMessageBox.Information)
            msg.addButton("确认", QMessageBox.AcceptRole)
            msg.exec()
            # 退出应用
            QApplication.instance().quit()

    def closeEvent(self, event):
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join()
            # 删除规则
            try:
                subprocess.run([sys.executable, 'SurveillanceON.py'], check=True)
            except Exception as e:
                print(f"删除规则时出错: {e}")
        event.accept()

    def show_user_agreement(self):
        from PopUps import SplashDialog
        splash = SplashDialog()
        result = splash.exec()

        if result == QDialog.Accepted:
            self.db.update_agreement_config('True')
            self.show()
        else:
            sys.exit(0)


def surveillance_worker(yuanshen_path, ban_duration, intermittent, connect_duration):
    import time
    import subprocess
    import sys
    import psutil
    from datetime import datetime

    print("监控进程已启动...")
    start_time = datetime.now()
    max_wait_time = 60  # 最大等待时间60秒

    # 预处理路径格式
    target_path = os.path.normpath(yuanshen_path).lower()

    # 检测程序是否启动
    target_proc = None
    while (datetime.now() - start_time).total_seconds() < max_wait_time:
        print("检查程序是否启动...")

        # 遍历所有进程
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                # 检查进程名称和路径
                if proc.info['name'] == 'YuanShen.exe':
                    proc_path = os.path.normpath(proc.info['exe']).lower()
                    if proc_path == target_path:
                        print(f"检测到目标进程启动：{proc_path}")
                        target_proc = proc
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        else:
            # 循环正常结束（未找到进程）
            time.sleep(3)  # 每3秒检查一次
            continue

        # 找到匹配进程，跳出循环
        break
    else:
        print("未能在指定时间内检测到游戏的启动，已结束监控。")
        return

    print("开始执行网络规则操作...")
    try:
        # 首次立即禁用网络
        print(f"\x1b[94m程序以启动，立即禁用网络 {ban_duration} 秒\x1b[0m")
        subprocess.run([sys.executable, 'Surveillance.py'], check=True)
        time.sleep(ban_duration)

        while True:
            # 解禁网络
            print(f"\x1b[92m解除网络限制 {connect_duration} 秒\x1b[0m")
            subprocess.run([sys.executable, 'SurveillanceON.py'], check=True)
            time.sleep(connect_duration)

            # 再次禁用网络
            print(f"\x1b[91m限制程序网络 {intermittent} 秒\x1b[0m")
            subprocess.run([sys.executable, 'Surveillance.py'], check=True)
            time.sleep(intermittent)

            # 检查目标进程是否仍在运行
            if not target_proc.is_running():
                print("检测到目标进程已结束，准备退出监控...")
                subprocess.run([sys.executable, 'SurveillanceON.py'], check=True)
                break

    except KeyboardInterrupt:
        print("用户终止进程，正在清理...")
        try:
            subprocess.run([sys.executable, 'SurveillanceON.py'], check=True)
        except Exception as e:
            print(f"删除规则时出错: {e}")
        print("规则已删除，监控进程结束。")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    # 确保只有在用户协议通过后才显示主窗口
    if window.db.check_agreement_config():
        window.show()
    sys.exit(app.exec())