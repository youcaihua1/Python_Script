"""
模块名称: waf_reboot.py

该模块的目标：
    waf前端重启
  
作者: ych
修改历史:
    1. 2025/9/2 - 创建文件
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys

service = webdriver.ChromeService(r'D:\Programs\driver\chromedriver-win64\chromedriver.exe')  # 手动指定 ChromeDriver 位置

# 配置Chrome选项（忽略SSL证书错误）
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-running-insecure-content')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument('--start-maximized')  # 添加全屏显示参数

# 初始化WebDriver（请确保chromedriver在系统PATH中）
driver = webdriver.Chrome(service=service, options=chrome_options)


def waf_reboot(ip):
    try:
        # =============================打开登录页面==================================
        driver.get(f'https://{ip}/#/login')
        wait = WebDriverWait(driver, 15)  # 显式等待页面元素加载
        # =============================输入账号密码==================================
        username_field = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder='用户名']")
        ))  # 等待用户名输入框出现
        username_field.send_keys('admin')  # 输入用户名
        password_field = driver.find_element(
            By.CSS_SELECTOR, "input[placeholder='密码']"
        )  # 定位密码输入框
        password_field.send_keys('Admin@1234')
        login_button = driver.find_element(
            By.CSS_SELECTOR, "button[type='button']"
        )  # 提交登录表单
        login_button.click()
        print("登录操作已完成，请检查页面状态")
        time.sleep(1)  # 等待登录完成
        # =============================waf前端重启==================================
        target_url = f"https://{ip}/#/device/hardware"
        driver.get(target_url)  # 跳转
        print(f"已跳转到: {target_url}")
        # 查找所有折叠链接
        fold_links = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "a.content-fold[href='javascript://']")
        ))
        print(f"找到 {len(fold_links)} 个折叠链接")
        # 点击第一个折叠链接
        if len(fold_links) > 0:
            fold_links[0].click()
            print("已点击第一个折叠链接")
            time.sleep(0.5)  # 等待动画完成
        # 点击第二个折叠链接
        if len(fold_links) > 1:
            fold_links[1].click()
            print("已点击第二个折叠链接")
            time.sleep(0.5)  # 等待动画完成
        # 点击第三个折叠链接
        if len(fold_links) > 2:
            fold_links[2].click()
            print("已点击第三个折叠链接")
            time.sleep(0.5)  # 等待动画完成
        reboot_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "//button[contains(@class, 'el-button--default') and contains(@class, 'el-button--mini')]//span[text()='重启']/..")
        ))
        # 确保按钮可见
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", reboot_button)
        # 点击重启按钮
        reboot_button.click()
        print("已点击重启按钮")
        # time.sleep(0.5)
        # 定位确定按钮
        confirm_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "//div[@class='el-message-box__btns']//button[contains(@class, 'el-button--primary') and contains(@class, 'el-button--danger')]")
        ))
        # 点击确定按钮
        confirm_button.click()
        print("已点击确定按钮")
        time.sleep(3)

    except Exception as e:
        print(f"登录过程中出错: {str(e)}")
    finally:
        # 调试时可注释掉close以便查看登录后的页面
        driver.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("用法: python waf_reboot.py <输入IP>")
        print("示例: python waf_reboot.py 10.20.192.106")
        sys.exit(1)

    ip = sys.argv[1]
    waf_reboot(ip)
