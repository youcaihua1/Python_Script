"""
模块名称: first_script.py

该模块的目标：
    第一个paramiko脚本，通过SSH协议连接远程服务器并执行命令。
  
作者: ych
修改历史:
    1. 2025/8/21 - 创建文件
"""
import paramiko
from loguru import logger


class SSHServer:
    def __init__(self, host, port, username, password=None, key_path=None):
        """
        创建SSH服务器连接对象
        :param host: 服务器IP或域名
        :param port: SSH端口（默认22）
        :param username: 登录用户名
        :param password: 密码（可选）
        :param key_path: SSH密钥路径（可选）
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_path = key_path
        self.client = None
        self.sftp = None

    def connect(self):
        """建立SSH连接"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.key_path:
                # 使用密钥认证
                key = paramiko.RSAKey.from_private_key_file(self.key_path)
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    pkey=key
                )
            else:
                # 使用密码认证
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password
                )

            logger.success(f"成功连接到 {self.host}")
            return True
        except Exception as e:
            logger.error(f"连接失败: {str(e)}")
            return False

    def exec_command(self, command):
        """执行远程命令"""
        if not self.client:
            self.connect()

        stdin, stdout, stderr = self.client.exec_command(command)
        return {
            'stdout': stdout.read().decode(),
            'stderr': stderr.read().decode(),
            'exit_code': stdout.channel.recv_exit_status()
        }

    def open_sftp(self):
        """打开SFTP连接"""
        if not self.client:
            self.connect()

        self.sftp = self.client.open_sftp()
        return self.sftp

    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()
            logger.info(f"已关闭与 {self.host} 的连接")

    def __enter__(self):
        """支持上下文管理器"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭"""
        self.close()


if __name__ == '__main__':
    # 使用示例
    with SSHServer('10.20.192.106', 22, 'root', password='Admin@998*&') as server:
        result = server.exec_command('ls -l')
        print(result['stdout'])
    """
    运行结果：
    2025-08-21 10:24:23.309 | SUCCESS  | __main__:connect:57 - 成功连接到 10.20.192.106
    total 1317056
    -r--r--r--. 1 root root       2409 Oct 18  2023 anaconda-ks.cfg
    -rw-r--r--  1 root root 1348655205 Jun 16 13:43 WAF-V3.0R05C45B250613-1656-x86_64-container.bin
    
    2025-08-21 10:24:23.580 | INFO     | __main__:close:87 - 已关闭与 10.20.192.106 的连接
    """
