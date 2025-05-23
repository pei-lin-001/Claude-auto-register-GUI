import re
import socket
import urllib.parse
from typing import Tuple, Optional, Union

class ValidationResult:
    """验证结果类"""
    
    def __init__(self, is_valid: bool, message: str = ""):
        self.is_valid = is_valid
        self.message = message
    
    def __bool__(self):
        return self.is_valid

class Validators:
    """输入验证工具类"""
    
    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        """验证邮箱地址"""
        if not email:
            return ValidationResult(False, "邮箱地址不能为空")
        
        # 基本格式验证
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return ValidationResult(False, "邮箱地址格式无效")
        
        # 长度验证
        if len(email) > 254:
            return ValidationResult(False, "邮箱地址过长")
        
        return ValidationResult(True, "邮箱地址有效")
    
    @staticmethod
    def validate_proxy(proxy: str) -> ValidationResult:
        """验证代理地址"""
        if not proxy:
            return ValidationResult(False, "代理地址不能为空")
        
        # 支持的格式：
        # ip:port
        # user:pass@ip:port
        # protocol://ip:port
        # protocol://user:pass@ip:port
        
        try:
            # 移除协议部分
            if "://" in proxy:
                protocol, rest = proxy.split("://", 1)
                if protocol not in ['http', 'https', 'socks4', 'socks5']:
                    return ValidationResult(False, f"不支持的代理协议: {protocol}")
            else:
                rest = proxy
            
            # 检查是否有认证信息
            if "@" in rest:
                auth_part, host_part = rest.rsplit("@", 1)
                if ":" not in auth_part:
                    return ValidationResult(False, "代理认证格式错误，应为 user:pass")
            else:
                host_part = rest
            
            # 验证主机和端口
            if ":" not in host_part:
                return ValidationResult(False, "代理地址缺少端口号")
            
            host, port_str = host_part.rsplit(":", 1)
            
            # 验证主机
            if not host:
                return ValidationResult(False, "代理主机地址不能为空")
            
            # 验证端口
            try:
                port = int(port_str)
                if not (1 <= port <= 65535):
                    return ValidationResult(False, "代理端口号必须在1-65535之间")
            except ValueError:
                return ValidationResult(False, "代理端口号必须是数字")
            
            # 验证IP地址格式（如果不是域名）
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', host):
                parts = host.split('.')
                for part in parts:
                    if not (0 <= int(part) <= 255):
                        return ValidationResult(False, "无效的IP地址")
            
            return ValidationResult(True, "代理地址有效")
            
        except Exception as e:
            return ValidationResult(False, f"代理地址格式错误: {str(e)}")
    
    @staticmethod
    def validate_url(url: str) -> ValidationResult:
        """验证URL地址"""
        if not url:
            return ValidationResult(False, "URL不能为空")
        
        try:
            result = urllib.parse.urlparse(url)
            
            # 检查scheme
            if not result.scheme:
                return ValidationResult(False, "URL缺少协议（如http://或https://）")
            
            if result.scheme not in ['http', 'https']:
                return ValidationResult(False, "只支持HTTP和HTTPS协议")
            
            # 检查netloc
            if not result.netloc:
                return ValidationResult(False, "URL缺少主机名")
            
            return ValidationResult(True, "URL有效")
            
        except Exception as e:
            return ValidationResult(False, f"URL格式错误: {str(e)}")
    
    @staticmethod
    def validate_port(port: Union[str, int]) -> ValidationResult:
        """验证端口号"""
        try:
            port_num = int(port) if isinstance(port, str) else port
            
            if not (1 <= port_num <= 65535):
                return ValidationResult(False, "端口号必须在1-65535之间")
            
            return ValidationResult(True, "端口号有效")
            
        except ValueError:
            return ValidationResult(False, "端口号必须是数字")
    
    @staticmethod
    def validate_ip_address(ip: str) -> ValidationResult:
        """验证IP地址"""
        if not ip:
            return ValidationResult(False, "IP地址不能为空")
        
        try:
            socket.inet_aton(ip)
            return ValidationResult(True, "IP地址有效")
        except socket.error:
            return ValidationResult(False, "IP地址格式无效")
    
    @staticmethod
    def validate_domain(domain: str) -> ValidationResult:
        """验证域名"""
        if not domain:
            return ValidationResult(False, "域名不能为空")
        
        # 域名长度限制
        if len(domain) > 253:
            return ValidationResult(False, "域名过长")
        
        # 域名格式验证
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        if not re.match(pattern, domain):
            return ValidationResult(False, "域名格式无效")
        
        return ValidationResult(True, "域名有效")
    
    @staticmethod
    def validate_positive_integer(value: Union[str, int]) -> ValidationResult:
        """验证正整数"""
        try:
            num = int(value) if isinstance(value, str) else value
            
            if num <= 0:
                return ValidationResult(False, "必须是正整数")
            
            return ValidationResult(True, "正整数有效")
            
        except ValueError:
            return ValidationResult(False, "必须是数字")
    
    @staticmethod
    def validate_integer_range(value: Union[str, int], min_val: int, max_val: int) -> ValidationResult:
        """验证整数范围"""
        try:
            num = int(value) if isinstance(value, str) else value
            
            if not (min_val <= num <= max_val):
                return ValidationResult(False, f"数值必须在{min_val}-{max_val}之间")
            
            return ValidationResult(True, "数值范围有效")
            
        except ValueError:
            return ValidationResult(False, "必须是数字")
    
    @staticmethod
    def validate_not_empty(value: str, field_name: str = "字段") -> ValidationResult:
        """验证非空"""
        if not value or not value.strip():
            return ValidationResult(False, f"{field_name}不能为空")
        
        return ValidationResult(True, f"{field_name}不为空")
    
    @staticmethod
    def validate_length(value: str, min_length: int = 0, max_length: int = None, field_name: str = "字段") -> ValidationResult:
        """验证字符串长度"""
        length = len(value) if value else 0
        
        if length < min_length:
            return ValidationResult(False, f"{field_name}长度不能少于{min_length}个字符")
        
        if max_length is not None and length > max_length:
            return ValidationResult(False, f"{field_name}长度不能超过{max_length}个字符")
        
        return ValidationResult(True, f"{field_name}长度有效")
    
    @staticmethod
    def validate_password_strength(password: str) -> ValidationResult:
        """验证密码强度"""
        if not password:
            return ValidationResult(False, "密码不能为空")
        
        if len(password) < 8:
            return ValidationResult(False, "密码长度至少8位")
        
        # 检查字符类型
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        score = sum([has_upper, has_lower, has_digit, has_special])
        
        if score < 2:
            return ValidationResult(False, "密码必须包含至少两种字符类型（大写字母、小写字母、数字、特殊字符）")
        
        if score < 3:
            return ValidationResult(True, "密码强度：中等")
        else:
            return ValidationResult(True, "密码强度：强")
    
    @staticmethod
    def validate_phone_number(phone: str) -> ValidationResult:
        """验证手机号码（中国大陆）"""
        if not phone:
            return ValidationResult(False, "手机号码不能为空")
        
        # 移除空格和连字符
        phone = re.sub(r'[\s-]', '', phone)
        
        # 中国大陆手机号码格式
        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, phone):
            return ValidationResult(False, "手机号码格式无效")
        
        return ValidationResult(True, "手机号码有效")
    
    @staticmethod
    def validate_file_path(file_path: str) -> ValidationResult:
        """验证文件路径"""
        if not file_path:
            return ValidationResult(False, "文件路径不能为空")
        
        # 检查非法字符
        illegal_chars = '<>:"|?*'
        for char in illegal_chars:
            if char in file_path:
                return ValidationResult(False, f"文件路径包含非法字符: {char}")
        
        # 检查路径长度
        if len(file_path) > 260:  # Windows路径长度限制
            return ValidationResult(False, "文件路径过长")
        
        return ValidationResult(True, "文件路径有效")
    
    @staticmethod
    def validate_hotkey(hotkey: str) -> ValidationResult:
        """验证快捷键格式"""
        if not hotkey:
            return ValidationResult(False, "快捷键不能为空")
        
        # 快捷键格式：Ctrl+Alt+Key 或 Ctrl+Key 等
        parts = [part.strip() for part in hotkey.split('+')]
        
        if len(parts) < 2:
            return ValidationResult(False, "快捷键至少需要一个修饰键和一个主键")
        
        valid_modifiers = {'Ctrl', 'Alt', 'Shift', 'Win', 'Cmd'}
        valid_keys = {
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
            'Space', 'Enter', 'Tab', 'Esc', 'Delete', 'Backspace', 'Insert', 'Home', 'End',
            'PageUp', 'PageDown', 'Up', 'Down', 'Left', 'Right',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'Comma', 'Period', 'Semicolon', 'Quote', 'Bracket', 'Backslash'
        }
        
        # 检查修饰键
        main_key = parts[-1]
        modifier_keys = parts[:-1]
        
        for modifier in modifier_keys:
            if modifier not in valid_modifiers:
                return ValidationResult(False, f"无效的修饰键: {modifier}")
        
        # 检查主键
        if main_key not in valid_keys:
            return ValidationResult(False, f"无效的主键: {main_key}")
        
        return ValidationResult(True, "快捷键格式有效")

