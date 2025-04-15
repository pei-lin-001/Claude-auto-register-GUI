import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chrome_bot import chromeBot
from utils.cookie_utils import CookieManager, CookiePartitionKey
import time

def save_cookies_demo():
    """保存cookie演示"""
    # 创建Chrome实例
    bot = chromeBot()
    # 这里使用一个假的代理IP，实际使用时应该替换为真实代理
    chrome = bot.createWebView("127.0.0.1", "8080")
    
    # 访问Claude网站
    chrome.get("https://claude.ai")
    print("等待页面加载...")
    time.sleep(5)  # 等待页面加载
    
    # 获取所有cookie，包括httpOnly
    cookies = CookieManager.get_all_cookies(chrome)
    
    # 输出cookie信息
    print(f"获取到 {len(cookies)} 个cookie")
    for i, cookie in enumerate(cookies):
        is_http_only = cookie.get('httpOnly', False)
        domain = cookie.get('domain', 'N/A')
        name = cookie.get('name', 'N/A')
        print(f"{i+1}. {name} - 域: {domain} - httpOnly: {is_http_only}")
    
    # 保存cookie到文件
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "claude_cookies.json")
    CookieManager.save_cookies(cookies, save_path)
    print(f"Cookie已保存到: {save_path}")
    
    # 关闭浏览器
    chrome.quit()
    return save_path

def load_cookies_demo(cookie_file):
    """加载cookie演示"""
    # 创建Chrome实例
    bot = chromeBot()
    # 这里使用一个假的代理IP，实际使用时应该替换为真实代理
    chrome = bot.createWebView("127.0.0.1", "8080")
    
    # 先访问Claude域，因为需要在同一域下才能设置cookie
    chrome.get("https://claude.ai")
    print("等待页面加载...")
    time.sleep(3)  # 等待页面加载
    
    # 加载cookie
    cookies = CookieManager.load_cookies(cookie_file)
    print(f"从文件加载了 {len(cookies)} 个cookie")
    
    # 设置cookie
    success_count = CookieManager.set_cookies(chrome, cookies)
    print(f"成功设置了 {success_count} 个cookie")
    
    # 刷新页面，查看是否已登录
    chrome.refresh()
    print("刷新页面，检查cookie是否生效...")
    time.sleep(10)  # 等待查看结果
    
    # 关闭浏览器
    chrome.quit()

if __name__ == "__main__":
    # 保存cookie
    cookie_file = save_cookies_demo()
    
    # 加载cookie
    print("\n" + "="*50 + "\n")
    time.sleep(3)  # 等待几秒钟
    load_cookies_demo(cookie_file) 