#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Claude 自动注册工具 - 现代化GUI应用程序

一个简洁、现代化的Claude AI账号自动注册工具界面
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查必要依赖项"""
    missing_deps = []

    required_packages = [
        ("selenium", "selenium"),
        ("undetected_chromedriver", "undetected-chromedriver"),
        ("requests", "requests"),
        ("bs4", "beautifulsoup4")
    ]

    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
        except ImportError:
            missing_deps.append(package_name)

    if missing_deps:
        error_msg = (
            f"缺少以下依赖项：\n{', '.join(missing_deps)}\n\n"
            f"请运行以下命令安装：\n"
            f"pip install {' '.join(missing_deps)}"
        )
        messagebox.showerror("依赖项缺失", error_msg)
        return False

    return True

def main():
    """主函数"""
    print("🚀 启动 Claude 自动注册工具...")

    # 检查依赖项
    if not check_dependencies():
        return 1

    try:
        # 导入重构后的GUI模块
        from gui.modern_app import ModernClaudeApp

        # 创建并运行应用程序
        app = ModernClaudeApp()
        print("✅ GUI 界面已启动")
        app.run()

    except ImportError as e:
        error_msg = f"导入GUI模块失败：{str(e)}\n\n请确保所有文件都在正确的位置。"
        print(f"❌ {error_msg}")
        messagebox.showerror("启动失败", error_msg)
        return 1

    except Exception as e:
        error_msg = f"应用程序启动失败：{str(e)}"
        print(f"❌ {error_msg}")
        messagebox.showerror("启动失败", error_msg)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())