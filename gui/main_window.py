"""
主窗口模块

实现应用程序的主窗口界面，包括菜单栏、标签页和状态栏。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.resources.styles import COLORS, FONTS, SIZES, ICONS, STYLES
from gui.components.dashboard import DashboardFrame
from gui.components.config_panel import ConfigFrame
from gui.components.proxy_manager import ProxyManagerFrame
from gui.components.batch_register import BatchRegisterFrame
from gui.components.log_viewer import LogViewerFrame


class MainApplication:
    """主应用程序类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.current_tab = "dashboard"  # 提前初始化
        self.setup_window()
        self.create_menu()
        self.create_main_interface()
        self.create_status_bar()
        
    def setup_window(self):
        """设置主窗口属性"""
        self.root.title("Claude 自动注册工具 v1.0 - 现代化界面")
        self.root.geometry(f"{SIZES['window_width']}x{SIZES['window_height']}")
        self.root.minsize(SIZES['window_min_width'], SIZES['window_min_height'])
        
        # 设置窗口背景
        self.root.configure(bg=COLORS['bg_secondary'])
        
        # 设置窗口图标和配置
        try:
            # 如果有图标文件，可以在这里设置
            # self.root.iconbitmap('path/to/icon.ico')
            pass
        except:
            pass
            
        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 绑定窗口大小变化事件
        self.root.bind('<Configure>', self.on_window_resize)
        
        # 居中窗口
        self.center_window()
        
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_menu(self):
        """创建菜单栏"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # 文件菜单
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入配置", command=self.import_config)
        file_menu.add_command(label="导出配置", command=self.export_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 工具菜单
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="代理测试", command=self.test_proxies)
        tools_menu.add_command(label="邮箱测试", command=self.test_email)
        tools_menu.add_command(label="清理日志", command=self.clear_logs)
        
        # 视图菜单
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="刷新", command=self.refresh_current_tab)
        view_menu.add_separator()
        view_menu.add_command(label="仪表板", command=lambda: self.switch_tab("dashboard"))
        view_menu.add_command(label="代理管理", command=lambda: self.switch_tab("proxy"))
        view_menu.add_command(label="配置设置", command=lambda: self.switch_tab("config"))
        view_menu.add_command(label="批量注册", command=lambda: self.switch_tab("batch"))
        view_menu.add_command(label="日志查看", command=lambda: self.switch_tab("logs"))
        
        # 帮助菜单
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
        
    def create_main_interface(self):
        """创建主界面"""
        # 创建主框架
        self.main_frame = tk.Frame(self.root, **STYLES['main_frame'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_large'], pady=SIZES['padding_large'])
        
        # 创建标签页框架
        self.create_tab_bar()
        
        # 创建内容区域
        self.content_frame = tk.Frame(
            self.main_frame, 
            **STYLES['card_frame_elevated']
        )
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(SIZES['padding_medium'], 0))
        
        # 初始化各个页面
        self.pages = {}
        self.init_pages()
        
        # 显示默认页面
        self.switch_tab("dashboard")
        
    def create_tab_bar(self):
        """创建标签栏"""
        # 创建标签栏容器
        tab_container = tk.Frame(
            self.main_frame, 
            bg=COLORS['bg_primary'],
            relief='flat',
            bd=0,
            highlightbackground=COLORS['border_light'],
            highlightthickness=1
        )
        tab_container.pack(fill=tk.X, pady=(0, SIZES['padding_medium']))
        
        # 创建标签栏框架
        self.tab_frame = tk.Frame(
            tab_container, 
            bg=COLORS['bg_primary'], 
            height=60,
            relief='flat',
            bd=0
        )
        self.tab_frame.pack(fill=tk.X, padx=SIZES['padding_large'], pady=SIZES['padding_medium'])
        self.tab_frame.pack_propagate(False)
        
        # 标签按钮配置
        self.tabs = [
            ("dashboard", f"{ICONS['dashboard']} 仪表板"),
            ("proxy", f"{ICONS['proxy']} 代理管理"),
            ("config", f"{ICONS['config']} 配置设置"),
            ("batch", f"{ICONS['batch']} 批量注册"),
            ("logs", f"{ICONS['logs']} 日志查看"),
        ]
        
        self.tab_buttons = {}
        
        for i, (tab_id, tab_text) in enumerate(self.tabs):
            btn = tk.Button(
                self.tab_frame,
                text=tab_text,
                **STYLES['tab_button_inactive'],
                command=lambda t=tab_id: self.switch_tab(t)
            )
            btn.pack(side=tk.LEFT, padx=(0, SIZES['padding_small']))
            self.tab_buttons[tab_id] = btn
            
        # 添加右侧工具按钮
        self.create_toolbar_buttons()
        
    def init_pages(self):
        """初始化各个页面"""
        # 仪表板页面
        self.pages["dashboard"] = DashboardFrame(self.content_frame)
        
        # 代理管理页面
        self.pages["proxy"] = ProxyManagerFrame(self.content_frame)
        
        # 配置设置页面
        self.pages["config"] = ConfigFrame(self.content_frame)
        
        # 批量注册页面
        self.pages["batch"] = BatchRegisterFrame(self.content_frame)
        
        # 日志查看页面
        self.pages["logs"] = LogViewerFrame(self.content_frame)
        
    def switch_tab(self, tab_id):
        """切换标签页"""
        if tab_id not in self.pages:
            return
            
        # 隐藏当前页面
        if hasattr(self, 'current_page') and self.current_page:
            self.current_page.pack_forget()
            
        # 更新标签按钮样式
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.config(**STYLES['tab_button_active'])
            else:
                btn.config(**STYLES['tab_button_inactive'])
                
        # 显示新页面
        self.current_page = self.pages[tab_id]
        self.current_page.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_large'], pady=SIZES['padding_large'])
        self.current_tab = tab_id
        
        # 更新状态栏（只有在状态栏已创建时才更新）
        if hasattr(self, 'status_label'):
            self.update_status(f"当前页面: {dict(self.tabs)[tab_id]}")
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_frame = tk.Frame(self.root, **STYLES['status_bar'])
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 左侧状态信息
        left_frame = tk.Frame(self.status_frame, bg=COLORS['bg_secondary'])
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 主状态标签
        self.status_label = tk.Label(
            left_frame,
            text="🚀 就绪",
            font=FONTS['caption'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=SIZES['padding_medium'], pady=SIZES['padding_small'])
        
        # 分隔符
        separator1 = tk.Label(
            left_frame,
            text="•",
            font=FONTS['caption'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_muted']
        )
        separator1.pack(side=tk.LEFT, padx=SIZES['padding_xs'])
        
        # 代理状态
        self.proxy_status_label = tk.Label(
            left_frame,
            text="🌐 代理: 检查中...",
            font=FONTS['caption'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary']
        )
        self.proxy_status_label.pack(side=tk.LEFT, padx=SIZES['padding_small'], pady=SIZES['padding_small'])
        
        # 分隔符2
        separator2 = tk.Label(
            left_frame,
            text="•",
            font=FONTS['caption'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_muted']
        )
        separator2.pack(side=tk.LEFT, padx=SIZES['padding_xs'])
        
        # 内存使用情况
        self.memory_label = tk.Label(
            left_frame,
            text="💾 内存: 0MB",
            font=FONTS['caption'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary']
        )
        self.memory_label.pack(side=tk.LEFT, padx=SIZES['padding_small'], pady=SIZES['padding_small'])
        
        # 右侧信息
        right_frame = tk.Frame(self.status_frame, bg=COLORS['bg_secondary'])
        right_frame.pack(side=tk.RIGHT)
        
        # 版本信息
        version_label = tk.Label(
            right_frame,
            text="v1.0.0",
            font=FONTS['caption'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_muted']
        )
        version_label.pack(side=tk.RIGHT, padx=SIZES['padding_medium'], pady=SIZES['padding_small'])
        
        # 分隔符3
        separator3 = tk.Label(
            right_frame,
            text="•",
            font=FONTS['caption'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_muted']
        )
        separator3.pack(side=tk.RIGHT, padx=SIZES['padding_xs'])
        
        # 时间标签
        self.time_label = tk.Label(
            right_frame,
            text="",
            font=FONTS['caption'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_muted']
        )
        self.time_label.pack(side=tk.RIGHT, padx=SIZES['padding_small'], pady=SIZES['padding_small'])
        
        # 启动定时更新
        self.update_time()
        self.update_memory_usage()
        
    def update_status(self, message):
        """更新状态栏消息"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
        
    def update_proxy_status(self, active_count, total_count):
        """更新代理状态"""
        if hasattr(self, 'proxy_status_label'):
            self.proxy_status_label.config(text=f"🌐 代理: {active_count}/{total_count}可用")
        
    def update_time(self):
        """更新时间显示"""
        import time
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
        
    def update_memory_usage(self):
        """更新内存使用情况"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.memory_label.config(text=f"💾 内存: {memory_mb:.1f}MB")
        except ImportError:
            # 如果没有psutil库，显示简单信息
            import sys
            memory_mb = sys.getsizeof(self.root) / 1024 / 1024
            self.memory_label.config(text=f"💾 内存: {memory_mb:.1f}MB")
        except Exception:
            self.memory_label.config(text="💾 内存: N/A")
            
        # 每30秒更新一次内存信息
        self.root.after(30000, self.update_memory_usage)
        
    def refresh_current_tab(self):
        """刷新当前标签页"""
        if hasattr(self.pages[self.current_tab], 'refresh'):
            self.pages[self.current_tab].refresh()
        if hasattr(self, 'status_label'):
            self.update_status("页面已刷新")
        
    # 菜单回调函数
    def import_config(self):
        """导入配置"""
        messagebox.showinfo("功能提示", "导入配置功能开发中...")
        
    def export_config(self):
        """导出配置"""
        messagebox.showinfo("功能提示", "导出配置功能开发中...")
        
    def test_proxies(self):
        """测试代理"""
        messagebox.showinfo("功能提示", "代理测试功能开发中...")
        
    def test_email(self):
        """测试邮箱"""
        messagebox.showinfo("功能提示", "邮箱测试功能开发中...")
        
    def clear_logs(self):
        """清理日志"""
        result = messagebox.askyesno("确认", "确定要清理所有日志吗？")
        if result:
            messagebox.showinfo("提示", "日志清理功能开发中...")
            
    def show_help(self):
        """显示帮助"""
        help_text = """
