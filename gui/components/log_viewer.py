import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
import time
from datetime import datetime
from ..resources.styles import COLORS, FONTS, ICONS

class LogViewerFrame(ttk.Frame):
    """日志查看界面组件"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.log_files = []
        self.current_log_file = None
        self.auto_scroll = True
        self.is_monitoring = False
        self.monitor_thread = None
        self.last_position = 0
        self.setup_ui()
        self.scan_log_files()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题和控制栏
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 标题
        title_label = ttk.Label(
            header_frame,
            text=f"{ICONS['logs']} 日志查看器",
            font=FONTS['title']
        )
        title_label.pack(side=tk.LEFT)
        
        # 工具栏
        toolbar_frame = ttk.Frame(main_container)
        toolbar_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 日志文件选择
        ttk.Label(toolbar_frame, text="日志文件:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.log_file_var = tk.StringVar()
        self.log_file_combo = ttk.Combobox(
            toolbar_frame,
            textvariable=self.log_file_var,
            state="readonly",
            width=30
        )
        self.log_file_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.log_file_combo.bind('<<ComboboxSelected>>', self.on_log_file_selected)
        
        # 刷新按钮
        self.refresh_btn = ttk.Button(
            toolbar_frame,
            text=f"{ICONS['refresh']} 刷新",
            command=self.scan_log_files,
            style="secondary.TButton"
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 实时监控按钮
        self.monitor_btn = ttk.Button(
            toolbar_frame,
            text=f"{ICONS['play']} 开始监控",
            command=self.toggle_monitoring,
            style="primary.TButton"
        )
        self.monitor_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空日志按钮
        self.clear_btn = ttk.Button(
            toolbar_frame,
            text=f"{ICONS['clear']} 清空显示",
            command=self.clear_log_display,
            style="secondary.TButton"
        )
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 保存日志按钮
        self.save_btn = ttk.Button(
            toolbar_frame,
            text=f"{ICONS['save']} 保存",
            command=self.save_log,
            style="secondary.TButton"
        )
        self.save_btn.pack(side=tk.RIGHT)
        
        # 搜索栏
        search_frame = ttk.Frame(main_container)
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search_changed)
        
        # 搜索按钮
        self.search_btn = ttk.Button(
            search_frame,
            text=f"{ICONS['search']} 搜索",
            command=self.search_logs,
            style="secondary.TButton"
        )
        self.search_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 过滤器
        ttk.Label(search_frame, text="级别:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.level_filter_var = tk.StringVar(value="全部")
        level_filter_combo = ttk.Combobox(
            search_frame,
            textvariable=self.level_filter_var,
            values=["全部", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            state="readonly",
            width=10
        )
        level_filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        level_filter_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # 自动滚动复选框
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = ttk.Checkbutton(
            search_frame,
            text="自动滚动",
            variable=self.auto_scroll_var,
            command=self.toggle_auto_scroll
        )
        auto_scroll_check.pack(side=tk.RIGHT)
        
        # 日志显示区域
        log_container = ttk.Frame(main_container)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        # 日志文本框
        self.log_text = tk.Text(
            log_container,
            wrap=tk.NONE,
            font=('Consolas', 10) if os.name == 'nt' else ('Monaco', 10),
            bg='#1e1e1e',
            fg='#ffffff',
            insertbackground='#ffffff',
            selectbackground='#404040'
        )
        
        # 滚动条
        v_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview)
        h_scrollbar = ttk.Scrollbar(log_container, orient=tk.HORIZONTAL, command=self.log_text.xview)
        self.log_text.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 布局
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 配置文本标签样式
        self.log_text.tag_configure("DEBUG", foreground="#9e9e9e")
        self.log_text.tag_configure("INFO", foreground="#81c784")
        self.log_text.tag_configure("WARNING", foreground="#ffb74d")
        self.log_text.tag_configure("ERROR", foreground="#e57373")
        self.log_text.tag_configure("CRITICAL", foreground="#f44336")
        self.log_text.tag_configure("TIMESTAMP", foreground="#64b5f6")
        self.log_text.tag_configure("SEARCH_HIGHLIGHT", background="#ffeb3b", foreground="#000000")
        
        # 状态栏
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.status_label = ttk.Label(
            status_frame,
            text="就绪",
            font=FONTS['body']
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.line_count_label = ttk.Label(
            status_frame,
            text="行数: 0",
            font=FONTS['body']
        )
        self.line_count_label.pack(side=tk.RIGHT)
        
    def scan_log_files(self):
        """扫描日志文件"""
        self.log_files = []
        log_dirs = ['logs', '.', 'log']
        
        for log_dir in log_dirs:
            if os.path.exists(log_dir):
                for file in os.listdir(log_dir):
                    if file.endswith(('.log', '.txt')):
                        self.log_files.append(os.path.join(log_dir, file))
                        
        # 更新下拉列表
        self.log_file_combo['values'] = self.log_files
        if self.log_files and not self.current_log_file:
            self.log_file_var.set(self.log_files[0])
            self.current_log_file = self.log_files[0]
            self.load_log_file()
            
    def on_log_file_selected(self, event=None):
        """日志文件选择事件"""
        selected_file = self.log_file_var.get()
        if selected_file and selected_file != self.current_log_file:
            self.current_log_file = selected_file
            self.load_log_file()
            
    def load_log_file(self):
        """加载日志文件"""
        if not self.current_log_file or not os.path.exists(self.current_log_file):
            return
            
        try:
            self.log_text.delete(1.0, tk.END)
            
            with open(self.current_log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # 按行处理并添加样式
            lines = content.split('\n')
            for line in lines:
                self.add_log_line(line)
                
            self.update_line_count()
            self.status_label.config(text=f"已加载: {os.path.basename(self.current_log_file)}")
            
            # 滚动到底部
            if self.auto_scroll_var.get():
                self.log_text.see(tk.END)
                
        except Exception as e:
            messagebox.showerror("错误", f"加载日志文件失败: {str(e)}")
            
    def add_log_line(self, line):
        """添加日志行并应用样式"""
        if not line.strip():
            self.log_text.insert(tk.END, '\n')
            return
            
        # 检测日志级别并应用样式
        level_tags = []
        if 'DEBUG' in line:
            level_tags.append('DEBUG')
        elif 'INFO' in line:
            level_tags.append('INFO')
        elif 'WARNING' in line or 'WARN' in line:
            level_tags.append('WARNING')
        elif 'ERROR' in line:
            level_tags.append('ERROR')
        elif 'CRITICAL' in line or 'FATAL' in line:
            level_tags.append('CRITICAL')
            
        # 检测时间戳
        if line[:19].count('-') == 2 and line[:19].count(':') == 2:
            # 添加时间戳部分
            self.log_text.insert(tk.END, line[:19], 'TIMESTAMP')
            # 添加其余部分
            self.log_text.insert(tk.END, line[19:] + '\n', level_tags)
        else:
            self.log_text.insert(tk.END, line + '\n', level_tags)
            
    def toggle_monitoring(self):
        """切换监控状态"""
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
            
    def start_monitoring(self):
        """开始实时监控"""
        if not self.current_log_file:
            messagebox.showwarning("警告", "请先选择一个日志文件")
            return
            
        self.is_monitoring = True
        self.monitor_btn.config(text=f"{ICONS['stop']} 停止监控", style="warning.TButton")
        self.status_label.config(text="正在监控日志文件...")
        
        # 记录当前文件位置
        if os.path.exists(self.current_log_file):
            self.last_position = os.path.getsize(self.current_log_file)
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_log_file, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        self.monitor_btn.config(text=f"{ICONS['play']} 开始监控", style="primary.TButton")
        self.status_label.config(text="监控已停止")
        
    def _monitor_log_file(self):
        """监控日志文件线程"""
        while self.is_monitoring:
            try:
                if os.path.exists(self.current_log_file):
                    current_size = os.path.getsize(self.current_log_file)
                    
                    if current_size > self.last_position:
                        # 读取新内容
                        with open(self.current_log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            f.seek(self.last_position)
                            new_content = f.read()
                            
                        # 在UI线程中更新显示
                        if new_content.strip():
                            self.after(0, lambda: self._append_new_content(new_content))
                            
                        self.last_position = current_size
                        
                time.sleep(1)  # 每秒检查一次
                
            except Exception as e:
                self.after(0, lambda: self.status_label.config(text=f"监控错误: {str(e)}"))
                break
                
    def _append_new_content(self, content):
        """追加新内容到日志显示"""
        lines = content.strip().split('\n')
        for line in lines:
            if line.strip():
                self.add_log_line(line)
                
        self.update_line_count()
        
        # 自动滚动到底部
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
            
    def clear_log_display(self):
        """清空日志显示"""
        if messagebox.askyesno("确认", "确定要清空日志显示吗？"):
            self.log_text.delete(1.0, tk.END)
            self.update_line_count()
            
    def save_log(self):
        """保存日志"""
        content = self.log_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("警告", "没有日志内容可保存")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="保存日志",
            defaultextension=".log",
            filetypes=[("日志文件", "*.log"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"日志已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
                
    def search_logs(self):
        """搜索日志"""
        search_term = self.search_var.get().strip()
        if not search_term:
            return
            
        # 清除之前的高亮
        self.log_text.tag_remove("SEARCH_HIGHLIGHT", 1.0, tk.END)
        
        # 搜索并高亮
        start_pos = "1.0"
        count = 0
        
        while True:
            pos = self.log_text.search(search_term, start_pos, tk.END)
            if not pos:
                break
                
            end_pos = f"{pos}+{len(search_term)}c"
            self.log_text.tag_add("SEARCH_HIGHLIGHT", pos, end_pos)
            start_pos = end_pos
            count += 1
            
        if count > 0:
            self.status_label.config(text=f"找到 {count} 个匹配项")
            # 滚动到第一个匹配项
            first_match = self.log_text.tag_ranges("SEARCH_HIGHLIGHT")
            if first_match:
                self.log_text.see(first_match[0])
        else:
            self.status_label.config(text="未找到匹配项")
            
    def on_search_changed(self, event=None):
        """搜索框内容改变事件"""
        if not self.search_var.get().strip():
            # 清除高亮
            self.log_text.tag_remove("SEARCH_HIGHLIGHT", 1.0, tk.END)
            
    def apply_filters(self, event=None):
        """应用过滤器"""
        # 这里可以实现基于日志级别的过滤功能
        # 暂时只更新状态显示
        level = self.level_filter_var.get()
        if level != "全部":
            self.status_label.config(text=f"过滤器: {level}")
        else:
            self.status_label.config(text="显示所有日志")
            
    def toggle_auto_scroll(self):
        """切换自动滚动"""
        self.auto_scroll = self.auto_scroll_var.get()
        
    def update_line_count(self):
        """更新行数显示"""
        line_count = int(self.log_text.index(tk.END).split('.')[0]) - 1
        self.line_count_label.config(text=f"行数: {line_count}")
        
    def write_log(self, message, level="INFO"):
        """写入日志消息（供其他组件调用）"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} - {level} - {message}"
        
        # 添加到显示
        self.add_log_line(log_line)
        
        # 如果在监控模式且自动滚动，滚动到底部
        if self.is_monitoring and self.auto_scroll_var.get():
            self.log_text.see(tk.END)
            
        self.update_line_count()
        
    def get_log_content(self):
        """获取当前显示的日志内容"""
        return self.log_text.get(1.0, tk.END) 