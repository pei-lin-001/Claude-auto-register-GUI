"""
注册服务模块

提供注册相关的服务功能，连接GUI与核心注册逻辑。
"""

import threading
import queue
import time
import logging
import random
import string
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mail import QQMail
from cloudflare import mailCloud
from chrome_bot import chromeBot
from chrome_bot.robust_automation import create_robust_automation
from utils.config import config
from utils.cookie_utils import CookieManager
from utils.proxy_manager import ProxyManager
from selenium.webdriver.common.by import By
import json


class RegistrationService:
    """注册服务类"""
    
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.task_thread = None
        self.progress_callback = None
        self.log_callback = None
        self.status_callback = None
        
        # 初始化组件
        self.mail_cloud = mailCloud()
        self.qq_mail = QQMail()
        self.proxy_manager = ProxyManager(max_usage_count=3)
        
        # 配置日志
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # 统计信息
        self.stats = {
            'total': 0,
            'current': 0,
            'success': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }
        
    def setup_logging(self):
        """设置日志"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def set_callbacks(self, progress_callback=None, log_callback=None, status_callback=None):
        """设置回调函数"""
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.status_callback = status_callback
    
    def _log(self, message, level="INFO"):
        """记录日志"""
        if self.log_callback:
            self.log_callback(message, level)
        
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def _update_progress(self, current, total, message=""):
        """更新进度"""
        if self.progress_callback:
            progress = (current / total * 100) if total > 0 else 0
            self.progress_callback(progress, current, total, message)
    
    def _update_status(self, status):
        """更新状态"""
        if self.status_callback:
            self.status_callback(status)
    
    def generate_random_email_prefix(self, length=8):
        """生成随机邮箱前缀"""
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))
    
    def create_email(self):
        """创建邮箱"""
        try:
            random_string = self.generate_random_email_prefix()
            mail_result = self.mail_cloud.createEmailRules(random_string)
            
            if mail_result.get("type") == "True":
                return mail_result.get("mail")
            else:
                self._log(f"邮箱创建失败: {mail_result}", "ERROR")
                return None
                
        except Exception as e:
            self._log(f"创建邮箱时发生错误: {str(e)}", "ERROR")
            return None
    
    def get_dom_list(self):
        """获取DOM元素列表"""
        try:
            with open("domList.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            self._log(f"读取DOM配置文件失败: {str(e)}", "ERROR")
            return {}
    
    def init_chrome_browser(self, position=(0, 0), incognito=True):
        """初始化Chrome浏览器"""
        try:
            bot = chromeBot()
            proxy_details = self.proxy_manager.get_available_proxy()
            
            if proxy_details is None:
                self._log("无可用代理，使用直连", "WARNING")
            else:
                self._log(f"使用代理: {proxy_details['proxy_string']}", "INFO")
            
            # 使用无痕模式启动浏览器
            chrome = bot.createWebView(proxy_details=proxy_details, incognito=incognito)
            
            if chrome is None:
                self._log("浏览器初始化失败", "ERROR")
                return None
            
            chrome.get("https://claude.ai")
            chrome.set_window_position(position[0], position[1])
            
            # 记录代理使用
            if proxy_details:
                self.proxy_manager.record_proxy_usage(
                    proxy_details["proxy_string"], 
                    proxy_details["file_path"]
                )
            
            mode_text = "无痕模式" if incognito else "普通模式"
            self._log(f"浏览器初始化成功（{mode_text}）", "INFO")
            
            return chrome
            
        except Exception as e:
            self._log(f"初始化浏览器失败: {str(e)}", "ERROR")
            return None
    
    def register_single_account(self, position=(0, 0)):
        """注册单个账号 - 使用健壮的自动化方法"""
        result = {
            'success': False,
            'email': None,
            'message': '',
            'start_time': time.time(),
            'end_time': None
        }
        
        chrome = None
        automation = None
        
        try:
            # 步骤1：创建邮箱
            self._log("开始创建邮箱...", "INFO")
            email = self.create_email()
            if not email:
                result['message'] = "邮箱创建失败"
                return result
            
            result['email'] = email
            self._log(f"邮箱创建成功: {email}", "INFO")
            
            # 步骤2：初始化浏览器
            self._log("初始化浏览器...", "INFO")
            chrome = self.init_chrome_browser(position)
            if not chrome:
                result['message'] = "浏览器初始化失败"
                return result
            
            # 步骤3：创建健壮自动化实例
            automation = create_robust_automation(chrome, self.logger)
            
            # 步骤4：获取DOM配置
            dom_list = self.get_dom_list()
            if not dom_list:
                result['message'] = "DOM配置加载失败"
                return result
            
            self._log("开始注册流程...", "INFO")
            
            # 步骤5：等待并填写邮箱 - 使用健壮方法
            self._log("查找邮箱输入框...", "INFO")
            mail_input_selectors = [
                dom_list.get("mailInput", ""),
                "//input[@type='email']",
                "//input[contains(@placeholder, 'email')]",
                "//input[contains(@name, 'email')]",
                "//input[contains(@id, 'email')]"
            ]
            
            mail_input = automation.find_element_robust(
                mail_input_selectors, 
                timeout=30, 
                description="邮箱输入框"
            )
            
            if not mail_input:
                result['message'] = "邮箱输入框未找到"
                return result
            
            # 输入邮箱
            mail_input.clear()
            mail_input.send_keys(email)
            self._log(f"已输入邮箱: {email}", "INFO")
            
            # 随机等待
            wait_time = random.randint(2, 5)
            self._log(f"等待 {wait_time} 秒...", "INFO")
            time.sleep(wait_time)
            
            # 步骤6：点击下一步 - 使用健壮方法
            self._log("查找并点击下一步按钮...", "INFO")
            next_button_selectors = [
                dom_list.get("nextMailButton", ""),
                "//button[contains(text(), 'Continue')]",
                "//button[contains(text(), 'Next')]",
                "//button[@type='submit']",
                "//form//button[last()]"
            ]
            
            if not automation.find_and_click_robust(
                next_button_selectors,
                timeout=30,
                description="下一步按钮"
            ):
                result['message'] = "下一步按钮点击失败"
                return result
            
            self._log("已点击下一步按钮", "INFO")
            
            # 步骤7：获取验证邮件
            time.sleep(5)
            self._log("获取邮箱验证链接...", "INFO")
            
            jump_url = self.qq_mail.getUserTo(email, config["mail"]["mail_password"])
            if jump_url.get("type") == "error":
                result['message'] = "获取验证邮件失败"
                return result
            
            verification_link = jump_url.get("link")
            if not verification_link:
                result['message'] = "验证链接为空"
                return result
            
            self._log(f"获取到验证链接: {verification_link}", "INFO")
            
            # 步骤8：访问验证链接
            chrome.get(verification_link)
            
            # 等待页面加载
            automation.wait_for_page_load()
            
            # 步骤9：查找并点击年龄验证元素 - 使用专门的健壮方法
            self._log("查找年龄验证元素...", "INFO")
            age_verification = automation.find_age_verification_element(timeout=30)
            
            if not age_verification:
                result['message'] = "年龄验证元素未找到"
                return result
            
            # 点击年龄验证
            if not automation.click_element_robust(age_verification, "年龄验证元素"):
                result['message'] = "年龄验证元素点击失败"
                return result
            
            self._log("已点击年龄验证元素", "INFO")
            
            # 步骤10：等待页面跳转并保存cookies
            time.sleep(3)
            automation.wait_for_page_load()
            
            # 保存cookies
            cookies = CookieManager.get_all_cookies(chrome)
            cookie_count = CookieManager.save_cookies(cookies)
            self._log(f"成功保存 {cookie_count} 个cookie", "INFO")
            
            # 检查是否是手机版 - 使用健壮方法
            phone_selectors = [
                dom_list.get("isPheon", ""),
                "//input[contains(@name, 'phone')]",
                "//input[contains(@id, 'phone')]",
                "//input[@type='checkbox'][contains(@class, 'phone')]"
            ]
            
            is_phone = automation.find_element_robust(
                phone_selectors,
                timeout=10,
                description="手机版标识"
            )
            
            if is_phone:
                automation.click_element_robust(is_phone, "手机版标识")
                CookieManager.save_session_key(cookies, is_phone=True, email=email)
                self._log("检测到手机版，已保存到 sessionKey-phone.txt", "INFO")
            else:
                CookieManager.save_session_key(cookies, is_phone=False, email=email)
                self._log("已保存到 sessionKey.txt", "INFO")
            
            result['success'] = True
            result['message'] = "注册成功"
            self._log(f"账号 {email} 注册成功！", "INFO")
            
        except Exception as e:
            result['message'] = f"注册过程中发生错误: {str(e)}"
            self._log(result['message'], "ERROR")
            
        finally:
            # 清理浏览器
            try:
                if chrome:
                    chrome.quit()
            except:
                pass
            
            result['end_time'] = time.time()
            
        return result
    
    def start_single_registration(self):
        """启动单个注册"""
        if self.is_running:
            self._log("注册任务已在运行中", "WARNING")
            return False
        
        def worker():
            self.is_running = True
            self._update_status("注册中...")
            result = {'success': False}  # 初始化result变量
            
            try:
                result = self.register_single_account()
                
                if result['success']:
                    self.stats['success'] += 1
                    self._update_status("注册成功")
                else:
                    self.stats['failed'] += 1
                    self._update_status("注册失败")
                    
            except Exception as e:
                self._log(f"注册任务异常: {str(e)}", "ERROR")
                self._update_status("注册异常")
                
            finally:
                self.is_running = False
                # 通知GUI注册任务已完成
                self._update_status("就绪" if result.get('success') else "注册失败")
        
        self.task_thread = threading.Thread(target=worker)
        self.task_thread.daemon = True
        self.task_thread.start()
        
        return True
    
    def start_batch_registration(self, account_count, concurrent=3, interval=5):
        """启动批量注册"""
        if self.is_running:
            self._log("注册任务已在运行中", "WARNING")
            return False
        
        def batch_worker():
            self.is_running = True
            self.is_paused = False
            self.stats = {
                'total': account_count,
                'current': 0,
                'success': 0,
                'failed': 0,
                'start_time': time.time(),
                'end_time': None
            }
            
            self._update_status("批量注册中...")
            self._log(f"开始批量注册 {account_count} 个账号", "INFO")
            
            try:
                # 使用线程池进行并发注册
                import concurrent.futures
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent) as executor:
                    futures = []
                    
                    for i in range(account_count):
                        if not self.is_running:
                            break
                            
                        # 暂停检查
                        while self.is_paused and self.is_running:
                            time.sleep(0.5)
                        
                        if not self.is_running:
                            break
                        
                        # 计算窗口位置（避免重叠）
                        position = (i % 3 * 100, (i // 3) % 3 * 100)
                        
                        future = executor.submit(self.register_single_account, position)
                        futures.append(future)
                        
                        # 间隔等待
                        if i < account_count - 1:
                            time.sleep(interval)
                    
                    # 等待所有任务完成
                    for i, future in enumerate(concurrent.futures.as_completed(futures)):
                        if not self.is_running:
                            break
                            
                        result = future.result()
                        self.stats['current'] = i + 1
                        
                        if result['success']:
                            self.stats['success'] += 1
                        else:
                            self.stats['failed'] += 1
                        
                        # 更新进度
                        self._update_progress(
                            self.stats['current'], 
                            self.stats['total'],
                            f"已完成 {self.stats['current']}/{self.stats['total']}"
                        )
                        
            except Exception as e:
                self._log(f"批量注册异常: {str(e)}", "ERROR")
                
            finally:
                self.stats['end_time'] = time.time()
                self.is_running = False
                self.is_paused = False
                
                # 最终状态更新
                success_rate = (self.stats['success'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
                self._update_status(f"批量注册完成 - 成功率: {success_rate:.1f}%")
                self._log(f"批量注册完成: 成功 {self.stats['success']}, 失败 {self.stats['failed']}", "INFO")
        
        self.task_thread = threading.Thread(target=batch_worker)
        self.task_thread.daemon = True
        self.task_thread.start()
        
        return True
    
    def pause_registration(self):
        """暂停注册"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self._update_status("注册已暂停")
            self._log("注册任务已暂停", "INFO")
            return True
        return False
    
    def resume_registration(self):
        """恢复注册"""
        if self.is_running and self.is_paused:
            self.is_paused = False
            self._update_status("注册已恢复")
            self._log("注册任务已恢复", "INFO")
            return True
        return False
    
    def stop_registration(self):
        """停止注册"""
        if self.is_running:
            self.is_running = False
            self.is_paused = False
            self._update_status("注册已停止")
            self._log("注册任务已停止", "INFO")
            return True
        return False
    
    def get_stats(self):
        """获取统计信息"""
        return self.stats.copy()
    
    def is_registration_running(self):
        """检查注册是否在运行"""
        return self.is_running
    
    def is_registration_paused(self):
        """检查注册是否暂停"""
        return self.is_paused 