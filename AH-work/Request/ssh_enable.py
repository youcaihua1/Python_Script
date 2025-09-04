"""
模块名称: ssh_enable.py

该模块的目标：
    打开ssh服务
  
作者: ych
修改历史:
    1. 2025/9/3 - 创建文件
"""
from waf_http.http import HttpObj
import time
from loguru import logger


class DeviceUrl:
    """设备管理API端点类"""

    def __init__(self, http_obj):
        self.http_obj = http_obj
        self.URL_PREFIX = 'api/v2/device/'

    def api_hardware_sshd_get(self):
        """获取SSH服务状态"""
        url = self.URL_PREFIX + 'hardware/sshd/'
        return self.http_obj._http_get(url)

    def api_hardware_sshd_set(self, params):
        """设置SSH服务状态"""
        url = self.URL_PREFIX + 'hardware/sshd/'
        return self.http_obj._http_post(url, params)


class SSHService:
    """SSH服务管理类"""

    SSH_ENABLE = {"ssh_enable": True, "ssh_ask_code": "123456"}
    SSH_DISABLE = {"ssh_enable": False, "ssh_ask_code": "123456"}

    def __init__(self, ip, username, password, port=443, otp_key=None):
        self.http_obj = HttpObj(ip=ip, usr=username, pwd=password, port=port, otp_key=otp_key)
        self.http_obj.get_token()  # 认证获取token
        self.device = DeviceUrl(self.http_obj)  # 设备API接口

    def get_ssh_status(self):
        """获取当前SSH服务状态"""
        return self.device.api_hardware_sshd_get()

    def enable_ssh(self, retry_count=60):
        """启用SSH服务（带重试机制）"""
        for index in range(retry_count):
            try:
                status = self.get_ssh_status()
                if status.get("ssh_enable"):
                    logger.info("SSH服务已启用")
                    return status

                logger.info(f"尝试启用SSH服务 ({index + 1}/{retry_count})")
                self.device.api_hardware_sshd_set(params=self.SSH_ENABLE)
            except Exception as e:
                logger.error(f"SSH操作失败: {e}")

            time.sleep(10)  # 等待操作生效

        # 最终检查状态
        return self.get_ssh_status()

    def disable_ssh(self):
        """禁用SSH服务"""
        try:
            logger.info("尝试禁用SSH服务")
            return self.device.api_hardware_sshd_set(params=self.SSH_DISABLE)
        except Exception as e:
            logger.error(f"禁用SSH失败: {e}")
            raise


if __name__ == "__main__":
    # 创建SSH服务管理器（基础认证）
    ssh_manager = SSHService(
        ip="10.20.192.106",
        username="admin",
        password="Admin@1234"
    )

    # 获取当前SSH状态
    status = ssh_manager.get_ssh_status()
    print(f'当前设备：{ssh_manager.http_obj.ip}')
    print(f"当前SSH状态: {'已启用' if status['ssh_enable'] else '已禁用'}")

    # 启用SSH服务
    ssh_manager.enable_ssh()
    print("SSH服务已启用")

    # 禁用SSH服务
    # ssh_manager.disable_ssh()
    # print("SSH服务已禁用")
