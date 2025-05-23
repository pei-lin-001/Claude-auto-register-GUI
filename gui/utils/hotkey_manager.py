import tkinter as tk
from typing import Dict, Callable, Optional
import threading
import time

# 尝试导入keyboard库，如果未安装则提供降级方案
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("注意: 未安装keyboard库，全局快捷键功能不可用")

class HotkeyManager:
    """键盘快捷键管理器"""
    
    def __init__(self):
        self.hotkeys: Dict[str, Dict] = {}
        self.main_window = None
        self.is_listening = False
        self.listener_thread = None
        
        # 默认快捷键配置
        self.default_hotkeys = {
            'show_hide_window': {
                'combination': 'ctrl+shift+c',
                'description': '显示/隐藏主窗口',
                'callback': None,
                'enabled': True
            },
            'start_stop': {
                'combination': 'f5',
                'description': '开始/停止注册',
                'callback': None,
                'enabled': True
            },
            'emergency_stop': {
                'combination': 'ctrl+alt+s',
                'description': '紧急停止',
                'callback': None,
                'enabled': True
            },
            'open_logs': {
                'combination': 'ctrl+l',
                'description': '打开日志',
                'callback': None,
                'enabled': True
            },
            'open_config': {
                'combination': 'ctrl+comma',
                'description': '打开设置',
                'callback': None,
                'enabled': True
            }
        }
        
        self.hotkeys = self.default_hotkeys.copy()
        
        if not KEYBOARD_AVAILABLE:
            print("警告: 全局快捷键功能不可用，请安装keyboard库")
    
    def setup(self, main_window):
        """设置快捷键管理器"""
        self.main_window = main_window
        
        # 绑定默认回调函数
        self._setup_default_callbacks()
        
        if KEYBOARD_AVAILABLE:
            self.start_listening()
        else:
            # 降级方案：只设置窗口内快捷键
            self._setup_window_hotkeys()
    
    def _setup_default_callbacks(self):
        """设置默认回调函数"""
        self.hotkeys['show_hide_window']['callback'] = self._toggle_window
        self.hotkeys['start_stop']['callback'] = self._toggle_registration
        self.hotkeys['emergency_stop']['callback'] = self._emergency_stop
        self.hotkeys['open_logs']['callback'] = self._open_logs
        self.hotkeys['open_config']['callback'] = self._open_config
    
    def _setup_window_hotkeys(self):
        """设置窗口内快捷键（降级方案）"""
        if not self.main_window:
            return
        
        # 绑定窗口内快捷键
        window_bindings = {
            '<F5>': self._toggle_registration,
            '<Control-l>': self._open_logs,
            '<Control-comma>': self._open_config,
            '<Control-Alt-s>': self._emergency_stop
        }
        
        for key_combo, callback in window_bindings.items():
            try:
                self.main_window.bind(key_combo, lambda e, cb=callback: cb())
            except Exception as e:
                print(f"绑定快捷键失败 {key_combo}: {e}")
    
    def start_listening(self):
        """开始监听全局快捷键"""
        if not KEYBOARD_AVAILABLE or self.is_listening:
            return
        
        try:
            self.is_listening = True
            
            # 注册所有启用的快捷键
            for hotkey_id, hotkey_info in self.hotkeys.items():
                if hotkey_info['enabled'] and hotkey_info['callback']:
                    try:
                        keyboard.add_hotkey(
                            hotkey_info['combination'],
                            self._safe_callback_wrapper(hotkey_info['callback']),
                            suppress=False
                        )
                        print(f"已注册全局快捷键: {hotkey_info['combination']} - {hotkey_info['description']}")
                    except Exception as e:
                        print(f"注册快捷键失败 {hotkey_info['combination']}: {e}")
            
            print("全局快捷键监听已启动")
            
        except Exception as e:
            print(f"启动快捷键监听失败: {e}")
            self.is_listening = False
    
    def stop_listening(self):
        """停止监听全局快捷键"""
        if not KEYBOARD_AVAILABLE or not self.is_listening:
            return
        
        try:
            keyboard.unhook_all()
            self.is_listening = False
            print("全局快捷键监听已停止")
        except Exception as e:
            print(f"停止快捷键监听失败: {e}")
    
    def _safe_callback_wrapper(self, callback):
        """安全的回调包装器"""
        def wrapper():
            try:
                if self.main_window and callback:
                    # 在主线程中执行回调
                    self.main_window.after(0, callback)
            except Exception as e:
                print(f"快捷键回调执行失败: {e}")
        return wrapper
    
    def register_hotkey(self, hotkey_id: str, combination: str, callback: Callable, 
                       description: str = "", enabled: bool = True):
        """注册自定义快捷键"""
        self.hotkeys[hotkey_id] = {
            'combination': combination.lower(),
            'description': description,
            'callback': callback,
            'enabled': enabled
        }
        
        # 如果正在监听，重新注册快捷键
        if self.is_listening and KEYBOARD_AVAILABLE:
            self.stop_listening()
            self.start_listening()
    
    def unregister_hotkey(self, hotkey_id: str):
        """注销快捷键"""
        if hotkey_id in self.hotkeys:
            del self.hotkeys[hotkey_id]
            
            # 如果正在监听，重新注册快捷键
            if self.is_listening and KEYBOARD_AVAILABLE:
                self.stop_listening()
                self.start_listening()
    
    def enable_hotkey(self, hotkey_id: str):
        """启用快捷键"""
        if hotkey_id in self.hotkeys:
            self.hotkeys[hotkey_id]['enabled'] = True
            
            # 重新注册快捷键
            if self.is_listening and KEYBOARD_AVAILABLE:
                self.stop_listening()
                self.start_listening()
    
    def disable_hotkey(self, hotkey_id: str):
        """禁用快捷键"""
        if hotkey_id in self.hotkeys:
            self.hotkeys[hotkey_id]['enabled'] = False
            
            # 重新注册快捷键
            if self.is_listening and KEYBOARD_AVAILABLE:
                self.stop_listening()
                self.start_listening()
    
    def update_hotkey_combination(self, hotkey_id: str, new_combination: str):
        """更新快捷键组合"""
        if hotkey_id in self.hotkeys:
            self.hotkeys[hotkey_id]['combination'] = new_combination.lower()
            
            # 重新注册快捷键
            if self.is_listening and KEYBOARD_AVAILABLE:
                self.stop_listening()
                self.start_listening()
    
    def get_hotkeys(self) -> Dict[str, Dict]:
        """获取所有快捷键"""
        return self.hotkeys.copy()
    
    def get_hotkey(self, hotkey_id: str) -> Optional[Dict]:
        """获取指定快捷键"""
        return self.hotkeys.get(hotkey_id, {}).copy()
    
    def is_combination_available(self, combination: str) -> bool:
        """检查快捷键组合是否可用"""
        combination = combination.lower()
        
        for hotkey_info in self.hotkeys.values():
            if hotkey_info['combination'] == combination and hotkey_info['enabled']:
                return False
        
        return True
    
    # 默认快捷键回调函数
    def _toggle_window(self):
        """切换窗口显示/隐藏"""
        try:
            if self.main_window:
                if self.main_window.state() == 'withdrawn' or self.main_window.state() == 'iconic':
                    # 显示窗口
                    self.main_window.deiconify()
                    self.main_window.lift()
                    self.main_window.focus_force()
                else:
                    # 隐藏窗口
                    self.main_window.withdraw()
        except Exception as e:
            print(f"切换窗口显示状态失败: {e}")
    
    def _toggle_registration(self):
        """切换注册状态"""
        try:
            if self.main_window and hasattr(self.main_window, 'toggle_registration'):
                self.main_window.toggle_registration()
        except Exception as e:
            print(f"切换注册状态失败: {e}")
    
    def _emergency_stop(self):
        """紧急停止"""
        try:
            if self.main_window and hasattr(self.main_window, 'emergency_stop'):
                self.main_window.emergency_stop()
        except Exception as e:
            print(f"紧急停止失败: {e}")
    
    def _open_logs(self):
        """打开日志"""
        try:
            if self.main_window:
                # 显示窗口
                self.main_window.deiconify()
                self.main_window.lift()
                
                # 切换到日志页面
                if hasattr(self.main_window, 'switch_to_logs'):
                    self.main_window.switch_to_logs()
        except Exception as e:
            print(f"打开日志失败: {e}")
    
    def _open_config(self):
        """打开设置"""
        try:
            if self.main_window:
                # 显示窗口
                self.main_window.deiconify()
                self.main_window.lift()
                
                # 切换到设置页面
                if hasattr(self.main_window, 'switch_to_config'):
                    self.main_window.switch_to_config()
        except Exception as e:
            print(f"打开设置失败: {e}")

