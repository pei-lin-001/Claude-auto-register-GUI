# coding:utf-8
# from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os, random, platform


def create_web_view(proxy_details=None):
    try:
        # 根据操作系统选择正确的chromedriver文件名
        if platform.system() == "Windows":
            driver_filename = "chromedriver.exe"
        else:
            driver_filename = "chromedriver"
        
        chrome_driver_path = os.path.join(os.getcwd(), "driver", driver_filename)
        service = Service(chrome_driver_path)
        chromeOption = webdriver.ChromeOptions()
        
        prefs = {"profile.managed_default_content_settings.images": 2}
        chromeOption.add_experimental_option("prefs", prefs)

        if proxy_details and isinstance(proxy_details, dict) and proxy_details.get("proxy_string") and proxy_details.get("type"):
            proxy_string = proxy_details["proxy_string"]
            proxy_type = proxy_details["type"]
            
            formatted_proxy = None
            if proxy_type == "http_ip_port":
                # 假设 proxy_string 是 "IP:端口" 格式
                formatted_proxy = f"http://{proxy_string}"
            elif proxy_type == "http_user_pass":
                # 假设 proxy_string 是 "用户名:密码@IP:端口" 格式
                # 对于Chrome，--proxy-server=http://用户名:密码@主机:端口是标准方式
                # 除非代理本身行为异常，否则通常不需要特殊扩展
                formatted_proxy = f"http://{proxy_string}"
            elif proxy_type == "socks5":
                # 假设 proxy_string 是 "IP:端口" 格式
                formatted_proxy = f"socks5://{proxy_string}"
            elif proxy_type == "socks5_user_pass": 
                # 假设 proxy_string 是 "用户名:密码@IP:端口" 格式
                formatted_proxy = f"socks5://{proxy_string}"
            
            if formatted_proxy:
                print(f"尝试使用代理: {formatted_proxy} (类型: {proxy_type})")
                chromeOption.add_argument(f"--proxy-server={formatted_proxy}")
            else:
                print(f"不支持的代理类型 ('{proxy_type}') 或无效的代理字符串。将不使用代理继续。")
        else:
            print("未提供有效的代理详情。将不使用代理继续。")

        chromeOption.add_argument("--no-sandbox")
        chromeOption.add_argument("--disable-dev-shm-usage")
        # file_path = os.path.join(os.getcwd(), "pro.zip")
        # chromeOption.add_extension(file_path)
        print("等待启动")
        chrome = webdriver.Chrome(
            service=service, options=chromeOption, keep_alive=True
        )
        # 设置请求拦截器来阻止CSS请求
        chrome.execute_cdp_cmd('Network.setBlockedURLs', {
            'urls': ['.css', '*.css', 'https://*.css', 'http://*.css','.woff2', '*.woff2', 'https://*.woff2', 'http://*.woff2']
        })
        chrome.execute_cdp_cmd('Network.enable', {})
        return chrome
    except Exception as e:
        print("An error occurred:", str(e))
        return None

def wait_for_element(driver, by, selector, timeout=30):
    """
    等待元素出现并返回该元素，有超时时间
    
    参数:
    driver - WebDriver实例
    by - 定位策略 (e.g., By.XPATH, By.ID)
    selector - 元素选择器
    timeout - 超时时间（秒）
    
    返回:
    找到的元素或None（如果超时）
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element
    except TimeoutException:
        print(f"等待元素 {selector} 超时")
        return None

def wait_for_element_clickable(driver, by, selector, timeout=30):
    """
    等待元素可点击并返回该元素
    
    参数:
    driver - WebDriver实例
    by - 定位策略 (e.g., By.XPATH, By.ID)
    selector - 元素选择器
    timeout - 超时时间（秒）
    
    返回:
    可点击的元素或None（如果超时）
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        return element
    except TimeoutException:
        print(f"等待元素 {selector} 可点击超时")
        return None

# 添加获取所有cookie的方法
def get_all_cookies(driver):
    """
    获取所有cookie，包括httpOnly标记的cookie
    
    Args:
        driver: WebDriver实例
        
    Returns:
        cookie列表
    """
    try:
        all_cookies = driver.execute_cdp_cmd('Network.getAllCookies', {})
        return all_cookies.get('cookies', [])
    except Exception as e:
        print(f"获取cookie失败: {str(e)}")
        return []

# 添加设置cookie的方法
def set_cookie(driver, cookie):
    """
    使用CDP设置单个cookie
    
    Args:
        driver: WebDriver实例
        cookie: 要设置的cookie字典
        
    Returns:
        成功返回True，失败返回False
    """
    try:
        driver.execute_cdp_cmd('Network.setCookie', cookie)
        return True
    except Exception as e:
        print(f"设置cookie失败: {str(e)}")
        return False

# 添加批量设置cookie的方法
def set_cookies(driver, cookies):
    """
    批量设置cookie
    
    Args:
        driver: WebDriver实例
        cookies: cookie列表
        
    Returns:
        成功设置的cookie数量
    """
    success_count = 0
    for cookie in cookies:
        if set_cookie(driver, cookie):
            success_count += 1
    return success_count
