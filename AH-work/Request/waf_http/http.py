"""
模块名称: http.py

该模块的目标：
    存放 waf 的 HttpObj 类
  
作者: ych
修改历史:
    1. 2025/9/4 - 创建文件
"""
import urllib3
import requests
import base64
import pyotp
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding

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

    def _http_delete(self, url, params=None):
        """发送DELETE请求 """
        full_url = self.url_prefix + url
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
        }

        response = self.session.delete(full_url, headers=headers, params=params, verify=False)
        response.raise_for_status()

        # 尝试解析JSON响应，如果响应为空则返回成功消息
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"success": True, "message": "删除操作成功完成"}

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
