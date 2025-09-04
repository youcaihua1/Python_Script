"""
模块名称: hardware_interface_viewer.py

该模块的目标：

  
作者: ych
修改历史:
    1. 2025/9/4 - 创建文件
"""
import argparse
from datetime import datetime
from waf_http.http import HttpObj


class DeviceHardwareInterfaceManager:
    """设备硬件接口管理类"""

    def __init__(self, http_obj):
        self.http_obj = http_obj

    def get_hardware_interfaces(self):
        """获取硬件接口信息"""
        url = "api/v2/device/hardware/interfaces/"
        return self.http_obj._http_get(url)


def main():
    parser = argparse.ArgumentParser(description='设备硬件接口信息获取工具')
    parser.add_argument('--ip', required=True, help='设备IP地址')
    parser.add_argument('--user', default='admin', help='用户名')
    parser.add_argument('--password', default='Admin@1234', help='密码')
    parser.add_argument('--port', type=int, default=443, help='端口号')
    parser.add_argument('--otp', help='OTP密钥（双因子认证）')

    args = parser.parse_args()

    try:
        # 创建HTTP连接对象
        print(f"正在连接设备: {args.ip}")
        http_obj = HttpObj(
            ip=args.ip,
            usr=args.user,
            pwd=args.password,
            port=args.port,
            otp_key=args.otp
        )
        http_obj.get_token()
        # print("认证成功")

        # 创建硬件接口管理器实例
        hardware_interface_manager = DeviceHardwareInterfaceManager(http_obj)

        # 获取硬件接口信息
        interfaces = hardware_interface_manager.get_hardware_interfaces()

        # 美观打印接口信息
        # print("\n硬件接口信息:")
        print_hardware_interfaces(interfaces)

    except Exception as e:
        print(f"操作失败: {e}")


def print_hardware_interfaces(info_list):
    """打印硬件接口信息"""
    print("\n硬件接口信息:")
    print("=" * 80)

    for i, interface in enumerate(info_list, 1):
        print(f"\n接口 {i}: {interface.get('name', 'N/A')}")
        print("-" * 60)

        # 基本信息
        print(f"  MAC地址: {interface.get('mac', 'N/A')}")
        print(f"  类型: {interface.get('type', 'N/A')}")

        # 旁路信息
        bypass_pair = interface.get('bypass_pair')
        print(f"  Bypass对: {bypass_pair if bypass_pair is not None else '无'}")

        poweroff_bypass = interface.get('poweroff_bypass', False)
        print(f"  断电旁路: {'是' if poweroff_bypass else '否'}")

        print("-" * 60)

    print("=" * 80)


if __name__ == "__main__":
    # 使用：python hardware_interface_viewer.py --ip 10.20.192.106
    main()
