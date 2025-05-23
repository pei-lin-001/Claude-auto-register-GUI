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


class MainApplication:
    """主应用程序类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_menu()
        self.create_main_interface()
        self.create_status_bar()
        self.current_tab = "dashboard"
        
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
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding_medium'], pady=SIZES['padding_medium'])
        
        # 创建标签页框架
        self.create_tab_bar()
        
        # 创建内容区域
        self.content_frame = tk.Frame(
            self.main_frame, 
            bg=COLORS['bg_primary'], 
            relief='flat', 
            bd=0,
            highlightbackground=COLORS['border_light'],
            highlightthickness=1
        )
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(SIZES['padding_small'], 0))
        
        # 初始化各个页面
        self.pages = {}
        self.init_pages()
        
        # 显示默认页面
        self.switch_tab("dashboard")
        
    def create_tab_bar(self):
        """创建标签栏"""
        self.tab_frame = tk.Frame(
            self.main_frame, 
            bg=COLORS['bg_secondary'], 
            height=50,
            relief='flat',
            bd=0
        )
        self.tab_frame.pack(fill=tk.X, pady=(0, SIZES['padding_small']))
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
            btn.pack(side=tk.LEFT, padx=(0, SIZES['padding_xs']))
            self.tab_buttons[tab_id] = btn
            
    def init_pages(self):
        """初始化各个页面"""
        # 仪表板页面
        self.pages["dashboard"] = DashboardFrame(self.content_frame)
        
        # 配置设置页面
        self.pages["config"] = ConfigFrame(self.content_frame)
        
        # 其他页面暂时用占位符
        for page_id in ["proxy", "batch", "logs"]:
            placeholder = tk.Frame(self.content_frame, bg=COLORS['bg_primary'])
            
            # 创建居中容器
            center_frame = tk.Frame(placeholder, bg=COLORS['bg_primary'])
            center_frame.pack(expand=True, fill=tk.BOTH)
            
            # 图标和文字
            icon_label = tk.Label(
                center_frame,
                text=ICONS.get(page_id, '🔧'),
                font=(FONTS['title'][0], 48),
                bg=COLORS['bg_primary'],
                fg=COLORS['text_muted']
            )
            icon_label.pack(expand=True, pady=(0, SIZES['padding_medium']))
            
            text_label = tk.Label(
                center_frame,
                text=f"{page_id.title()} 页面正在开发中...",
                font=FONTS['heading'],
                bg=COLORS['bg_primary'],
                fg=COLORS['text_secondary']
            )
            text_label.pack(expand=True, pady=(0, SIZES['padding_xl']))
            
            self.pages[page_id] = placeholder
            
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
        
        # 状态标签
        self.status_label = tk.Label(
            self.status_frame,
            text="就绪",
            font=FONTS['caption'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=SIZES['padding_medium'], pady=SIZES['padding_small'])
        
        # 分隔符
        separator = tk.Label(
            self.status_frame,
            text="•",
            font=FONTS['caption'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_muted']
        )
        separator.pack(side=tk.LEFT, padx=SIZES['padding_small'])
        
        # 代理状态
        self.proxy_status_label = tk.Label(
            self.status_frame,
            text="代理: 未检查",
            font=FONTS['caption'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary']
        )
        self.proxy_status_label.pack(side=tk.LEFT, padx=SIZES['padding_small'], pady=SIZES['padding_small'])
        
        # 时间标签
        self.time_label = tk.Label(
            self.status_frame,
            text="",
            font=FONTS['caption'],
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_muted']
        )
        self.time_label.pack(side=tk.RIGHT, padx=SIZES['padding_medium'], pady=SIZES['padding_small'])
        
        # 更新时间
        self.update_time()
        
    def update_status(self, message):
        """更新状态栏消息"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
        
    def update_proxy_status(self, active_count, total_count):
        """更新代理状态"""
        if hasattr(self, 'proxy_status_label'):
            self.proxy_status_label.config(text=f"代理: {active_count}/{total_count}可用")
        
    def update_time(self):
        """更新时间显示"""
        import time
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
        
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


if __name__ == "__main__":
    app = MainApplication()
    app.run() 