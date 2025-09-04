"""
模块名称: ip_adder.py

该模块的目标：
    在网络接口添加ip
  
作者: ych
修改历史:
    1. 2025/9/4 - 创建文件
"""
from waf_http.http import HttpObj
import argparse


class NetworkManager:
    """网络管理类，用于添加IP地址"""

    def __init__(self, http_obj):
        self.http_obj = http_obj

    def get_ips(self):
        """获取所有IP地址配置"""
        url = "api/v2/network/ips/"
        return self.http_obj._http_get(url)

    def add_ip(self, ip, mask, net_dev, vrrp="", gateway="", client_ip=None,
               server_ip=None, service_filter=None, source_ip_enable=False):
        """添加IP地址

        Args:
            ip (str): IP地址，如 "1.1.1.4"
            mask (int): 子网掩码，如 24
            net_dev (str): 网络设备，如 "eth3"
            vrrp (str): VRRP配置，默认为空字符串
            gateway (str): 网关地址，默认为空字符串
            client_ip (list): 客户端IP列表，默认为空列表
            server_ip (list): 服务器IP列表，默认为空列表
            service_filter (dict): 服务过滤器，默认为 {"ha":false,"admin":false,"traffic":true,"embedded":false}
            source_ip_enable (bool): 源IP启用状态，默认为False
        """
        if client_ip is None:
            client_ip = []
        if server_ip is None:
            server_ip = []
        if service_filter is None:
            service_filter = {
                "ha": False,
                "admin": False,
                "traffic": True,
                "embedded": False
            }

        data = {
            "ip": ip,
            "mask": mask,
            "vrrp": vrrp,
            "gateway": gateway,
            "net_dev": net_dev,
            "client_ip": client_ip,
            "server_ip": server_ip,
            "service_filter": service_filter,
            "source_ip_enable": source_ip_enable
        }

        url = "api/v2/network/ips/"
        return self.http_obj._http_post(url, data)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='WAF IP地址添加工具')
    parser.add_argument('--ip', required=True, help='设备IP地址')
    parser.add_argument('--user', type=str, default='admin', help='用户名')
    parser.add_argument('--password', type=str, default='Admin@1234', help='密码')
    parser.add_argument('--port', type=int, default=443, help='端口号，默认为443')
    parser.add_argument('--otp', help='OTP密钥（如果需要双因子认证）')

    # IP地址配置参数
    parser.add_argument('--address', required=True, help='要添加的IP地址，如 1.1.1.4')
    parser.add_argument('--mask', type=int, required=True, help='子网掩码，如 24')
    parser.add_argument('--net-dev', required=True, help='网络设备，如 eth3')
    parser.add_argument('--vrrp', default="", help='VRRP配置，默认为空字符串')
    parser.add_argument('--gateway', default="", help='网关地址，默认为空字符串')
    parser.add_argument('--client-ip', nargs='*', default=[], help='客户端IP列表，默认为空')
    parser.add_argument('--server-ip', nargs='*', default=[], help='服务器IP列表，默认为空')
    parser.add_argument('--ha', action='store_true', help='启用HA服务过滤')
    parser.add_argument('--admin', action='store_true', help='启用Admin服务过滤')
    parser.add_argument('--traffic', action='store_true', default=True, help='启用Traffic服务过滤（默认启用）')
    parser.add_argument('--embedded', action='store_true', help='启用Embedded服务过滤')
    parser.add_argument('--source-ip-enable', action='store_true', help='启用源IP')

    args = parser.parse_args()

    try:
        # 创建HTTP对象并认证
        print(f"正在连接到设备: {args.ip}")
        http_obj = HttpObj(
            ip=args.ip,
            usr=args.user,
            pwd=args.password,
            port=args.port,
            otp_key=args.otp
        )
        http_obj.get_token()
        # print("认证成功")

        # 创建网络管理对象
        network_manager = NetworkManager(http_obj)

        # 构建服务过滤器
        service_filter = {
            "ha": args.ha,
            "admin": args.admin,
            "traffic": args.traffic,
            "embedded": args.embedded
        }

        # 添加IP地址
        # print("正在添加IP地址...")
        print(f"配置参数: IP={args.address}, 掩码={args.mask}, 网络设备={args.net_dev}")

        result = network_manager.add_ip(
            ip=args.address,
            mask=args.mask,
            net_dev=args.net_dev,
            vrrp=args.vrrp,
            gateway=args.gateway,
            client_ip=args.client_ip,
            server_ip=args.server_ip,
            service_filter=service_filter,
            source_ip_enable=args.source_ip_enable
        )

        print(f"IP地址添加成功: {result}")

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    # 使用示例:
    # python ip_adder.py --ip 10.20.192.106 --address 2.2.2.4 --mask 24 --net-dev eth3
    # python ip_adder.py --ip 10.20.192.106 --address 1.1.1.4 --mask 24 --net-dev eth3 --traffic --source-ip-enable
    main()
