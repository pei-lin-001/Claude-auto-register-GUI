"""
注册引擎模块

集成实际的Claude注册逻辑，提供给现代化GUI使用
"""

import sys
import os
import time
import random
import string
import logging
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mail import QQMail
from cloudflare import mailCloud
from chrome_bot import chromeBot
from selenium.webdriver.common.by import By
from chrome_bot.insbot import wait_for_element, wait_for_element_clickable
import json
from utils.config import config
from utils.cookie_utils import CookieManager
from utils.proxy_manager import ProxyManager


class ClaudeRegisterEngine:
    """Claude注册引擎"""
    
    def __init__(self, callback=None):
        """
        初始化注册引擎
        
        Args:
            callback: 回调函数，用于更新UI状态
        """
        self.callback = callback
        self.mail_cloud = mailCloud()
        self.qq_mail = QQMail()
        self.proxy_manager = ProxyManager(max_usage_count=3)
        self.is_running = False
        
        # 设置日志
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志记录"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # 创建文件处理器
        log_file = time.strftime("./logs/%Y-%m-%d_%H-%M-%S.log", time.localtime())
        os.makedirs("./logs", exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        
        # 创建格式化器
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        
    def log_and_callback(self, message, level="info"):
        """记录日志并回调UI更新"""
        # 记录到日志文件
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "debug":
            self.logger.debug(message)
            
        # 回调UI更新
        if self.callback:
            self.callback(message, level)
            
    def generate_random_string(self, length=8):
        """生成随机字符串"""
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))
        
    def create_temp_email(self):
        """创建临时邮箱"""
        try:
            random_string = self.generate_random_string()
            self.log_and_callback(f"正在创建临时邮箱: {random_string}@{config['cloudflare']['rules_domain']}")
            
            mail_result = self.mail_cloud.createEmailRules(random_string)
            if mail_result["type"] == "True":
                email = mail_result["mail"]
                self.log_and_callback(f"临时邮箱创建成功: {email}")
                return email
            else:
                self.log_and_callback(f"临时邮箱创建失败: {mail_result.get('msg', '未知错误')}", "error")
                return None
                
        except Exception as e:
            self.log_and_callback(f"创建临时邮箱时出错: {str(e)}", "error")
            return None
            
    def init_chrome_browser(self, x=0, y=0):
        """初始化Chrome浏览器"""
        try:
            self.log_and_callback("正在初始化Chrome浏览器...")
            
            bot = chromeBot()
            proxy_details = self.proxy_manager.get_available_proxy()
            
            if proxy_details:
                self.log_and_callback(f"使用代理: {proxy_details['proxy_string']}")
            else:
                self.log_and_callback("未使用代理", "warning")
                
            chrome = bot.createWebView(proxy_details=proxy_details)
            
            if chrome is None:
                self.log_and_callback("Chrome浏览器初始化失败", "error")
                return None
                
            # 访问Claude网站
            self.log_and_callback("正在访问Claude.ai...")
            chrome.get("https://claude.ai")
            chrome.set_window_position(x, y)
            
            # 记录代理使用
            if proxy_details:
                self.proxy_manager.record_proxy_usage(
                    proxy_details["proxy_string"], 
                    proxy_details["file_path"]
                )
                
                stats = self.proxy_manager.get_proxy_statistics()
                self.log_and_callback(
                    f"代理统计: 总计 {stats['total_proxies']} 个，"
                    f"活跃 {stats['active_proxies']} 个，"
                    f"已耗尽 {stats['exhausted_proxies']} 个"
                )
                
            self.log_and_callback("Chrome浏览器初始化成功")
            return chrome
            
        except Exception as e:
            self.log_and_callback(f"初始化Chrome浏览器时出错: {str(e)}", "error")
            return None
            
    def get_dom_list(self):
        """获取DOM元素列表"""
        try:
            with open("domList.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            self.log_and_callback(f"加载DOM列表失败: {str(e)}", "error")
            return {}
            
    def fill_registration_form(self, chrome, email):
        """填写注册表单 - 使用智能自动化"""
        try:
            # 导入智能自动化模块
            from chrome_bot.smart_automation import ClaudeAutomationEngine

            self.log_and_callback("正在初始化智能自动化引擎...")
            automation = ClaudeAutomationEngine(chrome, self.logger)

            # 获取页面信息
            page_info = automation.get_page_info()
            self.log_and_callback(f"当前页面: {page_info.get('title', 'Unknown')}")

            # 使用智能填写表单
            self.log_and_callback("正在智能填写注册表单...")
            success = automation.fill_email_form(email)

            if success:
                self.log_and_callback(f"成功填写邮箱表单: {email}")

                # 等待页面跳转或状态变化
                current_url = chrome.current_url
                if automation.wait_for_page_change(current_url, timeout=15):
                    self.log_and_callback("页面已跳转，表单提交成功")
                else:
                    self.log_and_callback("页面未跳转，但表单可能已提交", "warning")

                return True
            else:
                self.log_and_callback("智能填写表单失败，尝试备用方案", "warning")
                return self._fallback_fill_form(chrome, email)

        except Exception as e:
            self.log_and_callback(f"智能填写表单时出错: {str(e)}", "error")
            return self._fallback_fill_form(chrome, email)

    def _fallback_fill_form(self, chrome, email):
        """备用表单填写方案"""
        try:
            self.log_and_callback("使用备用方案填写表单...")

            dom_list = self.get_dom_list()
            if not dom_list:
                return False

            # 等待邮箱输入框
            mail_input = wait_for_element(chrome, By.XPATH, dom_list["mailInput"], timeout=30)
            if mail_input is None:
                self.log_and_callback("备用方案：未找到邮箱输入框", "error")
                return False

            # 输入邮箱
            mail_input.clear()
            mail_input.send_keys(email)
            self.log_and_callback(f"备用方案：已输入邮箱: {email}")

            # 随机等待
            wait_time = random.randint(2, 5)
            self.log_and_callback(f"等待 {wait_time} 秒...")
            time.sleep(wait_time)

            # 点击下一步按钮
            next_button = wait_for_element_clickable(
                chrome, By.XPATH, dom_list["nextMailButton"], timeout=30
            )
            if next_button is None:
                self.log_and_callback("备用方案：未找到下一步按钮", "error")
                return False

            next_button.click()
            self.log_and_callback("备用方案：已点击下一步按钮")
            return True

        except Exception as e:
            self.log_and_callback(f"备用方案填写表单时出错: {str(e)}", "error")
            return False
            
    def get_verification_link(self, email):
        """获取验证链接"""
        try:
            self.log_and_callback("正在获取邮箱验证链接...")
            
            # 等待邮件到达
            time.sleep(5)
            
            jump_url = self.qq_mail.getUserTo(email, config["mail"]["mail_password"])
            
            if jump_url["type"] != "error":
                self.log_and_callback("验证链接获取成功")
                return jump_url["link"]
            else:
                self.log_and_callback(f"验证链接获取失败: {jump_url['msg']}", "error")
                return None
                
        except Exception as e:
            self.log_and_callback(f"获取验证链接时出错: {str(e)}", "error")
            return None
            
    def complete_verification(self, chrome, verification_link):
        """完成邮箱验证 - 使用智能自动化"""
        try:
            self.log_and_callback("正在完成邮箱验证...")

            # 跳转到验证链接
            chrome.get(verification_link)

            # 导入智能自动化模块
            from chrome_bot.smart_automation import ClaudeAutomationEngine

            automation = ClaudeAutomationEngine(chrome, self.logger)

            # 等待页面加载
            if not automation.locator.wait_for_page_load(timeout=30):
                self.log_and_callback("验证页面加载超时", "warning")

            # 获取页面信息
            page_info = automation.get_page_info()
            self.log_and_callback(f"验证页面: {page_info.get('title', 'Unknown')}")

            # 智能处理验证页面
            verification_success = automation.handle_verification_page()

            if verification_success:
                self.log_and_callback("智能验证页面处理成功")
            else:
                self.log_and_callback("智能验证失败，使用备用方案", "warning")
                verification_success = self._fallback_verification(chrome)

            if verification_success:
                # 获取并保存Cookie
                cookies = CookieManager.get_all_cookies(chrome)
                cookie_count = CookieManager.save_cookies(cookies)
                self.log_and_callback(f"成功保存 {cookie_count} 个Cookie")

                # 保存SessionKey
                CookieManager.save_session_key(cookies, is_phone=verification_success == "phone")
                session_type = "手机版" if verification_success == "phone" else "桌面版"
                self.log_and_callback(f"已保存{session_type}SessionKey")

                # 截图保存
                screenshot_path = automation.take_screenshot("verification_success.png")
                if screenshot_path:
                    self.log_and_callback(f"验证成功截图: {screenshot_path}")

                self.log_and_callback("邮箱验证完成")
                return True
            else:
                # 失败时也截图
                automation.take_screenshot("verification_failed.png")
                return False

        except Exception as e:
            self.log_and_callback(f"完成邮箱验证时出错: {str(e)}", "error")
            return False

    def _fallback_verification(self, chrome):
        """备用验证方案"""
        try:
            self.log_and_callback("使用备用验证方案...")

            dom_list = self.get_dom_list()
            if not dom_list:
                return False

            # 等待验证页面加载
            jump_page_years = wait_for_element(chrome, By.XPATH, dom_list["jumpPageYears"], timeout=30)
            if jump_page_years is None:
                self.log_and_callback("备用方案：验证页面加载失败", "error")
                return False

            # 检查是否为手机版本
            is_phone = wait_for_element(chrome, By.XPATH, dom_list["isPheon"], timeout=10)
            if is_phone is not None:
                try:
                    is_phone.click()
                    self.log_and_callback("备用方案：已点击手机版复选框")
                    return "phone"
                except Exception as e:
                    self.log_and_callback(f"备用方案：点击手机版复选框失败: {str(e)}", "warning")
                    return True
            else:
                self.log_and_callback("备用方案：未发现手机版复选框，使用桌面版")
                return True

        except Exception as e:
            self.log_and_callback(f"备用验证方案失败: {str(e)}", "error")
            return False
            
    def register_single_account(self, x=0, y=0):
        """注册单个账号"""
        chrome = None
        try:
            self.log_and_callback("开始注册新账号")
            
            # 1. 创建临时邮箱
            email = self.create_temp_email()
            if not email:
                return {"success": False, "message": "临时邮箱创建失败", "email": None}
                
            # 2. 初始化浏览器
            chrome = self.init_chrome_browser(x, y)
            if not chrome:
                return {"success": False, "message": "浏览器初始化失败", "email": email}
                
            # 3. 填写注册表单
            if not self.fill_registration_form(chrome, email):
                return {"success": False, "message": "注册表单填写失败", "email": email}
                
            # 4. 获取验证链接
            verification_link = self.get_verification_link(email)
            if not verification_link:
                return {"success": False, "message": "验证链接获取失败", "email": email}
                
            # 5. 完成验证
            if not self.complete_verification(chrome, verification_link):
                return {"success": False, "message": "邮箱验证失败", "email": email}
                
            self.log_and_callback("账号注册成功！")
            return {"success": True, "message": "注册成功", "email": email}
            
        except Exception as e:
            error_msg = f"注册过程中出现异常: {str(e)}"
            self.log_and_callback(error_msg, "error")
            return {"success": False, "message": error_msg, "email": None}
            
        finally:
            # 清理浏览器资源
            if chrome:
                try:
                    chrome.quit()
                    self.log_and_callback("浏览器已关闭")
                except:
                    pass
                    
    def register_multiple_accounts(self, count, interval=30, x=0, y=0):
        """批量注册账号"""
        self.is_running = True
        results = []
        
        try:
            self.log_and_callback(f"开始批量注册 {count} 个账号")
            
            for i in range(count):
                if not self.is_running:
                    self.log_and_callback("注册已被停止")
                    break
                    
                self.log_and_callback(f"正在注册第 {i+1}/{count} 个账号")
                
                # 注册单个账号
                result = self.register_single_account(x, y)
                results.append({
                    "index": i + 1,
                    "email": result.get("email", ""),
                    "success": result["success"],
                    "message": result["message"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # 间隔等待（除了最后一个）
                if i < count - 1 and self.is_running:
                    self.log_and_callback(f"等待 {interval} 秒后继续...")
                    time.sleep(interval)
                    
            self.log_and_callback("批量注册完成")
            return results
            
        except Exception as e:
            self.log_and_callback(f"批量注册过程中出错: {str(e)}", "error")
            return results
            
        finally:
            self.is_running = False
            
    def stop_registration(self):
        """停止注册"""
        self.is_running = False
        self.log_and_callback("正在停止注册...")
        
    def get_proxy_statistics(self):
        """获取代理统计信息"""
        return self.proxy_manager.get_proxy_statistics()
