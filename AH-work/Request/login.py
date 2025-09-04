"""
模块名称: login.py

该模块的目标：
    实现waf登录
  
作者: ych
修改历史:
    1. 2025/9/3 - 创建文件
"""
from waf_http.http import HttpObj


if __name__ == '__main__':
    # 基础登录
    http = HttpObj(ip="10.20.192.106", usr="admin", pwd="Admin@1234")
    token = http.get_token()
    print(f"Obtained token: {token}")
