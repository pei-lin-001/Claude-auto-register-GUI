#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Claude 自动注册工具 - 依赖安装脚本

自动检查和安装项目所需的所有依赖包。
"""

import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并显示进度"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True, encoding='utf-8')
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    print(f"📌 当前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print("✅ Python版本检查通过")
    return True

def upgrade_pip():
    """升级pip到最新版本"""
    return run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "升级pip"
    )

def install_requirements():
    """安装requirements.txt中的依赖"""
    if not os.path.exists("requirements.txt"):
        print("❌ 未找到requirements.txt文件")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "安装项目依赖"
    )

def verify_installation():
    """验证关键依赖是否安装成功"""
    print("🔍 验证依赖安装...")
    
    critical_packages = [
        "selenium",
        "undetected_chromedriver", 
        "requests",
        "beautifulsoup4",
        "tkinter"  # 内置模块
    ]
    
    failed_packages = []
    
    for package in critical_packages:
        try:
            if package == "tkinter":
                import tkinter
            elif package == "undetected_chromedriver":
                import undetected_chromedriver
            elif package == "beautifulsoup4":
                import bs4
            else:
                __import__(package)
            print(f"✅ {package} 验证通过")
        except ImportError:
            print(f"❌ {package} 验证失败")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"❌ 以下包安装失败: {', '.join(failed_packages)}")
        return False
    
    print("✅ 所有关键依赖验证通过")
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Claude 自动注册工具 - 依赖安装脚本")
    print("=" * 60)
    
    # 步骤1: 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    print()
    
    # 步骤2: 升级pip
    if not upgrade_pip():
        print("⚠️  pip升级失败，但继续安装...")
    
    print()
    
    # 步骤3: 安装依赖
    if not install_requirements():
        print("❌ 依赖安装失败")
        sys.exit(1)
    
    print()
    
    # 步骤4: 验证安装
    if not verify_installation():
        print("❌ 依赖验证失败，请检查安装")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("🎉 所有依赖安装完成！")
    print("💡 现在可以运行 'python gui_app.py' 启动GUI界面")
    print("=" * 60)

if __name__ == "__main__":
    main() 