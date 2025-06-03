"""
现代化Claude自动注册工具主应用程序

采用简洁的卡片式设计，流程化的用户体验
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import threading
import time
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import config
from utils.proxy_manager import ProxyManager
from utils.cookie_utils import CookieManager


class ModernClaudeApp:
    """现代化Claude自动注册工具主应用程序"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.proxy_manager = ProxyManager(max_usage_count=3)
        self.is_running = False
        self.current_step = 1
        self.setup_window()
        self.setup_styles()
        self.create_interface()
        
    def setup_window(self):
        """设置主窗口"""
        self.root.title("Claude AI 自动注册工具 - 现代化版本")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 设置窗口背景色
        self.root.configure(bg='#f8fafc')
        
        # 居中窗口
        self.center_window()
        
        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_styles(self):
        """设置现代化样式"""
        self.colors = {
            'primary': '#3b82f6',
            'primary_hover': '#2563eb',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'bg_primary': '#ffffff',
            'bg_secondary': '#f8fafc',
            'bg_card': '#ffffff',
            'text_primary': '#1f2937',
            'text_secondary': '#6b7280',
            'text_muted': '#9ca3af',
            'border': '#e5e7eb',
            'border_focus': '#3b82f6'
        }
        
        self.fonts = {
            'title': ('SF Pro Display', 24, 'bold'),
            'heading': ('SF Pro Display', 18, 'bold'),
            'subheading': ('SF Pro Display', 14, 'bold'),
            'body': ('SF Pro Text', 12),
            'caption': ('SF Pro Text', 10),
            'button': ('SF Pro Text', 12, 'bold')
        }
        
    def create_interface(self):
        """创建主界面"""
        # 主容器
        main_container = tk.Frame(self.root, bg=self.colors['bg_secondary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 顶部标题区域
        self.create_header(main_container)
        
        # 主内容区域
        content_frame = tk.Frame(main_container, bg=self.colors['bg_secondary'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # 左侧步骤导航
        self.create_step_navigation(content_frame)
        
        # 右侧内容区域
        self.create_content_area(content_frame)
        
        # 底部状态栏
        self.create_status_bar(main_container)
        
    def create_header(self, parent):
        """创建顶部标题区域"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat', bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 添加圆角效果（通过padding模拟）
        header_content = tk.Frame(header_frame, bg=self.colors['bg_card'])
        header_content.pack(fill=tk.X, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(
            header_content,
            text="🤖 Claude AI 自动注册工具",
            font=self.fonts['title'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        )
        title_label.pack(side=tk.LEFT)
        
        # 版本信息
        version_label = tk.Label(
            header_content,
            text="v2.0 现代化版本",
            font=self.fonts['caption'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_muted']
        )
        version_label.pack(side=tk.RIGHT, anchor='e')
        
    def create_step_navigation(self, parent):
        """创建左侧步骤导航"""
        nav_frame = tk.Frame(parent, bg=self.colors['bg_card'], width=250)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        nav_frame.pack_propagate(False)
        
        # 导航标题
        nav_title = tk.Label(
            nav_frame,
            text="📋 注册流程",
            font=self.fonts['heading'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        )
        nav_title.pack(pady=(20, 30))
        
        # 步骤列表
        self.steps = [
            ("1", "📧 配置邮箱", "设置接收验证码的邮箱"),
            ("2", "☁️ Cloudflare设置", "配置临时邮箱服务"),
            ("3", "🌐 代理配置", "添加和管理代理服务器"),
            ("4", "🚀 开始注册", "启动自动注册流程"),
            ("5", "📊 查看结果", "检查注册结果和日志")
        ]
        
        self.step_buttons = {}
        for step_num, step_title, step_desc in self.steps:
            self.create_step_item(nav_frame, step_num, step_title, step_desc)
            
    def create_step_item(self, parent, step_num, title, description):
        """创建单个步骤项"""
        step_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        step_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # 步骤按钮
        btn_frame = tk.Frame(step_frame, bg=self.colors['bg_card'])
        btn_frame.pack(fill=tk.X)
        
        # 步骤编号圆圈
        circle_frame = tk.Frame(btn_frame, bg=self.colors['border'], width=30, height=30)
        circle_frame.pack(side=tk.LEFT, pady=5)
        circle_frame.pack_propagate(False)
        
        step_label = tk.Label(
            circle_frame,
            text=step_num,
            font=self.fonts['button'],
            bg=self.colors['border'],
            fg=self.colors['text_primary']
        )
        step_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # 步骤内容
        content_frame = tk.Frame(btn_frame, bg=self.colors['bg_card'])
        content_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        title_label = tk.Label(
            content_frame,
            text=title,
            font=self.fonts['subheading'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            anchor='w'
        )
        title_label.pack(fill=tk.X)
        
        desc_label = tk.Label(
            content_frame,
            text=description,
            font=self.fonts['caption'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary'],
            anchor='w'
        )
        desc_label.pack(fill=tk.X)
        
        # 存储引用以便后续更新样式
        self.step_buttons[step_num] = {
            'circle': circle_frame,
            'circle_label': step_label,
            'frame': step_frame
        }
        
        # 绑定点击事件
        for widget in [step_frame, btn_frame, circle_frame, step_label, content_frame, title_label, desc_label]:
            widget.bind("<Button-1>", lambda e, s=step_num: self.switch_step(s))
            widget.bind("<Enter>", lambda e, s=step_num: self.on_step_hover(s, True))
            widget.bind("<Leave>", lambda e, s=step_num: self.on_step_hover(s, False))
            
    def create_content_area(self, parent):
        """创建右侧内容区域"""
        self.content_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 初始化所有步骤页面
        self.pages = {}
        self.init_all_pages()
        
        # 显示第一步
        self.switch_step("1")
        
    def create_status_bar(self, parent):
        """创建底部状态栏"""
        status_frame = tk.Frame(parent, bg=self.colors['bg_card'], height=50)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        status_frame.pack_propagate(False)
        
        # 状态信息
        self.status_label = tk.Label(
            status_frame,
            text="🟢 就绪 - 请按步骤配置参数",
            font=self.fonts['body'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # 时间显示
        self.time_label = tk.Label(
            status_frame,
            text="",
            font=self.fonts['caption'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_muted']
        )
        self.time_label.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # 更新时间
        self.update_time()
        
    def init_all_pages(self):
        """初始化所有步骤页面"""
        from gui.modern_pages import (
            EmailConfigPage, CloudflareConfigPage, ProxyConfigPage,
            RegisterPage, ResultsPage
        )
        
        self.pages["1"] = EmailConfigPage(self.content_frame, self)
        self.pages["2"] = CloudflareConfigPage(self.content_frame, self)
        self.pages["3"] = ProxyConfigPage(self.content_frame, self)
        self.pages["4"] = RegisterPage(self.content_frame, self)
        self.pages["5"] = ResultsPage(self.content_frame, self)
        
    def switch_step(self, step_num):
        """切换到指定步骤"""
        # 隐藏当前页面
        for page in self.pages.values():
            page.pack_forget()
            
        # 显示新页面
        if step_num in self.pages:
            self.pages[step_num].pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
        # 更新步骤样式
        self.update_step_styles(step_num)
        self.current_step = int(step_num)
        
    def update_step_styles(self, active_step):
        """更新步骤样式"""
        for step_num, widgets in self.step_buttons.items():
            if step_num == active_step:
                # 激活状态
                widgets['circle'].config(bg=self.colors['primary'])
                widgets['circle_label'].config(bg=self.colors['primary'], fg='white')
            else:
                # 非激活状态
                widgets['circle'].config(bg=self.colors['border'])
                widgets['circle_label'].config(bg=self.colors['border'], fg=self.colors['text_primary'])
                
    def on_step_hover(self, step_num, is_enter):
        """步骤悬停效果"""
        if step_num != str(self.current_step):
            widgets = self.step_buttons[step_num]
            if is_enter:
                widgets['circle'].config(bg=self.colors['primary_hover'])
                widgets['circle_label'].config(bg=self.colors['primary_hover'], fg='white')
            else:
                widgets['circle'].config(bg=self.colors['border'])
                widgets['circle_label'].config(bg=self.colors['border'], fg=self.colors['text_primary'])
                
    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
        
    def update_status(self, message, status_type="info"):
        """更新状态信息"""
        icons = {
            "info": "🟢",
            "warning": "🟡", 
            "error": "🔴",
            "success": "✅",
            "running": "🔄"
        }
        
        icon = icons.get(status_type, "🟢")
        self.status_label.config(text=f"{icon} {message}")
        
    def on_closing(self):
        """窗口关闭事件"""
        if self.is_running:
            if messagebox.askyesno("确认", "注册任务正在运行，确定要退出吗？"):
                self.is_running = False
                self.root.destroy()
        else:
            self.root.destroy()
            
    def run(self):
        """运行应用程序"""
        self.root.mainloop()
