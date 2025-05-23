import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
import requests
from ..resources.styles import COLORS, FONTS, ICONS
import os

class ProxyManagerFrame(ttk.Frame):
    """代理管理界面组件"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.proxy_list = []
        self.proxy_file_path = "Proxy.txt"
        self.setup_ui()
        self.load_proxies()
        
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
            text=f"{ICONS['proxy']} 代理服务器管理",
            font=FONTS['title']
        )
        title_label.pack(side=tk.LEFT)
        
        # 工具栏
        toolbar_frame = ttk.Frame(main_container)
        toolbar_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 添加代理按钮
        self.add_btn = ttk.Button(
            toolbar_frame,
            text=f"{ICONS['add']} 添加代理",
            command=self.show_add_proxy_dialog,
            style="primary.TButton"
        )
        self.add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 批量导入按钮
        self.import_btn = ttk.Button(
            toolbar_frame,
            text=f"{ICONS['import']} 批量导入",
            command=self.import_proxies,
            style="secondary.TButton"
        )
        self.import_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 测试所有代理按钮
        self.test_all_btn = ttk.Button(
            toolbar_frame,
            text=f"{ICONS['test']} 测试所有",
            command=self.test_all_proxies,
            style="secondary.TButton"
        )
        self.test_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空列表按钮
        self.clear_btn = ttk.Button(
            toolbar_frame,
            text=f"{ICONS['delete']} 清空列表",
            command=self.clear_all_proxies,
            style="danger.TButton"
        )
        self.clear_btn.pack(side=tk.RIGHT)
        
        # 代理列表容器
        list_container = ttk.Frame(main_container)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # 代理列表
        columns = ("序号", "地址", "端口", "类型", "用户名", "状态", "延迟", "操作")
        self.proxy_tree = ttk.Treeview(list_container, columns=columns, show="headings", height=15)
        
        # 设置列
        col_widths = {"序号": 50, "地址": 150, "端口": 80, "类型": 80, "用户名": 100, "状态": 80, "延迟": 80, "操作": 120}
        for col in columns:
            self.proxy_tree.heading(col, text=col)
            self.proxy_tree.column(col, width=col_widths.get(col, 100), minwidth=50)
            
        # 滚动条
        scrollbar_y = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.proxy_tree.yview)
        scrollbar_x = ttk.Scrollbar(list_container, orient=tk.HORIZONTAL, command=self.proxy_tree.xview)
        self.proxy_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # 布局
        self.proxy_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 右键菜单
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label=f"{ICONS['edit']} 编辑", command=self.edit_selected_proxy)
        self.context_menu.add_command(label=f"{ICONS['test']} 测试", command=self.test_selected_proxy)
        self.context_menu.add_separator()
        self.context_menu.add_command(label=f"{ICONS['delete']} 删除", command=self.delete_selected_proxy)
        
        # 绑定事件
        self.proxy_tree.bind("<Button-3>", self.show_context_menu)
        self.proxy_tree.bind("<Double-1>", self.edit_selected_proxy)
        
        # 状态信息
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.status_label = ttk.Label(
            status_frame,
            text="就绪",
            font=FONTS['body']
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.proxy_count_label = ttk.Label(
            status_frame,
            text="代理数量: 0",
            font=FONTS['body']
        )
        self.proxy_count_label.pack(side=tk.RIGHT)
        
    def load_proxies(self):
        """加载代理列表"""
        try:
            if os.path.exists(self.proxy_file_path):
                with open(self.proxy_file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.proxy_list = []
                        for line in content.split('\n'):
                            if line.strip():
                                proxy_info = self.parse_proxy_string(line.strip())
                                if proxy_info:
                                    self.proxy_list.append(proxy_info)
            self.refresh_proxy_list()
        except Exception as e:
            messagebox.showerror("错误", f"加载代理列表失败: {str(e)}")
            
    def parse_proxy_string(self, proxy_str):
        """解析代理字符串"""
        try:
            # 支持格式: ip:port 或 ip:port:username:password
            parts = proxy_str.split(':')
            if len(parts) >= 2:
                return {
                    'host': parts[0],
                    'port': int(parts[1]),
                    'type': 'HTTP',
                    'username': parts[2] if len(parts) > 2 else '',
                    'password': parts[3] if len(parts) > 3 else '',
                    'status': '未测试',
                    'latency': '-'
                }
        except:
            pass
        return None
        
    def save_proxies(self):
        """保存代理列表到文件"""
        try:
            with open(self.proxy_file_path, 'w', encoding='utf-8') as f:
                for proxy in self.proxy_list:
                    if proxy['username'] and proxy['password']:
                        f.write(f"{proxy['host']}:{proxy['port']}:{proxy['username']}:{proxy['password']}\n")
                    else:
                        f.write(f"{proxy['host']}:{proxy['port']}\n")
        except Exception as e:
            messagebox.showerror("错误", f"保存代理列表失败: {str(e)}")
            
    def refresh_proxy_list(self):
        """刷新代理列表显示"""
        # 清空现有项目
        for item in self.proxy_tree.get_children():
            self.proxy_tree.delete(item)
            
        # 添加代理项目
        for i, proxy in enumerate(self.proxy_list, 1):
            self.proxy_tree.insert('', 'end', values=(
                i,
                proxy['host'],
                proxy['port'],
                proxy['type'],
                proxy['username'] if proxy['username'] else '-',
                proxy['status'],
                proxy['latency'],
                "编辑 | 测试 | 删除"
            ))
            
        # 更新状态
        self.proxy_count_label.config(text=f"代理数量: {len(self.proxy_list)}")
        
    def show_add_proxy_dialog(self):
        """显示添加代理对话框"""
        self.show_proxy_dialog()
        
    def show_proxy_dialog(self, proxy_data=None, edit_index=None):
        """显示代理配置对话框"""
        dialog = tk.Toplevel(self)
        dialog.title("添加代理" if proxy_data is None else "编辑代理")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 居中显示
        dialog.geometry("+%d+%d" % (
            self.winfo_rootx() + 50,
            self.winfo_rooty() + 50
        ))
        
        # 表单
        form_frame = ttk.Frame(dialog)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 字段
        fields = [
            ("主机地址", "host"),
            ("端口", "port"),
            ("用户名", "username"),
            ("密码", "password")
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form_frame, text=label + ":").grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=(10, 0), pady=5)
            entries[key] = entry
            
            # 填充现有数据
            if proxy_data and key in proxy_data:
                entry.insert(0, str(proxy_data[key]))
                
        # 代理类型
        ttk.Label(form_frame, text="类型:").grid(row=len(fields), column=0, sticky=tk.W, pady=5)
        type_var = tk.StringVar(value=proxy_data.get('type', 'HTTP') if proxy_data else 'HTTP')
        type_combo = ttk.Combobox(form_frame, textvariable=type_var, values=['HTTP', 'HTTPS', 'SOCKS4', 'SOCKS5'], state="readonly")
        type_combo.grid(row=len(fields), column=1, padx=(10, 0), pady=5)
        
        # 按钮
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(fields)+2, column=0, columnspan=2, pady=20)
        
        def save_proxy():
            try:
                host = entries['host'].get().strip()
                port = int(entries['port'].get().strip())
                username = entries['username'].get().strip()
                password = entries['password'].get().strip()
                proxy_type = type_var.get()
                
                if not host or not port:
                    messagebox.showerror("错误", "主机地址和端口不能为空")
                    return
                    
                proxy_info = {
                    'host': host,
                    'port': port,
                    'type': proxy_type,
                    'username': username,
                    'password': password,
                    'status': '未测试',
                    'latency': '-'
                }
                
                if edit_index is not None:
                    self.proxy_list[edit_index] = proxy_info
                else:
                    self.proxy_list.append(proxy_info)
                    
                self.save_proxies()
                self.refresh_proxy_list()
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("错误", "端口必须是数字")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
                
        ttk.Button(button_frame, text="保存", command=save_proxy, style="primary.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT)
        
    def import_proxies(self):
        """批量导入代理"""
        file_path = filedialog.askopenfilename(
            title="选择代理文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                imported_count = 0
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        proxy_info = self.parse_proxy_string(line.strip())
                        if proxy_info:
                            self.proxy_list.append(proxy_info)
                            imported_count += 1
                            
                self.save_proxies()
                self.refresh_proxy_list()
                messagebox.showinfo("成功", f"成功导入 {imported_count} 个代理")
                
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {str(e)}")
                
    def test_proxy(self, proxy_info):
        """测试单个代理"""
        try:
            proxy_url = f"http://{proxy_info['host']}:{proxy_info['port']}"
            if proxy_info['username'] and proxy_info['password']:
                proxy_url = f"http://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"
                
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            import time
            start_time = time.time()
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
            latency = round((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                proxy_info['status'] = '可用'
                proxy_info['latency'] = f"{latency}ms"
                return True
            else:
                proxy_info['status'] = '不可用'
                proxy_info['latency'] = '-'
                return False
                
        except Exception as e:
            proxy_info['status'] = '错误'
            proxy_info['latency'] = '-'
            return False
            
    def test_selected_proxy(self):
        """测试选中的代理"""
        selection = self.proxy_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个代理")
            return
            
        item = selection[0]
        index = int(self.proxy_tree.item(item)['values'][0]) - 1
        
        if 0 <= index < len(self.proxy_list):
            self.status_label.config(text="正在测试代理...")
            
            def test_thread():
                self.test_proxy(self.proxy_list[index])
                self.after(0, lambda: [
                    self.refresh_proxy_list(),
                    self.status_label.config(text="测试完成")
                ])
                
            threading.Thread(target=test_thread, daemon=True).start()
            
    def test_all_proxies(self):
        """测试所有代理"""
        if not self.proxy_list:
            messagebox.showwarning("警告", "没有代理可测试")
            return
            
        self.status_label.config(text="正在测试所有代理...")
        self.test_all_btn.config(state='disabled')
        
        def test_all_thread():
            for i, proxy in enumerate(self.proxy_list):
                self.after(0, lambda i=i: self.status_label.config(text=f"正在测试代理 {i+1}/{len(self.proxy_list)}..."))
                self.test_proxy(proxy)
                
            self.after(0, lambda: [
                self.refresh_proxy_list(),
                self.status_label.config(text="所有代理测试完成"),
                self.test_all_btn.config(state='normal')
            ])
            
        threading.Thread(target=test_all_thread, daemon=True).start()
        
    def edit_selected_proxy(self, event=None):
        """编辑选中的代理"""
        selection = self.proxy_tree.selection()
        if not selection:
            if event is None:  # 不是双击事件
                messagebox.showwarning("警告", "请先选择一个代理")
            return
            
        item = selection[0]
        index = int(self.proxy_tree.item(item)['values'][0]) - 1
        
        if 0 <= index < len(self.proxy_list):
            self.show_proxy_dialog(self.proxy_list[index], index)
            
    def delete_selected_proxy(self):
        """删除选中的代理"""
        selection = self.proxy_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个代理")
            return
            
        if messagebox.askyesno("确认", "确定要删除选中的代理吗？"):
            item = selection[0]
            index = int(self.proxy_tree.item(item)['values'][0]) - 1
            
            if 0 <= index < len(self.proxy_list):
                del self.proxy_list[index]
                self.save_proxies()
                self.refresh_proxy_list()
                
    def clear_all_proxies(self):
        """清空所有代理"""
        if not self.proxy_list:
            messagebox.showwarning("警告", "代理列表已经是空的")
            return
            
        if messagebox.askyesno("确认", "确定要清空所有代理吗？此操作不可撤销！"):
            self.proxy_list.clear()
            self.save_proxies()
            self.refresh_proxy_list()
            
    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.proxy_tree.identify_row(event.y)
        if item:
            self.proxy_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def get_available_proxies(self):
        """获取可用的代理列表"""
        return [proxy for proxy in self.proxy_list if proxy['status'] == '可用'] 