"""
模块名称: server_ping.py

该模块的目标：
    执行ping命令
  
作者: ych
修改历史:
    1. 2025/9/1 - 创建文件
"""
import paramiko
import time
import os
import sys
import argparse
from datetime import datetime
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
        self.shell = None

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
        """执行远程命令并返回结果"""
        if not self.client:
            self.connect()

        stdin, stdout, stderr = self.client.exec_command(command)
        return {
            'stdout': stdout.read().decode(),
            'stderr': stderr.read().decode(),
            'exit_code': stdout.channel.recv_exit_status()
        }

    def invoke_shell(self):
        """创建交互式shell会话"""
        if not self.client:
            self.connect()

        self.shell = self.client.invoke_shell()
        return self.shell

    def execute_and_save_ping(self, target, count=15, local_path='ping_output.txt'):
        """
        执行ping命令并实时保存结果到本地文件
        :param target: ping的目标地址
        :param count: ping的次数
        :param local_path: 本地保存路径
        """
        # 确保目录存在
        dir_path = os.path.dirname(local_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"创建目录: {dir_path}")

        # 创建交互式shell
        if not self.shell:
            self.invoke_shell()

        # 构造命令（添加行号）
        command = f"ping {target} -c {count}"
        logger.info(f"执行命令: {command}")

        # 发送命令
        self.shell.send(command + '\n')

        # 设置超时时间（秒）
        start_time = time.time()
        timeout = count * 2 + 5  # 根据ping次数计算超时

        # 创建本地文件
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(f"命令执行开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"服务器: {self.host}:{self.port}\n")
            f.write(f"用户: {self.username}\n")
            f.write(f"目标地址: {target}\n")
            f.write(f"ping次数: {count}\n")
            f.write(f"执行命令: {command}\n")
            f.write("-" * 80 + "\n\n")

            # 实时接收输出
            while True:
                # 检查超时
                if time.time() - start_time > timeout:
                    logger.warning(f"超过最大等待时间 ({timeout}秒)，终止命令执行")
                    self.shell.send('\x03')  # 发送Ctrl+C中断命令
                    f.write("\n\n[系统] 命令执行超时已中断\n")
                    break

                # 检查命令是否结束
                if self.shell.exit_status_ready():
                    # 确保读取最后的数据
                    if self.shell.recv_ready():
                        output = self.shell.recv(4096).decode('utf-8', errors='ignore')
                        f.write(output)
                    break

                # 读取可用数据
                if self.shell.recv_ready():
                    output = self.shell.recv(4096).decode('utf-8', errors='ignore')
                    f.write(output)
                    f.flush()  # 确保实时写入

                    # 记录日志
                    logger.debug(f"接收到 {len(output)} 字节数据")
                else:
                    time.sleep(0.1)  # 减少CPU占用

        # 添加结束标记和时间
        with open(local_path, 'a', encoding='utf-8') as f:
            f.write("\n" + "-" * 80 + "\n")
            f.write(f"命令执行结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        logger.success(f"结果已保存至: {local_path}")
        return local_path

    def open_sftp(self):
        """打开SFTP连接"""
        if not self.client:
            self.connect()

        self.sftp = self.client.open_sftp()
        return self.sftp

    def close(self):
        """关闭所有连接"""
        try:
            if self.shell:
                self.shell.close()
                logger.debug("关闭shell会话")
        except:
            pass

        try:
            if self.sftp:
                self.sftp.close()
                logger.debug("关闭SFTP连接")
        except:
            pass

        try:
            if self.client:
                self.client.close()
                logger.info(f"已关闭与 {self.host} 的SSH连接")
        except:
            pass

    def __enter__(self):
        """支持上下文管理器"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭"""
        self.close()


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='通过SSH远程执行ping命令并保存结果',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('--host', type=str, required=True,
                        help='服务器IP地址 (必填)')
    parser.add_argument('--port', type=int, default=22,
                        help='SSH端口号')
    parser.add_argument('--username', type=str, default='root',
                        help='SSH用户名')
    parser.add_argument('--password', type=str,
                        help='SSH密码 (如果使用密钥认证，则不需要)')
    parser.add_argument('--key-path', type=str,
                        help='SSH私钥文件路径')
    parser.add_argument('--target', type=str, default='1.1.1.4',
                        help='ping的目标地址')
    parser.add_argument('--count', type=int, default=15,
                        help='ping的次数')
    parser.add_argument('--local-path', type=str, default='./ping_file/ping_output.txt',
                        help='本地保存结果的路径')
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='日志级别')

    return parser.parse_args()


def main():
    """主程序入口"""
    args = parse_arguments()

    # 配置日志
    logger.remove()  # 移除默认配置
    logger.add(sys.stdout, level=args.log_level,
               format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    logger.add("ssh_ping.log", rotation="10 MB", level=args.log_level)

    logger.info("启动SSH ping测试")
    logger.info(f"服务器: {args.host}:{args.port}")
    logger.info(f"目标: {args.target}, ping次数: {args.count}")
    logger.info(f"保存位置: {args.local_path}")

    try:
        # 使用上下文管理器确保连接关闭
        with SSHServer(
                host=args.host,
                port=args.port,
                username=args.username,
                password=args.password,
                key_path=args.key_path
        ) as ssh:
            # 执行ping命令并保存结果
            result_file = ssh.execute_and_save_ping(
                target=args.target,
                count=args.count,
                local_path=args.local_path
            )

            logger.info(f"Ping测试完成，结果保存在: {result_file}")

    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        sys.exit(1)

    logger.info("程序执行完毕")


if __name__ == '__main__':
    # 使用示例：
    # python server_ping.py --host=10.50.36.46 --password='_(0)waf-TEST(1)_' --target=2.2.2.26 --count=400 --local-path='./ping_file/9-1-c2.txt'
    main()
