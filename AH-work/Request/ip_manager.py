"""
模块名称: ip_manager.py

该模块的目标：
    实现网络接口的ip查询和删除操作
  
作者: ych
修改历史:
    1. 2025/9/4 - 创建文件
"""
import argparse
import time
from waf_http.http import HttpObj  # 使用现有的HttpObj类


class NetworkIPManager:
    """网络IP地址管理类"""

    def __init__(self, http_obj):
        self.http_obj = http_obj

    def get_ips(self):
        """获取所有IP地址配置"""
        url = "api/v2/network/ips/"
        return self.http_obj._http_get(url)

    def delete_ip(self, ip_pk):
        """删除指定IP地址 """
        # 构造URL，包含IP主键
        url = f"api/v2/network/ips/{ip_pk}/"

        # 生成时间戳参数
        params = {"_ts": int(time.time() * 1000)}

        # 发送DELETE请求
        return self.http_obj._http_delete(url, params=params)

    def delete_ips_by_net_dev(self, net_dev):
        """删除指定网卡上的所有IP地址"""
        # 获取所有IP配置
        ips_data = self.get_ips()

        # 筛选出指定网卡的IP地址
        ips_to_delete = []
        for ip_config in ips_data.get('result', []):
            if ip_config.get('net_dev') == net_dev:
                ips_to_delete.append({
                    'pk': ip_config.get('_pk'),
                    'ip': ip_config.get('ip'),
                    'mask': ip_config.get('mask')
                })

        # 如果没有找到符合条件的IP地址
        if not ips_to_delete:
            print(f"在网卡 {net_dev} 上未找到任何IP地址配置")
            return {"deleted": 0, "errors": 0}

        # 显示找到的IP地址并确认删除
        print(f"在网卡 {net_dev} 上找到以下IP地址配置:")
        for ip_info in ips_to_delete:
            print(f"  - {ip_info['ip']}/{ip_info['mask']} (主键: {ip_info['pk']})")

        confirm = input(f"\n确定要删除以上 {len(ips_to_delete)} 个IP地址吗？此操作不可逆！(y/N): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            return {"deleted": 0, "errors": 0}

        # 逐个删除IP地址
        deleted_count = 0
        error_count = 0

        for ip_info in ips_to_delete:
            try:
                print(f"正在删除 {ip_info['ip']}/{ip_info['mask']}...")
                result = self.delete_ip(ip_info['pk'])

                if result.get('success', False) or 'success' not in result:
                    print(f"  ✓ 成功删除 {ip_info['ip']}/{ip_info['mask']}")
                    deleted_count += 1
                else:
                    print(f"  ✗ 删除失败: {result.get('message', '未知错误')}")
                    error_count += 1

            except Exception as e:
                print(f"  ✗ 删除 {ip_info['ip']}/{ip_info['mask']} 时发生异常: {e}")
                error_count += 1

        return {"deleted": deleted_count, "errors": error_count}


def main():
    parser = argparse.ArgumentParser(description='网络IP地址管理工具')
    parser.add_argument('--ip', required=True, help='设备IP地址')
    parser.add_argument('--user', default='admin', help='用户名')
    parser.add_argument('--password', default='Admin@1234', help='密码')
    parser.add_argument('--port', type=int, default=443, help='端口号')
    parser.add_argument('--otp', help='OTP密钥（双因子认证）')
    parser.add_argument('--net-dev', required=True, help='要操作的网卡名称（如eth3）')
    parser.add_argument('--list', action='store_true', help='列出所有IP地址配置')

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

        # 创建IP地址管理器实例
        ip_manager = NetworkIPManager(http_obj)

        # 列出所有IP地址配置
        if args.list:
            ips = ip_manager.get_ips()
            print("\nIP地址配置列表:")
            print("=" * 100)
            for ip_config in ips.get('result', []):
                print(f"接口: {ip_config.get('net_dev')}")
                print(f"IP地址: {ip_config.get('ip')}/{ip_config.get('mask')}")
                print(f"主键: {ip_config.get('_pk')}")
                print(f"网关: {ip_config.get('gateway')}")
                # print(f"创建时间: {ip_config.get('_create_timestamp')}")
                print("-" * 100)
            return

        # 删除指定网卡上的所有IP地址
        if args.net_dev:
            result = ip_manager.delete_ips_by_net_dev(args.net_dev)
            print(f"\n操作完成: 成功删除 {result['deleted']} 个IP地址，失败 {result['errors']} 个")
            return

        print("请指定要执行的操作: 使用 --list 查看IP配置列表或 --net-dev 指定要操作的网卡")

    except Exception as e:
        print(f"操作失败: {e}")


if __name__ == "__main__":
    # 使用：python ip_manager.py --ip 10.20.192.106 --list --net-dev eth3
    # python ip_manager.py --ip 10.20.192.106 --net-dev eth3
    main()