class HotkeyConfigDialog:
    """快捷键配置对话框"""
    
    def __init__(self, parent, hotkey_manager: HotkeyManager):
        self.parent = parent
        self.hotkey_manager = hotkey_manager
        self.dialog = None
        self.hotkey_vars = {}
        self.enabled_vars = {}
        
    def show(self):
        """显示配置对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("快捷键设置")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # 使对话框模态
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self._create_widgets()
        self._load_current_settings()
        
        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
    
    def _create_widgets(self):
        """创建控件"""
        # 标题
        title_label = tk.Label(self.dialog, text="快捷键设置", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # 说明
        info_label = tk.Label(
            self.dialog, 
            text="配置全局快捷键。修改后需要重启应用程序才能生效。",
            fg="gray"
        )
        info_label.pack(pady=(0, 10))
        
        # 快捷键列表框架
        list_frame = tk.Frame(self.dialog)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # 创建快捷键配置项
        self.config_frame = tk.Frame(list_frame)
        self.config_frame.pack(fill="both", expand=True)
        
        # 按钮框架
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        # 按钮
        tk.Button(button_frame, text="重置默认", command=self._reset_to_default).pack(side="left", padx=5)
        tk.Button(button_frame, text="应用", command=self._apply_changes).pack(side="left", padx=5)
        tk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side="left", padx=5)
        tk.Button(button_frame, text="确定", command=self._ok_clicked).pack(side="left", padx=5)
    
    def _load_current_settings(self):
        """加载当前设置"""
        hotkeys = self.hotkey_manager.get_hotkeys()
        
        row = 0
        for hotkey_id, hotkey_info in hotkeys.items():
            # 启用复选框
            enabled_var = tk.BooleanVar(value=hotkey_info['enabled'])
            self.enabled_vars[hotkey_id] = enabled_var
            
            enabled_cb = tk.Checkbutton(
                self.config_frame,
                variable=enabled_var,
                text=""
            )
            enabled_cb.grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            # 描述标签
            desc_label = tk.Label(
                self.config_frame,
                text=hotkey_info['description'],
                width=20,
                anchor="w"
            )
            desc_label.grid(row=row, column=1, padx=5, pady=2, sticky="w")
            
            # 快捷键输入框
            hotkey_var = tk.StringVar(value=hotkey_info['combination'])
            self.hotkey_vars[hotkey_id] = hotkey_var
            
            hotkey_entry = tk.Entry(
                self.config_frame,
                textvariable=hotkey_var,
                width=20
            )
            hotkey_entry.grid(row=row, column=2, padx=5, pady=2)
            
            row += 1
    
    def _reset_to_default(self):
        """重置为默认值"""
        if tk.messagebox.askyesno("确认重置", "确定要重置所有快捷键为默认值吗？"):
            for hotkey_id in self.hotkey_vars:
                if hotkey_id in self.hotkey_manager.default_hotkeys:
                    default_hotkey = self.hotkey_manager.default_hotkeys[hotkey_id]
                    self.hotkey_vars[hotkey_id].set(default_hotkey['combination'])
                    self.enabled_vars[hotkey_id].set(default_hotkey['enabled'])
    
    def _apply_changes(self):
        """应用更改"""
        try:
            # 验证快捷键
            for hotkey_id, hotkey_var in self.hotkey_vars.items():
                combination = hotkey_var.get().strip()
                if not combination:
                    tk.messagebox.showerror("错误", f"快捷键 {hotkey_id} 不能为空")
                    return
            
            # 检查重复
            combinations = []
            for hotkey_id, hotkey_var in self.hotkey_vars.items():
                if self.enabled_vars[hotkey_id].get():
                    combination = hotkey_var.get().strip().lower()
                    if combination in combinations:
                        tk.messagebox.showerror("错误", f"快捷键重复: {combination}")
                        return
                    combinations.append(combination)
            
            # 应用更改
            for hotkey_id, hotkey_var in self.hotkey_vars.items():
                combination = hotkey_var.get().strip()
                enabled = self.enabled_vars[hotkey_id].get()
                
                self.hotkey_manager.update_hotkey_combination(hotkey_id, combination)
                if enabled:
                    self.hotkey_manager.enable_hotkey(hotkey_id)
                else:
                    self.hotkey_manager.disable_hotkey(hotkey_id)
            
            tk.messagebox.showinfo("成功", "快捷键设置已更新")
            
        except Exception as e:
            tk.messagebox.showerror("错误", f"应用设置失败: {str(e)}")
    
    def _ok_clicked(self):
        """确定按钮点击"""
        self._apply_changes()
        self.dialog.destroy()

# 全局快捷键管理器实例
hotkey_manager = HotkeyManager()

def create_hotkey_fallback():
    """降级方案：创建简单的窗口内快捷键"""
    print("使用降级方案：仅支持窗口内快捷键")
    
    class FallbackHotkeyManager:
        def __init__(self):
            self.main_window = None
            self.hotkeys = {}
        
        def setup(self, main_window):
            self.main_window = main_window
            self._setup_window_hotkeys()
        
        def _setup_window_hotkeys(self):
            if not self.main_window:
                return
            
            # 绑定基本快捷键
            bindings = {
                '<F5>': lambda e: self._trigger_callback('start_stop'),
                '<Control-l>': lambda e: self._trigger_callback('open_logs'),
                '<Control-comma>': lambda e: self._trigger_callback('open_config'),
            }
            
            for key, callback in bindings.items():
                try:
                    self.main_window.bind(key, callback)
                except Exception as e:
                    print(f"绑定快捷键失败 {key}: {e}")
        
        def _trigger_callback(self, action):
            if action == 'start_stop' and hasattr(self.main_window, 'toggle_registration'):
                self.main_window.toggle_registration()
            elif action == 'open_logs' and hasattr(self.main_window, 'switch_to_logs'):
                self.main_window.switch_to_logs()
            elif action == 'open_config' and hasattr(self.main_window, 'switch_to_config'):
                self.main_window.switch_to_config()
        
        def start_listening(self): pass
        def stop_listening(self): pass
        def get_hotkeys(self): return {}
    
    return FallbackHotkeyManager()

# 如果keyboard不可用，使用降级方案
if not KEYBOARD_AVAILABLE:
    hotkey_manager = create_hotkey_fallback() 