import os
import sys
import pygame
import multiprocessing
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QFileDialog, QMessageBox,
    QDialog, QFormLayout, QLabel, QComboBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase, QIntValidator, QIcon
from database import DatabaseWindow
from Surveillance import surveillance_worker
from Dyeing import ColorSupport


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.color_support = ColorSupport()
        self.load_custom_font()
        self.db = DatabaseWindow()
        self.init_ui()
        self.load_history()
        self.center_window()
        self.process = None
        # 检查用户是否同意协议说明
        if not self.db.check_agreement_config():
            self.show_user_agreement()
        self.setWindowIcon(QIcon('ResourceFolders/img/🚫GenshinImpact_YuanShen_miHoYo🚫.ico'))

    def center_window(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        x = screen_geometry.x() + (screen_geometry.width() - window_geometry.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - window_geometry.height()) // 2 - 150
        self.move(x, y)

    def load_history(self):
        # 加载原神路径
        latest_path = self.db.get_latest_path()
        if latest_path:
            self.path_display.setText(latest_path)

        # 加载XXMI路径
        latest_xxmi_path = self.db.get_latest_xxmi_path()
        if latest_xxmi_path:
            self.xxmi_path_display.setText(latest_xxmi_path)

    def load_custom_font(self):
        font_file = "./ResourceFolders/ttf_A/zh-cn.ttf"
        font_id = QFontDatabase.addApplicationFont(font_file)
        if font_id == -1:
            self.color_support.print("\x1b[91m加载字体失败，请检查字体文件路径是否正确\x1b[0m")
        else:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                app_font = QFont(font_families[0], 9)
                app_font.setStyleStrategy(QFont.PreferAntialias)
                app_font.setHintingPreference(QFont.PreferNoHinting)
                QApplication.setFont(app_font)

    def init_ui(self):
        self.setWindowTitle('WindowsFirewall_Proxy V1.0.5.1')
        self.resize(777, 240)
        self.setFixedSize(self.width(), self.height())

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 5, 10, 5)

        h_container = QWidget()
        h_layout = QHBoxLayout(h_container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(8)

        self.path_display = QLineEdit()
        self.path_display.setAlignment(Qt.AlignLeft)
        self.path_display.setPlaceholderText("请添加您的游戏路径信息")
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
                background: #fd7e14;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #e06d0c;
            }
        ''')
        self.start_btn.clicked.connect(self.start_surveillance)

        h_layout.addWidget(self.path_display)
        h_layout.addWidget(self.select_btn)
        h_layout.addWidget(self.start_btn)

        # XXMI路径选择部分
        xxmi_container = QWidget()
        xxmi_layout = QHBoxLayout(xxmi_container)
        xxmi_layout.setContentsMargins(0, 0, 0, 0)
        xxmi_layout.setSpacing(8)

        # XXMI路径显示
        self.xxmi_path_display = QLineEdit()
        self.xxmi_path_display.setAlignment(Qt.AlignLeft)
        self.xxmi_path_display.setPlaceholderText("可选加XXMI路径信息，方便快速启动")
        self.xxmi_path_display.setReadOnly(True)
        self.xxmi_path_display.setStyleSheet('''
            QLineEdit {
                background: #f8f9fa;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
            }
        ''')

        # XXMI添加按钮
        self.xxmi_select_btn = QPushButton("添加")
        self.xxmi_select_btn.setFixedWidth(66)
        self.xxmi_select_btn.setStyleSheet('''
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
        self.xxmi_select_btn.clicked.connect(self.select_xxmi_executable)

        # XXMI启动按钮
        self.xxmi_start_btn = QPushButton("启动")
        self.xxmi_start_btn.setFixedWidth(66)
        self.xxmi_start_btn.setStyleSheet('''
            QPushButton {
                background: #fd7e14;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #e06d0c;
            }
        ''')
        self.xxmi_start_btn.clicked.connect(self.start_xxmi)

        xxmi_layout.addWidget(self.xxmi_path_display)
        xxmi_layout.addWidget(self.xxmi_select_btn)
        xxmi_layout.addWidget(self.xxmi_start_btn)

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
            }'''

        # 启动后禁网时间
        ban_label = QLabel("启动后延迟禁网时间(秒):")
        ban_label.setStyleSheet("QLabel { color: #444444; font-weight: normal; }")
        self.ban_duration_input = QLineEdit()
        self.ban_duration_input.setPlaceholderText("输入原神启动后延迟禁网时间：")
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
        self.ban_duration_input.returnPressed.connect(self.save_ban_btn.click)

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
        self.save_intermittent_btn.clicked.connect(
            lambda: self.save_input_value(self.intermittent_input, "intermittent"))
        self.intermittent_input.returnPressed.connect(self.save_intermittent_btn.click)

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
        self.connect_duration_input.setValidator(QIntValidator(0, 120))
        self.save_connect_btn = QPushButton("保存值")
        self.save_connect_btn.setStyleSheet(button_style)
        self.save_connect_btn.clicked.connect(
            lambda: self.save_input_value(self.connect_duration_input, "connect_duration"))
        self.connect_duration_input.returnPressed.connect(self.save_connect_btn.click)  # 支持回车保存值

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

        # 添加防火墙工具选择
        firewall_label = QLabel("选择Powershell或Cmd+Netsh进行：")
        firewall_label.setStyleSheet("QLabel { color: #444444; font-weight: normal; }")

        self.firewall_combo = QComboBox()
        self.firewall_combo.addItems(["1. PowerShell", "2. Cmd+Netsh"])

        # 设置默认值
        saved_tool = self.db.get_firewall_tool()
        if saved_tool == 'cmd_netsh':
            self.firewall_combo.setCurrentIndex(1)
        else:
            self.firewall_combo.setCurrentIndex(0)

        self.firewall_combo.currentIndexChanged.connect(self.on_firewall_tool_changed)

        input_layout.addRow(firewall_label, self.firewall_combo)

        # 添加容器控件到容器中
        main_layout.addWidget(h_container)
        main_layout.addWidget(xxmi_container)
        main_layout.addWidget(input_container)
        self.setCentralWidget(main_widget)

        # 加载保存的值
        self.load_saved_values()

    def on_firewall_tool_changed(self, index):
        """当用户选择不同的防火墙工具时调用"""
        if index == 0:  # PowerShell
            tool_name = 'powershell'
        else:  # Cmd+Netsh
            tool_name = 'cmd_netsh'
            from Cmd.CSurveillance import FirewallRuleManager

        # 保存选择到数据库
        self.db.save_firewall_tool(tool_name)

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

    def select_xxmi_executable(self):
        """选择XXMI可执行文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择XXMI可执行文件",
            "",
            "*.exe"
        )
        if file_path and "XXMI Launcher.exe" in file_path:
            # 保存路径到数据库
            if self.db.save_xxmi_path(file_path):
                # 更新UI
                self.xxmi_path_display.setText(file_path)
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("成功添加")
                success_msg.setText("<font color='#28a745'>成功添加XXMI路径！</font>")
                success_msg.setIcon(QMessageBox.Information)
                success_msg.addButton("确定", QMessageBox.AcceptRole)
                success_msg.exec()
            else:
                # 保存失败提示
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("添加失败")
                error_msg.setText("<font color='#ff5f40'>添加XXMI路径失败，请重试！</font>")
                error_msg.setIcon(QMessageBox.Warning)
                error_msg.addButton("确定", QMessageBox.AcceptRole)
                error_msg.exec()

    def show_xxmi_error_message(self):
        """显示XXMI路径错误提示"""
        error_msg = QMessageBox(self)
        error_msg.setWindowTitle("错误")
        error_msg.setText("<font color='#ff5f40'>未设置XXMI路径信息！</font>")
        error_msg.setIcon(QMessageBox.Warning)
        error_msg.addButton("确认", QMessageBox.AcceptRole)
        error_msg.exec()

    def start_xxmi(self):
        """启动XXMI程序"""
        latest_xxmi_path = self.db.get_latest_xxmi_path()
        if not latest_xxmi_path:
            self.show_xxmi_error_message()
            return

        try:
            # 启动程序
            os.startfile(latest_xxmi_path)

            # 显示成功消息
            success_msg = QMessageBox(self)
            success_msg.setWindowTitle("启动成功")
            success_msg.setText(f"<font color='#28a745'>已启动XXMI程序：<br>{os.path.basename(latest_xxmi_path)}</font>")
            success_msg.setIcon(QMessageBox.Information)
            success_msg.addButton("确定", QMessageBox.AcceptRole)
            success_msg.exec()
        except Exception as e:
            # 启动失败提示
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("启动失败")
            error_msg.setText(f"<font color='#ff5f40'>启动XXMI失败：{str(e)}</font>")
            error_msg.setIcon(QMessageBox.Warning)
            error_msg.addButton("确定", QMessageBox.AcceptRole)
            error_msg.exec()

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
            "选择游戏可执行文件",
            "",
            "*YuanShen.exe *GenshinImpact.exe"
        )
        if file_path:
            # 先尝试保存路径到数据库
            if self.db.save_path(file_path):
                # 如果保存成功，再更新 UI
                self.path_display.setText(file_path)
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("成功添加")
                success_msg.setText("<font color='#28a745'>成功添加路径！</font>")
                success_msg.setIcon(QMessageBox.Information)
                success_msg.addButton("确定", QMessageBox.AcceptRole)
                success_msg.exec()
            else:
                # 如果保存失败，提示用户
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("添加失败")
                error_msg.setText("<font color='#ff5f40'>添加路径失败，请重试！</font>")
                error_msg.setIcon(QMessageBox.Warning)
                error_msg.addButton("确定", QMessageBox.AcceptRole)
                error_msg.exec()

    def show_error_message(self):
        error_msg = QMessageBox(self)
        error_msg.setWindowTitle("错误")
        error_msg.setText("<font color='#ff5f40'>未设置YuanShen.exe路径信息！</font>")
        error_msg.setIcon(QMessageBox.Warning)
        error_msg.addButton("确认", QMessageBox.AcceptRole)
        error_msg.exec()

    def start_surveillance(self):
        from Utility import PathManager  # 导入 PathManager 类

        latest_path = self.db.get_latest_path()
        if not latest_path:
            self.show_error_message()
            return

        try:
            path_manager = PathManager()
            path_manager.clean_persistent_log()
        except Exception as e:
            print(f"Error calling clean_persistent_log: {e}")

        ban_duration = self.get_input_value(self.ban_duration_input, 0, 300)
        intermittent = self.get_input_value(self.intermittent_input, 0, 30)
        connect_duration = self.get_input_value(self.connect_duration_input, 0, 120)

        if ban_duration is None or intermittent is None or connect_duration is None:
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("配置错误")
            error_msg.setText("<font color='#ff5f40'>程序未能找到执行配置，请重试！</font>")
            error_msg.setIcon(QMessageBox.Warning)
            error_msg.addButton("确定", QMessageBox.AcceptRole)
            error_msg.exec()
            return

        # 获取用户选择的防火墙工具
        firewall_tool = self.db.get_firewall_tool()  # 返回 'powershell' 或 'cmd_netsh'

        # 启动子进程，传递防火墙工具参数
        self.process = multiprocessing.Process(
            target=surveillance_worker,
            args=(latest_path, ban_duration, intermittent, connect_duration, firewall_tool)
        )
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
        # 播放关闭声音
        try:
            pygame.mixer.init()
            pygame.mixer.music.load("./ResourceFolders/mp3/Jssu.wav")
            pygame.mixer.music.play()
            # 等待音频播放完成
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(0)
            # 隐藏窗口
            self.hide()
            # 使用用户优先选择的方式删除规则
            firewall_tool = self.db.get_firewall_tool()  # 返回 'powershell' 或 'cmd_netsh'

            # 根据用户选择动态导入对应模块
            if firewall_tool == 'cmd_netsh':
                from Cmd.CSurveillance import FirewallRuleManager
            else:
                from PowerShell.Surveillance import FirewallRuleManager

            # 创建实例并删除规则
            firewall_manager = FirewallRuleManager()
            result = firewall_manager.delete_firewall_rule()
            if result["success"]:
                print("防火墙规则已成功删除")
            else:
                print(f"删除防火墙规则失败或不存在相关规则")

        except Exception as e:
            pass
        sys.exit(0)

    def show_user_agreement(self):
        from PopUps import SplashDialog
        splash = SplashDialog()
        result = splash.exec()

        if result == QDialog.Accepted:
            self.db.update_agreement_config('True')
            self.show()
        else:
            sys.exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    if window.db.check_agreement_config():
        window.show()
    sys.exit(app.exec())
