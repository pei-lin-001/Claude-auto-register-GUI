"""
GUI服务模块

提供GUI界面与后端功能的连接服务。
"""

from .registration_service import RegistrationService
from .proxy_service import ProxyService
from .config_service import ConfigService
from .log_service import LogService

__all__ = [
    'RegistrationService',
    'ProxyService', 
    'ConfigService',
    'LogService'
] 