Claude 自动注册工具 使用说明

1. 配置设置：在"配置设置"页面设置邮箱和Cloudflare参数
2. 代理管理：在"代理管理"页面添加和管理代理服务器
3. 批量注册：在"批量注册"页面设置注册参数并开始注册
4. 日志查看：在"日志查看"页面监控运行状态

更多详情请查看 README.md 文件。
        """
        messagebox.showinfo("使用说明", help_text)
        
    def show_about(self):
        """显示关于"""
        about_text = """
Claude 自动注册工具 v1.0

这是一个用于自动化注册Claude AI账号的工具。

开发团队：Claude Auto Register Team
技术栈：Python + tkinter
许可证：MIT License

感谢您的使用！
        """
        messagebox.showinfo("关于", about_text)
        
    def on_closing(self):
        """窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.root.destroy()
            
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

    def create_toolbar_buttons(self):
        """创建工具栏按钮"""
        # 右侧工具栏框架
        toolbar_frame = tk.Frame(self.tab_frame, bg=COLORS['bg_primary'])
        toolbar_frame.pack(side=tk.RIGHT)
        
        # 刷新按钮
        refresh_btn = tk.Button(
            toolbar_frame,
            text=f"{ICONS['refresh']}",
            **STYLES['button_icon'],
            command=self.refresh_current_tab
        )
        refresh_btn.pack(side=tk.RIGHT, padx=(SIZES['padding_xs'], 0))
        
        # 设置按钮
        settings_btn = tk.Button(
            toolbar_frame,
            text=f"{ICONS['settings']}",
            **STYLES['button_icon'],
            command=lambda: self.switch_tab("config")
        )
        settings_btn.pack(side=tk.RIGHT, padx=(SIZES['padding_xs'], 0))
        
        # 帮助按钮
        help_btn = tk.Button(
            toolbar_frame,
            text=f"{ICONS['help']}",
            **STYLES['button_icon'],
            command=self.show_help
        )
        help_btn.pack(side=tk.RIGHT, padx=(SIZES['padding_xs'], 0))

    def on_window_resize(self, event):
        """处理窗口大小变化"""
        # 只处理主窗口的resize事件
        if event.widget == self.root:
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            # 根据窗口大小调整布局
            self.adjust_layout_for_size(width, height)
            
    def adjust_layout_for_size(self, width, height):
        """根据窗口大小调整布局"""
        # 确保必要的属性已经初始化
        if not hasattr(self, 'tab_buttons') or not hasattr(self, 'main_frame'):
            return
            
        # 小屏幕模式 (宽度 < 1200px)
        if width < 1200:
            # 调整标签栏字体大小
            for tab_id, btn in self.tab_buttons.items():
                btn.config(font=FONTS['small'])
                
            # 调整边距
            self.main_frame.config(padx=SIZES['padding_medium'], pady=SIZES['padding_medium'])
        else:
            # 正常模式
            for tab_id, btn in self.tab_buttons.items():
                if tab_id == self.current_tab:
                    btn.config(font=FONTS['button'])
                else:
                    btn.config(font=FONTS['body'])
                    
            # 恢复正常边距
            self.main_frame.config(padx=SIZES['padding_large'], pady=SIZES['padding_large'])


if __name__ == "__main__":
    app = MainApplication()
    app.run() 