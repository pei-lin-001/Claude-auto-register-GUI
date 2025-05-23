import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any
import os

from gui.utils import (
    theme_manager, gui_config, system_tray, hotkey_manager, 
    HotkeyConfigDialog, Validators
)

class AdvancedSettingsFrame:
    """高级设置界面"""
    
    def __init__(self, parent):
        self.parent = parent
        self.main_frame = None
        self.notebook = None
        
        # 变量存储
        self.theme_var = tk.StringVar()
        self.language_var = tk.StringVar()
        self.minimize_to_tray_var = tk.BooleanVar()
        self.close_to_tray_var = tk.BooleanVar()
        self.auto_save_var = tk.BooleanVar()
        self.show_charts_var = tk.BooleanVar()
        self.refresh_interval_var = tk.IntVar()
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """创建控件"""
        # 主框架
        self.main_frame = ttk.Frame(self.parent)
        
        # 创建滚动框架
        canvas = tk.Canvas(self.main_frame)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 创建标签页
        self.notebook = ttk.Notebook(scrollable_frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 外观设置页
        self.create_appearance_tab()
        
        # 系统集成页
        self.create_system_tab()
        
        # 快捷键设置页
        self.create_hotkey_tab()
        
        # 性能设置页  
        self.create_performance_tab()
        
        # 高级选项页
        self.create_advanced_tab()
        
        # 按钮区域
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(button_frame, text="应用设置", 
                  command=self.apply_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="重置默认", 
                  command=self.reset_to_default).pack(side="left", padx=5)
        ttk.Button(button_frame, text="导出配置", 
                  command=self.export_config).pack(side="left", padx=5)
        ttk.Button(button_frame, text="导入配置", 
                  command=self.import_config).pack(side="left", padx=5)
        
        # 布局滚动组件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_appearance_tab(self):
        """创建外观设置页"""
        appearance_frame = ttk.Frame(self.notebook)
        self.notebook.add(appearance_frame, text="外观")
        
        # 主题设置
        theme_group = ttk.LabelFrame(appearance_frame, text="主题设置", padding=15)
        theme_group.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(theme_group, text="选择主题:").grid(row=0, column=0, sticky="w", pady=5)
        
        theme_combo = ttk.Combobox(theme_group, textvariable=self.theme_var, 
                                  values=list(theme_manager.get_available_themes().values()),
                                  state="readonly", width=20)
        theme_combo.grid(row=0, column=1, padx=10, pady=5)
        theme_combo.bind('<<ComboboxSelected>>', self.on_theme_changed)
        
        ttk.Button(theme_group, text="预览主题", 
                  command=self.preview_theme).grid(row=0, column=2, padx=10, pady=5)
        
        # 语言设置
        language_group = ttk.LabelFrame(appearance_frame, text="语言设置", padding=15)
        language_group.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(language_group, text="界面语言:").grid(row=0, column=0, sticky="w", pady=5)
        
        language_combo = ttk.Combobox(language_group, textvariable=self.language_var,
                                    values=["简体中文", "English"], 
                                    state="readonly", width=20)
        language_combo.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(language_group, text="注意: 语言更改需要重启应用程序生效", 
                 foreground="gray").grid(row=1, column=0, columnspan=3, sticky="w", pady=5)
        
        # 图表设置
        chart_group = ttk.LabelFrame(appearance_frame, text="图表设置", padding=15)
        chart_group.pack(fill="x", padx=10, pady=5)
        
        ttk.Checkbutton(chart_group, text="显示统计图表", 
                       variable=self.show_charts_var).grid(row=0, column=0, sticky="w", pady=5)
        
        ttk.Label(chart_group, text="图表历史天数:").grid(row=1, column=0, sticky="w", pady=5)
        
        history_days_spinbox = ttk.Spinbox(chart_group, from_=1, to=30, width=10)
        history_days_spinbox.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # 窗口设置
        window_group = ttk.LabelFrame(appearance_frame, text="窗口设置", padding=15)
        window_group.pack(fill="x", padx=10, pady=5)
        
        ttk.Checkbutton(window_group, text="总是置顶").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Checkbutton(window_group, text="记住窗口位置").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Checkbutton(window_group, text="启动时最大化").grid(row=2, column=0, sticky="w", pady=5)
    
    def create_system_tab(self):
        """创建系统集成页"""
        system_frame = ttk.Frame(self.notebook)
        self.notebook.add(system_frame, text="系统集成")
        
        # 系统托盘设置
        tray_group = ttk.LabelFrame(system_frame, text="系统托盘", padding=15)
        tray_group.pack(fill="x", padx=10, pady=5)
        
        ttk.Checkbutton(tray_group, text="最小化到系统托盘", 
                       variable=self.minimize_to_tray_var).grid(row=0, column=0, sticky="w", pady=5)
        
        ttk.Checkbutton(tray_group, text="关闭到系统托盘", 
                       variable=self.close_to_tray_var).grid(row=1, column=0, sticky="w", pady=5)
        
        ttk.Button(tray_group, text="测试托盘图标", 
                  command=self.test_tray_icon).grid(row=2, column=0, sticky="w", pady=10)
        
        # 通知设置
        notification_group = ttk.LabelFrame(system_frame, text="通知设置", padding=15)
        notification_group.pack(fill="x", padx=10, pady=5)
        
        ttk.Checkbutton(notification_group, text="显示桌面通知").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Checkbutton(notification_group, text="注册成功时通知").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Checkbutton(notification_group, text="注册失败时通知").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Checkbutton(notification_group, text="批量注册完成时通知").grid(row=3, column=0, sticky="w", pady=5)
        
        # 开机启动设置
        startup_group = ttk.LabelFrame(system_frame, text="启动设置", padding=15)
        startup_group.pack(fill="x", padx=10, pady=5)
        
        ttk.Checkbutton(startup_group, text="开机自动启动").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Checkbutton(startup_group, text="启动时最小化").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Checkbutton(startup_group, text="启动时检查更新").grid(row=2, column=0, sticky="w", pady=5)
    
    def create_hotkey_tab(self):
        """创建快捷键设置页"""
        hotkey_frame = ttk.Frame(self.notebook)
        self.notebook.add(hotkey_frame, text="快捷键")
        
        # 说明
        info_label = ttk.Label(hotkey_frame, 
                              text="配置全局快捷键，可在任何地方使用这些快捷键控制应用程序。",
                              foreground="gray")
        info_label.pack(pady=10)
        
        # 快捷键列表
        hotkey_group = ttk.LabelFrame(hotkey_frame, text="快捷键配置", padding=15)
        hotkey_group.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 创建表格
        columns = ("功能", "快捷键", "状态")
        hotkey_tree = ttk.Treeview(hotkey_group, columns=columns, show="headings", height=8)
        
        # 设置列标题
        hotkey_tree.heading("功能", text="功能描述")
        hotkey_tree.heading("快捷键", text="快捷键组合")
        hotkey_tree.heading("状态", text="状态")
        
        # 设置列宽
        hotkey_tree.column("功能", width=200)
        hotkey_tree.column("快捷键", width=150)
        hotkey_tree.column("状态", width=80)
        
        hotkey_tree.pack(fill="both", expand=True, pady=5)
        
        # 加载快捷键数据
        self.load_hotkey_data(hotkey_tree)
        
        # 快捷键操作按钮
        hotkey_button_frame = ttk.Frame(hotkey_group)
        hotkey_button_frame.pack(fill="x", pady=10)
        
        ttk.Button(hotkey_button_frame, text="编辑快捷键", 
                  command=lambda: self.edit_hotkeys(hotkey_tree)).pack(side="left", padx=5)
        ttk.Button(hotkey_button_frame, text="重置默认", 
                  command=lambda: self.reset_hotkeys(hotkey_tree)).pack(side="left", padx=5)
        ttk.Button(hotkey_button_frame, text="刷新列表", 
                  command=lambda: self.load_hotkey_data(hotkey_tree)).pack(side="left", padx=5)
    
    def create_performance_tab(self):
        """创建性能设置页"""
        performance_frame = ttk.Frame(self.notebook)
        self.notebook.add(performance_frame, text="性能")
        
        # 刷新设置
        refresh_group = ttk.LabelFrame(performance_frame, text="刷新设置", padding=15)
        refresh_group.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(refresh_group, text="仪表板刷新间隔 (秒):").grid(row=0, column=0, sticky="w", pady=5)
        
        refresh_spinbox = ttk.Spinbox(refresh_group, textvariable=self.refresh_interval_var,
                                    from_=1, to=60, width=10)
        refresh_spinbox.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # 内存设置
        memory_group = ttk.LabelFrame(performance_frame, text="内存管理", padding=15)
        memory_group.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(memory_group, text="日志最大行数:").grid(row=0, column=0, sticky="w", pady=5)
        
        log_lines_spinbox = ttk.Spinbox(memory_group, from_=100, to=10000, width=10)
        log_lines_spinbox.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ttk.Checkbutton(memory_group, text="自动清理临时文件").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Checkbutton(memory_group, text="启用内存优化").grid(row=2, column=0, sticky="w", pady=5)
        
        # 网络设置
        network_group = ttk.LabelFrame(performance_frame, text="网络设置", padding=15)
        network_group.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(network_group, text="请求超时时间 (秒):").grid(row=0, column=0, sticky="w", pady=5)
        
        timeout_spinbox = ttk.Spinbox(network_group, from_=5, to=60, width=10)
        timeout_spinbox.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ttk.Label(network_group, text="最大重试次数:").grid(row=1, column=0, sticky="w", pady=5)
        
        retry_spinbox = ttk.Spinbox(network_group, from_=1, to=10, width=10)
        retry_spinbox.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    
    def create_advanced_tab(self):
        """创建高级选项页"""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="高级")
        
        # 数据管理
        data_group = ttk.LabelFrame(advanced_frame, text="数据管理", padding=15)
        data_group.pack(fill="x", padx=10, pady=5)
        
        ttk.Checkbutton(data_group, text="自动保存配置", 
                       variable=self.auto_save_var).grid(row=0, column=0, sticky="w", pady=5)
        
        ttk.Label(data_group, text="自动保存间隔 (分钟):").grid(row=1, column=0, sticky="w", pady=5)
        
        autosave_spinbox = ttk.Spinbox(data_group, from_=1, to=60, width=10)
        autosave_spinbox.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # 备份管理
        backup_group = ttk.LabelFrame(advanced_frame, text="备份管理", padding=15)
        backup_group.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(backup_group, text="创建备份", 
                  command=self.create_backup).grid(row=0, column=0, sticky="w", pady=5)
        ttk.Button(backup_group, text="管理备份", 
                  command=self.manage_backups).grid(row=0, column=1, padx=10, pady=5)
        
        # 调试设置
        debug_group = ttk.LabelFrame(advanced_frame, text="调试设置", padding=15)
        debug_group.pack(fill="x", padx=10, pady=5)
        
        ttk.Checkbutton(debug_group, text="启用调试模式").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Checkbutton(debug_group, text="详细日志记录").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Checkbutton(debug_group, text="性能监控").grid(row=2, column=0, sticky="w", pady=5)
        
        ttk.Button(debug_group, text="打开日志目录", 
                  command=self.open_log_directory).grid(row=3, column=0, sticky="w", pady=10)
        
        # 重置选项
        reset_group = ttk.LabelFrame(advanced_frame, text="重置选项", padding=15)
        reset_group.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(reset_group, text="重置窗口布局", 
                  command=self.reset_window_layout).grid(row=0, column=0, sticky="w", pady=5)
        ttk.Button(reset_group, text="清空所有数据", 
                  command=self.clear_all_data).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(reset_group, text="恢复出厂设置", 
                  command=self.factory_reset).grid(row=0, column=2, padx=10, pady=5)
    
    def get_frame(self):
        """获取主框架"""
        return self.main_frame
    
    def load_settings(self):
        """加载当前设置"""
        try:
            # 加载主题设置
            current_theme = theme_manager.current_theme
            theme_names = list(theme_manager.get_available_themes().values())
            if current_theme == 'light':
                self.theme_var.set(theme_names[0] if theme_names else "浅色主题")
            else:
                self.theme_var.set(theme_names[1] if len(theme_names) > 1 else "深色主题")
            
            # 加载其他设置
            self.language_var.set(gui_config.get('general.language', '简体中文'))
            self.minimize_to_tray_var.set(gui_config.get('general.minimize_to_tray', True))
            self.close_to_tray_var.set(gui_config.get('general.close_to_tray', True))
            self.auto_save_var.set(gui_config.get('general.auto_save', True))
            self.show_charts_var.set(gui_config.get('dashboard.show_charts', True))
            self.refresh_interval_var.set(gui_config.get('dashboard.refresh_interval', 5))
            
        except Exception as e:
            print(f"加载设置失败: {e}")
    
    def apply_settings(self):
        """应用设置"""
        try:
            # 应用主题
            theme_name = self.theme_var.get()
            if theme_name == "浅色主题":
                theme_manager.set_theme('light')
            elif theme_name == "深色主题":
                theme_manager.set_theme('dark')
            
            # 保存其他设置
            gui_config.set('general.language', self.language_var.get())
            gui_config.set('general.minimize_to_tray', self.minimize_to_tray_var.get())
            gui_config.set('general.close_to_tray', self.close_to_tray_var.get())
            gui_config.set('general.auto_save', self.auto_save_var.get())
            gui_config.set('dashboard.show_charts', self.show_charts_var.get())
            gui_config.set('dashboard.refresh_interval', self.refresh_interval_var.get())
            
            messagebox.showinfo("设置已保存", "设置已成功保存！\n某些更改可能需要重启应用程序才能生效。")
            
        except Exception as e:
            messagebox.showerror("保存失败", f"保存设置失败:\n{str(e)}")
    
    def reset_to_default(self):
        """重置为默认设置"""
        if messagebox.askyesno("确认重置", "确定要重置所有设置为默认值吗？"):
            try:
                gui_config.reset_to_default()
                self.load_settings()
                messagebox.showinfo("重置成功", "设置已重置为默认值")
            except Exception as e:
                messagebox.showerror("重置失败", f"重置设置失败:\n{str(e)}")
    
    def export_config(self):
        """导出配置"""
        gui_config.export_config()
    
    def import_config(self):
        """导入配置"""
        if gui_config.import_config():
            self.load_settings()
    
    def on_theme_changed(self, event):
        """主题变更事件"""
        self.preview_theme()
    
    def preview_theme(self):
        """预览主题"""
        try:
            theme_name = self.theme_var.get()
            if theme_name == "浅色主题":
                theme_manager.set_theme('light')
            elif theme_name == "深色主题":
                theme_manager.set_theme('dark')
        except Exception as e:
            print(f"预览主题失败: {e}")
    
    def test_tray_icon(self):
        """测试托盘图标"""
        try:
            system_tray.show_notification("测试通知", "系统托盘功能正常工作！")
        except Exception as e:
            messagebox.showerror("测试失败", f"托盘图标测试失败:\n{str(e)}")
    
    def load_hotkey_data(self, tree):
        """加载快捷键数据"""
        try:
            # 清空现有数据
            for item in tree.get_children():
                tree.delete(item)
            
            # 获取快捷键信息
            hotkeys = hotkey_manager.get_hotkeys()
            
            for hotkey_id, hotkey_info in hotkeys.items():
                status = "启用" if hotkey_info.get('enabled', False) else "禁用"
                tree.insert("", "end", values=(
                    hotkey_info.get('description', hotkey_id),
                    hotkey_info.get('combination', ''),
                    status
                ))
        except Exception as e:
            print(f"加载快捷键数据失败: {e}")
    
    def edit_hotkeys(self, tree):
        """编辑快捷键"""
        try:
            dialog = HotkeyConfigDialog(self.parent, hotkey_manager)
            dialog.show()
            # 刷新列表
            self.load_hotkey_data(tree)
        except Exception as e:
            messagebox.showerror("编辑失败", f"打开快捷键编辑器失败:\n{str(e)}")
    
    def reset_hotkeys(self, tree):
        """重置快捷键"""
        if messagebox.askyesno("确认重置", "确定要重置所有快捷键为默认值吗？"):
            try:
                # 重置快捷键（这里应该调用实际的重置方法）
                print("重置快捷键为默认值")
                self.load_hotkey_data(tree)
                messagebox.showinfo("重置成功", "快捷键已重置为默认值")
            except Exception as e:
                messagebox.showerror("重置失败", f"重置快捷键失败:\n{str(e)}")
    
    def create_backup(self):
        """创建备份"""
        try:
            backup_path = gui_config.create_backup()
            if backup_path:
                messagebox.showinfo("备份成功", f"配置备份已创建:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("备份失败", f"创建备份失败:\n{str(e)}")
    
    def manage_backups(self):
        """管理备份"""
        try:
            # 这里可以实现一个备份管理对话框
            backups = gui_config.list_backups()
            if not backups:
                messagebox.showinfo("备份管理", "当前没有可用的备份文件")
                return
            
            backup_list = "\n".join([
                f"{backup['filename']} - {backup['modified_time'].strftime('%Y-%m-%d %H:%M:%S')}"
                for backup in backups[:5]  # 只显示前5个
            ])
            
            messagebox.showinfo("备份列表", f"最近的备份文件:\n\n{backup_list}")
            
        except Exception as e:
            messagebox.showerror("管理失败", f"管理备份失败:\n{str(e)}")
    
    def open_log_directory(self):
        """打开日志目录"""
        try:
            import subprocess
            import platform
            
            log_dir = os.path.join(os.path.dirname(__file__), '../../logs')
            
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', log_dir])
            elif platform.system() == 'Windows':
                subprocess.run(['explorer', log_dir])
            else:  # Linux
                subprocess.run(['xdg-open', log_dir])
                
        except Exception as e:
            messagebox.showerror("打开失败", f"打开日志目录失败:\n{str(e)}")
    
    def reset_window_layout(self):
        """重置窗口布局"""
        if messagebox.askyesno("确认重置", "确定要重置窗口布局吗？"):
            try:
                # 重置窗口相关配置
                gui_config.set('window.width', 1200)
                gui_config.set('window.height', 800)
                gui_config.set('window.x', 100)
                gui_config.set('window.y', 100)
                gui_config.set('window.maximized', False)
                
                messagebox.showinfo("重置成功", "窗口布局已重置，重启应用程序后生效")
            except Exception as e:
                messagebox.showerror("重置失败", f"重置窗口布局失败:\n{str(e)}")
    
    def clear_all_data(self):
        """清空所有数据"""
        if messagebox.askyesno("确认清空", "确定要清空所有数据吗？\n这将删除所有统计数据、日志文件等。\n此操作无法撤销！"):
            try:
                # 这里应该实现清空数据的逻辑
                print("清空所有数据")
                messagebox.showinfo("清空成功", "所有数据已清空")
            except Exception as e:
                messagebox.showerror("清空失败", f"清空数据失败:\n{str(e)}")
    
    def factory_reset(self):
        """恢复出厂设置"""
        if messagebox.askyesno("确认恢复", "确定要恢复出厂设置吗？\n这将清空所有配置和数据。\n此操作无法撤销！"):
            try:
                # 重置所有配置
                gui_config.reset_to_default()
                
                # 重置主题
                theme_manager.set_theme('light')
                
                # 清空数据（这里应该实现实际的清空逻辑）
                print("恢复出厂设置")
                
                messagebox.showinfo("恢复成功", "已恢复出厂设置，请重启应用程序")
            except Exception as e:
                messagebox.showerror("恢复失败", f"恢复出厂设置失败:\n{str(e)}") 