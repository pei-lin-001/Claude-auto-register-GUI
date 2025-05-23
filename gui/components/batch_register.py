import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import csv
import time
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ..resources.styles import COLORS, FONTS, ICONS
from gui.services.registration_service import RegistrationService

class BatchRegisterFrame(ttk.Frame):
    """批量注册界面组件"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.is_running = False
        self.task_thread = None
        self.accounts_data = []
        self.results = []
        self.current_index = 0
        self.success_count = 0
        self.failed_count = 0
        
        # 初始化注册服务
        self.registration_service = RegistrationService()
        self.setup_service_callbacks()
        
        self.setup_ui()
        
    def setup_service_callbacks(self):
        """设置服务回调函数"""
        self.registration_service.set_callbacks(
            progress_callback=self.on_registration_progress,
            log_callback=self.on_log_message,
            status_callback=self.on_registration_status
        )
        
    def on_registration_progress(self, progress, current, total, message):
        """注册进度回调"""
        self.after(0, lambda: self.update_progress_display(progress, current, total, message))
        
    def on_log_message(self, message, level="INFO"):
        """日志消息回调"""
        print(f"[{level}] {message}")  # 可以添加到日志显示区域
        
    def on_registration_status(self, status):
        """注册状态回调"""
        self.after(0, lambda: self.update_status_display(status))
        
    def update_progress_display(self, progress, current, total, message):
        """更新进度显示"""
        try:
            self.progress_var.set(progress)
            self.current_label.config(text=f"当前: {current}")
            
            # 更新统计
            stats = self.registration_service.get_stats()
            self.success_label.config(text=f"成功: {stats['success']}")
            self.failed_label.config(text=f"失败: {stats['failed']}")
            
        except Exception as e:
            print(f"更新进度显示失败: {e}")
            
    def update_status_display(self, status):
        """更新状态显示"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.config(text=status)
        except Exception as e:
            print(f"更新状态显示失败: {e}")
        
    def setup_ui(self):
        """设置用户界面"""
        # 主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text=f"{ICONS['batch']} 批量注册管理",
            font=FONTS['title']
        )
        title_label.pack(side=tk.LEFT)
        
        # 配置区域
        config_frame = ttk.LabelFrame(main_container, text="注册配置", padding=15)
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 文件导入
        file_frame = ttk.Frame(config_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="账号文件:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        self.file_path_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        self.browse_btn = ttk.Button(
            file_frame,
            text=f"{ICONS['folder']} 浏览",
            command=self.browse_accounts_file,
            style="secondary.TButton"
        )
        self.browse_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        self.load_btn = ttk.Button(
            file_frame,
            text=f"{ICONS['load']} 加载",
            command=self.load_accounts_file,
            style="primary.TButton"
        )
        self.load_btn.pack(side=tk.RIGHT)
        
        # 注册参数
        params_frame = ttk.Frame(config_frame)
        params_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 并发数设置
        ttk.Label(params_frame, text="并发数:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.concurrent_var = tk.IntVar(value=3)
        concurrent_spin = ttk.Spinbox(
            params_frame, 
            from_=1, 
            to=10, 
            textvariable=self.concurrent_var,
            width=10
        )
        concurrent_spin.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # 间隔时间设置
        ttk.Label(params_frame, text="间隔时间(秒):").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.interval_var = tk.IntVar(value=5)
        interval_spin = ttk.Spinbox(
            params_frame,
            from_=1,
            to=60,
            textvariable=self.interval_var,
            width=10
        )
        interval_spin.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        # 重试次数设置
        ttk.Label(params_frame, text="重试次数:").grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        self.retry_var = tk.IntVar(value=3)
        retry_spin = ttk.Spinbox(
            params_frame,
            from_=0,
            to=10,
            textvariable=self.retry_var,
            width=10
        )
        retry_spin.grid(row=0, column=5, sticky=tk.W)
        
        # 控制按钮
        control_frame = ttk.Frame(main_container)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.start_btn = ttk.Button(
            control_frame,
            text=f"{ICONS['play']} 开始注册",
            command=self.start_batch_register,
            style="success.TButton"
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.pause_btn = ttk.Button(
            control_frame,
            text=f"{ICONS['pause']} 暂停",
            command=self.pause_register,
            style="warning.TButton",
            state='disabled'
        )
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(
            control_frame,
            text=f"{ICONS['stop']} 停止",
            command=self.stop_register,
            style="danger.TButton",
            state='disabled'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_btn = ttk.Button(
            control_frame,
            text=f"{ICONS['export']} 导出结果",
            command=self.export_results,
            style="secondary.TButton"
        )
        self.export_btn.pack(side=tk.RIGHT)
        
        # 进度显示
        progress_frame = ttk.LabelFrame(main_container, text="注册进度", padding=15)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # 统计信息
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.pack(fill=tk.X)
        
        self.total_label = ttk.Label(stats_frame, text="总数: 0", font=FONTS['body'])
        self.total_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.current_label = ttk.Label(stats_frame, text="当前: 0", font=FONTS['body'])
        self.current_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.success_label = ttk.Label(stats_frame, text="成功: 0", font=FONTS['body'], foreground=COLORS['success'])
        self.success_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.failed_label = ttk.Label(stats_frame, text="失败: 0", font=FONTS['body'], foreground=COLORS['error'])
        self.failed_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.speed_label = ttk.Label(stats_frame, text="速度: 0/min", font=FONTS['body'])
        self.speed_label.pack(side=tk.RIGHT)
        
        # 结果列表
        results_frame = ttk.LabelFrame(main_container, text="注册结果", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # 结果表格
        columns = ("序号", "邮箱", "状态", "消息", "耗时", "时间")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=12)
        
        # 设置列
        col_widths = {"序号": 50, "邮箱": 200, "状态": 80, "消息": 200, "耗时": 80, "时间": 150}
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=col_widths.get(col, 100), minwidth=50)
            
        # 滚动条
        results_scrollbar_y = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        results_scrollbar_x = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=results_scrollbar_y.set, xscrollcommand=results_scrollbar_x.set)
        
        # 布局
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        results_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 状态栏
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(
            status_frame,
            text="就绪",
            font=FONTS['body']
        )
        self.status_label.pack(side=tk.LEFT)
        
    def browse_accounts_file(self):
        """浏览账号文件"""
        file_path = filedialog.askopenfilename(
            title="选择账号文件",
            filetypes=[
                ("CSV文件", "*.csv"),
                ("JSON文件", "*.json"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
            
    def load_accounts_file(self):
        """加载账号文件"""
        file_path = self.file_path_var.get().strip()
        if not file_path:
            messagebox.showwarning("警告", "请先选择账号文件")
            return
            
        try:
            self.accounts_data = []
            
            if file_path.endswith('.csv'):
                self.load_csv_file(file_path)
            elif file_path.endswith('.json'):
                self.load_json_file(file_path)
            elif file_path.endswith('.txt'):
                self.load_txt_file(file_path)
            else:
                messagebox.showerror("错误", "不支持的文件格式")
                return
                
            # 更新统计信息
            self.update_stats()
            self.status_label.config(text=f"已加载 {len(self.accounts_data)} 个账号")
            messagebox.showinfo("成功", f"成功加载 {len(self.accounts_data)} 个账号")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败: {str(e)}")
            
    def load_csv_file(self, file_path):
        """加载CSV文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'email' in row:
                    account = {
                        'email': row['email'],
                        'password': row.get('password', ''),
                        'first_name': row.get('first_name', ''),
                        'last_name': row.get('last_name', ''),
                        'proxy': row.get('proxy', '')
                    }
                    self.accounts_data.append(account)
                    
    def load_json_file(self, file_path):
        """加载JSON文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                self.accounts_data = data
            else:
                messagebox.showerror("错误", "JSON文件格式不正确，应为账号数组")
                
    def load_txt_file(self, file_path):
        """加载文本文件（每行一个邮箱）"""
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                email = line.strip()
                if email and '@' in email:
                    account = {
                        'email': email,
                        'password': '',
                        'first_name': '',
                        'last_name': '',
                        'proxy': ''
                    }
                    self.accounts_data.append(account)
                    
    def start_batch_register(self):
        """开始批量注册"""
        if not self.accounts_data:
            messagebox.showwarning("警告", "请先加载账号文件")
            return
            
        if self.registration_service.is_registration_running():
            messagebox.showwarning("警告", "注册任务正在进行中")
            return
            
        # 获取注册参数
        account_count = len(self.accounts_data)
        concurrent = self.concurrent_var.get()
        interval = self.interval_var.get()
        
        # 重置状态
        self.reset_registration_state()
        
        # 更新按钮状态
        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self.stop_btn.config(state='normal')
        
        # 启动批量注册
        success = self.registration_service.start_batch_registration(
            account_count=account_count,
            concurrent=concurrent,
            interval=interval
        )
        
        if success:
            self.is_running = True
            messagebox.showinfo("开始注册", f"已启动批量注册任务，共 {account_count} 个账号")
        else:
            messagebox.showerror("启动失败", "批量注册任务启动失败，请检查配置")
            self.reset_button_state()
        
    def pause_register(self):
        """暂停/恢复注册"""
        if self.registration_service.is_registration_running():
            if self.registration_service.is_registration_paused():
                # 恢复注册
                if self.registration_service.resume_registration():
                    self.pause_btn.config(text=f"{ICONS['pause']} 暂停")
                    messagebox.showinfo("恢复", "注册任务已恢复")
            else:
                # 暂停注册
                if self.registration_service.pause_registration():
                    self.pause_btn.config(text=f"{ICONS['play']} 恢复")
                    messagebox.showinfo("暂停", "注册任务已暂停")
        else:
            messagebox.showwarning("警告", "没有正在运行的注册任务")
                
    def stop_register(self):
        """停止注册"""
        if self.registration_service.is_registration_running():
            result = messagebox.askyesno("确认停止", "确定要停止当前的注册任务吗？")
            if result:
                if self.registration_service.stop_registration():
                    self.reset_button_state()
                    messagebox.showinfo("停止", "注册任务已停止")
        else:
            messagebox.showwarning("警告", "没有正在运行的注册任务")
        
    def reset_button_state(self):
        """重置按钮状态"""
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled', text=f"{ICONS['pause']} 暂停")
        self.stop_btn.config(state='disabled')
        self.is_running = False
        
    def reset_registration_state(self):
        """重置注册状态"""
        self.results = []
        self.current_index = 0
        self.success_count = 0
        self.failed_count = 0
        
        # 清空结果列表
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        # 重置进度
        self.progress_var.set(0)
        self.update_stats()
        
    def _batch_register_worker(self):
        """批量注册工作线程（已由注册服务接管，保留用于兼容性）"""
        # 这个方法现在由RegistrationService处理
        pass
            
    def _simulate_register_account(self, account):
        """模拟注册账号（已由注册服务接管）"""
        # 这个方法现在由RegistrationService处理
        return {
            'status': '成功',
            'message': '注册完成'
        }
        
    def update_stats(self):
        """更新统计信息"""
        try:
            # 从注册服务获取统计信息
            stats = self.registration_service.get_stats()
            
            total = stats.get('total', len(self.accounts_data))
            current = stats.get('current', self.current_index)
            success = stats.get('success', self.success_count)
            failed = stats.get('failed', self.failed_count)
            
            # 更新显示
            self.total_label.config(text=f"总数: {total}")
            self.current_label.config(text=f"当前: {current}")
            self.success_label.config(text=f"成功: {success}")
            self.failed_label.config(text=f"失败: {failed}")
            
            # 更新进度条
            if total > 0:
                progress = (current / total) * 100
                self.progress_var.set(progress)
            
            # 计算速度
            if stats.get('start_time'):
                elapsed_time = time.time() - stats['start_time']
                if elapsed_time > 0:
                    speed = (current / elapsed_time) * 60  # 每分钟速度
                    self.speed_label.config(text=f"速度: {speed:.1f}/min")
                    
        except Exception as e:
            print(f"更新统计信息失败: {e}")
        
    def export_results(self):
        """导出结果"""
        if not self.results:
            messagebox.showwarning("警告", "没有结果可导出")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="导出结果",
            defaultextension=".csv",
            filetypes=[
                ("CSV文件", "*.csv"),
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.export_to_csv(file_path)
                elif file_path.endswith('.json'):
                    self.export_to_json(file_path)
                else:
                    self.export_to_csv(file_path)
                    
                messagebox.showinfo("成功", f"结果已导出到: {file_path}")
                
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
                
    def export_to_csv(self, file_path):
        """导出到CSV文件"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入标题
            writer.writerow(['序号', '邮箱', '状态', '消息', '耗时', '时间'])
            
            # 写入数据
            for result in self.results:
                writer.writerow([
                    result['index'],
                    result['email'],
                    result['status'],
                    result['message'],
                    result['time_taken'],
                    result['timestamp']
                ])
                
    def export_to_json(self, file_path):
        """导出到JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
            
    def get_registration_stats(self):
        """获取注册统计信息"""
        return {
            'total': len(self.accounts_data),
            'completed': self.current_index,
            'success': self.success_count,
            'failed': self.failed_count,
            'is_running': self.is_running
        } 