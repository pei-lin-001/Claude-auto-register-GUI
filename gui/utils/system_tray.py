import tkinter as tk
from tkinter import messagebox
import threading
import os
import sys
from typing import Callable, Optional

# 尝试导入pystray库，如果未安装则提供降级方案
try:
    import pystray
    from pystray import MenuItem as MenuItem_
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("注意: 未安装pystray库，系统托盘功能不可用")

class SystemTray:
    """系统托盘管理器"""
    
    def __init__(self, app_name: str = "Claude Auto Register"):
        self.app_name = app_name
        self.tray_icon = None
        self.main_window = None
        self.is_running = False
        self.show_callback = None
        self.quit_callback = None
        
        # 状态相关
        self.status = "待机"
        self.registered_count = 0
        self.failed_count = 0
        
        if not TRAY_AVAILABLE:
            print("警告: 系统托盘功能不可用，请安装pystray和pillow库")
    
    def create_icon(self, color: str = "#2E86AB") -> Optional[Image.Image]:
        """创建托盘图标"""
        if not TRAY_AVAILABLE:
            return None
        
        try:
            # 创建32x32的图标
            width = 32
            height = 32
            image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            dc = ImageDraw.Draw(image)
            
            # 绘制圆形背景
            margin = 2
            dc.ellipse([margin, margin, width-margin, height-margin], fill=color)
            
            # 绘制字母C
            font_size = 16
            text = "C"
            # 简单的文字绘制（居中）
            text_bbox = dc.textbbox((0, 0), text)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = (width - text_width) // 2
            text_y = (height - text_height) // 2 - 2
            
            dc.text((text_x, text_y), text, fill='white')
            
            return image
        except Exception as e:
            print(f"创建托盘图标失败: {e}")
            return None
    
    def create_menu(self):
        """创建托盘菜单"""
        if not TRAY_AVAILABLE:
            return None
        
        menu_items = [
            MenuItem_("显示主窗口", self._show_window, default=True),
            MenuItem_("状态信息", self._show_status),
            pystray.Menu.SEPARATOR,
            MenuItem_("开始注册", self._start_registration),
            MenuItem_("停止注册", self._stop_registration),
            pystray.Menu.SEPARATOR,
            MenuItem_("打开日志", self._open_logs),
            MenuItem_("设置", self._open_settings),
            pystray.Menu.SEPARATOR,
            MenuItem_("退出程序", self._quit_application)
        ]
        
        return pystray.Menu(*menu_items)
    
    def setup(self, main_window, show_callback: Callable = None, quit_callback: Callable = None):
        """设置托盘"""
        self.main_window = main_window
        self.show_callback = show_callback
        self.quit_callback = quit_callback
        
        if not TRAY_AVAILABLE:
            return False
        
        try:
            icon_image = self.create_icon()
            if icon_image is None:
                return False
            
            self.tray_icon = pystray.Icon(
                self.app_name,
                icon_image,
                menu=self.create_menu(),
                title=f"{self.app_name} - {self.status}"
            )
            
            return True
        except Exception as e:
            print(f"设置系统托盘失败: {e}")
            return False
    
    def show(self):
        """显示托盘图标"""
        if not TRAY_AVAILABLE or self.tray_icon is None:
            return
        
        try:
            if not self.is_running:
                self.is_running = True
                # 在单独线程中运行托盘
                tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
                tray_thread.start()
        except Exception as e:
            print(f"显示系统托盘失败: {e}")
    
    def hide(self):
        """隐藏托盘图标"""
        if self.tray_icon and self.is_running:
            try:
                self.tray_icon.stop()
                self.is_running = False
            except Exception as e:
                print(f"隐藏系统托盘失败: {e}")
    
    def update_status(self, status: str, registered_count: int = None, failed_count: int = None):
        """更新状态信息"""
        self.status = status
        if registered_count is not None:
            self.registered_count = registered_count
        if failed_count is not None:
            self.failed_count = failed_count
        
        if self.tray_icon:
            try:
                # 更新托盘图标标题
                tooltip = f"{self.app_name} - {self.status}"
                if self.registered_count > 0 or self.failed_count > 0:
                    tooltip += f"\n成功: {self.registered_count}, 失败: {self.failed_count}"
                
                self.tray_icon.title = tooltip
                
                # 根据状态更新图标颜色
                color = "#2E86AB"  # 默认蓝色
                if status == "运行中":
                    color = "#28A745"  # 绿色
                elif status == "错误":
                    color = "#DC3545"  # 红色
                elif status == "暂停":
                    color = "#FFC107"  # 黄色
                
                new_icon = self.create_icon(color)
                if new_icon:
                    self.tray_icon.icon = new_icon
                    
            except Exception as e:
                print(f"更新托盘状态失败: {e}")
    
    def show_notification(self, title: str, message: str, timeout: int = 5):
        """显示系统通知"""
        if self.tray_icon:
            try:
                self.tray_icon.notify(message, title)
            except Exception as e:
                print(f"显示通知失败: {e}")
        else:
            # 降级到tkinter消息框
            messagebox.showinfo(title, message)
    
    # 菜单项回调函数
    def _show_window(self, icon=None, item=None):
        """显示主窗口"""
        if self.main_window:
            try:
                self.main_window.after(0, self._restore_window)
            except Exception as e:
                print(f"显示主窗口失败: {e}")
    
    def _restore_window(self):
        """恢复主窗口（在主线程中执行）"""
        try:
            self.main_window.deiconify()
            self.main_window.lift()
            self.main_window.focus_force()
        except Exception as e:
            print(f"恢复主窗口失败: {e}")
    
    def _show_status(self, icon=None, item=None):
        """显示状态信息"""
        status_msg = f"当前状态: {self.status}\n"
        status_msg += f"成功注册: {self.registered_count}\n"
        status_msg += f"注册失败: {self.failed_count}"
        
        if self.main_window:
            self.main_window.after(0, lambda: messagebox.showinfo("状态信息", status_msg))
    
    def _start_registration(self, icon=None, item=None):
        """开始注册"""
        if self.main_window:
            # 触发主窗口的开始注册事件
            self.main_window.after(0, self._trigger_start)
    
    def _trigger_start(self):
        """触发开始注册（在主线程中执行）"""
        try:
            # 假设主窗口有start_registration方法
            if hasattr(self.main_window, 'start_registration'):
                self.main_window.start_registration()
        except Exception as e:
            print(f"开始注册失败: {e}")
    
    def _stop_registration(self, icon=None, item=None):
        """停止注册"""
        if self.main_window:
            # 触发主窗口的停止注册事件
            self.main_window.after(0, self._trigger_stop)
    
    def _trigger_stop(self):
        """触发停止注册（在主线程中执行）"""
        try:
            # 假设主窗口有stop_registration方法
            if hasattr(self.main_window, 'stop_registration'):
                self.main_window.stop_registration()
        except Exception as e:
            print(f"停止注册失败: {e}")
    
    def _open_logs(self, icon=None, item=None):
        """打开日志"""
        if self.main_window:
            self.main_window.after(0, self._switch_to_logs)
    
    def _switch_to_logs(self):
        """切换到日志页面（在主线程中执行）"""
        try:
            # 显示主窗口并切换到日志页面
            self.main_window.deiconify()
            self.main_window.lift()
            
            # 假设主窗口有switch_to_logs方法
            if hasattr(self.main_window, 'switch_to_logs'):
                self.main_window.switch_to_logs()
        except Exception as e:
            print(f"打开日志失败: {e}")
    
    def _open_settings(self, icon=None, item=None):
        """打开设置"""
        if self.main_window:
            self.main_window.after(0, self._switch_to_settings)
    
    def _switch_to_settings(self):
        """切换到设置页面（在主线程中执行）"""
        try:
            # 显示主窗口并切换到设置页面
            self.main_window.deiconify()
            self.main_window.lift()
            
            # 假设主窗口有switch_to_settings方法
            if hasattr(self.main_window, 'switch_to_settings'):
                self.main_window.switch_to_settings()
        except Exception as e:
            print(f"打开设置失败: {e}")
    
    def _quit_application(self, icon=None, item=None):
        """退出应用程序"""
        if self.quit_callback:
            self.quit_callback()
        elif self.main_window:
            self.main_window.after(0, self._quit_app)
    
    def _quit_app(self):
        """退出应用程序（在主线程中执行）"""
        try:
            # 隐藏托盘图标
            self.hide()
            
            # 退出主窗口
            if self.main_window:
                self.main_window.quit()
                self.main_window.destroy()
        except Exception as e:
            print(f"退出应用程序失败: {e}")

# 全局系统托盘实例
system_tray = SystemTray()

def create_tray_icon_fallback():
    """降级方案：创建简单的最小化到任务栏功能"""
    print("使用降级方案：最小化到任务栏")
    
    class FallbackTray:
        def __init__(self):
            self.main_window = None
        
        def setup(self, main_window, show_callback=None, quit_callback=None):
            self.main_window = main_window
            return True
        
        def show(self):
            pass
        
        def hide(self):
            pass
        
        def update_status(self, status, registered_count=None, failed_count=None):
            # 更新窗口标题显示状态
            if self.main_window:
                title = f"Claude Auto Register - {status}"
                if registered_count is not None and failed_count is not None:
                    title += f" (成功:{registered_count}, 失败:{failed_count})"
                self.main_window.title(title)
        
        def show_notification(self, title, message, timeout=5):
            if self.main_window:
                messagebox.showinfo(title, message)
    
    return FallbackTray()

# 如果pystray不可用，使用降级方案
if not TRAY_AVAILABLE:
    system_tray = create_tray_icon_fallback() 