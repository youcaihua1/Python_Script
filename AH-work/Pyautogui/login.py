"""
模块名称: login.py

该模块的目标：
    实现waf登录
  
作者: ych
修改历史:
    1. 2025/8/27 - 创建文件
    2. 2025/8/28 - 使用复制粘贴输入账号密码
"""
import pyautogui
import pyperclip
import time


def login_admin():
    # 等待用户切换到浏览器并定位到登录页面
    time.sleep(2)  # 给用户时间切换到浏览器并导航到登录页

    # 确保焦点在浏览器窗口
    # pyautogui.click(100, 100)  # 点击浏览器窗口的任意位置确保焦点

    # 导航到用户名字段并输入
    pyautogui.press('tab')  # 按Tab键直到焦点在用户名字段
    # 可能需要多次按Tab键，取决于页面结构
    # pyautogui.press('tab')  # 如果需要，再按一次

    pyperclip.copy('admin')  # 使用剪贴板输入用户名（避免输入法问题）
    pyautogui.hotkey('ctrl', 'v')

    # 导航到密码字段并输入
    pyautogui.press('tab')  # 移动到密码字段
    pyperclip.copy('Admin@1234')
    pyautogui.hotkey('ctrl', 'v')  # 粘贴

    # 提交表单
    pyautogui.press('enter')


if __name__ == '__main__':
    login_admin()  # waf登录
