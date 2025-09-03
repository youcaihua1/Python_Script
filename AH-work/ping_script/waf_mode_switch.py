"""
模块名称: waf_mode_switch.py

该模块的目标：
    实现waf的模式切换，并且截图关键内容
  
作者: ych
修改历史:
    1. 2025/9/3 - 创建文件
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import time
import sys

service = webdriver.ChromeService(r'D:\Programs\driver\chromedriver-win64\chromedriver.exe')  # 手动指定 ChromeDriver 位置

# 配置Chrome选项（忽略SSL证书错误）
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-running-insecure-content')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument('--start-maximized')  # 添加全屏显示参数
# chrome_options.add_argument("--headless=new")

# 初始化WebDriver（请确保chromedriver在系统PATH中）
driver = webdriver.Chrome(service=service, options=chrome_options)


def switch_run_level():
    """ 网桥直通和正常模式之间的切换 """
    driver.get(f'https://{ip}/#/device/runtype')
    # 获取并打印当前运行等级状态
    status_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//div[contains(@class, 'el-alert__content')]//span[contains(@class, 'el-alert__title') and contains(text(), '当前运行等级状态')]"
        ))
    )
    print(f"{status_element.text}")
    # 通过标签文本定位下拉菜单
    label = driver.find_element(
        By.XPATH,
        "//label[contains(text(), '运行等级')]"
    )
    # 找到相邻的下拉菜单输入框
    dropdown_input = label.find_element(
        By.XPATH,
        "./following-sibling::div//input[@placeholder='请选择']"
    )
    dropdown_input.click()
    # 获取所有选项及其文本
    options = driver.find_elements(By.XPATH, "//li[contains(@class, 'el-select-dropdown__item')]")
    option_texts = [option.text for option in options]
    # 如果"网桥直通"未被选中，选择它
    if "selected" not in options[option_texts.index("网桥直通")].get_attribute("class"):
        options[option_texts.index("网桥直通")].click()
        print("已选择'网桥直通'")
    else:
        # 如果"网桥直通"已被选中，选择"正常"
        options[option_texts.index("正常")].click()
        print("已选择'正常'")
    apply_button = driver.find_element(
        By.XPATH,
        "//button[contains(@class, 'el-button--primary') and contains(@class, 'el-button--mini')]//span[text()='应用']"
    )
    apply_button.click()


def waf_screenshot(img1, img2, img3):
    driver.get(f'https://{ip}/#/overview/dashboard')
    target_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            "//div[contains(@class, 'statics-item') and contains(@class, 'el-col-8')]"
        ))
    )
    # 使用JavaScript直接滚动到元素
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_element)
    # 等待滚动完成
    time.sleep(1)
    # 截取整个页面
    output_file = f"./img/{img1}.png"
    # print(f"正在截图并保存为: {output_file}")
    driver.save_screenshot(output_file)
    # 截图接口部分
    driver.get(f'https://{ip}/#/network/interface')
    # 定位选择框元素
    select_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//input[@type='text' and @readonly='readonly' and @placeholder='请选择' and contains(@class, 'el-input__inner')]"
        ))
    )
    # 点击选择框以展开下拉菜单
    select_box.click()
    # 定位并选择"50条/页"选项
    option_50 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//li[contains(@class, 'el-select-dropdown__item')]//span[text()='50条/页']"
        ))
    )
    option_50.click()
    time.sleep(0.5)
    # 截取整个页面
    output_file = f"./img/{img2}.png"
    driver.save_screenshot(output_file)
    # 启用表格滚动
    driver.execute_script("""
                var tableWrapper = document.querySelector('.el-table__body-wrapper');
                tableWrapper.classList.remove('is-scrolling-none');
                tableWrapper.style.overflowY = 'auto';
            """)
    # 定位可滚动的表格主体部分
    scrollable_table = driver.find_element(By.CLASS_NAME, "el-table__body-wrapper")
    # 滚动操作列
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scrollable_table)
    time.sleep(1.5)
    # 截取整个页面
    output_file = f"./img/{img3}.png"
    driver.save_screenshot(output_file)


def waf_login():
    # =============================打开登录页面==================================
    driver.get(f'https://{ip}/#/login')
    # =============================输入账号密码==================================
    username_field = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
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


def mode_switch():
    try:
        # =============================登录waf==================================
        waf_login()
        driver.execute_script("document.body.style.zoom = 0.75")  # 使用 JavaScript 直接设置缩放级别
        # =============================截图==================================
        waf_screenshot('1', '2', '3')
        # =============================切换模式：正常切换到网桥直通==================================
        switch_run_level()
        time.sleep(3)
        # =============================截图==================================
        waf_screenshot('4', '5', '6')
        # =============================切换模式：网桥直通切换到正常==================================
        switch_run_level()
        time.sleep(10)
        # =============================截图==================================
        waf_screenshot('7', '8', '9')

    except Exception as e:
        print(f"登录过程中出错: {str(e)}")
    finally:
        # 调试时可注释掉close以便查看登录后的页面
        driver.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("用法: python waf_mode_switch.py <输入IP>")
        print("示例: python waf_mode_switch.py 10.20.192.106")
        sys.exit(1)

    ip = sys.argv[1]
    mode_switch()
