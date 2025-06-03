"""
GUI 组件模块

包含应用程序的各个界面组件。
"""

from .dashboard import DashboardFrame
from .proxy_manager import ProxyManagerFrame
from .config_panel import ConfigFrame
from .batch_register import BatchRegisterFrame
from .log_viewer import LogViewerFrame

__all__ = [
    'DashboardFrame',
    'ProxyManagerFrame', 
    'ConfigFrame',
    'BatchRegisterFrame',
    'LogViewerFrame'
] 