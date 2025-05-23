"""
配置服务模块

提供配置管理相关的服务功能。
"""

import sys
import os
import json
import configparser
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from utils.config import config
except ImportError:
    config = {}


class ConfigService:
    """配置服务类"""
    
    def __init__(self):
        self.config_file = "config.json"
        self.env_file = ".env"
        self.status_callback = None
        self.default_config = {
            "mail": {
                "imap_server": "imap.qq.com",
                "imap_port": 993,
                "mail_address": "",
                "mail_password": "",
                "use_ssl": True
            },
            "cloudflare": {
                "api_key": "",
                "zone_id": "",
                "domain": "",
                "enabled": False
            },
            "browser": {
                "headless": False,
                "window_size": "1920,1080",
                "user_agent": "",
                "disable_images": True,
                "disable_javascript": False
            },
            "registration": {
                "max_concurrent": 3,
                "interval_seconds": 5,
                "max_retries": 3,
                "timeout_seconds": 30
            },
            "proxy": {
                "enabled": True,
                "file_path": "Proxy.txt",
                "max_usage": 3,
                "test_timeout": 10
            }
        }
        
    def set_callbacks(self, status_callback=None):
        """设置回调函数"""
        self.status_callback = status_callback
        
    def _update_status(self, message):
        """更新状态"""
        if self.status_callback:
            self.status_callback(message)
    
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # 合并默认配置
                merged_config = self._merge_config(self.default_config, loaded_config)
                self._update_status("配置加载成功")
                return merged_config
            else:
                self._update_status("使用默认配置")
                return self.default_config.copy()
                
        except Exception as e:
            self._update_status(f"配置加载失败: {str(e)}")
            return self.default_config.copy()
    
    def save_config(self, config_data):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            self._update_status("配置保存成功")
            return True
            
        except Exception as e:
            self._update_status(f"配置保存失败: {str(e)}")
            return False
    
    def _merge_config(self, default, loaded):
        """合并配置，保留默认值"""
        merged = default.copy()
        
        for key, value in loaded.items():
            if key in merged:
                if isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key] = self._merge_config(merged[key], value)
                else:
                    merged[key] = value
            else:
                merged[key] = value
                
        return merged
    
    def test_email_config(self, config_data):
        """测试邮箱配置"""
        try:
            import imaplib
            import ssl
            
            mail_config = config_data.get('mail', {})
            server = mail_config.get('imap_server')
            port = mail_config.get('imap_port', 993)
            email = mail_config.get('mail_address')
            password = mail_config.get('mail_password')
            use_ssl = mail_config.get('use_ssl', True)
            
            if not all([server, email, password]):
                return False, "邮箱配置信息不完整"
            
            # 尝试连接IMAP服务器
            if use_ssl:
                mail = imaplib.IMAP4_SSL(server, port)
            else:
                mail = imaplib.IMAP4(server, port)
            
            # 尝试登录
            mail.login(email, password)
            mail.logout()
            
            return True, "邮箱配置测试成功"
            
        except Exception as e:
            return False, f"邮箱配置测试失败: {str(e)}"
    
    def test_cloudflare_config(self, config_data):
        """测试Cloudflare配置"""
        try:
            import requests
            
            cf_config = config_data.get('cloudflare', {})
            api_key = cf_config.get('api_key')
            zone_id = cf_config.get('zone_id')
            
            if not all([api_key, zone_id]):
                return False, "Cloudflare配置信息不完整"
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # 测试API连接
            response = requests.get(
                f'https://api.cloudflare.com/client/v4/zones/{zone_id}',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "Cloudflare配置测试成功"
            else:
                return False, f"Cloudflare API响应异常: {response.status_code}"
                
        except Exception as e:
            return False, f"Cloudflare配置测试失败: {str(e)}"
    
    def export_config(self, file_path):
        """导出配置"""
        try:
            current_config = self.load_config()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(current_config, f, indent=4, ensure_ascii=False)
            
            return True, "配置导出成功"
            
        except Exception as e:
            return False, f"配置导出失败: {str(e)}"
    
    def import_config(self, file_path):
        """导入配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # 验证配置格式
            if self._validate_config(imported_config):
                if self.save_config(imported_config):
                    return True, "配置导入成功"
                else:
                    return False, "配置导入失败：保存错误"
            else:
                return False, "配置文件格式不正确"
                
        except Exception as e:
            return False, f"配置导入失败: {str(e)}"
    
    def _validate_config(self, config_data):
        """验证配置格式"""
        try:
            # 检查必需的顶级键
            required_keys = ['mail', 'browser', 'registration']
            
            for key in required_keys:
                if key not in config_data:
                    return False
            
            # 检查邮箱配置
            mail_config = config_data.get('mail', {})
            if not isinstance(mail_config, dict):
                return False
            
            return True
            
        except:
            return False
    
    def reset_to_default(self):
        """重置为默认配置"""
        try:
            if self.save_config(self.default_config):
                self._update_status("配置已重置为默认值")
                return True
            else:
                return False
                
        except Exception as e:
            self._update_status(f"重置配置失败: {str(e)}")
            return False
    
    def get_config_value(self, key_path, default=None):
        """获取配置值（支持点号分隔的路径）"""
        try:
            config_data = self.load_config()
            keys = key_path.split('.')
            value = config_data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
            
        except:
            return default
    
    def set_config_value(self, key_path, value):
        """设置配置值（支持点号分隔的路径）"""
        try:
            config_data = self.load_config()
            keys = key_path.split('.')
            current = config_data
            
            # 导航到父级
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # 设置值
            current[keys[-1]] = value
            
            return self.save_config(config_data)
            
        except Exception as e:
            self._update_status(f"设置配置值失败: {str(e)}")
            return False 