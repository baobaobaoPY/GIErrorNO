import ctypes
import os
from colorama import Fore, Style, init


class ColorSupport:
    def __init__(self):
        self.ansi_supported = self.is_ansi_supported()
        init(autoreset=True)  # 初始化 Colorama

    def is_ansi_supported(self):
        """检测当前终端是否支持 ANSI 转义序列"""
        # 检查 Windows 版本
        if os.name == 'nt':
            # Windows 10 及以上版本支持 ANSI
            ver = os.sys.getwindowsversion()
            if ver.major >= 10:
                return True
            # 尝试启用虚拟终端模式
            try:
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except:
                return False
        # 其他系统默认支持
        return os.getenv("TERM") in ["xterm", "xterm-256color"]

    def colored(self, text, color="white"):
        """返回带颜色的文本（自动检测是否支持 ANSI）"""
        colors = {
            "red": Fore.RED,
            "green": Fore.GREEN,
            "yellow": Fore.YELLOW,
            "blue": Fore.BLUE,
            "cyan": Fore.CYAN,
            "magenta": Fore.MAGENTA
        }
        if self.ansi_supported:
            return f"{colors.get(color.lower(), Fore.WHITE)}{text}{Style.RESET_ALL}"
        return text  # 不支持时返回纯文本

    def print(self, text, color="white"):
        """带颜色的打印函数（自动降级）"""
        print(self.colored(text, color))
