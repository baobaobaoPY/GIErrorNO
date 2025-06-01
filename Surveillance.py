import os
import sys


def surveillance_worker(yuanshen_path, ban_duration, intermittent, connect_duration, firewall_tool):
    import time
    import psutil
    from datetime import datetime

    print("监控进程已启动...")
    start_time = datetime.now()
    max_wait_time = 60  # 最大等待时间60秒

    # 根据用户选择导入不同模块
    if firewall_tool == 'cmd_netsh':
        from Cmd.CSurveillance import FirewallRuleManager
        from Cmd.__init__ import clean_temp_files
    else:
        from PowerShell.Surveillance import FirewallRuleManager
        from PowerShell.__init__ import clean_temp_files

    # 预处理路径格式
    target_path = os.path.normpath(yuanshen_path).lower()

    # 检测程序是否启动
    target_proc = None
    firewall_manager = FirewallRuleManager()  # 创建 FirewallRuleManager 实例

    while (datetime.now() - start_time).total_seconds() < max_wait_time:
        print("检查程序是否启动...")

        # 遍历所有进程
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                # 检查进程名称和路径
                if proc.info['name'] in ['YuanShen.exe', 'GenshinImpact.exe']:
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
    try:  # 清除不必要引起的报错因子
        cleanup_result = clean_temp_files()
        if cleanup_result["success"]:
            pass
        else:
            pass
        # 开始延迟开启禁网模式
        print(f"\x1b[94m程序以启动，开始延迟开启禁网 {ban_duration} 秒\x1b[0m")
        time.sleep(ban_duration)

        while True:
            # 解禁网络
            print(f"\x1b[92m解除网络限制 {connect_duration} 秒\x1b[0m")
            result = firewall_manager.delete_firewall_rule()  # 删除防火墙规则
            if result["success"]:
                print(result["output"])
            else:
                print(f"删除防火墙规则失败或不存在相关规则")
            time.sleep(connect_duration)

            # 再次禁用网络
            print(f"\x1b[91m限制程序网络 {intermittent} 秒\x1b[0m")
            result = firewall_manager.create_firewall_rule()  # 重新创建防火墙规则
            if result["success"]:
                print(result["output"])
            else:
                print(f"创建防火墙规则失败：{result['error']}")
            time.sleep(intermittent)

            # 检查目标进程是否仍在运行
            if not target_proc.is_running():
                print("检测到目标进程已结束，准备退出监控...")
                result = firewall_manager.delete_firewall_rule()  # 删除防火墙规则
                if result["success"]:
                    print(result["output"])
                else:
                    print(f"删除防火墙规则失败或不存在相关规则")
                break

    except KeyboardInterrupt:
        try:
            result = firewall_manager.delete_firewall_rule()  # 删除防火墙规则
            if result["success"]:
                print(result["output"])
                sys.exit(0)
            else:
                print(f"删除防火墙规则失败或不存在相关规则")
                sys.exit(-1)
        except Exception as e:
            print(f"删除规则时出错: {e}")
            sys.exit(-1)
