"""
模块名称: bridge_creator.py

该模块的目标：
    创建网桥
  
作者: ych
修改历史:
    1. 2025/9/4 - 创建文件
"""
import argparse
from waf_http.http import HttpObj


class NetworkManager:
    """网络管理类，用于创建网桥"""

    def __init__(self, http_obj):
        self.http_obj = http_obj

    def get_bridges(self):
        """获取所有网桥配置"""
        url = "api/v2/network/bridges/"
        return self.http_obj._http_get(url)

    def create_bridge(self, mtu=1500, stp=False, desc="", net_dev=None):
        """创建网桥

        Args:
            mtu (int): 最大传输单元，默认1500
            stp (bool): 生成树协议状态，默认False
            desc (str): 描述信息，默认空字符串
            net_dev (list): 网络设备列表，如["eth2", "eth3"]
        """
        if net_dev is None:
            net_dev = ["eth2", "eth3"]

        data = {
            "mtu": mtu,
            "stp": stp,
            "desc": desc,
            "net_dev": net_dev
        }

        url = "api/v2/network/bridges/"
        return self.http_obj._http_post(url, data)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='WAF网桥创建工具')
    parser.add_argument('--ip', required=True, help='设备IP地址')
    parser.add_argument('--user', required=True, help='用户名')
    parser.add_argument('--password', required=True, help='密码')
    parser.add_argument('--port', type=int, default=443, help='端口号，默认为443')
    parser.add_argument('--otp', help='OTP密钥（如果需要双因子认证）')

    # 网桥配置参数
    parser.add_argument('--mtu', type=int, default=1500, help='最大传输单元，默认1500')
    parser.add_argument('--stp', action='store_true', help='启用生成树协议')
    parser.add_argument('--desc', default="", help='网桥描述信息')
    parser.add_argument('--net-dev', nargs='+', default=["eth2", "eth3"],
                        help='网络设备列表，如 eth2 eth3')

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

        # 创建网桥
        print("正在创建网桥...")
        print(f"配置参数: MTU={args.mtu}, STP={args.stp}, 描述='{args.desc}', 网络设备={args.net_dev}")

        result = network_manager.create_bridge(
            mtu=args.mtu,
            stp=args.stp,
            desc=args.desc,
            net_dev=args.net_dev
        )

        print(f"网桥创建成功: {result}")

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    # 使用示例:
    # python bridge_creator.py --ip 10.20.192.106 --user admin --password Admin@1234
    # python bridge_creator.py --ip 10.20.192.106 --user admin --password Admin@1234 --net-dev eth2 eth3
    main()
