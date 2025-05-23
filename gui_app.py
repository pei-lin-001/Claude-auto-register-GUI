#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Claude 自动注册工具 GUI 应用程序启动文件

启动图形用户界面版本的Claude自动注册工具。
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查依赖项"""
    missing_deps = []
    
    try:
        import selenium
    except ImportError:
        missing_deps.append("selenium")
    
    try:
        import undetected_chromedriver
    except ImportError:
        missing_deps.append("undetected-chromedriver")
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    try:
        import bs4
    except ImportError:
        missing_deps.append("beautifulsoup4")
    
    if missing_deps:
        error_msg = f"缺少以下依赖项：\n{', '.join(missing_deps)}\n\n请运行以下命令安装：\npip install {' '.join(missing_deps)}"
        messagebox.showerror("依赖项缺失", error_msg)
        return False
    
    return True

def main():
    """主函数"""
    print("正在启动 Claude 自动注册工具 GUI...")
    
    # 检查依赖项
    if not check_dependencies():
        return 1
    
    try:
        # 导入GUI模块
        from gui import MainApplication
        
        # 创建并运行应用程序
        app = MainApplication()
        print("GUI 界面已启动")
        app.run()
        
    except ImportError as e:
        error_msg = f"导入GUI模块失败：{str(e)}\n\n请确保所有文件都在正确的位置。"
        print(error_msg)
        messagebox.showerror("启动失败", error_msg)
        return 1
    
    except Exception as e:
        error_msg = f"应用程序启动失败：{str(e)}"
        print(error_msg)
        messagebox.showerror("启动失败", error_msg)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 