#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健壮的自动化点击模块

提供多策略、自适应的元素查找和点击功能，提高自动化的成功率和健壮性。
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains


class RobustAutomation:
    """健壮的自动化操作类"""
    
    def __init__(self, driver, logger=None):
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        self.wait_short = WebDriverWait(driver, 5)
        self.wait_medium = WebDriverWait(driver, 15)
        self.wait_long = WebDriverWait(driver, 30)
        
    def find_element_robust(self, selectors, timeout=15, description="元素"):
        """
        健壮的元素查找方法
        
        Args:
            selectors: 选择器列表，支持多种格式
            timeout: 超时时间
            description: 元素描述
            
        Returns:
            找到的元素或None
        """
        if isinstance(selectors, str):
            selectors = [selectors]
            
        self.logger.info(f"开始查找{description}，尝试{len(selectors)}种选择器...")
        
        for i, selector in enumerate(selectors):
            try:
                self.logger.debug(f"尝试选择器 {i+1}/{len(selectors)}: {selector}")
                
                # 根据选择器类型选择查找方法
                by_type, selector_value = self._parse_selector(selector)
                
                # 等待元素出现
                element = WebDriverWait(self.driver, timeout // len(selectors)).until(
                    EC.presence_of_element_located((by_type, selector_value))
                )
                
                if element and element.is_displayed():
                    self.logger.info(f"✅ 成功找到{description}，使用选择器: {selector}")
                    return element
                    
            except TimeoutException:
                self.logger.debug(f"选择器 {i+1} 超时: {selector}")
                continue
            except Exception as e:
                self.logger.debug(f"选择器 {i+1} 出错: {selector}, 错误: {str(e)}")
                continue
        
        self.logger.warning(f"❌ 未能找到{description}")
        return None
    
    def click_element_robust(self, element, description="元素", max_retries=3):
        """
        健壮的元素点击方法
        
        Args:
            element: 要点击的元素
            description: 元素描述
            max_retries: 最大重试次数
            
        Returns:
            是否点击成功
        """
        if not element:
            self.logger.error(f"❌ 无法点击{description}：元素为空")
            return False
            
        for attempt in range(max_retries):
            try:
                # 方法1：直接点击
                if self._try_direct_click(element, description):
                    return True
                    
                # 方法2：JavaScript点击
                if self._try_js_click(element, description):
                    return True
                    
                # 方法3：ActionChains点击
                if self._try_action_click(element, description):
                    return True
                    
                # 方法4：滚动到元素后点击
                if self._try_scroll_and_click(element, description):
                    return True
                    
                self.logger.warning(f"⚠️ 第{attempt + 1}次点击{description}失败，等待重试...")
                time.sleep(1)
                
            except Exception as e:
                self.logger.warning(f"⚠️ 点击{description}时发生异常: {str(e)}")
                
        self.logger.error(f"❌ 多次尝试后仍无法点击{description}")
        return False
    
    def find_and_click_robust(self, selectors, timeout=15, description="元素", max_retries=3):
        """
        健壮的查找并点击方法
        
        Args:
            selectors: 选择器列表
            timeout: 查找超时时间
            description: 元素描述
            max_retries: 点击重试次数
            
        Returns:
            是否成功
        """
        element = self.find_element_robust(selectors, timeout, description)
        if element:
            return self.click_element_robust(element, description, max_retries)
        return False
    
    def wait_for_page_load(self, timeout=30):
        """等待页面加载完成"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(1)  # 额外等待确保页面稳定
            return True
        except TimeoutException:
            self.logger.warning("页面加载超时")
            return False
    
    def find_age_verification_element(self, timeout=30):
        """
        专门用于查找年龄验证元素的方法
        支持多种可能的年龄验证元素格式
        """
        age_verification_selectors = [
            # ID选择器
            "//*[@id='age-verification']",
            "//input[@id='age-verification']",
            "//label[@for='age-verification']",
            
            # 类名选择器
            "//input[contains(@class, 'age')]",
            "//input[contains(@class, 'verification')]",
            "//label[contains(@class, 'age')]",
            
            # 文本内容选择器
            "//label[contains(text(), '18')]",
            "//span[contains(text(), '18')]",
            "//div[contains(text(), '18')]",
            "//label[contains(text(), 'age')]",
            "//span[contains(text(), 'age')]",
            "//label[contains(text(), 'verify')]",
            "//label[contains(text(), 'confirm')]",
            
            # 复选框选择器
            "//input[@type='checkbox']",
            "//input[@type='radio']",
            
            # 通用表单元素
            "//form//input[not(@type='email') and not(@type='password') and not(@type='text')]",
            "//form//label[position()>1]",
            
            # 原始选择器作为备用
            "/html/body/main/div/div/form/div/label[2]/div/div",
            "/html/body/main/div/div/form/div/label[1]/div/div",
            "/html/body/main/div/div/form/div/div/label/div/div",
        ]
        
        self.logger.info("开始查找年龄验证元素...")
        
        # 首先等待页面稳定
        self.wait_for_page_load()
        
        # 尝试查找元素
        element = self.find_element_robust(
            age_verification_selectors, 
            timeout, 
            "年龄验证元素"
        )
        
        if element:
            # 验证元素是否真的是年龄验证相关
            element_info = self._analyze_element(element)
            self.logger.info(f"找到年龄验证元素信息: {element_info}")
            
            # 如果元素看起来不像年龄验证，尝试查找父元素或相邻元素
            if not self._is_likely_age_verification(element):
                self.logger.info("当前元素可能不是年龄验证元素，尝试查找相关元素...")
                alternative_element = self._find_related_age_element(element)
                if alternative_element:
                    element = alternative_element
        
        return element
    
    def _parse_selector(self, selector):
        """解析选择器类型"""
        if selector.startswith("//") or selector.startswith("/"):
            return By.XPATH, selector
        elif selector.startswith("#"):
            return By.ID, selector[1:]
        elif selector.startswith("."):
            return By.CLASS_NAME, selector[1:]
        elif "[@id=" in selector or "[@class=" in selector or "//" in selector:
            return By.XPATH, selector
        else:
            # 默认作为CSS选择器
            return By.CSS_SELECTOR, selector
    
    def _try_direct_click(self, element, description):
        """尝试直接点击"""
        try:
            if element.is_enabled() and element.is_displayed():
                element.click()
                self.logger.info(f"✅ 直接点击{description}成功")
                return True
        except Exception as e:
            self.logger.debug(f"直接点击失败: {str(e)}")
        return False
    
    def _try_js_click(self, element, description):
        """尝试JavaScript点击"""
        try:
            self.driver.execute_script("arguments[0].click();", element)
            self.logger.info(f"✅ JavaScript点击{description}成功")
            return True
        except Exception as e:
            self.logger.debug(f"JavaScript点击失败: {str(e)}")
        return False
    
    def _try_action_click(self, element, description):
        """尝试ActionChains点击"""
        try:
            ActionChains(self.driver).move_to_element(element).click().perform()
            self.logger.info(f"✅ ActionChains点击{description}成功")
            return True
        except Exception as e:
            self.logger.debug(f"ActionChains点击失败: {str(e)}")
        return False
    
    def _try_scroll_and_click(self, element, description):
        """尝试滚动到元素后点击"""
        try:
            # 滚动到元素
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            
            # 再次尝试点击
            element.click()
            self.logger.info(f"✅ 滚动后点击{description}成功")
            return True
        except Exception as e:
            self.logger.debug(f"滚动后点击失败: {str(e)}")
        return False
    
    def _analyze_element(self, element):
        """分析元素信息"""
        try:
            return {
                'tag': element.tag_name,
                'id': element.get_attribute('id'),
                'class': element.get_attribute('class'),
                'text': element.text,
                'type': element.get_attribute('type'),
                'name': element.get_attribute('name'),
                'visible': element.is_displayed(),
                'enabled': element.is_enabled()
            }
        except:
            return {'error': 'Unable to analyze element'}
    
    def _is_likely_age_verification(self, element):
        """判断元素是否可能是年龄验证元素"""
        try:
            element_text = (element.text or '').lower()
            element_id = (element.get_attribute('id') or '').lower()
            element_class = (element.get_attribute('class') or '').lower()
            
            age_keywords = ['18', 'age', 'verify', 'confirm', 'adult', 'years']
            
            for keyword in age_keywords:
                if keyword in element_text or keyword in element_id or keyword in element_class:
                    return True
                    
            # 如果是复选框或单选框，也可能是年龄验证
            if element.get_attribute('type') in ['checkbox', 'radio']:
                return True
                
        except:
            pass
        
        return False
    
    def _find_related_age_element(self, element):
        """查找与当前元素相关的年龄验证元素"""
        try:
            # 查找父元素中的其他输入元素
            parent = element.find_element(By.XPATH, "..")
            inputs = parent.find_elements(By.XPATH, ".//input[@type='checkbox' or @type='radio']")
            
            for input_elem in inputs:
                if self._is_likely_age_verification(input_elem):
                    return input_elem
                    
            # 查找相邻的label元素
            labels = parent.find_elements(By.XPATH, ".//label")
            for label in labels:
                if self._is_likely_age_verification(label):
                    # 尝试找到label对应的input
                    for_attr = label.get_attribute('for')
                    if for_attr:
                        try:
                            input_elem = self.driver.find_element(By.ID, for_attr)
                            return input_elem
                        except:
                            pass
                    return label
                    
        except:
            pass
        
        return None


def create_robust_automation(driver, logger=None):
    """创建健壮自动化实例的工厂函数"""
    return RobustAutomation(driver, logger) 