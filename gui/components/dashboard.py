"""
仪表板组件

显示系统状态、快速操作和统计信息的主界面。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import threading
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gui.resources.styles import COLORS, FONTS, SIZES, ICONS, STYLES
from gui.services.registration_service import RegistrationService
from gui.services.proxy_service import ProxyService
from gui.services.config_service import ConfigService
from gui.services.log_service import LogService


class DashboardFrame(tk.Frame):
    """仪表板框架类"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.parent = parent
        
        # 初始化服务
        self.registration_service = RegistrationService()
        self.proxy_service = ProxyService()
        self.config_service = ConfigService()
        self.log_service = LogService()
        
        # 设置回调函数
        self.setup_service_callbacks()
        
        # 自动滚动变量
        self.auto_scroll_var = tk.BooleanVar(value=True)
        
        # 初始化UI
        self.setup_ui()
        self.refresh()
        
        # 启动自动刷新
        self.start_auto_refresh()
        
        # 启动按钮状态监控
        self.start_button_status_monitor()
        
    def setup_service_callbacks(self):
        """设置服务回调函数"""
        # 注册服务回调
        self.registration_service.set_callbacks(
            progress_callback=self.on_registration_progress,
            log_callback=self.on_log_message,
            status_callback=self.on_registration_status
        )
        
        # 日志服务回调
        self.log_service.add_log_listener(self.on_log_message)
        
    def on_registration_progress(self, progress, current, total, message):
        """注册进度回调"""
        # 更新统计显示
        self.after(0, lambda: self.update_registration_stats(current, total, message))
        
    def on_log_message(self, message, level="INFO"):
        """日志消息回调"""
        self.after(0, lambda: self.add_log_message(message, level))
        
    def on_registration_status(self, status):
        """注册状态回调"""
        def update_status():
            self.update_system_status(status)
            # 当注册完成时，重置按钮状态
            if status in ["就绪", "注册成功", "注册失败", "注册异常"] and not self.registration_service.is_registration_running():
                self.start_btn.config(text=f"{ICONS['start']} 开始注册")
        
        self.after(0, update_status)
        
    def add_log_message(self, message, level="INFO"):
        """添加日志消息到界面"""
        try:
            current_time = time.strftime("%H:%M:%S")
            log_line = f"[{current_time}] [{level}] {message}\n"
            
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, log_line)
            
            # 如果开启了自动滚动
            if self.auto_scroll_var.get():
                self.log_text.see(tk.END)
                
            self.log_text.config(state='disabled')
            
        except Exception as e:
            print(f"添加日志消息失败: {e}")

    def update_registration_stats(self, current, total, message):
        """更新注册统计信息"""
        try:
            # 更新最近活动区域的统计
            stats = self.registration_service.get_stats()
            
            self.success_count_label.config(
                text=f"{ICONS['success']} 注册成功 {stats['success']}个"
            )
            
            if hasattr(self, 'failed_count_label'):
                self.failed_count_label.config(
                    text=f"{ICONS['error']} 注册失败 {stats['failed']}个"
                )
                
        except Exception as e:
            print(f"更新注册统计失败: {e}")
            
    def update_system_status(self, status):
        """更新系统状态"""
        try:
            # 根据状态更新系统状态显示
            if "成功" in status:
                self.system_status_label.config(
                    text=f"{ICONS['success']} {status}",
                    fg=COLORS['success']
                )
            elif "失败" in status or "错误" in status:
                self.system_status_label.config(
                    text=f"{ICONS['error']} {status}",
                    fg=COLORS['error']
                )
            elif "注册中" in status or "运行中" in status:
                self.system_status_label.config(
                    text=f"{ICONS['loading']} {status}",
                    fg=COLORS['info']
                )
            else:
                self.system_status_label.config(
                    text=f"{ICONS['info']} {status}",
                    fg=COLORS['text_primary']
                )
                
        except Exception as e:
            print(f"更新系统状态失败: {e}")

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
        top_frame.pack(fill=tk.X, padx=SIZES['padding_xl'], pady=(SIZES['padding_xl'], SIZES['padding_medium']))
        
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
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, SIZES['padding_large']))
        
        # 内容框架 - 添加内边距
        content_frame = tk.Frame(frame, bg=COLORS['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_large'], pady=SIZES['padding_medium'])
        
        # 开始注册按钮
        self.start_btn = tk.Button(
            content_frame,
            text=f"{ICONS['start']} 开始注册",
            **STYLES['button_success'],
            command=self.start_registration
        )
        self.start_btn.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 快速配置按钮
        config_btn = tk.Button(
            content_frame,
            text=f"{ICONS['config']} 快速配置",
            **STYLES['button_primary'],
            command=self.quick_config
        )
        config_btn.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 查看日志按钮
        log_btn = tk.Button(
            content_frame,
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
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, SIZES['padding_large']))
        
        # 状态信息框架
        status_frame = tk.Frame(frame, bg=COLORS['bg_primary'])
        status_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_large'], pady=SIZES['padding_medium'])
        
        # 系统状态
        self.system_status_label = tk.Label(
            status_frame,
            text=f"{ICONS['success']} 系统正常",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['success'],
            anchor='w'
        )
        self.system_status_label.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 代理状态
        self.proxy_status_display = tk.Label(
            status_frame,
            text=f"{ICONS['proxy']} 代理: 检查中...",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        )
        self.proxy_status_display.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 邮箱状态
        self.email_status_label = tk.Label(
            status_frame,
            text=f"{ICONS['email']} 邮箱: 未测试",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary'],
            anchor='w'
        )
        self.email_status_label.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
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
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_large'], pady=SIZES['padding_medium'])
        
        # 统计信息
        self.success_count_label = tk.Label(
            activity_frame,
            text=f"{ICONS['success']} 注册成功 0个",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['success'],
            anchor='w'
        )
        self.success_count_label.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 失败统计
        self.failed_count_label = tk.Label(
            activity_frame,
            text=f"{ICONS['error']} 注册失败 0个",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['error'],
            anchor='w'
        )
        self.failed_count_label.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 运行状态
        self.running_status_label = tk.Label(
            activity_frame,
            text=f"{ICONS['info']} 系统就绪",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary'],
            anchor='w'
        )
        self.running_status_label.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 查看详情按钮
        details_btn = tk.Button(
            activity_frame,
            text=f"{ICONS['detail']} 查看详情",
            **STYLES['button_secondary'],
            command=self.view_details
        )
        details_btn.pack(fill=tk.X)
        
    def create_statistics_section(self):
        """创建统计区域"""
        stats_frame = tk.LabelFrame(
            self.scrollable_frame,
            text=f" {ICONS['chart']} 注册统计",
            **STYLES['label_frame']
        )
        stats_frame.pack(fill=tk.X, padx=SIZES['padding_xl'], pady=(SIZES['padding_medium'], SIZES['padding_large']))
        
        # 统计信息容器
        stats_container = tk.Frame(stats_frame, bg=COLORS['bg_primary'])
        stats_container.pack(fill=tk.X, padx=SIZES['padding_large'], pady=SIZES['padding_medium'])
        
        # 创建统计卡片网格
        # 第一行：今日和本周统计
        row1_frame = tk.Frame(stats_container, bg=COLORS['bg_primary'])
        row1_frame.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 今日统计卡片
        today_card = tk.Frame(row1_frame, **STYLES['card_frame'])
        today_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, SIZES['padding_medium']))
        
        today_title = tk.Label(
            today_card,
            text=f"{ICONS['dashboard']} 今日注册",
            font=FONTS['subheading'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        )
        today_title.pack(fill=tk.X, padx=SIZES['padding_large'], pady=(SIZES['padding_large'], SIZES['padding_small']))
        
        today_stats = tk.Label(
            today_card,
            text="0 成功 / 0 失败",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary'],
            anchor='w'
        )
        today_stats.pack(fill=tk.X, padx=SIZES['padding_large'], pady=(0, SIZES['padding_large']))
        
        # 本周统计卡片
        week_card = tk.Frame(row1_frame, **STYLES['card_frame'])
        week_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        week_title = tk.Label(
            week_card,
            text=f"{ICONS['chart']} 本周注册",
            font=FONTS['subheading'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        )
        week_title.pack(fill=tk.X, padx=SIZES['padding_large'], pady=(SIZES['padding_large'], SIZES['padding_small']))
        
        week_stats = tk.Label(
            week_card,
            text="0 成功 / 0 失败",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary'],
            anchor='w'
        )
        week_stats.pack(fill=tk.X, padx=SIZES['padding_large'], pady=(0, SIZES['padding_large']))
        
        # 第二行：成功率和平均用时
        row2_frame = tk.Frame(stats_container, bg=COLORS['bg_primary'])
        row2_frame.pack(fill=tk.X)
        
        # 成功率卡片
        success_card = tk.Frame(row2_frame, **STYLES['card_frame'])
        success_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, SIZES['padding_medium']))
        
        success_title = tk.Label(
            success_card,
            text=f"{ICONS['success']} 成功率",
            font=FONTS['subheading'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        )
        success_title.pack(fill=tk.X, padx=SIZES['padding_large'], pady=(SIZES['padding_large'], SIZES['padding_small']))
        
        self.success_rate_label = tk.Label(
            success_card,
            text="0%",
            font=FONTS['heading'],
            bg=COLORS['bg_primary'],
            fg=COLORS['success'],
            anchor='w'
        )
        self.success_rate_label.pack(fill=tk.X, padx=SIZES['padding_large'], pady=(0, SIZES['padding_large']))
        
        # 平均用时卡片
        time_card = tk.Frame(row2_frame, **STYLES['card_frame'])
        time_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        time_title = tk.Label(
            time_card,
            text=f"{ICONS['performance']} 平均用时",
            font=FONTS['subheading'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        )
        time_title.pack(fill=tk.X, padx=SIZES['padding_large'], pady=(SIZES['padding_large'], SIZES['padding_small']))
        
        self.avg_time_label = tk.Label(
            time_card,
            text="0分0秒",
            font=FONTS['heading'],
            bg=COLORS['bg_primary'],
            fg=COLORS['info'],
            anchor='w'
        )
        self.avg_time_label.pack(fill=tk.X, padx=SIZES['padding_large'], pady=(0, SIZES['padding_large']))
        
    def create_log_preview_section(self):
        """创建日志预览区域"""
        log_frame = tk.LabelFrame(
            self.scrollable_frame,
            text=f" {ICONS['logs']} 操作日志预览",
            **STYLES['label_frame']
        )
        log_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_xl'], pady=(0, SIZES['padding_xl']))
        
        # 日志容器
        log_container = tk.Frame(log_frame, bg=COLORS['bg_primary'])
        log_container.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_large'], pady=SIZES['padding_medium'])
        
        # 日志头部工具栏
        log_toolbar = tk.Frame(log_container, bg=COLORS['bg_primary'])
        log_toolbar.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 日志级别筛选
        level_label = tk.Label(
            log_toolbar,
            text="级别筛选:",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary']
        )
        level_label.pack(side=tk.LEFT)
        
        self.log_level_var = tk.StringVar(value="全部")
        level_combo = ttk.Combobox(
            log_toolbar,
            textvariable=self.log_level_var,
            values=["全部", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=8
        )
        level_combo.pack(side=tk.LEFT, padx=(SIZES['padding_small'], SIZES['padding_medium']))
        
        # 自动滚动开关
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = tk.Checkbutton(
            log_toolbar,
            text="自动滚动",
            variable=self.auto_scroll_var,
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary'],
            selectcolor=COLORS['bg_primary'],
            activebackground=COLORS['bg_primary']
        )
        auto_scroll_check.pack(side=tk.LEFT, padx=(0, SIZES['padding_medium']))
        
        # 清空日志按钮
        clear_btn = tk.Button(
            log_toolbar,
            text=f"{ICONS['clear']}",
            **STYLES['button_icon'],
            command=self.clear_log_preview
        )
        clear_btn.pack(side=tk.RIGHT)
        
        # 日志文本区域
        log_text_container = tk.Frame(log_container, **STYLES['card_frame'])
        log_text_container.pack(fill=tk.BOTH, expand=True, pady=(0, SIZES['padding_medium']))
        
        # 日志文本框和滚动条
        self.log_text = tk.Text(
            log_text_container,
            height=8,
            **STYLES['text'],
            state='disabled'
        )
        
        log_scrollbar = ttk.Scrollbar(log_text_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True, padx=SIZES['padding_medium'], pady=SIZES['padding_medium'])
        log_scrollbar.pack(side="right", fill="y", padx=(0, SIZES['padding_medium']), pady=SIZES['padding_medium'])
        
        # 底部按钮栏
        button_frame = tk.Frame(log_container, bg=COLORS['bg_primary'])
        button_frame.pack(fill=tk.X)
        
        # 查看全部日志按钮
        view_all_btn = tk.Button(
            button_frame,
            text=f"{ICONS['logs']} 查看全部日志",
            **STYLES['button_primary'],
            command=self.view_all_logs
        )
        view_all_btn.pack(side=tk.LEFT)
        
        # 导出日志按钮
        export_btn = tk.Button(
            button_frame,
            text=f"{ICONS['export']} 导出日志",
            **STYLES['button_secondary'],
            command=self.export_logs
        )
        export_btn.pack(side=tk.LEFT, padx=(SIZES['padding_medium'], 0))
        
        # 初始化日志内容
        self.update_log_preview()
        
    def clear_log_preview(self):
        """清空日志预览"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
    def export_logs(self):
        """导出日志"""
        messagebox.showinfo("功能提示", "日志导出功能开发中...")
        
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
            stats = self.proxy_service.get_proxy_statistics()
            active_count = stats['active_proxies']
            total_count = stats['total_proxies']
            
            if total_count == 0:
                status_text = f"{ICONS['warning']} 代理: 未配置"
                status_color = COLORS['warning']
            elif active_count == 0:
                status_text = f"{ICONS['error']} 代理: 无可用代理"
                status_color = COLORS['error']
            else:
                status_text = f"{ICONS['proxy']} 代理: {active_count}/{total_count}可用"
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
        if self.registration_service.is_registration_running():
            # 如果已在运行，显示暂停/继续选项
            if self.registration_service.is_registration_paused():
                result = messagebox.askyesno("恢复注册", "注册任务已暂停，是否要恢复？")
                if result:
                    self.registration_service.resume_registration()
                    self.start_btn.config(text=f"{ICONS['pause']} 暂停注册")
            else:
                result = messagebox.askyesno("暂停注册", "注册任务正在运行，是否要暂停？")
                if result:
                    self.registration_service.pause_registration()
                    self.start_btn.config(text=f"{ICONS['play']} 恢复注册")
        else:
            # 开始新的注册任务 - 弹出自定义注册对话框
            registration_dialog = RegistrationConfigDialog(self)
            if registration_dialog.result:
                account_count = registration_dialog.account_count
                concurrent = registration_dialog.concurrent
                interval = registration_dialog.interval
                
                if account_count == 1:
                    # 单个注册
                    success = self.registration_service.start_single_registration()
                    if success:
                        self.start_btn.config(text=f"{ICONS['stop']} 停止注册")
                        self.add_log_message("开始单个账号注册任务", "INFO")
                    else:
                        messagebox.showerror("启动失败", "注册任务启动失败，请检查配置")
                else:
                    # 批量注册
                    success = self.registration_service.start_batch_registration(
                        account_count=account_count,
                        concurrent=concurrent,
                        interval=interval
                    )
                    if success:
                        self.start_btn.config(text=f"{ICONS['stop']} 停止注册")
                        self.add_log_message(f"开始批量注册任务: {account_count} 个账号", "INFO")
                    else:
                        messagebox.showerror("启动失败", "批量注册任务启动失败，请检查配置")
        
    def quick_config(self):
        """快速配置"""
        # 弹出快速配置对话框
        config_dialog = QuickConfigDialog(self)
        if config_dialog.result:
            self.add_log_message("配置已更新", "INFO")
        
    def view_logs(self):
        """查看日志"""
        if hasattr(self.parent, 'switch_tab'):
            self.parent.switch_tab("logs")
        else:
            messagebox.showinfo("提示", "请切换到日志查看页面")
        
    def view_details(self):
        """查看详情"""
        stats = self.registration_service.get_stats()
        proxy_stats = self.proxy_service.get_proxy_statistics()
        
        details_text = f"""系统状态详情:
        
注册统计:
- 总数: {stats['total']}
- 当前: {stats['current']}  
- 成功: {stats['success']}
- 失败: {stats['failed']}

代理状态:
- 总代理数: {proxy_stats['total_proxies']}
- 可用代理: {proxy_stats['active_proxies']}
- 已耗尽: {proxy_stats['exhausted_proxies']}

运行状态: {'运行中' if self.registration_service.is_registration_running() else '就绪'}
"""
        
        messagebox.showinfo("系统详情", details_text)
        
    def view_all_logs(self):
        """查看全部日志"""
        if hasattr(self.parent, 'switch_tab'):
            self.parent.switch_tab("logs")
        else:
            messagebox.showinfo("提示", "请切换到日志查看页面")

    def start_auto_refresh(self):
        """启动自动刷新"""
        def refresh_worker():
            while True:
                try:
                    # 每5秒刷新一次代理状态
                    self.after(0, self.update_proxy_status)
                    time.sleep(5)
                except:
                    break
        
        refresh_thread = threading.Thread(target=refresh_worker)
        refresh_thread.daemon = True
        refresh_thread.start()

    def start_button_status_monitor(self):
        """启动按钮状态监控"""
        def monitor_worker():
            while True:
                try:
                    # 每5秒检查一次按钮状态
                    self.after(0, self.check_button_status)
                    time.sleep(5)
                except:
                    break
        
        monitor_thread = threading.Thread(target=monitor_worker)
        monitor_thread.daemon = True
        monitor_thread.start()

    def check_button_status(self):
        """检查按钮状态"""
        if self.registration_service.is_registration_running():
            # 如果已在运行，检查按钮状态
            if self.registration_service.is_registration_paused():
                self.start_btn.config(text=f"{ICONS['play']} 恢复注册")
            else:
                self.start_btn.config(text=f"{ICONS['pause']} 暂停注册")
        else:
            # 如果未在运行，重置按钮状态
            self.start_btn.config(text=f"{ICONS['start']} 开始注册")


class QuickConfigDialog:
    """快速配置对话框"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = False
        self.config_service = ConfigService()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("快速配置")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.load_current_config()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
    def setup_ui(self):
        """设置UI"""
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 邮箱配置
        tk.Label(main_frame, text="邮箱地址:", font=FONTS['body']).grid(row=0, column=0, sticky="w", pady=5)
        self.email_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=self.email_var, width=30).grid(row=0, column=1, pady=5, padx=(10, 0))
        
        tk.Label(main_frame, text="邮箱密码:", font=FONTS['body']).grid(row=1, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=self.password_var, width=30, show="*").grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # 并发数配置
        tk.Label(main_frame, text="并发数:", font=FONTS['body']).grid(row=2, column=0, sticky="w", pady=5)
        self.concurrent_var = tk.IntVar(value=3)
        tk.Spinbox(main_frame, from_=1, to=10, textvariable=self.concurrent_var, width=28).grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # 按钮
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="保存", command=self.save_config, **STYLES['button_success']).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="取消", command=self.cancel, **STYLES['button_secondary']).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="测试邮箱", command=self.test_email, **STYLES['button_primary']).pack(side=tk.LEFT, padx=5)
        
    def load_current_config(self):
        """加载当前配置"""
        try:
            config = self.config_service.load_config()
            
            self.email_var.set(config.get('mail', {}).get('mail_address', ''))
            self.password_var.set(config.get('mail', {}).get('mail_password', ''))
            self.concurrent_var.set(config.get('registration', {}).get('max_concurrent', 3))
            
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败: {str(e)}")
            
    def save_config(self):
        """保存配置"""
        try:
            config = self.config_service.load_config()
            
            # 更新邮箱配置
            config['mail']['mail_address'] = self.email_var.get()
            config['mail']['mail_password'] = self.password_var.get()
            
            # 更新注册配置
            config['registration']['max_concurrent'] = self.concurrent_var.get()
            
            if self.config_service.save_config(config):
                self.result = True
                messagebox.showinfo("成功", "配置保存成功")
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "配置保存失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
            
    def test_email(self):
        """测试邮箱配置"""
        try:
            config = {
                'mail': {
                    'imap_server': 'imap.qq.com',
                    'imap_port': 993,
                    'mail_address': self.email_var.get(),
                    'mail_password': self.password_var.get(),
                    'use_ssl': True
                }
            }
            
            success, message = self.config_service.test_email_config(config)
            
            if success:
                messagebox.showinfo("测试成功", message)
            else:
                messagebox.showerror("测试失败", message)
                
        except Exception as e:
            messagebox.showerror("错误", f"测试邮箱失败: {str(e)}")
            
    def cancel(self):
        """取消"""
        self.dialog.destroy()


