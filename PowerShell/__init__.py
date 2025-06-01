import os
import subprocess


def clean_folder(username, folder_path, args="-Recurse -Force -ErrorAction SilentlyContinue"):
    """清理指定文件夹(使用 PowerShell)"""
    try:
        powershell_command = f'Remove-Item -Path "C:/Users/{username}/{folder_path}/*" {args}'
        result = subprocess.run(
            ['powershell', '-Command', powershell_command],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return {
            "success": True,
            "output": result.stdout,
            "error": result.stderr
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "output": e.stdout,
            "error": e.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def clean_temp_files():
    """清理指定文件夹"""
    username = os.getlogin()
    temp_result = clean_folder(username, "AppData/Local/Temp")
    mi_hoyo_result = clean_folder(username, "AppData/LocalLow/miHoYo")
    return {
        "success": temp_result["success"] and mi_hoyo_result["success"],
        "temp_result": temp_result,
        "mi_hoyo_result": mi_hoyo_result
    }
