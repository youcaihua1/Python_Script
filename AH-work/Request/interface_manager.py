"""
模块名称: interface_manager.py

该模块的目标：
    查看网络接口信息
  
作者: ych
修改历史:
    1. 2025/9/4 - 创建文件
"""
import argparse
from waf_http.http import HttpObj


class NetworkInterfaceManager:
    """网络接口管理类"""

    def __init__(self, http_obj):
        self.http_obj = http_obj

    def get_interfaces(self):
        """获取所有网络接口信息"""
        url = "api/v2/network/effects/interfaces/aggregate/"
        return self.http_obj._http_get(url)


def print_interface_info(interface_data):
    """打印接口信息"""
    # 打印总体信息
    print(f"设备类型: {interface_data.get('dev_type', 'N/A')}")
    print(f"接口总数: {interface_data.get('count', 0)}")
    print(f"当前页码: {interface_data.get('page', 1)}")
    print(f"每页数量: {interface_data.get('per_page', 20)}")
    print("=" * 80)

    # 打印每个接口的详细信息
    for i, interface in enumerate(interface_data.get('result', []), 1):
        print(f"\n接口 {i}: {interface.get('name', 'N/A')}")
        print("-" * 60)

        # 基本信息
        print(f"  主键 (PK): {interface.get('_pk', 'N/A')}")
        print(f"  类型: {interface.get('type', 'N/A')}")
        print(f"  状态: {interface.get('status', 'N/A')}")
        print(f"  MAC地址: {interface.get('mac', 'N/A')}")
        print(f"  命名空间ID: {interface.get('namespace_id', 'N/A')}")

        # 状态信息
        print(f"  是否活跃: {'是' if interface.get('alive') else '否'}")
        print(f"  管理接口: {'是' if interface.get('admin') else '否'}")
        print(f"  高可用: {'是' if interface.get('ha') else '否'}")
        print(f"  会话同步: {interface.get('session_sync', 0)}")
        print(f"  启用状态: {'启用' if interface.get('enable') else '禁用'}")
        print(f"  支持禁用: {'是' if interface.get('support_disable') else '否'}")

        # IP地址信息
        ips = interface.get('ips', [])
        if ips:
            print(f"  IP地址配置:")
            for ip_info in ips:
                print(f"    - IP: {ip_info.get('ip', 'N/A')}/{ip_info.get('mask', 'N/A')}")
                print(f"      网关: {ip_info.get('gateway', 'N/A')}")
                print(f"      MAC: {ip_info.get('mac', 'N/A')}")
                print(f"      主键: {ip_info.get('_pk', 'N/A')}")
                print(f"      默认路由: {'是' if ip_info.get('_is_default') else '否'}")
                print(f"      VRRP: {ip_info.get('vrrp', 'N/A')}")
                print(f"      会话同步: {ip_info.get('session_sync', 0)}")
                print(f"      源IP启用: {'是' if ip_info.get('source_ip_enable') else '否'}")

                # 服务过滤器
                service_filter = ip_info.get('service_filter', {})
                if service_filter:
                    print(f"      服务过滤器:")
                    print(f"        管理: {'是' if service_filter.get('admin') else '否'}")
                    print(f"        流量: {'是' if service_filter.get('traffic') else '否'}")
                    print(f"        高可用: {'是' if service_filter.get('ha') else '否'}")
                    print(f"        嵌入式: {'是' if service_filter.get('embedded') else '否'}")
        else:
            print(f"  IP地址配置: 无")

        # IP池信息
        ip_pool = interface.get('ip_pool', [])
        if ip_pool:
            print(f"  IP池: {', '.join(ip_pool)}")
        else:
            print(f"  IP池: 无")

        # 父接口信息
        parent_interface = interface.get('parent_interface', [])
        if parent_interface:
            print(f"  父接口: {', '.join(parent_interface)}")
        else:
            print(f"  父接口: 无")

        # 网络设备信息
        net_dev = interface.get('net_dev', [])
        if net_dev:
            print(f"  网络设备: {', '.join(net_dev)}")
        else:
            print(f"  网络设备: 无")

        print("-" * 60)


def main():
    parser = argparse.ArgumentParser(description='网络接口信息获取工具')
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

        # 创建接口管理器实例
        interface_manager = NetworkInterfaceManager(http_obj)

        # 获取所有接口列表
        interfaces = interface_manager.get_interfaces()
        print_interface_info(interfaces)

    except Exception as e:
        print(f"操作失败: {e}")


if __name__ == "__main__":
    # python interface_manager.py --ip 10.20.192.106
    main()
