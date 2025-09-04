"""
模块名称: bond_manager.py

该模块的目标：
    查看，创建，删除链路聚合功能
  
作者: ych
修改历史:
    1. 2025/9/4 - 创建文件
"""
import argparse
import time
from datetime import datetime
from waf_http.http import HttpObj


class NetworkBondManager:
    """网络链路聚合管理类"""

    def __init__(self, http_obj):
        self.http_obj = http_obj

    def get_bonds(self):
        """获取所有链路聚合信息"""
        url = "api/v2/network/bonds/"
        return self.http_obj._http_get(url)

    def create_bond(self, name, net_devs, desc=""):
        """创建网络链路聚合"""
        url = "api/v2/network/bonds/"
        # 构造请求体
        data = {
            "desc": desc,
            "net_dev": net_devs,
            "name": name
        }
        # 发送POST请求
        return self.http_obj._http_post(url, data=data)

    def delete_bond(self, bond_pk):
        """删除网络链路聚合"""
        # 构造URL，包含链路聚合主键
        url = f"api/v2/network/bonds/{bond_pk}/"
        # 生成时间戳参数
        params = {"_ts": int(time.time() * 1000)}
        # 发送DELETE请求
        return self.http_obj._http_delete(url, params=params)


def print_bonds_info(bonds_data):
    """打印链路聚合信息"""
    print("\n网络链路聚合信息:")
    print("=" * 80)

    if 'count' in bonds_data:
        print(f"链路聚合总数: {bonds_data.get('count', 0)}")
        print(f"当前页码: {bonds_data.get('page', 1)}")
        print(f"每页数量: {bonds_data.get('per_page', 20)}")
        print("=" * 80)

        # 打印每个链路聚合的详细信息
        for i, bond in enumerate(bonds_data.get('result', []), 1):
            print(f"\n链路聚合 {i}: {bond.get('name', 'N/A')}")
            print("-" * 60)

            # 基本信息
            print(f"  主键 (PK): {bond.get('_pk', 'N/A')}")
            print(f"  描述: {bond.get('desc', 'N/A')}")
            print(f"  网络设备: {', '.join(bond.get('net_dev', []))}")
            print(f"  命名空间ID: {bond.get('namespace_id', 'N/A')}")
            print(f"  用户ID: {bond.get('_user_id', 'N/A')}")

            # 状态信息
            print(f"  是否删除: {'是' if bond.get('_is_delete') else '否'}")
            print(f"  创建时间: {format_timestamp(bond.get('_create_timestamp'))}")
            print(f"  更新时间: {format_timestamp(bond.get('_update_timestamp'))}")

            # 补丁信息
            patch = bond.get('patch', {})
            if patch:
                print(f"  补丁配置:")
                for key, value in patch.items():
                    print(f"    {key}: {value}")
            else:
                print(f"  补丁配置: 无")

            print("-" * 60)


def format_timestamp(timestamp):
    """将时间戳格式化为可读时间"""
    if timestamp:
        try:
            # 将毫秒时间戳转换为秒
            dt = datetime.fromtimestamp(timestamp / 1000)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, OSError):
            return str(timestamp)
    return "N/A"


def main():
    parser = argparse.ArgumentParser(description='网络链路聚合管理工具')
    parser.add_argument('--ip', required=True, help='设备IP地址')
    parser.add_argument('--user', default='admin', help='用户名')
    parser.add_argument('--password', default='Admin@1234', help='密码')
    parser.add_argument('--port', type=int, default=443, help='端口号')
    parser.add_argument('--otp', help='OTP密钥（双因子认证）')

    # 创建链路聚合参数
    parser.add_argument('--create', action='store_true', help='创建链路聚合')
    parser.add_argument('--name', help='链路聚合名称')
    parser.add_argument('--net-devs', nargs='+', help='网络设备列表（如eth2 eth3）')
    parser.add_argument('--desc', default='', help='链路聚合描述')

    # 删除链路聚合参数
    parser.add_argument('--delete', action='store_true', help='删除链路聚合')
    parser.add_argument('--bond-pk', help='链路聚合的主键')

    # 查看链路聚合参数
    parser.add_argument('--list', action='store_true', help='列出所有链路聚合')

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

        # 创建链路聚合管理器实例
        bond_manager = NetworkBondManager(http_obj)

        # 创建链路聚合
        if args.create:
            if not args.name or not args.net_devs:
                print("创建链路聚合需要指定名称和网络设备列表")
                return
            print(f"正在创建链路聚合: {args.name}")
            result = bond_manager.create_bond(args.name, args.net_devs, args.desc)
            if result.get('success', False) or '_pk' in result:
                print(f"链路聚合创建成功! 主键: {result.get('_pk', 'N/A')}")
            else:
                print(f"链路聚合创建失败: {result.get('message', '未知错误')}")
            return

        # 删除链路聚合
        if args.delete:
            # 如果提供了名称但没有提供主键，则通过名称查找主键
            if not args.bond_pk and args.name:
                # 获取所有链路聚合信息
                bonds = bond_manager.get_bonds()
                found_bond = None
                # 在结果中查找匹配名称的链路聚合
                for bond in bonds.get('result', []):
                    if bond.get('name') == args.name:
                        found_bond = bond
                        break
                if found_bond:
                    args.bond_pk = found_bond.get('_pk')
                    print(f"找到链路聚合 '{args.name}'，主键为: {args.bond_pk}")
                else:
                    print(f"未找到名为 '{args.name}' 的链路聚合")
                    return
            elif not args.bond_pk:
                print("删除链路聚合需要指定链路聚合的主键(--bond-pk)或名称(--name)")
                return
            # 确认删除操作
            confirm = input(f"确定要删除链路聚合 (主键: {args.bond_pk}) 吗？此操作不可逆！(y/N): ")
            if confirm.lower() != 'y':
                print("操作已取消")
                return
            print(f"正在删除链路聚合: {args.bond_pk}")
            result = bond_manager.delete_bond(args.bond_pk)
            if result.get('code') == 'SUCCESS':
                print("链路聚合删除成功!")
            else:
                print(f"链路聚合删除失败: {result.get('message', '未知错误')}")
            return

        # 列出所有链路聚合
        if args.list:
            bonds = bond_manager.get_bonds()
            print_bonds_info(bonds)
            return

        print("请指定要执行的操作: 使用 --list 查看链路聚合列表, --create 创建链路聚合, 或 --delete 删除链路聚合")

    except Exception as e:
        print(f"操作失败: {e}")


if __name__ == "__main__":
    # 查看用法：python bond_manager.py --ip 10.20.192.106 --list
    # 删除：python bond_manager.py --ip 10.20.192.106 --delete --name bond1
    # 创建：python bond_manager.py --ip 10.20.192.106 --create --name bond1 --net-devs eth2 eth3
    main()
