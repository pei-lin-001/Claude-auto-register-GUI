"""
配置面板组件

实现系统配置参数的设置界面，包括邮箱、Cloudflare、浏览器等配置。
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gui.resources.styles import COLORS, FONTS, SIZES, ICONS, STYLES
from utils.config import config


class ConfigFrame(tk.Frame):
    """配置设置框架类"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.parent = parent
        self.config_data = config.copy()  # 复制配置数据
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """设置UI界面"""
        # 创建主滚动区域
        self.create_scrollable_area()
        
        # 创建配置区域
        self.create_config_sections()
        
        # 创建按钮区域
        self.create_button_section()
        
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
        
    def create_config_sections(self):
        """创建配置区域"""
        main_container = tk.Frame(self.scrollable_frame, bg=COLORS['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_xl'], pady=SIZES['padding_xl'])
        
        # 顶部区域（邮箱和Cloudflare配置）
        top_frame = tk.Frame(main_container, bg=COLORS['bg_primary'])
        top_frame.pack(fill=tk.X, pady=(0, SIZES['padding_large']))
        
        # 邮箱配置
        self.create_email_config_section(top_frame)
        
        # Cloudflare配置
        self.create_cloudflare_config_section(top_frame)
        
        # 浏览器配置
        self.create_browser_config_section(main_container)
        
        # 注册配置
        self.create_registration_config_section(main_container)
        
    def create_email_config_section(self, parent):
        """创建邮箱配置区域"""
        frame = tk.LabelFrame(
            parent,
            text=f" {ICONS['email']} 邮箱配置",
            **STYLES['label_frame']
        )
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, SIZES['padding_medium']))
        
        # 配置容器
        config_container = tk.Frame(frame, bg=COLORS['bg_primary'])
        config_container.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_large'], pady=SIZES['padding_large'])
        
        # IMAP服务器
        tk.Label(
            config_container,
            text="IMAP服务器:",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(0, SIZES['padding_xs']))
        
        self.imap_server_var = tk.StringVar()
        imap_entry = tk.Entry(
            config_container,
            textvariable=self.imap_server_var,
            **STYLES['entry']
        )
        imap_entry.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 邮箱地址
        tk.Label(
            config_container,
            text="邮箱地址:",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(0, SIZES['padding_xs']))
        
        self.email_address_var = tk.StringVar()
        email_entry = tk.Entry(
            config_container,
            textvariable=self.email_address_var,
            **STYLES['entry']
        )
        email_entry.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 授权码
        tk.Label(
            config_container,
            text="授权码:",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(0, SIZES['padding_xs']))
        
        self.email_password_var = tk.StringVar()
        password_entry = tk.Entry(
            config_container,
            textvariable=self.email_password_var,
            show='*',
            **STYLES['entry']
        )
        password_entry.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 超时时间
        tk.Label(
            config_container,
            text="超时时间(秒):",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(0, SIZES['padding_xs']))
        
        self.email_timeout_var = tk.StringVar()
        timeout_entry = tk.Entry(
            config_container,
            textvariable=self.email_timeout_var,
            **STYLES['entry']
        )
        timeout_entry.pack(fill=tk.X, pady=(0, SIZES['padding_large']))
        
        # 测试连接按钮
        test_email_btn = tk.Button(
            config_container,
            text=f"{ICONS['test']} 测试连接",
            **STYLES['button_secondary'],
            command=self.test_email_connection
        )
        test_email_btn.pack(anchor='w')
        
    def create_cloudflare_config_section(self, parent):
        """创建Cloudflare配置区域"""
        frame = tk.LabelFrame(
            parent,
            text=f" {ICONS['cloudflare']} Cloudflare配置",
            **STYLES['label_frame']
        )
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 配置容器
        config_container = tk.Frame(frame, bg=COLORS['bg_primary'])
        config_container.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_large'], pady=SIZES['padding_large'])
        
        # API密钥
        tk.Label(
            config_container,
            text="API密钥:",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 2))
        
        self.cf_api_key_var = tk.StringVar()
        api_key_entry = tk.Entry(
            config_container,
            textvariable=self.cf_api_key_var,
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='sunken',
            bd=1,
            show='*'
        )
        api_key_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 区域ID
        tk.Label(
            config_container,
            text="区域ID:",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 2))
        
        self.cf_zone_id_var = tk.StringVar()
        zone_id_entry = tk.Entry(
            config_container,
            textvariable=self.cf_zone_id_var,
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='sunken',
            bd=1
        )
        zone_id_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 认证邮箱
        tk.Label(
            config_container,
            text="认证邮箱:",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 2))
        
        self.cf_auth_email_var = tk.StringVar()
        auth_email_entry = tk.Entry(
            config_container,
            textvariable=self.cf_auth_email_var,
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='sunken',
            bd=1
        )
        auth_email_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 规则域名
        tk.Label(
            config_container,
            text="规则域名:",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 2))
        
        self.cf_domain_var = tk.StringVar()
        domain_entry = tk.Entry(
            config_container,
            textvariable=self.cf_domain_var,
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='sunken',
            bd=1
        )
        domain_entry.pack(fill=tk.X, pady=(0, 15))
        
        # 测试API按钮
        test_cf_btn = tk.Button(
            config_container,
            text=f"{ICONS['test']} 测试API",
            font=FONTS['default'],
            bg=COLORS['info'],
            fg=COLORS['text_light'],
            relief='raised',
            bd=2,
            command=self.test_cloudflare_api
        )
        test_cf_btn.pack(anchor='w')
        
    def create_browser_config_section(self, parent):
        """创建浏览器配置区域"""
        frame = tk.LabelFrame(
            parent,
            text=f"{ICONS['config']} 浏览器配置",
            font=FONTS['subheading'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='groove',
            bd=2
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # 配置容器
        config_container = tk.Frame(frame, bg=COLORS['bg_primary'])
        config_container.pack(fill=tk.X, padx=15, pady=15)
        
        # 窗口位置和大小
        position_frame = tk.Frame(config_container, bg=COLORS['bg_primary'])
        position_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            position_frame,
            text="窗口位置:",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            position_frame,
            text="X:",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        self.browser_x_var = tk.StringVar()
        x_entry = tk.Entry(
            position_frame,
            textvariable=self.browser_x_var,
            font=FONTS['default'],
            width=8,
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='sunken',
            bd=1
        )
        x_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            position_frame,
            text="Y:",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(10, 5))
        
        self.browser_y_var = tk.StringVar()
        y_entry = tk.Entry(
            position_frame,
            textvariable=self.browser_y_var,
            font=FONTS['default'],
            width=8,
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='sunken',
            bd=1
        )
        y_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(
            position_frame,
            text="窗口大小: W:",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        tk.Label(
            position_frame,
            text="1200",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            position_frame,
            text="H:",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(10, 5))
        
        tk.Label(
            position_frame,
            text="800",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.LEFT)
        
        # ChromeDriver路径
        driver_frame = tk.Frame(config_container, bg=COLORS['bg_primary'])
        driver_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            driver_frame,
            text="ChromeDriver路径:",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 2))
        
        driver_input_frame = tk.Frame(driver_frame, bg=COLORS['bg_primary'])
        driver_input_frame.pack(fill=tk.X)
        
        self.driver_path_var = tk.StringVar()
        driver_entry = tk.Entry(
            driver_input_frame,
            textvariable=self.driver_path_var,
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='sunken',
            bd=1
        )
        driver_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(
            driver_input_frame,
            text="浏览",
            font=FONTS['default'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            relief='raised',
            bd=1,
            command=self.browse_driver_path
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # 浏览器选项
        options_frame = tk.Frame(config_container, bg=COLORS['bg_primary'])
        options_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.headless_var = tk.BooleanVar()
        self.disable_images_var = tk.BooleanVar()
        self.disable_css_var = tk.BooleanVar(value=True)
        self.debug_mode_var = tk.BooleanVar()
        
        options_row1 = tk.Frame(options_frame, bg=COLORS['bg_primary'])
        options_row1.pack(fill=tk.X)
        
        tk.Checkbutton(
            options_row1,
            text="无头模式",
            variable=self.headless_var,
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Checkbutton(
            options_row1,
            text="禁用图片",
            variable=self.disable_images_var,
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Checkbutton(
            options_row1,
            text="禁用CSS",
            variable=self.disable_css_var,
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Checkbutton(
            options_row1,
            text="调试模式",
            variable=self.debug_mode_var,
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(side=tk.LEFT)
        
        # 超时设置
        timeout_frame = tk.Frame(config_container, bg=COLORS['bg_primary'])
        timeout_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(
            timeout_frame,
            text="页面超时(秒):",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.page_timeout_var = tk.StringVar(value="30")
        page_timeout_entry = tk.Entry(
            timeout_frame,
            textvariable=self.page_timeout_var,
            font=FONTS['default'],
            width=8,
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='sunken',
            bd=1
        )
        page_timeout_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(
            timeout_frame,
            text="元素等待(秒):",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.element_timeout_var = tk.StringVar(value="10")
        element_timeout_entry = tk.Entry(
            timeout_frame,
            textvariable=self.element_timeout_var,
            font=FONTS['default'],
            width=8,
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='sunken',
            bd=1
        )
        element_timeout_entry.pack(side=tk.LEFT)
        
    def create_registration_config_section(self, parent):
        """创建注册配置区域"""
        frame = tk.LabelFrame(
            parent,
            text=f"{ICONS['config']} 注册配置",
            font=FONTS['subheading'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='groove',
            bd=2
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # 配置容器
        config_container = tk.Frame(frame, bg=COLORS['bg_primary'])
        config_container.pack(fill=tk.X, padx=15, pady=15)
        
        # 数值配置
        values_frame = tk.Frame(config_container, bg=COLORS['bg_primary'])
        values_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            values_frame,
            text="最大轮询次数:",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.max_polling_var = tk.StringVar()
        polling_entry = tk.Entry(
            values_frame,
            textvariable=self.max_polling_var,
            font=FONTS['default'],
            width=8,
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='sunken',
            bd=1
        )
        polling_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(
            values_frame,
            text="注册间隔(秒):",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.register_interval_var = tk.StringVar(value="60")
        interval_entry = tk.Entry(
            values_frame,
            textvariable=self.register_interval_var,
            font=FONTS['default'],
            width=8,
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='sunken',
            bd=1
        )
        interval_entry.pack(side=tk.LEFT)
        
        # 第二行配置
        values_frame2 = tk.Frame(config_container, bg=COLORS['bg_primary'])
        values_frame2.pack(fill=tk.X, pady=(10, 10))
        
        tk.Label(
            values_frame2,
            text="代理最大使用次数:",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.proxy_max_usage_var = tk.StringVar(value="3")
        proxy_usage_entry = tk.Entry(
            values_frame2,
            textvariable=self.proxy_max_usage_var,
            font=FONTS['default'],
            width=8,
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='sunken',
            bd=1
        )
        proxy_usage_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(
            values_frame2,
            text="失败重试次数:",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.retry_count_var = tk.StringVar(value="3")
        retry_entry = tk.Entry(
            values_frame2,
            textvariable=self.retry_count_var,
            font=FONTS['default'],
            width=8,
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='sunken',
            bd=1
        )
        retry_entry.pack(side=tk.LEFT)
        
        # 关键字设置
        keyword_frame = tk.Frame(config_container, bg=COLORS['bg_primary'])
        keyword_frame.pack(fill=tk.X, pady=(10, 10))
        
        tk.Label(
            keyword_frame,
            text="关键字:",
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 2))
        
        self.keyword_var = tk.StringVar()
        keyword_entry = tk.Entry(
            keyword_frame,
            textvariable=self.keyword_var,
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            relief='sunken',
            bd=1
        )
        keyword_entry.pack(fill=tk.X)
        
        # 选项设置
        options_frame = tk.Frame(config_container, bg=COLORS['bg_primary'])
        options_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.auto_retry_var = tk.BooleanVar()
        self.save_logs_var = tk.BooleanVar(value=True)
        self.auto_backup_var = tk.BooleanVar(value=True)
        self.verify_email_var = tk.BooleanVar()
        
        tk.Checkbutton(
            options_frame,
            text="自动重试",
            variable=self.auto_retry_var,
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Checkbutton(
            options_frame,
            text="保存日志",
            variable=self.save_logs_var,
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Checkbutton(
            options_frame,
            text="自动备份",
            variable=self.auto_backup_var,
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Checkbutton(
            options_frame,
            text="验证邮件",
            variable=self.verify_email_var,
            font=FONTS['default'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            anchor='w'
        ).pack(side=tk.LEFT)
        
    def create_button_section(self):
        """创建按钮区域"""
        button_frame = tk.Frame(self.scrollable_frame, bg=COLORS['bg_primary'])
        button_frame.pack(fill=tk.X, padx=SIZES['padding_xl'], pady=(0, SIZES['padding_xl']))
        
        # 保存配置按钮
        save_btn = tk.Button(
            button_frame,
            text=f"{ICONS['save']} 保存配置",
            **STYLES['button_success'],
            command=self.save_config
        )
        save_btn.pack(side=tk.LEFT, padx=(0, SIZES['padding_medium']))
        
        # 重置默认按钮
        reset_btn = tk.Button(
            button_frame,
            text=f"{ICONS['refresh']} 重置默认",
            **STYLES['button_warning'],
            command=self.reset_config
        )
        reset_btn.pack(side=tk.LEFT, padx=(0, SIZES['padding_medium']))
        
        # 导入配置按钮
        import_btn = tk.Button(
            button_frame,
            text=f"{ICONS['import']} 导入配置",
            **STYLES['button_secondary'],
            command=self.import_config
        )
        import_btn.pack(side=tk.LEFT, padx=(0, SIZES['padding_medium']))
        
        # 导出配置按钮
        export_btn = tk.Button(
            button_frame,
            text=f"{ICONS['export']} 导出配置",
            **STYLES['button_primary'],
            command=self.export_config
        )
        export_btn.pack(side=tk.LEFT)
        
    def load_config(self):
        """加载配置到界面"""
        # 邮箱配置
        self.imap_server_var.set(self.config_data.get('mail', {}).get('imap_server', ''))
        self.email_address_var.set(self.config_data.get('mail', {}).get('mail_address', ''))
        self.email_password_var.set(self.config_data.get('mail', {}).get('mail_password', ''))
        self.email_timeout_var.set(str(self.config_data.get('mail', {}).get('mail_timeout', 4)))
        
        # Cloudflare配置
        cf_config = self.config_data.get('cloudflare', {})
        self.cf_api_key_var.set(cf_config.get('api_key', ''))
        self.cf_zone_id_var.set(cf_config.get('zone_identifier', ''))
        self.cf_auth_email_var.set(cf_config.get('auth_email', ''))
        self.cf_domain_var.set(cf_config.get('rules_domain', ''))
        
        # 浏览器配置
        chrome_config = self.config_data.get('chrome', {})
        self.browser_x_var.set(str(chrome_config.get('x', 0)))
        self.browser_y_var.set(str(chrome_config.get('y', 0)))
        self.driver_path_var.set("driver/chromedriver")
        
        # 注册配置
        self.max_polling_var.set(str(self.config_data.get('lunxun', 10)))
        self.keyword_var.set(self.config_data.get('claude_title_key', 'log in to Claude.ai'))
        
    def browse_driver_path(self):
        """浏览选择ChromeDriver路径"""
        filename = filedialog.askopenfilename(
            title="选择ChromeDriver",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.driver_path_var.set(filename)
            
    def test_email_connection(self):
        """测试邮箱连接"""
        messagebox.showinfo("功能提示", "邮箱连接测试功能开发中...")
        
    def test_cloudflare_api(self):
        """测试Cloudflare API"""
        messagebox.showinfo("功能提示", "Cloudflare API测试功能开发中...")
        
    def save_config(self):
        """保存配置"""
        try:
            # 更新配置数据
            self.config_data['mail']['imap_server'] = self.imap_server_var.get()
            self.config_data['mail']['mail_address'] = self.email_address_var.get()
            self.config_data['mail']['mail_password'] = self.email_password_var.get()
            self.config_data['mail']['mail_timeout'] = int(self.email_timeout_var.get() or 4)
            
            self.config_data['cloudflare']['api_key'] = self.cf_api_key_var.get()
            self.config_data['cloudflare']['zone_identifier'] = self.cf_zone_id_var.get()
            self.config_data['cloudflare']['auth_email'] = self.cf_auth_email_var.get()
            self.config_data['cloudflare']['rules_domain'] = self.cf_domain_var.get()
            
            self.config_data['chrome']['x'] = int(self.browser_x_var.get() or 0)
            self.config_data['chrome']['y'] = int(self.browser_y_var.get() or 0)
            
            self.config_data['lunxun'] = int(self.max_polling_var.get() or 10)
            self.config_data['claude_title_key'] = self.keyword_var.get()
            
            messagebox.showinfo("成功", "配置保存成功！")
            
        except ValueError as e:
            messagebox.showerror("错误", f"配置保存失败，请检查数值输入: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"配置保存失败: {str(e)}")
            
    def reset_config(self):
        """重置配置"""
        result = messagebox.askyesno("确认", "确定要重置为默认配置吗？")
        if result:
            self.config_data = config.copy()
            self.load_config()
            messagebox.showinfo("提示", "配置已重置为默认值")
            
    def import_config(self):
        """导入配置"""
        messagebox.showinfo("功能提示", "导入配置功能开发中...")
        
    def export_config(self):
        """导出配置"""
        messagebox.showinfo("功能提示", "导出配置功能开发中...")
        
    def refresh(self):
        """刷新配置页面"""
        self.load_config() 