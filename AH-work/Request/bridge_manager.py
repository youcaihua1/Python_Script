"""
模块名称: bridge_manager.py

该模块的目标：
    查看网桥列表，以及删除网桥
  
作者: ych
修改历史:
    1. 2025/9/4 - 创建文件
"""
import argparse
import time
from waf_http.http import HttpObj


class NetworkBridgeManager:
    """网络网桥管理类"""

    def __init__(self, http_obj):
        self.http_obj = http_obj

    def get_bridges(self):
        """获取所有网桥列表"""
        url = "api/v2/network/bridges/"
        return self.http_obj._http_get(url)

    def delete_bridge(self, bridge_pk):
        """删除指定网桥"""
        # 构造URL，包含网桥主键和时间戳参数
        url = f"api/v2/network/bridges/{bridge_pk}/"
        params = {"_ts": int(time.time() * 1000)}  # 生成时间戳

        # 发送DELETE请求
        return self.http_obj._http_delete(url, params=params)


def main():
    parser = argparse.ArgumentParser(description='网络网桥管理工具')
    parser.add_argument('--ip', required=True, help='设备IP地址')
    parser.add_argument('--user', default='admin', help='用户名')
    parser.add_argument('--password', default='Admin@1234', help='密码')
    parser.add_argument('--port', type=int, default=443, help='端口号')
    parser.add_argument('--otp', help='OTP密钥（双因子认证）')
    parser.add_argument('--bridge-name', help='要删除的网桥名称')
    parser.add_argument('--bridge-pk', help='要删除的网桥主键')
    parser.add_argument('--list', action='store_true', help='列出所有网桥')

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

        # 创建网桥管理器实例
        bridge_manager = NetworkBridgeManager(http_obj)

        # 列出所有网桥
        if args.list:
            bridges = bridge_manager.get_bridges()
            print("\n网桥列表:")
            print("=" * 80)
            for bridge in bridges.get('result', []):
                print(f"名称: {bridge.get('name')}")
                print(f"主键: {bridge.get('_pk')}")
                print(f"网络设备: {', '.join(bridge.get('net_dev', []))}")
                print(f"MTU: {bridge.get('mtu')}")
                print(f"描述: {bridge.get('desc')}")
                print(f"创建时间: {bridge.get('_create_timestamp')}")
                print("-" * 80)
            return

        # 删除指定网桥
        if args.bridge_pk or args.bridge_name:
            # 如果没有直接提供主键，但提供了名称，则先获取网桥列表
            if not args.bridge_pk and args.bridge_name:
                bridges = bridge_manager.get_bridges()
                for bridge in bridges.get('result', []):
                    if bridge.get('name') == args.bridge_name:
                        args.bridge_pk = bridge.get('_pk')
                        break
                if not args.bridge_pk:
                    print(f"未找到名为 '{args.bridge_name}' 的网桥")
                    return

            # 执行删除操作
            print(f"正在删除网桥 (主键: {args.bridge_pk})...")
            result = bridge_manager.delete_bridge(args.bridge_pk)
            # print(result)
            if result.get('code') == 'SUCCESS':
                print("网桥删除成功!")
            else:
                print(f"网桥删除失败: {result.get('message', '未知错误')}")
            return
        print("请指定要执行的操作: 使用 --list 查看网桥列表或 --bridge-name/--bridge-pk 删除网桥")

    except Exception as e:
        print(f"操作失败: {e}")


if __name__ == "__main__":
    # 使用：python bridge_manager.py --ip 10.20.192.106 --list
    # python bridge_manager.py --ip 10.20.192.106 --bridge-name Protect1
    main()
