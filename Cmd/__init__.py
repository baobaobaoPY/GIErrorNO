import os
import subprocess


def clean_folder(username, folder_path):
    """清理指定文件夹 (使用 CMD)"""
    try:
        user_path = f"C:/Users/{username}/{folder_path}"
        # 构建 CMD 命令
        del_files_cmd = f'del /q /f "{user_path}\\*"'
        del_dirs_cmd = f'rmdir /s /q "{user_path}"'

        # 执行删除文件操作
        result_del = subprocess.run(
            del_files_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 如果文件夹仍然存在，则执行删除整个文件夹的操作
        if os.path.exists(user_path):
            result_rmdir = subprocess.run(
                del_dirs_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output = result_del.stdout + result_rmdir.stdout
            error = result_del.stderr + result_rmdir.stderr
        else:
            output = result_del.stdout
            error = result_del.stderr

        return {
            "success": True,
            "output": output,
            "error": error
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def clean_temp_files():
    """清理临时文件夹"""
    username = os.getlogin()
    temp_result = clean_folder(username, "AppData/Local/Temp")
    mi_hoyo_result = clean_folder(username, "AppData/LocalLow/miHoYo")
    return {
        "success": temp_result["success"] and mi_hoyo_result["success"],
        "temp_result": temp_result,
        "mi_hoyo_result": mi_hoyo_result
    }


# if __name__ == "__main__":
#     result = clean_temp_files()
#     print("清理结果：")
#     print(f"整体成功: {result['success']}")
#     print("Temp 文件夹清理详情：")
#     print(f"输出: {result['temp_result']['output']}")
#     print(f"错误: {result['temp_result']['error']}")
#     print("miHoYo 文件夹清理详情：")
#     print(f"输出: {result['mi_hoyo_result']['output']}")
#     print(f"错误: {result['mi_hoyo_result']['error']}")