# 便捷的验证函数
def validate_proxy_list(proxy_list: str) -> Tuple[bool, str, list]:
    """验证代理列表"""
    if not proxy_list.strip():
        return False, "代理列表不能为空", []
    
    lines = [line.strip() for line in proxy_list.split('\n') if line.strip()]
    valid_proxies = []
    errors = []
    
    for i, line in enumerate(lines, 1):
        result = Validators.validate_proxy(line)
        if result.is_valid:
            valid_proxies.append(line)
        else:
            errors.append(f"第{i}行: {result.message}")
    
    if errors:
        error_msg = "以下代理地址格式错误:\n" + "\n".join(errors[:5])
        if len(errors) > 5:
            error_msg += f"\n... 还有{len(errors) - 5}个错误"
        return False, error_msg, valid_proxies
    
    return True, f"成功验证{len(valid_proxies)}个代理地址", valid_proxies

def validate_email_list(email_list: str) -> Tuple[bool, str, list]:
    """验证邮箱列表"""
    if not email_list.strip():
        return False, "邮箱列表不能为空", []
    
    lines = [line.strip() for line in email_list.split('\n') if line.strip()]
    valid_emails = []
    errors = []
    
    for i, line in enumerate(lines, 1):
        result = Validators.validate_email(line)
        if result.is_valid:
            valid_emails.append(line)
        else:
            errors.append(f"第{i}行: {result.message}")
    
    if errors:
        error_msg = "以下邮箱地址格式错误:\n" + "\n".join(errors[:5])
        if len(errors) > 5:
            error_msg += f"\n... 还有{len(errors) - 5}个错误"
        return False, error_msg, valid_emails
    
    return True, f"成功验证{len(valid_emails)}个邮箱地址", valid_emails 