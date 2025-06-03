"""
智能自动化模块

提供更智能、更稳定的元素定位和交互功能
"""

import time
import random
import logging
from typing import List, Dict, Optional, Tuple, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementNotInteractableException,
    StaleElementReferenceException, WebDriverException
)


class SmartElementLocator:
    """智能元素定位器"""
    
    def __init__(self, driver: webdriver.Chrome, logger: Optional[logging.Logger] = None):
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        
    def find_element_smart(self, selectors: List[Dict], timeout: int = 30, 
                          description: str = "元素") -> Optional[webdriver.remote.webelement.WebElement]:
        """
        智能元素查找，支持多种选择器策略
        
        Args:
            selectors: 选择器列表，每个包含 {'by': By.XPATH, 'value': '...', 'priority': 1}
            timeout: 超时时间
            description: 元素描述
            
        Returns:
            找到的元素或None
        """
        # 按优先级排序
        selectors = sorted(selectors, key=lambda x: x.get('priority', 999))
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            for selector in selectors:
                try:
                    by = selector['by']
                    value = selector['value']
                    
                    # 尝试查找元素
                    element = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((by, value))
                    )
                    
                    # 验证元素是否可见和可交互
                    if self._is_element_interactive(element):
                        self.logger.info(f"成功找到{description}: {selector.get('name', value)}")
                        return element
                        
                except (TimeoutException, NoSuchElementException):
                    continue
                except Exception as e:
                    self.logger.debug(f"查找{description}时出错: {str(e)}")
                    continue
                    
            # 短暂等待后重试
            time.sleep(0.5)
            
        self.logger.error(f"未能找到{description}，已尝试所有选择器")
        return None
        
    def _is_element_interactive(self, element) -> bool:
        """检查元素是否可交互"""
        try:
            return (element.is_displayed() and 
                   element.is_enabled() and 
                   element.size['height'] > 0 and 
                   element.size['width'] > 0)
        except StaleElementReferenceException:
            return False
            
    def wait_for_page_load(self, timeout: int = 30) -> bool:
        """等待页面加载完成"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            # 额外等待JavaScript执行
            time.sleep(1)
            return True
        except TimeoutException:
            self.logger.warning("页面加载超时")
            return False


class SmartInteractor:
    """智能交互器"""
    
    def __init__(self, driver: webdriver.Chrome, logger: Optional[logging.Logger] = None):
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        self.actions = ActionChains(driver)
        
    def smart_click(self, element, max_retries: int = 3, 
                   use_js: bool = False) -> bool:
        """
        智能点击，支持多种点击策略
        
        Args:
            element: 要点击的元素
            max_retries: 最大重试次数
            use_js: 是否使用JavaScript点击
            
        Returns:
            是否点击成功
        """
        for attempt in range(max_retries):
            try:
                # 滚动到元素可见位置
                self._scroll_to_element(element)
                
                # 等待元素可点击
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(element)
                )
                
                if use_js or attempt > 0:
                    # 使用JavaScript点击
                    self.driver.execute_script("arguments[0].click();", element)
                    self.logger.info("使用JavaScript点击成功")
                else:
                    # 使用Selenium点击
                    element.click()
                    self.logger.info("使用Selenium点击成功")
                    
                return True
                
            except ElementNotInteractableException:
                self.logger.warning(f"元素不可交互，尝试第{attempt + 1}次")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    use_js = True  # 下次尝试使用JS点击
                    
            except StaleElementReferenceException:
                self.logger.warning("元素引用过期，需要重新查找")
                return False
                
            except Exception as e:
                self.logger.error(f"点击失败: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    
        return False
        
    def smart_input(self, element, text: str, clear_first: bool = True,
                   simulate_typing: bool = True) -> bool:
        """
        智能输入文本
        
        Args:
            element: 输入元素
            text: 要输入的文本
            clear_first: 是否先清空
            simulate_typing: 是否模拟人工输入
            
        Returns:
            是否输入成功
        """
        try:
            # 滚动到元素
            self._scroll_to_element(element)
            
            # 点击聚焦
            element.click()
            
            if clear_first:
                element.clear()
                # 确保清空完成
                time.sleep(0.2)
                
            if simulate_typing:
                # 模拟人工输入
                for char in text:
                    element.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
            else:
                element.send_keys(text)
                
            # 验证输入
            if element.get_attribute('value') == text:
                self.logger.info(f"成功输入文本: {text}")
                return True
            else:
                self.logger.warning("输入验证失败，尝试重新输入")
                element.clear()
                element.send_keys(text)
                return element.get_attribute('value') == text
                
        except Exception as e:
            self.logger.error(f"输入文本失败: {str(e)}")
            return False
            
    def _scroll_to_element(self, element):
        """滚动到元素位置"""
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                element
            )
            time.sleep(0.5)
        except Exception as e:
            self.logger.debug(f"滚动到元素失败: {str(e)}")
            
    def human_like_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """人性化延迟"""
        delay = random.uniform(min_delay, max_delay)
        self.logger.debug(f"等待 {delay:.2f} 秒...")
        time.sleep(delay)


class ClaudeAutomationEngine:
    """Claude自动化引擎"""
    
    def __init__(self, driver: webdriver.Chrome, logger: Optional[logging.Logger] = None):
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        self.locator = SmartElementLocator(driver, logger)
        self.interactor = SmartInteractor(driver, logger)
        
        # 定义智能选择器配置
        self.selectors = self._load_smart_selectors()
        
    def _load_smart_selectors(self) -> Dict:
        """加载智能选择器配置"""
        try:
            import json
            import os

            # 尝试从配置文件加载
            config_path = "smart_selectors.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    selectors = {}

                    # 转换配置格式
                    for key, selector_config in config.get("selectors", {}).items():
                        selectors[key] = []
                        for strategy in selector_config.get("strategies", []):
                            by_map = {
                                "xpath": By.XPATH,
                                "css": By.CSS_SELECTOR,
                                "id": By.ID,
                                "class": By.CLASS_NAME,
                                "tag": By.TAG_NAME
                            }

                            selectors[key].append({
                                "by": by_map.get(strategy["by"], By.XPATH),
                                "value": strategy["value"],
                                "priority": strategy.get("priority", 999),
                                "name": strategy.get("name", strategy["value"]),
                                "timeout": strategy.get("timeout", 30)
                            })

                    self.logger.info("成功加载智能选择器配置文件")
                    return selectors

        except Exception as e:
            self.logger.warning(f"加载选择器配置文件失败: {str(e)}，使用默认配置")

        # 默认配置
        return {
            "email_input": [
                {
                    "by": By.XPATH,
                    "value": "//input[@type='email']",
                    "priority": 1,
                    "name": "邮箱输入框(type=email)",
                    "timeout": 15
                },
                {
                    "by": By.XPATH,
                    "value": "//input[contains(@placeholder, 'email') or contains(@placeholder, 'Email')]",
                    "priority": 2,
                    "name": "邮箱输入框(placeholder)",
                    "timeout": 10
                },
                {
                    "by": By.CSS_SELECTOR,
                    "value": "form input[type='email'], form input[placeholder*='email']",
                    "priority": 3,
                    "name": "邮箱输入框(CSS)",
                    "timeout": 10
                },
                {
                    "by": By.XPATH,
                    "value": "/html/body/div[2]/div/div[1]/main/div[1]/div/div[2]/div/div[1]/div/form/input",
                    "priority": 9,
                    "name": "邮箱输入框(绝对路径)",
                    "timeout": 5
                }
            ],
            "continue_button": [
                {
                    "by": By.XPATH,
                    "value": "//button[contains(text(), 'Continue') or contains(text(), '继续') or contains(text(), 'Next')]",
                    "priority": 1,
                    "name": "下一步按钮(文本)",
                    "timeout": 15
                },
                {
                    "by": By.XPATH,
                    "value": "//button[@type='submit']",
                    "priority": 2,
                    "name": "提交按钮",
                    "timeout": 10
                },
                {
                    "by": By.CSS_SELECTOR,
                    "value": "button[type='submit'], .btn-primary, .continue-btn",
                    "priority": 3,
                    "name": "CSS继续按钮",
                    "timeout": 10
                },
                {
                    "by": By.XPATH,
                    "value": "/html/body/div[2]/div/div[1]/main/div[1]/div/div[2]/div/div[1]/div/form/button",
                    "priority": 9,
                    "name": "下一步按钮(绝对路径)",
                    "timeout": 5
                }
            ],
            "age_verification": [
                {
                    "by": By.XPATH,
                    "value": "//div[contains(text(), 'year') or contains(text(), '年')]",
                    "priority": 1,
                    "name": "年龄验证页面",
                    "timeout": 20
                },
                {
                    "by": By.XPATH,
                    "value": "/html/body/main/div/div/form/div/label[2]/div/div",
                    "priority": 9,
                    "name": "年龄验证页面(绝对路径)",
                    "timeout": 5
                }
            ],
            "phone_checkbox": [
                {
                    "by": By.XPATH,
                    "value": "//input[@type='checkbox' and contains(@name, 'phone')]",
                    "priority": 1,
                    "name": "手机版复选框",
                    "timeout": 15
                },
                {
                    "by": By.XPATH,
                    "value": "/html/body/main/div/div/form/div[1]/div/div/input",
                    "priority": 9,
                    "name": "手机版复选框(绝对路径)",
                    "timeout": 5
                }
            ]
        }
        
    def fill_email_form(self, email: str) -> bool:
        """填写邮箱表单"""
        try:
            self.logger.info("开始填写邮箱表单...")
            
            # 等待页面加载
            if not self.locator.wait_for_page_load():
                return False
                
            # 查找邮箱输入框
            email_input = self.locator.find_element_smart(
                self.selectors["email_input"], 
                timeout=30, 
                description="邮箱输入框"
            )
            
            if not email_input:
                return False
                
            # 输入邮箱
            if not self.interactor.smart_input(email_input, email):
                return False
                
            # 人性化延迟
            self.interactor.human_like_delay(2, 5)
            
            # 查找并点击下一步按钮
            next_button = self.locator.find_element_smart(
                self.selectors["continue_button"],
                timeout=15,
                description="下一步按钮"
            )
            
            if not next_button:
                return False
                
            if not self.interactor.smart_click(next_button):
                return False
                
            self.logger.info("邮箱表单填写完成")
            return True
            
        except Exception as e:
            self.logger.error(f"填写邮箱表单失败: {str(e)}")
            return False
            
    def handle_verification_page(self) -> bool:
        """处理验证页面"""
        try:
            self.logger.info("处理验证页面...")
            
            # 等待验证页面加载
            verification_element = self.locator.find_element_smart(
                self.selectors["age_verification"],
                timeout=30,
                description="验证页面"
            )
            
            if not verification_element:
                return False
                
            # 检查是否有手机版复选框
            phone_checkbox = self.locator.find_element_smart(
                self.selectors["phone_checkbox"],
                timeout=10,
                description="手机版复选框"
            )
            
            if phone_checkbox:
                self.logger.info("发现手机版复选框，进行点击")
                self.interactor.smart_click(phone_checkbox)
                return True
            else:
                self.logger.info("未发现手机版复选框，使用桌面版")
                return True
                
        except Exception as e:
            self.logger.error(f"处理验证页面失败: {str(e)}")
            return False
            
    def wait_for_page_change(self, current_url: str, timeout: int = 30) -> bool:
        """等待页面跳转"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.driver.current_url != current_url:
                    self.logger.info(f"页面已跳转: {self.driver.current_url}")
                    return True
                time.sleep(0.5)
            return False
        except Exception as e:
            self.logger.error(f"等待页面跳转失败: {str(e)}")
            return False
            
    def get_page_info(self) -> Dict:
        """获取页面信息"""
        try:
            return {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "ready_state": self.driver.execute_script("return document.readyState"),
                "page_height": self.driver.execute_script("return document.body.scrollHeight"),
                "viewport_height": self.driver.execute_script("return window.innerHeight")
            }
        except Exception as e:
            self.logger.error(f"获取页面信息失败: {str(e)}")
            return {}
            
    def take_screenshot(self, filename: str = None) -> str:
        """截图保存"""
        try:
            if not filename:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                
            screenshot_path = f"logs/{filename}"
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"截图已保存: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            self.logger.error(f"截图失败: {str(e)}")
            return ""
