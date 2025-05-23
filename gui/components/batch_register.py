import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import csv
import time
from datetime import datetime
from ..resources.styles import COLORS, FONTS, ICONS

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
        self.setup_ui()
        
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
            
        if self.is_running:
            messagebox.showwarning("警告", "注册任务正在进行中")
            return
            
        # 重置状态
        self.reset_registration_state()
        
        # 更新按钮状态
        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self.stop_btn.config(state='normal')
        
        self.is_running = True
        self.status_label.config(text="正在开始批量注册...")
        
        # 启动注册线程
        self.task_thread = threading.Thread(target=self._batch_register_worker, daemon=True)
        self.task_thread.start()
        
    def pause_register(self):
        """暂停/恢复注册"""
        if self.is_running:
            self.is_running = False
            self.pause_btn.config(text=f"{ICONS['play']} 恢复")
            self.status_label.config(text="注册已暂停")
        else:
            self.is_running = True
            self.pause_btn.config(text=f"{ICONS['pause']} 暂停")
            self.status_label.config(text="正在继续注册...")
            # 继续注册任务
            if not self.task_thread or not self.task_thread.is_alive():
                self.task_thread = threading.Thread(target=self._batch_register_worker, daemon=True)
                self.task_thread.start()
                
    def stop_register(self):
        """停止注册"""
        self.is_running = False
        
        # 更新按钮状态
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled', text=f"{ICONS['pause']} 暂停")
        self.stop_btn.config(state='disabled')
        
        self.status_label.config(text="注册已停止")
        
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
        """批量注册工作线程"""
        start_time = time.time()
        
        try:
            while self.current_index < len(self.accounts_data) and self.is_running:
                # 等待暂停状态解除
                while not self.is_running and self.current_index < len(self.accounts_data):
                    time.sleep(0.1)
                    
                if not self.is_running:
                    break
                    
                account = self.accounts_data[self.current_index]
                
                # 更新当前状态
                self.after(0, lambda: self.status_label.config(
                    text=f"正在注册: {account['email']} ({self.current_index + 1}/{len(self.accounts_data)})"
                ))
                
                # 模拟注册过程
                register_start = time.time()
                result = self._simulate_register_account(account)
                register_time = time.time() - register_start
                
                # 记录结果
                result_data = {
                    'index': self.current_index + 1,
                    'email': account['email'],
                    'status': result['status'],
                    'message': result['message'],
                    'time_taken': f"{register_time:.2f}s",
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                }
                
                # 更新UI
                self.after(0, lambda r=result_data: self._update_result_ui(r))
                
                self.current_index += 1
                
                # 计算并更新统计信息
                elapsed_time = time.time() - start_time
                speed = (self.current_index / elapsed_time) * 60 if elapsed_time > 0 else 0
                
                self.after(0, lambda s=speed: [
                    self.update_stats(),
                    self.speed_label.config(text=f"速度: {s:.1f}/min")
                ])
                
                # 间隔时间
                if self.current_index < len(self.accounts_data):
                    time.sleep(self.interval_var.get())
                    
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("错误", f"批量注册过程中发生错误: {str(e)}"))
        finally:
            # 完成后更新UI状态
            self.after(0, self._finish_registration)
            
    def _simulate_register_account(self, account):
        """模拟注册账号（这里应该调用实际的注册逻辑）"""
        import random
        
        # 模拟注册时间
        time.sleep(random.uniform(2, 5))
        
        # 模拟注册结果
        success_rate = 0.8  # 80%成功率
        if random.random() < success_rate:
            return {
                'status': '成功',
                'message': '注册完成'
            }
        else:
            errors = [
                '邮箱已存在',
                '网络超时',
                '代理连接失败',
                '验证码识别失败',
                '服务器错误'
            ]
            return {
                'status': '失败',
                'message': random.choice(errors)
            }
            
    def _update_result_ui(self, result_data):
        """更新结果UI"""
        # 添加到结果列表
        item_values = (
            result_data['index'],
            result_data['email'],
            result_data['status'],
            result_data['message'],
            result_data['time_taken'],
            result_data['timestamp']
        )
        
        item = self.results_tree.insert('', 'end', values=item_values)
        
        # 根据状态设置颜色
        if result_data['status'] == '成功':
            self.results_tree.item(item, tags=('success',))
            self.success_count += 1
        else:
            self.results_tree.item(item, tags=('failed',))
            self.failed_count += 1
            
        # 配置标签样式
        self.results_tree.tag_configure('success', foreground=COLORS['success'])
        self.results_tree.tag_configure('failed', foreground=COLORS['error'])
        
        # 滚动到最新项目
        self.results_tree.see(item)
        
        # 存储结果
        self.results.append(result_data)
        
    def _finish_registration(self):
        """完成注册"""
        self.is_running = False
        
        # 更新按钮状态
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled', text=f"{ICONS['pause']} 暂停")
        self.stop_btn.config(state='disabled')
        
        # 显示完成信息
        total = len(self.accounts_data)
        completed = self.current_index
        success_rate = (self.success_count / completed * 100) if completed > 0 else 0
        
        message = f"批量注册完成！\n"
        message += f"总数: {total}\n"
        message += f"完成: {completed}\n"
        message += f"成功: {self.success_count}\n"
        message += f"失败: {self.failed_count}\n"
        message += f"成功率: {success_rate:.1f}%"
        
        self.status_label.config(text="批量注册完成")
        messagebox.showinfo("完成", message)
        
    def update_stats(self):
        """更新统计信息"""
        total = len(self.accounts_data)
        current = self.current_index
        
        # 更新标签
        self.total_label.config(text=f"总数: {total}")
        self.current_label.config(text=f"当前: {current}")
        self.success_label.config(text=f"成功: {self.success_count}")
        self.failed_label.config(text=f"失败: {self.failed_count}")
        
        # 更新进度条
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
        else:
            self.progress_var.set(0)
            
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