class RegistrationConfigDialog:
    """自定义注册对话框"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = False
        self.account_count = 1
        self.concurrent = 3
        self.interval = 60
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("自定义注册配置")
        self.dialog.geometry("450x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
    def setup_ui(self):
        """设置UI"""
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = tk.Label(
            main_frame, 
            text="🚀 自定义注册配置", 
            font=FONTS['heading'], 
            fg=COLORS['primary']
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 账号数量配置
        tk.Label(main_frame, text="注册账号数量:", font=FONTS['body']).grid(row=1, column=0, sticky="w", pady=8)
        self.account_count_var = tk.IntVar(value=1)
        account_spinbox = tk.Spinbox(
            main_frame, 
            from_=1, 
            to=100, 
            textvariable=self.account_count_var, 
            width=28,
            font=FONTS['body']
        )
        account_spinbox.grid(row=1, column=1, pady=8, padx=(10, 0))
        
        # 并发数配置
        tk.Label(main_frame, text="并发数量:", font=FONTS['body']).grid(row=2, column=0, sticky="w", pady=8)
        self.concurrent_var = tk.IntVar(value=3)
        concurrent_spinbox = tk.Spinbox(
            main_frame, 
            from_=1, 
            to=10, 
            textvariable=self.concurrent_var, 
            width=28,
            font=FONTS['body']
        )
        concurrent_spinbox.grid(row=2, column=1, pady=8, padx=(10, 0))
        
        # 间隔时间配置
        tk.Label(main_frame, text="间隔时间 (秒):", font=FONTS['body']).grid(row=3, column=0, sticky="w", pady=8)
        self.interval_var = tk.IntVar(value=60)
        interval_spinbox = tk.Spinbox(
            main_frame, 
            from_=5, 
            to=3600, 
            textvariable=self.interval_var, 
            width=28,
            font=FONTS['body']
        )
        interval_spinbox.grid(row=3, column=1, pady=8, padx=(10, 0))
        
        # 说明文本
        info_frame = tk.Frame(main_frame)
        info_frame.grid(row=4, column=0, columnspan=2, pady=(20, 10), sticky="ew")
        
        info_text = tk.Text(
            info_frame,
            height=4,
            width=50,
            font=FONTS['small'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary'],
            wrap=tk.WORD,
            relief='flat',
            bd=1
        )
        info_text.pack(fill=tk.BOTH, expand=True)
        
        info_content = """💡 配置说明：
