import sys
import pygame
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QApplication
from PySide6.QtCore import QTimer, Qt
from Window import MainWindow


class SplashDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("用户协议")
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setFixedSize(500, 250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        message = QLabel("""本产品完全免费且开源并遵循GPLv3开源协议，如果您不是通过正规免费渠道获取本产品则说明您被骗了！\n
本产品完全由「594766562」QQ群群主自主开发，完全免费！如果您喜欢此产品一定要为此「github」项目点个免费的Star哟~\n
注：本产品在您使用后须自行承担使用时出现的一切后果，出现的问题均不在开发者承担范围内！！！""")
        message.setAlignment(Qt.AlignCenter)
        message.setOpenExternalLinks(True)
        message.setWordWrap(True)
        message.setStyleSheet("font-size: 14px; color: #9140ff;")
        layout.addWidget(message)

        self.confirm_btn = QPushButton("同意并继续 (20)")
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setStyleSheet('''
            QPushButton {
                background: #177be5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px 24px;
                font-size: 16px;
            }
            QPushButton:disabled {
                background: #ced4da;
            }
        ''')
        self.confirm_btn.clicked.connect(self.accept)
        layout.addWidget(self.confirm_btn, 0, Qt.AlignCenter)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.remaining = 20
        self.timer.start(1000)

        self.setModal(True)  # 确保弹窗是模态的

        # 初始化音频播放
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound("ResourceFolders/mp3/(⊙_⊙).wav")
        self.sound.play()

    def accept(self):
        super().accept()

    def update_timer(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self.timer.stop()
            self.confirm_btn.setEnabled(True)
            self.confirm_btn.setText("同意并继续")
            # 停止音频播放
            self.sound.stop()
        else:
            self.confirm_btn.setText(f"同意并继续 ({self.remaining})")

    def closeEvent(self, event):
        # 确保用户关闭弹窗时会终止程序
        if self.timer.isActive() or not self.confirm_btn.isEnabled():
            event.ignore()  # 阻止关闭事件
        else:
            event.accept()
            # 停止音频播放
            self.sound.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 初始化pygame音频
    pygame.init()

    # 先显示协议弹窗
    splash = SplashDialog()
    result = splash.exec()

    # 只有用户接受协议后才显示主窗口
    if result == QDialog.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        # 用户没有接受协议，直接退出
        sys.exit(0)