"""
仪表板组件

显示系统状态、快速操作和统计信息的主界面。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gui.resources.styles import COLORS, FONTS, SIZES, ICONS, STYLES
from utils.proxy_manager import ProxyManager


class DashboardFrame(tk.Frame):
    """仪表板框架类"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.parent = parent
        self.proxy_manager = ProxyManager()
        self.setup_ui()
        self.refresh()
        
    def setup_ui(self):
        """设置UI界面"""
        # 创建主滚动区域
        self.create_scrollable_area()
        
        # 创建顶部区域（快速启动、系统状态、最近活动）
        self.create_top_section()
        
        # 创建统计区域
        self.create_statistics_section()
        
        # 创建日志预览区域
        self.create_log_preview_section()
        
    def create_scrollable_area(self):
        """创建可滚动区域"""
        # 创建Canvas和滚动条
        self.canvas = tk.Canvas(self, bg=COLORS['bg_primary'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS['bg_primary'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # 布局
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        """鼠标滚轮事件"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def create_top_section(self):
        """创建顶部区域"""
        top_frame = tk.Frame(self.scrollable_frame, bg=COLORS['bg_primary'])
        top_frame.pack(fill=tk.X, padx=SIZES['padding_xl'], pady=SIZES['padding_xl'])
        
        # 快速启动区域
        self.create_quick_start_section(top_frame)
        
        # 系统状态区域
        self.create_system_status_section(top_frame)
        
        # 最近活动区域
        self.create_recent_activity_section(top_frame)
        
    def create_quick_start_section(self, parent):
        """创建快速启动区域"""
        frame = tk.LabelFrame(
            parent,
            text=f" {ICONS['start']} 快速启动",
            **STYLES['label_frame']
        )
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, SIZES['padding_medium']))
        
        # 按钮框架
        btn_frame = tk.Frame(frame, bg=COLORS['bg_primary'])
        btn_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_large'], pady=SIZES['padding_large'])
        
        # 开始注册按钮
        self.start_btn = tk.Button(
            btn_frame,
            text=f"{ICONS['start']} 开始注册",
            **STYLES['button_success'],
            command=self.start_registration
        )
        self.start_btn.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 快速配置按钮
        config_btn = tk.Button(
            btn_frame,
            text=f"{ICONS['config']} 快速配置",
            **STYLES['button_primary'],
            command=self.quick_config
        )
        config_btn.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 查看日志按钮
        log_btn = tk.Button(
            btn_frame,
            text=f"{ICONS['logs']} 查看日志",
            **STYLES['button_secondary'],
            command=self.view_logs
        )
        log_btn.pack(fill=tk.X)
        
    def create_system_status_section(self, parent):
        """创建系统状态区域"""
        frame = tk.LabelFrame(
            parent,
            text=f" {ICONS['info']} 系统状态",
            **STYLES['label_frame']
        )
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, SIZES['padding_medium']))
        
        # 状态信息框架
        status_frame = tk.Frame(frame, bg=COLORS['bg_primary'])
        status_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_large'], pady=SIZES['padding_large'])
        
        # 系统状态
        self.system_status_label = tk.Label(
            status_frame,
            text=f"{ICONS['success']} 系统正常",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['success'],
            anchor='w'
        )
        self.system_status_label.pack(fill=tk.X, pady=(0, SIZES['padding_small']))
        
        # 代理状态
        self.proxy_status_display = tk.Label(
            status_frame,
            text=f"{ICONS['proxy']} 代理: 检查中...",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        )
        self.proxy_status_display.pack(fill=tk.X, pady=(0, SIZES['padding_small']))
        
        # 邮箱状态
        self.email_status_label = tk.Label(
            status_frame,
            text=f"{ICONS['email']} 邮箱: 未测试",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary'],
            anchor='w'
        )
        self.email_status_label.pack(fill=tk.X, pady=(0, SIZES['padding_small']))
        
        # 网络状态
        self.network_status_label = tk.Label(
            status_frame,
            text=f"{ICONS['cloudflare']} 网络: 稳定",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['success'],
            anchor='w'
        )
        self.network_status_label.pack(fill=tk.X)
        
    def create_recent_activity_section(self, parent):
        """创建最近活动区域"""
        frame = tk.LabelFrame(
            parent,
            text=f" {ICONS['logs']} 最近活动",
            **STYLES['label_frame']
        )
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 活动信息框架
        activity_frame = tk.Frame(frame, bg=COLORS['bg_primary'])
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_large'], pady=SIZES['padding_large'])
        
        # 统计信息
        self.success_count_label = tk.Label(
            activity_frame,
            text=f"{ICONS['success']} 注册成功 0个",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['success'],
            anchor='w'
        )
        self.success_count_label.pack(fill=tk.X, pady=(0, SIZES['padding_small']))
        
        self.failed_count_label = tk.Label(
            activity_frame,
            text=f"{ICONS['error']} 失败 0个",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['error'],
            anchor='w'
        )
        self.failed_count_label.pack(fill=tk.X, pady=(0, SIZES['padding_small']))
        
        self.running_count_label = tk.Label(
            activity_frame,
            text=f"{ICONS['loading']} 进行中 0个",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['info'],
            anchor='w'
        )
        self.running_count_label.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 查看详情按钮
        detail_btn = tk.Button(
            activity_frame,
            text="查看详情",
            **STYLES['button_secondary'],
            command=self.view_details
        )
        detail_btn.pack(anchor='w')
        
    def create_statistics_section(self):
        """创建统计区域"""
        stats_frame = tk.LabelFrame(
            self.scrollable_frame,
            text=f" {ICONS['dashboard']} 注册统计",
            **STYLES['label_frame']
        )
        stats_frame.pack(fill=tk.X, padx=SIZES['padding_xl'], pady=(0, SIZES['padding_xl']))
        
        # 统计信息容器
        stats_container = tk.Frame(stats_frame, bg=COLORS['bg_primary'])
        stats_container.pack(fill=tk.X, padx=SIZES['padding_large'], pady=SIZES['padding_large'])
        
        # 今日统计
        today_frame = tk.Frame(stats_container, bg=COLORS['bg_secondary'], relief='flat', bd=0)
        today_frame.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        tk.Label(
            today_frame,
            text=f"{ICONS['dashboard']} 今日注册: 0 成功 / 0 失败",
            font=FONTS['body'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(fill=tk.X, padx=SIZES['padding_medium'], pady=SIZES['padding_small'])
        
        # 本周统计
        week_frame = tk.Frame(stats_container, bg=COLORS['bg_secondary'], relief='flat', bd=0)
        week_frame.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        tk.Label(
            week_frame,
            text=f"{ICONS['dashboard']} 本周注册: 0 成功 / 0 失败",
            font=FONTS['body'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(fill=tk.X, padx=SIZES['padding_medium'], pady=SIZES['padding_small'])
        
        # 成功率和平均用时
        metrics_frame = tk.Frame(stats_container, bg=COLORS['bg_primary'])
        metrics_frame.pack(fill=tk.X)
        
        success_rate_frame = tk.Frame(metrics_frame, bg=COLORS['bg_secondary'], relief='flat', bd=0)
        success_rate_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, SIZES['padding_small']))
        
        tk.Label(
            success_rate_frame,
            text=f"{ICONS['success']} 成功率: 0%",
            font=FONTS['body'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        ).pack(padx=SIZES['padding_medium'], pady=SIZES['padding_small'])
        
        avg_time_frame = tk.Frame(metrics_frame, bg=COLORS['bg_secondary'], relief='flat', bd=0)
        avg_time_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(SIZES['padding_small'], 0))
        
        tk.Label(
            avg_time_frame,
            text=f"{ICONS['info']} 平均用时: 0分0秒",
            font=FONTS['body'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary']
        ).pack(padx=SIZES['padding_medium'], pady=SIZES['padding_small'])
        
    def create_log_preview_section(self):
        """创建日志预览区域"""
        log_frame = tk.LabelFrame(
            self.scrollable_frame,
            text=f" {ICONS['logs']} 操作日志预览",
            **STYLES['label_frame']
        )
        log_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_xl'], pady=(0, SIZES['padding_xl']))
        
        # 日志文本区域
        log_container = tk.Frame(log_frame, bg=COLORS['bg_primary'])
        log_container.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_large'], pady=SIZES['padding_large'])
        
        # 日志文本框和滚动条
        log_text_frame = tk.Frame(log_container, bg=COLORS['bg_primary'])
        log_text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, SIZES['padding_medium']))
        
        self.log_text = tk.Text(
            log_text_frame,
            height=8,
            **STYLES['text']
        )
        self.log_text.config(state='disabled')
        
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
        # 初始化日志内容
        self.update_log_preview()
        
        # 查看全部日志按钮
        view_all_btn = tk.Button(
            log_container,
            text="查看全部日志",
            **STYLES['button_primary'],
            command=self.view_all_logs
        )
        view_all_btn.pack(anchor='w')
        
    def update_log_preview(self):
        """更新日志预览"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        
        # 模拟日志内容
        sample_logs = [
            "系统启动完成",
            "代理管理器初始化成功",
            "配置文件加载完成",
            "GUI界面加载完成",
            "等待用户操作..."
        ]
        
        import time
        current_time = time.strftime("%H:%M:%S")
        
        for i, log in enumerate(sample_logs):
            timestamp = time.strftime("%H:%M:%S", time.localtime(time.time() - (len(sample_logs) - i) * 10))
            log_line = f"[{timestamp}] [INFO] {log}\n"
            self.log_text.insert(tk.END, log_line)
            
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)
        
    def refresh(self):
        """刷新仪表板数据"""
        self.update_proxy_status()
        self.update_log_preview()
        
    def update_proxy_status(self):
        """更新代理状态"""
        try:
            stats = self.proxy_manager.get_proxy_statistics()
            active_count = stats['active_proxies']
            total_count = stats['total_proxies']
            
            if total_count == 0:
                status_text = f"{ICONS['warning']} 代理: 未配置"
                status_color = COLORS['warning']
            elif active_count == 0:
                status_text = f"{ICONS['error']} 代理: 无可用代理"
                status_color = COLORS['error']
            else:
                status_text = f"{ICONS['proxy_active']} 代理: {active_count}/{total_count}可用"
                status_color = COLORS['success']
                
            self.proxy_status_display.config(text=status_text, fg=status_color)
            
        except Exception as e:
            self.proxy_status_display.config(
                text=f"{ICONS['error']} 代理: 检查失败",
                fg=COLORS['error']
            )
            
    # 按钮回调函数
    def start_registration(self):
        """开始注册"""
        messagebox.showinfo("功能提示", "注册功能开发中...")
        
    def quick_config(self):
        """快速配置"""
        # 这里可以切换到配置页面
        messagebox.showinfo("功能提示", "请切换到配置设置页面进行配置")
        
    def view_logs(self):
        """查看日志"""
        messagebox.showinfo("功能提示", "请切换到日志查看页面")
        
    def view_details(self):
        """查看详情"""
        messagebox.showinfo("功能提示", "详情查看功能开发中...")
        
    def view_all_logs(self):
        """查看全部日志"""
        messagebox.showinfo("功能提示", "请切换到日志查看页面") 