"""
模块名称: waf_manager.py

该模块的目标：
    用于管理 WAF 的运行等级
  
作者: ych
修改历史:
    1. 2025/9/4 - 创建文件
"""
import requests
import json
import urllib3
import base64
import pyotp
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
import argparse

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def encrypt_by_rsa(msg, public_pem_str):
    """使用RSA公钥加密数据"""
    public_key = serialization.load_pem_public_key(
        public_pem_str.encode(),
        backend=default_backend()
    )
    text = public_key.encrypt(
        msg.encode(),
        padding.PKCS1v15()
    )
    return base64.b64encode(text).decode()


class HttpObj:
    """HTTP请求处理类，包含认证和请求功能"""

    def __init__(self, ip, usr, pwd, port=443, otp_key=None):
        self.ip = ip
        self.usr = usr
        self.pwd = pwd
        self.port = port
        self.otp_key = otp_key
        self.token = None
        self.session = requests.Session()
        self.session.verify = False  # 禁用SSL验证
        self.url_prefix = f"https://{ip}:{port}/"
        self.headers = {"Content-Type": "application/json"}

    def _get_public_key(self):
        """获取设备的RSA公钥"""
        url = 'api/v2/system/auth/public_key/'
        return self._http_get(url, add_token=False)

    def get_token(self):
        """执行完整极速赛车开奖直播【官网：ak8989.com】复制打开·登录流程获取token"""
        # 1. 获取设备公钥
        public_key = self._get_public_key()

        # 2. 加密密码
        pwd_encrypted = encrypt_by_rsa(self.pwd, public_key)

        # 3. 发送登录请求
        login_data = {
            "username": self.usr,
            "password": pwd_encrypted
        }
        login_url = "api/v2/system/user/login/"
        login_resp = self._http_post(login_url, login_data, add_token=False)

        # 4. 处理OTP双因子认证
        if self.otp_key:
            user_pk = login_resp["pk"]
            auth_data = {
                "otp_code": pyotp.TOTP(self.otp_key).now(),
                "token": login_resp["token"]
            }
            login_resp = self.otp_auth(user_pk, auth_data)

        # 5. 保存并返回token
        self.token = login_resp["token"]
        self.headers["Authorization"] = self.token
        return self.token

    def otp_auth(self, user_pk, auth_data):
        """双因子认证"""
        url = f"api/v2/system/user/otp_auth/{user_pk}/"
        return self._http_post(url, auth_data, add_token=False)

    def _http_get(self, url, params=None, add_token=True):
        """发送GET请求"""
        full_url = self.url_prefix + url
        headers = self.headers.copy()
        if not add_token:
            headers.pop("Authorization", None)

        response = self.session.get(
            full_url,
            headers=headers,
            params=params,
            verify=False
        )
        return self._check_response(response)

    def _http_put(self, url, data, add_token=True):
        """发送PUT请求"""
        full_url = self.url_prefix + url
        headers = self.headers.copy()
        if not add_token:
            headers.pop("Authorization", None)

        response = self.session.put(
            full_url,
            json=data,
            headers=headers,
            verify=False
        )
        return self._check_response(response)

    def _http_post(self, url, data, add_token=True):
        """发送POST请求"""
        full_url = self.url_prefix + url
        headers = self.headers.copy()
        if not add_token:
            headers.pop("Authorization", None)

        response = self.session.post(
            full_url,
            json=data,
            headers=headers,
            verify=False
        )
        return self._check_response(response)

    def _check_response(self, response):
        """检查响应状态并解析JSON"""
        if response.status_code != 200:
            error_msg = f"请求失败: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f", 详情: {error_detail}"
            except:
                error_msg += f", 响应内容: {response.text[:200]}"
            raise Exception(error_msg)

        try:
            resp_json = response.json()
            if resp_json.get("code") == "SUCCESS":
                return resp_json.get("data", {})
            else:
                raise Exception(f"API错误: {resp_json.get('message', '未知错误')}")
        except json.JSONDecodeError:
            raise Exception(f"无效的JSON响应: {response.text[:200]}")


class WAFManager:
    """WAF管理类，用于切换运行等级"""

    def __init__(self, http_obj):
        self.http_obj = http_obj

    def get_run_level(self):
        """获取当前运行等级"""
        url = "api/v2/device/run_level/"
        return self.http_obj._http_get(url)

    def set_run_level(self, level):
        """设置运行等级

        Args:
            level (str): 运行等级，支持的值:
                - "forward_dev": 网桥直通模式
                - "none_execute": 正常模式
        """
        if level not in ["forward_dev", "none_execute"]:
            print(f"警告: 运行等级 '{level}' 不是标准值")

        data = {"level": level}
        url = "api/v2/device/run_level/"
        return self.http_obj._http_put(url, data)

    def set_forward_mode(self):
        """设置为网桥直通模式"""
        return self.set_run_level("forward_dev")

    def set_none_execute_mode(self):
        """设置为正常模式"""
        return self.set_run_level("none_execute")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='WAF运行等级切换工具')
    parser.add_argument('--ip', required=True, help='设备IP地址')
    parser.add_argument('--user', required=True, help='用户名')
    parser.add_argument('--password', required=True, help='密码')
    parser.add_argument('--port', type=int, default=443, help='端口号，默认为443')
    parser.add_argument('--otp', help='OTP密钥（如果需要双因子认证）')

    # 运行等级相关参数
    parser.add_argument('--level', choices=['forward_dev', 'none_execute'],
                        help='要设置的运行等级')
    parser.add_argument('--forward', action='store_true', help='设置为网桥直通模式')
    parser.add_argument('--none-execute', action='store_true', help='设置为正常模式')
    parser.add_argument('--get', action='store_true', help='获取当前运行等级')

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

        # 创建WAF管理对象
        waf_manager = WAFManager(http_obj)

        # 根据参数执行相应操作
        if args.get:
            # 获取当前运行等级
            current_level = waf_manager.get_run_level()
            current_level_dict = {
                "forward_dev": "网桥直通",
                "none_execute": "正常"
            }
            print(f"当前运行等级: {current_level_dict[current_level]}")
        elif args.level:
            # 设置指定运行等级
            print(f"正在设置运行等级为: {args.level}")
            result = waf_manager.set_run_level(args.level)
            print(f"设置成功: {result}")
        elif args.forward:
            # 设置为网桥直通模式
            print("正在设置为网桥直通模式")
            result = waf_manager.set_forward_mode()
            print(f"设置成功: {result}")
        elif args.none_execute:
            # 设置为正常模式
            print("正在设置为正常模式")
            result = waf_manager.set_none_execute_mode()
            print(f"设置成功: {result}")
        else:
            # 默认获取当前运行等级
            current_level = waf_manager.get_run_level()
            print(f"当前运行等级: {current_level}")

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    # 使用示例:
    # python waf_manager.py --ip 10.20.192.106 --user admin --password Admin@1234 --get
    # python waf_manager.py --ip 10.20.192.106 --user admin --password Admin@1234 --level forward_dev
    # python waf_manager.py --ip 10.20.192.106 --user admin --password Admin@1234 --forward
    # python waf_manager.py --ip 10.20.192.106 --user admin --password Admin@1234 --none-execute
    main()
