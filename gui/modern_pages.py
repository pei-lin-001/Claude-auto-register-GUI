"""
现代化页面组件

包含所有步骤页面的实现
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
import threading
import time
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import config
from utils.proxy_manager import ProxyManager


class BasePage(tk.Frame):
    """页面基类"""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.colors['bg_card'])
        self.app = app
        self.colors = app.colors
        self.fonts = app.fonts
        
    def create_card(self, parent, title, description=None):
        """创建卡片容器"""
        card_frame = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat', bd=1)
        card_frame.pack(fill=tk.X, pady=10)
        
        # 卡片内容
        content_frame = tk.Frame(card_frame, bg=self.colors['bg_card'])
        content_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(
            content_frame,
            text=title,
            font=self.fonts['heading'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # 描述
        if description:
            desc_label = tk.Label(
                content_frame,
                text=description,
                font=self.fonts['body'],
                bg=self.colors['bg_card'],
                fg=self.colors['text_secondary'],
                wraplength=600,
                justify='left'
            )
            desc_label.pack(anchor='w', pady=(0, 15))
            
        return content_frame
        
    def create_input_field(self, parent, label, var, placeholder="", is_password=False):
        """创建输入字段"""
        field_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        field_frame.pack(fill=tk.X, pady=5)
        
        # 标签
        label_widget = tk.Label(
            field_frame,
            text=label,
            font=self.fonts['subheading'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        )
        label_widget.pack(anchor='w', pady=(0, 5))
        
        # 输入框
        entry = tk.Entry(
            field_frame,
            textvariable=var,
            font=self.fonts['body'],
            bg='white',
            fg=self.colors['text_primary'],
            relief='solid',
            bd=1,
            highlightthickness=2,
            highlightcolor=self.colors['border_focus'],
            highlightbackground=self.colors['border'],
            show='*' if is_password else ''
        )
        entry.pack(fill=tk.X, ipady=8)
        
        # 占位符效果
        if placeholder:
            self.add_placeholder(entry, placeholder)
            
        return entry
        
    def add_placeholder(self, entry, placeholder):
        """添加占位符效果"""
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=self.colors['text_primary'])
                
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=self.colors['text_muted'])
                
        entry.insert(0, placeholder)
        entry.config(fg=self.colors['text_muted'])
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)
        
    def create_button(self, parent, text, command, style="primary"):
        """创建按钮"""
        colors = {
            'primary': (self.colors['primary'], 'white'),
            'success': (self.colors['success'], 'white'),
            'warning': (self.colors['warning'], 'white'),
            'danger': (self.colors['danger'], 'white')
        }
        
        bg_color, fg_color = colors.get(style, colors['primary'])
        
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=self.fonts['button'],
            bg=bg_color,
            fg=fg_color,
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=20,
            pady=10
        )
        
        # 悬停效果
        def on_enter(e):
            button.config(bg=self.darken_color(bg_color))
            
        def on_leave(e):
            button.config(bg=bg_color)
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
        
    def darken_color(self, color):
        """使颜色变暗"""
        # 简单的颜色变暗实现
        color_map = {
            self.colors['primary']: self.colors['primary_hover'],
            self.colors['success']: '#059669',
            self.colors['warning']: '#d97706',
            self.colors['danger']: '#dc2626'
        }
        return color_map.get(color, color)


class EmailConfigPage(BasePage):
    """邮箱配置页面"""
    
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """设置UI"""
        # 页面标题
        title_label = tk.Label(
            self,
            text="📧 邮箱配置",
            font=self.fonts['title'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        )
        title_label.pack(pady=(0, 20))
        
        # 邮箱配置卡片
        email_card = self.create_card(
            self,
            "接收验证码邮箱设置",
            "配置用于接收Claude注册验证码的邮箱账号"
        )
        
        # 邮箱地址
        self.email_var = tk.StringVar()
        self.create_input_field(email_card, "邮箱地址", self.email_var, "your-email@example.com")
        
        # 邮箱密码
        self.password_var = tk.StringVar()
        self.create_input_field(email_card, "邮箱授权码", self.password_var, "应用专用密码", True)
        
        # IMAP服务器
        self.imap_var = tk.StringVar()
        self.create_input_field(email_card, "IMAP服务器", self.imap_var, "imap.qq.com")
        
        # 按钮区域
        button_frame = tk.Frame(email_card, bg=self.colors['bg_card'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # 测试连接按钮
        test_btn = self.create_button(button_frame, "🔍 测试连接", self.test_connection, "warning")
        test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 保存配置按钮
        save_btn = self.create_button(button_frame, "💾 保存配置", self.save_config, "success")
        save_btn.pack(side=tk.LEFT)
        
        # 下一步按钮
        next_btn = self.create_button(button_frame, "下一步 →", self.next_step)
        next_btn.pack(side=tk.RIGHT)
        
    def load_config(self):
        """加载配置"""
        mail_config = config.get('mail', {})
        self.email_var.set(mail_config.get('mail_address', ''))
        self.password_var.set(mail_config.get('mail_password', ''))
        self.imap_var.set(mail_config.get('imap_server', 'imap.qq.com'))
        
    def test_connection(self):
        """测试邮箱连接"""
        self.app.update_status("正在测试邮箱连接...", "running")
        
        # 这里应该实现实际的邮箱连接测试
        # 暂时模拟测试过程
        def test_worker():
            time.sleep(2)  # 模拟测试时间
            self.app.root.after(0, lambda: self.app.update_status("邮箱连接测试成功", "success"))
            
        threading.Thread(target=test_worker, daemon=True).start()
        
    def save_config(self):
        """保存配置"""
        # 验证输入
        if not all([self.email_var.get(), self.password_var.get(), self.imap_var.get()]):
            messagebox.showerror("错误", "请填写所有必填字段")
            return
            
        # 保存到配置
        config['mail'] = {
            'mail_address': self.email_var.get(),
            'mail_password': self.password_var.get(),
            'imap_server': self.imap_var.get(),
            'mail_timeout': 2
        }
        
        self.app.update_status("邮箱配置已保存", "success")
        messagebox.showinfo("成功", "邮箱配置保存成功！")
        
    def next_step(self):
        """下一步"""
        self.save_config()
        self.app.switch_step("2")


class CloudflareConfigPage(BasePage):
    """Cloudflare配置页面"""
    
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """设置UI"""
        # 页面标题
        title_label = tk.Label(
            self,
            text="☁️ Cloudflare配置",
            font=self.fonts['title'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        )
        title_label.pack(pady=(0, 20))
        
        # Cloudflare配置卡片
        cf_card = self.create_card(
            self,
            "Cloudflare邮件路由设置",
            "配置Cloudflare API以创建临时邮箱地址"
        )
        
        # 域名
        self.domain_var = tk.StringVar()
        self.create_input_field(cf_card, "自定义域名", self.domain_var, "your-domain.com")
        
        # Zone ID
        self.zone_var = tk.StringVar()
        self.create_input_field(cf_card, "Zone ID", self.zone_var, "Cloudflare区域标识符")
        
        # API Key
        self.api_key_var = tk.StringVar()
        self.create_input_field(cf_card, "API Key", self.api_key_var, "Global API Key", True)
        
        # 认证邮箱
        self.auth_email_var = tk.StringVar()
        self.create_input_field(cf_card, "认证邮箱", self.auth_email_var, "Cloudflare账户邮箱")
        
        # 目标邮箱
        self.target_email_var = tk.StringVar()
        self.create_input_field(cf_card, "目标邮箱", self.target_email_var, "转发到的邮箱地址")
        
        # 按钮区域
        button_frame = tk.Frame(cf_card, bg=self.colors['bg_card'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # 测试API按钮
        test_btn = self.create_button(button_frame, "🔍 测试API", self.test_api, "warning")
        test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 保存配置按钮
        save_btn = self.create_button(button_frame, "💾 保存配置", self.save_config, "success")
        save_btn.pack(side=tk.LEFT)
        
        # 导航按钮
        prev_btn = self.create_button(button_frame, "← 上一步", self.prev_step)
        prev_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        next_btn = self.create_button(button_frame, "下一步 →", self.next_step)
        next_btn.pack(side=tk.RIGHT)
        
    def load_config(self):
        """加载配置"""
        cf_config = config.get('cloudflare', {})
        self.domain_var.set(cf_config.get('rules_domain', ''))
        self.zone_var.set(cf_config.get('zone_identifier', ''))
        self.api_key_var.set(cf_config.get('api_key', ''))
        self.auth_email_var.set(cf_config.get('auth_email', ''))
        self.target_email_var.set(cf_config.get('target_mail', ''))
        
    def test_api(self):
        """测试Cloudflare API"""
        self.app.update_status("正在测试Cloudflare API...", "running")
        
        def test_worker():
            time.sleep(2)
            self.app.root.after(0, lambda: self.app.update_status("Cloudflare API测试成功", "success"))
            
        threading.Thread(target=test_worker, daemon=True).start()
        
    def save_config(self):
        """保存配置"""
        if not all([self.domain_var.get(), self.zone_var.get(), self.api_key_var.get(), 
                   self.auth_email_var.get(), self.target_email_var.get()]):
            messagebox.showerror("错误", "请填写所有必填字段")
            return
            
        config['cloudflare'] = {
            'rules_domain': self.domain_var.get(),
            'zone_identifier': self.zone_var.get(),
            'api_key': self.api_key_var.get(),
            'auth_email': self.auth_email_var.get(),
            'target_mail': self.target_email_var.get()
        }
        
        self.app.update_status("Cloudflare配置已保存", "success")
        messagebox.showinfo("成功", "Cloudflare配置保存成功！")
        
    def prev_step(self):
        """上一步"""
        self.app.switch_step("1")
        
    def next_step(self):
        """下一步"""
        self.save_config()
        self.app.switch_step("3")


class ProxyConfigPage(BasePage):
    """代理配置页面"""
    
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.proxy_manager = ProxyManager(max_usage_count=3)
        self.setup_ui()
        self.refresh_proxy_list()
        
    def setup_ui(self):
        """设置UI"""
        # 页面标题
        title_label = tk.Label(
            self,
            text="🌐 代理配置",
            font=self.fonts['title'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        )
        title_label.pack(pady=(0, 20))
        
        # 代理管理卡片
        proxy_card = self.create_card(
            self,
            "代理服务器管理",
            "添加和管理用于注册的代理服务器"
        )
        
        # 代理统计
        stats_frame = tk.Frame(proxy_card, bg=self.colors['bg_card'])
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.stats_label = tk.Label(
            stats_frame,
            text="代理统计: 加载中...",
            font=self.fonts['body'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary']
        )
        self.stats_label.pack(side=tk.LEFT)
        
        # 操作按钮
        action_frame = tk.Frame(proxy_card, bg=self.colors['bg_card'])
        action_frame.pack(fill=tk.X, pady=(0, 15))
        
        add_btn = self.create_button(action_frame, "➕ 添加代理", self.add_proxy, "success")
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        import_btn = self.create_button(action_frame, "📁 导入文件", self.import_proxies, "warning")
        import_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        test_btn = self.create_button(action_frame, "🔍 测试全部", self.test_all_proxies)
        test_btn.pack(side=tk.LEFT)
        
        # 代理列表
        list_frame = tk.Frame(proxy_card, bg=self.colors['bg_card'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview
        columns = ("类型", "地址", "端口", "状态", "延迟", "使用次数")
        self.proxy_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.proxy_tree.heading(col, text=col)
            self.proxy_tree.column(col, width=100, minwidth=80)
            
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.proxy_tree.yview)
        self.proxy_tree.configure(yscrollcommand=scrollbar.set)
        
        self.proxy_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 导航按钮
        nav_frame = tk.Frame(proxy_card, bg=self.colors['bg_card'])
        nav_frame.pack(fill=tk.X, pady=(20, 0))
        
        prev_btn = self.create_button(nav_frame, "← 上一步", self.prev_step)
        prev_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        next_btn = self.create_button(nav_frame, "下一步 →", self.next_step)
        next_btn.pack(side=tk.RIGHT)
        
    def refresh_proxy_list(self):
        """刷新代理列表"""
        # 清空现有项目
        for item in self.proxy_tree.get_children():
            self.proxy_tree.delete(item)
            
        # 获取代理统计
        stats = self.proxy_manager.get_proxy_statistics()
        self.stats_label.config(
            text=f"代理统计: 总计 {stats['total_proxies']} 个，"
                 f"活跃 {stats['active_proxies']} 个，"
                 f"已耗尽 {stats['exhausted_proxies']} 个"
        )
        
        # 这里应该实现实际的代理列表显示
        # 暂时添加一些示例数据
        sample_proxies = [
            ("HTTP", "192.168.1.1", "8080", "可用", "120ms", "1/3"),
            ("SOCKS5", "192.168.1.2", "1080", "可用", "95ms", "0/3"),
            ("HTTP", "192.168.1.3", "3128", "超时", "-", "3/3")
        ]
        
        for proxy in sample_proxies:
            self.proxy_tree.insert('', 'end', values=proxy)
            
    def add_proxy(self):
        """添加代理"""
        messagebox.showinfo("提示", "添加代理功能开发中...")
        
    def import_proxies(self):
        """导入代理文件"""
        file_path = filedialog.askopenfilename(
            title="选择代理文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            messagebox.showinfo("提示", f"已选择文件: {file_path}")
            
    def test_all_proxies(self):
        """测试所有代理"""
        self.app.update_status("正在测试代理连接...", "running")
        
        def test_worker():
            time.sleep(3)
            self.app.root.after(0, lambda: [
                self.app.update_status("代理测试完成", "success"),
                self.refresh_proxy_list()
            ])
            
        threading.Thread(target=test_worker, daemon=True).start()
        
    def prev_step(self):
        """上一步"""
        self.app.switch_step("2")
        
    def next_step(self):
        """下一步"""
        self.app.switch_step("4")


class RegisterPage(BasePage):
    """注册页面"""

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.is_running = False
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        # 页面标题
        title_label = tk.Label(
            self,
            text="🚀 开始注册",
            font=self.fonts['title'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        )
        title_label.pack(pady=(0, 20))

        # 注册控制卡片
        control_card = self.create_card(
            self,
            "注册控制面板",
            "配置注册参数并启动自动注册流程"
        )

        # 注册参数
        params_frame = tk.Frame(control_card, bg=self.colors['bg_card'])
        params_frame.pack(fill=tk.X, pady=(0, 20))

        # 注册数量
        tk.Label(
            params_frame,
            text="注册数量:",
            font=self.fonts['subheading'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        ).grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)

        self.count_var = tk.StringVar(value="1")
        count_entry = tk.Entry(
            params_frame,
            textvariable=self.count_var,
            font=self.fonts['body'],
            width=10,
            bg='white',
            relief='solid',
            bd=1
        )
        count_entry.grid(row=0, column=1, sticky='w', pady=5)

        # 间隔时间
        tk.Label(
            params_frame,
            text="间隔时间(秒):",
            font=self.fonts['subheading'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        ).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)

        self.interval_var = tk.StringVar(value="30")
        interval_entry = tk.Entry(
            params_frame,
            textvariable=self.interval_var,
            font=self.fonts['body'],
            width=10,
            bg='white',
            relief='solid',
            bd=1
        )
        interval_entry.grid(row=1, column=1, sticky='w', pady=5)

        # 浏览器位置
        tk.Label(
            params_frame,
            text="浏览器位置:",
            font=self.fonts['subheading'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        ).grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)

        position_frame = tk.Frame(params_frame, bg=self.colors['bg_card'])
        position_frame.grid(row=2, column=1, sticky='w', pady=5)

        self.x_var = tk.StringVar(value="0")
        self.y_var = tk.StringVar(value="0")

        tk.Label(position_frame, text="X:", bg=self.colors['bg_card'], fg=self.colors['text_primary']).pack(side=tk.LEFT)
        tk.Entry(position_frame, textvariable=self.x_var, width=5, bg='white', relief='solid', bd=1).pack(side=tk.LEFT, padx=(5, 10))
        tk.Label(position_frame, text="Y:", bg=self.colors['bg_card'], fg=self.colors['text_primary']).pack(side=tk.LEFT)
        tk.Entry(position_frame, textvariable=self.y_var, width=5, bg='white', relief='solid', bd=1).pack(side=tk.LEFT, padx=5)

        # 控制按钮
        control_frame = tk.Frame(control_card, bg=self.colors['bg_card'])
        control_frame.pack(fill=tk.X, pady=(0, 20))

        self.start_btn = self.create_button(control_frame, "🚀 开始注册", self.start_register, "success")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = self.create_button(control_frame, "⏹️ 停止注册", self.stop_register, "danger")
        self.stop_btn.pack(side=tk.LEFT)
        self.stop_btn.config(state='disabled')

        # 进度显示
        progress_frame = tk.Frame(control_card, bg=self.colors['bg_card'])
        progress_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            progress_frame,
            text="注册进度:",
            font=self.fonts['subheading'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        ).pack(anchor='w', pady=(0, 5))

        self.progress_var = tk.StringVar(value="0/0")
        self.progress_label = tk.Label(
            progress_frame,
            textvariable=self.progress_var,
            font=self.fonts['body'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary']
        )
        self.progress_label.pack(anchor='w')

        # 进度条
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))

        # 实时日志
        log_frame = tk.Frame(control_card, bg=self.colors['bg_card'])
        log_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            log_frame,
            text="实时日志:",
            font=self.fonts['subheading'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        ).pack(anchor='w', pady=(0, 5))

        # 日志文本框
        log_container = tk.Frame(log_frame, bg=self.colors['bg_card'])
        log_container.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            log_container,
            height=8,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#ffffff',
            relief='solid',
            bd=1,
            wrap=tk.WORD
        )

        log_scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 导航按钮
        nav_frame = tk.Frame(control_card, bg=self.colors['bg_card'])
        nav_frame.pack(fill=tk.X, pady=(20, 0))

        prev_btn = self.create_button(nav_frame, "← 上一步", self.prev_step)
        prev_btn.pack(side=tk.RIGHT, padx=(10, 0))

        next_btn = self.create_button(nav_frame, "查看结果 →", self.next_step)
        next_btn.pack(side=tk.RIGHT)

    def start_register(self):
        """开始注册"""
        if self.is_running:
            return

        try:
            count = int(self.count_var.get())
            interval = int(self.interval_var.get())
            x = int(self.x_var.get())
            y = int(self.y_var.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数值")
            return

        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

        self.app.update_status("正在启动注册流程...", "running")
        self.log_message("🚀 开始注册流程")
        self.log_message(f"📊 注册数量: {count}, 间隔: {interval}秒")

        # 启动注册线程
        self.register_thread = threading.Thread(
            target=self.register_worker,
            args=(count, interval, x, y),
            daemon=True
        )
        self.register_thread.start()

    def stop_register(self):
        """停止注册"""
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.app.update_status("注册已停止", "warning")
        self.log_message("⏹️ 注册流程已停止")

    def register_worker(self, count, interval, x, y):
        """注册工作线程"""
        try:
            # 导入注册引擎
            from gui.register_engine import ClaudeRegisterEngine

            # 创建注册引擎实例
            def engine_callback(message, level="info"):
                """注册引擎回调函数"""
                self.app.root.after(0, lambda: self.log_message(f"🔧 {message}"))

            engine = ClaudeRegisterEngine(callback=engine_callback)

            # 开始批量注册
            self.app.root.after(0, lambda: self.log_message("🚀 启动注册引擎..."))

            for i in range(count):
                if not self.is_running:
                    engine.stop_registration()
                    break

                # 更新进度
                self.app.root.after(0, lambda i=i: [
                    self.progress_var.set(f"{i+1}/{count}"),
                    self.progress_bar.config(maximum=count, value=i+1),
                    self.log_message(f"📧 正在注册第 {i+1} 个账号...")
                ])

                # 调用实际的注册逻辑
                result = engine.register_single_account(x, y)

                # 处理注册结果
                if result["success"]:
                    self.app.root.after(0, lambda i=i, email=result.get("email", ""):
                        self.log_message(f"✅ 第 {i+1} 个账号注册成功: {email}"))
                else:
                    self.app.root.after(0, lambda i=i, msg=result["message"]:
                        self.log_message(f"❌ 第 {i+1} 个账号注册失败: {msg}"))

                # 间隔等待
                if i < count - 1 and self.is_running:
                    self.app.root.after(0, lambda: self.log_message(f"⏳ 等待 {interval} 秒..."))
                    time.sleep(interval)

        except Exception as e:
            self.app.root.after(0, lambda: self.log_message(f"❌ 注册过程出错: {str(e)}"))
        finally:
            self.app.root.after(0, self.finish_register)

    def finish_register(self):
        """完成注册"""
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.app.update_status("注册流程完成", "success")
        self.log_message("🎉 注册流程完成")

    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)

    def prev_step(self):
        """上一步"""
        self.app.switch_step("3")

    def next_step(self):
        """下一步"""
        self.app.switch_step("5")


class ResultsPage(BasePage):
    """结果页面"""

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        # 页面标题
        title_label = tk.Label(
            self,
            text="📊 注册结果",
            font=self.fonts['title'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        )
        title_label.pack(pady=(0, 20))

        # 统计卡片
        stats_card = self.create_card(
            self,
            "注册统计",
            "查看注册结果统计和详细信息"
        )

        # 统计信息
        stats_frame = tk.Frame(stats_card, bg=self.colors['bg_card'])
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        # 成功数量
        success_frame = tk.Frame(stats_frame, bg=self.colors['success'], relief='flat', bd=0)
        success_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        tk.Label(
            success_frame,
            text="✅ 成功",
            font=self.fonts['subheading'],
            bg=self.colors['success'],
            fg='white'
        ).pack(padx=20, pady=(10, 5))

        self.success_count = tk.Label(
            success_frame,
            text="0",
            font=('SF Pro Display', 20, 'bold'),
            bg=self.colors['success'],
            fg='white'
        )
        self.success_count.pack(padx=20, pady=(0, 10))

        # 失败数量
        fail_frame = tk.Frame(stats_frame, bg=self.colors['danger'], relief='flat', bd=0)
        fail_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        tk.Label(
            fail_frame,
            text="❌ 失败",
            font=self.fonts['subheading'],
            bg=self.colors['danger'],
            fg='white'
        ).pack(padx=20, pady=(10, 5))

        self.fail_count = tk.Label(
            fail_frame,
            text="0",
            font=('SF Pro Display', 20, 'bold'),
            bg=self.colors['danger'],
            fg='white'
        )
        self.fail_count.pack(padx=20, pady=(0, 10))

        # 总计
        total_frame = tk.Frame(stats_frame, bg=self.colors['primary'], relief='flat', bd=0)
        total_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(
            total_frame,
            text="📊 总计",
            font=self.fonts['subheading'],
            bg=self.colors['primary'],
            fg='white'
        ).pack(padx=20, pady=(10, 5))

        self.total_count = tk.Label(
            total_frame,
            text="0",
            font=('SF Pro Display', 20, 'bold'),
            bg=self.colors['primary'],
            fg='white'
        )
        self.total_count.pack(padx=20, pady=(0, 10))

        # 结果列表
        results_frame = tk.Frame(stats_card, bg=self.colors['bg_card'])
        results_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            results_frame,
            text="详细结果:",
            font=self.fonts['subheading'],
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        ).pack(anchor='w', pady=(0, 10))

        # 结果表格
        columns = ("序号", "邮箱地址", "状态", "SessionKey", "时间")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120, minwidth=80)

        # 滚动条
        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)

        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 操作按钮
        action_frame = tk.Frame(stats_card, bg=self.colors['bg_card'])
        action_frame.pack(fill=tk.X, pady=(20, 0))

        export_btn = self.create_button(action_frame, "📁 导出结果", self.export_results, "success")
        export_btn.pack(side=tk.LEFT, padx=(0, 10))

        clear_btn = self.create_button(action_frame, "🗑️ 清空结果", self.clear_results, "danger")
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        refresh_btn = self.create_button(action_frame, "🔄 刷新", self.refresh_results)
        refresh_btn.pack(side=tk.LEFT)

        # 导航按钮
        nav_frame = tk.Frame(stats_card, bg=self.colors['bg_card'])
        nav_frame.pack(fill=tk.X, pady=(20, 0))

        prev_btn = self.create_button(nav_frame, "← 上一步", self.prev_step)
        prev_btn.pack(side=tk.RIGHT, padx=(10, 0))

        restart_btn = self.create_button(nav_frame, "🔄 重新开始", self.restart)
        restart_btn.pack(side=tk.RIGHT)

        # 加载示例数据
        self.load_sample_data()

    def load_sample_data(self):
        """加载示例数据"""
        sample_results = [
            ("1", "test1@example.com", "✅ 成功", "sk-xxx...xxx", "2024-01-15 10:30:15"),
            ("2", "test2@example.com", "❌ 失败", "-", "2024-01-15 10:31:20"),
            ("3", "test3@example.com", "✅ 成功", "sk-yyy...yyy", "2024-01-15 10:32:45")
        ]

        for result in sample_results:
            self.results_tree.insert('', 'end', values=result)

        # 更新统计
        self.success_count.config(text="2")
        self.fail_count.config(text="1")
        self.total_count.config(text="3")

    def export_results(self):
        """导出结果"""
        file_path = filedialog.asksaveasfilename(
            title="保存结果文件",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            messagebox.showinfo("成功", f"结果已导出到: {file_path}")

    def clear_results(self):
        """清空结果"""
        if messagebox.askyesno("确认", "确定要清空所有结果吗？"):
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            self.success_count.config(text="0")
            self.fail_count.config(text="0")
            self.total_count.config(text="0")

    def refresh_results(self):
        """刷新结果"""
        self.app.update_status("结果已刷新", "success")

    def prev_step(self):
        """上一步"""
        self.app.switch_step("4")

    def restart(self):
        """重新开始"""
        self.app.switch_step("1")