• 账号数量：要注册的Claude账号总数
• 并发数量：同时进行注册的浏览器窗口数（建议1-5个）
• 间隔时间：每个账号注册之间的等待时间（建议60秒以上）"""
        
        info_text.insert(tk.END, info_content)
        info_text.config(state='disabled')
        
        # 按钮
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        start_btn = tk.Button(
            button_frame, 
            text=f"{ICONS['start']} 开始注册", 
            command=self.start_registration, 
            **STYLES['button_success']
        )
        start_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame, 
            text=f"{ICONS['close']} 取消", 
            command=self.cancel, 
            **STYLES['button_secondary']
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
    def start_registration(self):
        """开始注册"""
        try:
            self.account_count = self.account_count_var.get()
            self.concurrent = self.concurrent_var.get()
            self.interval = self.interval_var.get()
            
            # 验证配置
            if self.account_count < 1 or self.account_count > 100:
                messagebox.showerror("错误", "账号数量必须在1-100之间")
                return
                
            if self.concurrent < 1 or self.concurrent > 10:
                messagebox.showerror("错误", "并发数量必须在1-10之间")
                return
                
            if self.interval < 5 or self.interval > 3600:
                messagebox.showerror("错误", "间隔时间必须在5-3600秒之间")
                return
            
            # 确认对话框
            if self.account_count == 1:
                confirm_msg = "确定要开始单个账号注册吗？"
            else:
                confirm_msg = f"""确定要开始批量注册吗？

配置信息：
• 注册数量：{self.account_count} 个账号
• 并发数量：{self.concurrent} 个
• 间隔时间：{self.interval} 秒

预计总时间：约 {self.account_count * self.interval // 60} 分钟"""
            
            result = messagebox.askyesno("确认注册", confirm_msg)
            if result:
                self.result = True
                self.dialog.destroy()
                
        except Exception as e:
            messagebox.showerror("错误", f"配置验证失败: {str(e)}")
            
    def cancel(self):
        """取消"""
        self.dialog.destroy() 