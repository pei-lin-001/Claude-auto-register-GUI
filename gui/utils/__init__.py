"""
GUI工具模块

包含GUI应用程序使用的各种工具类和函数：
- theme_manager: 主题管理器
- gui_config: GUI配置管理器  
- validators: 输入验证工具
- system_tray: 系统托盘支持
- hotkey_manager: 快捷键管理器
"""

from .theme_manager import ThemeManager, theme_manager
from .gui_config import GUIConfigManager, gui_config
from .validators import Validators, ValidationResult, validate_proxy_list, validate_email_list
from .system_tray import SystemTray, system_tray
from .hotkey_manager import HotkeyManager, hotkey_manager, HotkeyConfigDialog

__all__ = [
    'ThemeManager',
    'theme_manager',
    'GUIConfigManager', 
    'gui_config',
    'Validators',
    'ValidationResult',
    'validate_proxy_list',
    'validate_email_list',
    'SystemTray',
    'system_tray',
    'HotkeyManager',
    'hotkey_manager',
    'HotkeyConfigDialog'
] 