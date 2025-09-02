"""
模块名称: ssh_reboot.py

该模块的目标：
    使用ssh的reboot命令重启waf
  
作者: ych
修改历史:
    1. 2025/9/2 - 创建文件
"""
import sys

from open_ssh import open_ssh
from server_ping import SSHServer

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("用法: python ssh_reboot.py <输入IP> <输入密码>")
        print('示例: python ssh_reboot.py 10.20.192.106 "Admin@998*&"')
        sys.exit(1)

    ip = sys.argv[1]
    open_ssh(ip)
    password = sys.argv[2]
    try:
        # 使用上下文管理器确保连接关闭
        with SSHServer(
                host=ip,
                port=22,
                username='root',
                password=password,
        ) as ssh:
            result = ssh.exec_command('reboot')
            print(result['stdout'])

    except Exception as e:
        sys.exit(1)
