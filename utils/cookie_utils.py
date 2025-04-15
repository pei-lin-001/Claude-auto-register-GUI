from selenium import webdriver
import json

class CookiePartitionKey:
    def __init__(self, top_level_site=None, has_cross_site_ancestor=False):
        self.top_level_site = top_level_site
        self.has_cross_site_ancestor = has_cross_site_ancestor
    
    @classmethod
    def from_json(cls, json_input) -> 'CookiePartitionKey':
        """从JSON创建CookiePartitionKey对象"""
        if isinstance(json_input, str):
            return cls(
                top_level_site=json_input,
                has_cross_site_ancestor=False
            )
        elif isinstance(json_input, dict):
            return cls(
                top_level_site=str(json_input["topLevelSite"]),
                has_cross_site_ancestor=bool(json_input["hasCrossSiteAncestor"])
            )
        return None
    
    def to_dict(self):
        """将CookiePartitionKey对象转换为字典"""
        return {
            "topLevelSite": self.top_level_site,
            "hasCrossSiteAncestor": self.has_cross_site_ancestor
        }

class CookieManager:
    @staticmethod
    def get_all_cookies(driver):
        """获取所有cookie，包括httpOnly标记的cookie"""
        all_cookies = driver.execute_cdp_cmd('Network.getAllCookies', {})
        return all_cookies.get('cookies', [])
    
    @staticmethod
    def save_cookies(cookies, file_path='cookies.json'):
        """保存cookie到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=4)
        return len(cookies)
    
    @staticmethod
    def save_session_key(cookies, is_phone=False):
        """
        从cookies中提取sessionKey并保存
        
        Args:
            cookies: cookie列表
            is_phone: 是否为手机版本，决定保存的文件名
            
        Returns:
            bool: 保存是否成功
        """
        file_path = 'sessionKey-phone.txt' if is_phone else 'sessionKey.txt'
        for cookie in cookies:
            if cookie.get('name') == 'sessionKey':
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cookie.get('value', '') + '\n')
                return True
        return False
    
    @staticmethod
    def load_cookies(file_path='cookies.json'):
        """从文件加载cookie"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    @staticmethod
    def set_cookies(driver, cookies):
        """设置cookie到webdriver"""
        for cookie in cookies:
            # 处理分区键
            if 'partitionKey' in cookie:
                partition_key = CookiePartitionKey.from_json(cookie['partitionKey'])
                if partition_key:
                    cookie['partitionKey'] = partition_key.to_dict()
            
            # 使用CDP设置cookie
            driver.execute_cdp_cmd('Network.setCookie', cookie)
        return True 