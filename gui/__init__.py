"""
Claude 自动注册工具 GUI 模块 - 现代化版本

这个模块包含了重构后的现代化图形用户界面实现。
采用简洁的卡片式设计和流程化的用户体验。
"""

# 导入现代化GUI
from .modern_app import ModernClaudeApp

# 导入旧版GUI（保持兼容性）
try:
    from .legacy_main_window import MainApplication
except ImportError:
    # 如果旧版文件不存在，创建一个占位符
    class MainApplication:
        def __init__(self):
            raise ImportError("旧版GUI已被移除，请使用 ModernClaudeApp")

__version__ = "2.0.0"
__author__ = "Claude Auto Register Team"

# 导出主要类
__all__ = ["ModernClaudeApp", "MainApplication"]