"""
模块名称: open_ssh.py

该模块的目标：
    打开设备的ssh服务
  
作者: ych
修改历史:
    1. 2025/9/1 - 创建文件
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


def open_ssh(ip):
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
        # =============================打开ssh服务==================================
        target_url = f"https://{ip}/#/device/access/web"
        driver.get(target_url)  # 跳转到访问设置
        print(f"已跳转到: {target_url}")
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[@class='first-level-heading' and contains(text(), 'SSH访问')]")
        ))  # 等待页面加载完成
        print("SSH访问页面已加载完成")
        fold_link = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a.content-fold[href='javascript://']")
        ))  # 定位折叠链接
        fold_link.click()
        print("已点击折叠链接")
        ssh_label = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//label[@class='el-form-item__label' and contains(text(), 'SSH服务')]")
        ))  # 先找到包含"SSH服务"文本的label元素
        # 找到相邻的content区域
        content_div = ssh_label.find_element(By.XPATH, "./following-sibling::div[@class='el-form-item__content']")
        # 在content区域内查找el-switch组件
        el_switch = content_div.find_element(By.CLASS_NAME, "el-switch")
        # 获取隐藏的复选框input
        checkbox_input = el_switch.find_element(By.CLASS_NAME, "el-switch__input")
        # 获取可视的开关核心部分
        switch_core = el_switch.find_element(By.CLASS_NAME, "el-switch__core")
        # 检查开关状态 - Element UI的开关状态可以通过aria-checked属性或类名判断
        is_checked = (
                el_switch.get_attribute("aria-checked") == "true" or
                "is-checked" in el_switch.get_attribute("class") or
                checkbox_input.is_selected()
        )
        print(f"SSH服务当前状态: {'已启用' if is_checked else '未启用'}")
        # 如果未启用，则启用它
        if not is_checked:
            print("正在启用SSH服务...")
            # 点击开关的可视部分
            switch_core.click()
            print("SSH服务已启用")
            time.sleep(1)  # 等待状态更新
        save_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             '//*[@id="app"]/div/div[1]/div[2]/div/div[2]/div/div/div[2]/div[2]/div/div[3]/div/form/div[2]/div/button')
        ))
        # 确保按钮可见并可用
        wait.until(EC.visibility_of(save_button))
        # 点击保存按钮
        save_button.click()
        print("已点击保存按钮")
        # 等待操作完成，检查是否有成功提示
        try:
            success_message = wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 "//*[contains(text(), '成功') or contains(text(), '保存成功') or contains(text(), '设置已更新')]")
            ))
            print("操作成功:", success_message.text)
        except:
            print("保存操作已完成，但未检测到成功消息")

        print("SSH服务设置已完成")
        time.sleep(3)

    except Exception as e:
        print(f"登录过程中出错: {str(e)}")
    finally:
        # 调试时可注释掉close以便查看登录后的页面
        driver.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("用法: python open_ssh.py <输入IP>")
        print("示例: python open_ssh.py 10.20.192.106")
        sys.exit(1)

    ip = sys.argv[1]
    open_ssh(ip)
