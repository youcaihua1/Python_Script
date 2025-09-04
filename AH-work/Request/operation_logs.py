"""
模块名称: operation_logs.py

该模块的目标：
    获取操作日志的内容
  
作者: ych
修改历史:
    1. 2025/9/4 - 创建文件
"""
from datetime import datetime, timedelta
import argparse
from waf_http.http import HttpObj


class OperationLogService:
    """操作日志服务类"""

    def __init__(self, http_obj):
        self.http_obj = http_obj

    def get_today_operation_logs(self, start_time, end_time):
        """获取今天的操作日志"""
        # 构建查询参数
        params = {
            "per_page": 20,
            "page": 1,
            "timestamp__gte": start_time,
            "timestamp__lte": end_time
        }

        # 发送请求获取操作日志
        url = "api/v2/logs/events/"
        try:
            response_data = self.http_obj._http_get(url, params=params)

            logs = response_data.get("result", [])
            total_count = response_data.get("count", 0)
            per_page = response_data.get("per_page", 100)

            print(f"找到 {total_count} 条日志记录，每页 {per_page} 条")

            # 如果有多页数据，获取所有页
            if total_count > per_page:
                total_pages = (total_count + per_page - 1) // per_page
                print(f"需要获取 {total_pages} 页数据...")

                for page in range(2, total_pages + 1):
                    params["page"] = page
                    page_data = self.http_obj._http_get(url, params=params)

                    if page_data and "result" in page_data:
                        logs.extend(page_data["result"])

            return logs
        except Exception as e:
            print(f"获取日志失败: {e}")
            return []


def print_logs(logs, start_time, end_time):
    """格式化打印日志"""
    if not logs:
        print(f"在 {start_time} 到 {end_time} 范围内未找到操作日志")
        return

    print("\n" + "=" * 120)
    print(f"操作日志 ({start_time} 到 {end_time}) - 共 {len(logs)} 条记录")
    print("=" * 120)

    for i, log in enumerate(logs, 1):
        print(f"{i}. 时间: {log.get('timestamp', 'N/A')}")
        print(f"   用户: {log.get('user', 'N/A')}")
        print(f"   客户端IP: {log.get('ip', 'N/A')}")
        print(f"   事件名称: {log.get('target', 'N/A')}")
        print(f"   操作类型: {log.get('opt_type', 'N/A')}")
        print(f"   操作结果: {log.get('opt_res', 'N/A')}")
        # print(f"   设备ID: {log.get('device_id', 'N/A')}")
        # print(f"   设备名称: {log.get('device_name', 'N/A')}")
        # 打印详细信息
        # detail = log.get('detail', {})
        # if detail:
        #     print(f"   请求路径: {detail.get('extend', {}).get('Path', 'N/A')}")
        #     print(f"   请求方法: {detail.get('extend', {}).get('Method', 'N/A')}")
        #     print(f"   用户代理: {detail.get('extend', {}).get('User-Agent', 'N/A')}")
        print("-" * 120)


def parse_time_input(time_str, default_hour_minute="00:00:00"):
    """解析时间输入，支持多种格式"""
    if not time_str:
        return None
    # 如果只提供了日期，添加默认时间
    if len(time_str) == 10 and time_str.count("-") == 2:
        return f"{time_str} {default_hour_minute}"
    # 如果提供了完整日期时间，直接返回
    return time_str


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='获取今日操作日志工具')
    parser.add_argument('--ip', required=True, help='设备IP地址')
    parser.add_argument('--user', required=True, help='用户名')
    parser.add_argument('--password', required=True, help='密码')
    parser.add_argument('--port', type=int, default=443, help='端口号，默认为443')
    parser.add_argument('--otp', help='OTP密钥（如果需要双因子认证）')
    # 添加时间范围参数
    today = datetime.now().strftime("%Y-%m-%d")
    parser.add_argument('--start-time', default=f"{today} 00:00:00",
                        help='开始时间，格式: YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS (默认: 当天00:00:00)')
    parser.add_argument('--end-time', default=f"{today} 23:59:59",
                        help='结束时间，格式: YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS (默认: 当天23:59:59)')
    # 添加日期快捷方式
    parser.add_argument('--today', action='store_true', help='查询今天的日志 (默认)')
    parser.add_argument('--yesterday', action='store_true', help='查询昨天的日志')
    parser.add_argument('--last-7-days', action='store_true', help='查询最近7天的日志')
    parser.add_argument('--last-30-days', action='store_true', help='查询最近30天的日志')
    args = parser.parse_args()

    try:
        # 处理时间范围
        start_time = parse_time_input(args.start_time, "00:00:00")
        end_time = parse_time_input(args.end_time, "23:59:59")
        # 处理日期快捷方式
        now = datetime.now()
        if args.yesterday:
            yesterday = now - timedelta(days=1)
            start_time = yesterday.strftime("%Y-%m-%d 00:00:00")
            end_time = yesterday.strftime("%Y-%m-%d 23:59:59")
        elif args.last_7_days:
            start_time = (now - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
            end_time = now.strftime("%Y-%m-%d 23:59:59")
        elif args.last_30_days:
            start_time = (now - timedelta(days=30)).strftime("%Y-%m-%d 00:00:00")
            end_time = now.strftime("%Y-%m-%d 23:59:59")
        print(f"查询时间范围: {start_time} 到 {end_time}")
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
        print("认证成功")

        # 创建操作日志服务对象
        log_service = OperationLogService(http_obj)
        # 获取操作日志
        logs = log_service.get_today_operation_logs(start_time, end_time)
        # 打印日志
        print_logs(logs, start_time, end_time)

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    # 使用：python operation_logs.py --ip 10.20.192.106 --user admin --password Admin@1234
    # python operation_logs.py --ip 10.20.192.106 --user admin --password Admin@1234 --start-time "2025-09-01" --end-time "2025-09-04"
    # python operation_logs.py --ip 10.20.192.106 --user admin --password Admin@1234 --yesterday
    # python operation_logs.py --ip 10.20.192.106 --user admin --password Admin@1234 --last-7-days
    # python operation_logs.py --ip 10.20.192.106 --user admin --password Admin@1234 --start-time "2025-09-02 02:12:31" --end-time "2025-09-03 12:32:32"
    main()
