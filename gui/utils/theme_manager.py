import json
import os
from typing import Dict, Any
import tkinter as tk
from tkinter import ttk

class ThemeManager:
    """主题管理器 - 支持明暗主题切换"""
    
    def __init__(self):
        self.themes = {
            'light': {
                'name': '浅色主题',
                'colors': {
                    'primary': '#2E86AB',
                    'primary_light': '#4A9BC7',
                    'primary_dark': '#1B5E7A',
                    'secondary': '#6C757D',
                    'success': '#28A745',
                    'warning': '#FFC107',
                    'danger': '#DC3545',
                    'info': '#17A2B8',
                    'light': '#F8F9FA',
                    'dark': '#343A40',
                    'white': '#FFFFFF',
                    'black': '#000000',
                    
                    # 背景色
                    'bg_primary': '#FFFFFF',
                    'bg_secondary': '#F8F9FA',
                    'bg_tertiary': '#E9ECEF',
                    
                    # 文本色
                    'text_primary': '#212529',
                    'text_secondary': '#6C757D',
                    'text_muted': '#868E96',
                    
                    # 边框色
                    'border_primary': '#DEE2E6',
                    'border_secondary': '#CED4DA',
                    
                    # 按钮色
                    'btn_primary': '#2E86AB',
                    'btn_primary_hover': '#1B5E7A',
                    'btn_secondary': '#6C757D',
                    'btn_secondary_hover': '#545B62',
                    
                    # 输入框色
                    'input_bg': '#FFFFFF',
                    'input_border': '#CED4DA',
                    'input_focus': '#2E86AB',
                    
                    # 表格色
                    'table_header': '#E9ECEF',
                    'table_row_even': '#FFFFFF',
                    'table_row_odd': '#F8F9FA',
                    'table_hover': '#E3F2FD',
                    
                    # 状态栏色
                    'status_bg': '#F8F9FA',
                    'status_text': '#6C757D',
                }
            },
            'dark': {
                'name': '深色主题',
                'colors': {
                    'primary': '#4A9BC7',
                    'primary_light': '#6BB6D6',
                    'primary_dark': '#2E86AB',
                    'secondary': '#ADB5BD',
                    'success': '#40C057',
                    'warning': '#FFD43B',
                    'danger': '#FA5252',
                    'info': '#339AF0',
                    'light': '#495057',
                    'dark': '#212529',
                    'white': '#FFFFFF',
                    'black': '#000000',
                    
                    # 背景色
                    'bg_primary': '#212529',
                    'bg_secondary': '#343A40',
                    'bg_tertiary': '#495057',
                    
                    # 文本色
                    'text_primary': '#F8F9FA',
                    'text_secondary': '#CED4DA',
                    'text_muted': '#ADB5BD',
                    
                    # 边框色
                    'border_primary': '#495057',
                    'border_secondary': '#6C757D',
                    
                    # 按钮色
                    'btn_primary': '#4A9BC7',
                    'btn_primary_hover': '#6BB6D6',
                    'btn_secondary': '#ADB5BD',
                    'btn_secondary_hover': '#CED4DA',
                    
                    # 输入框色
                    'input_bg': '#343A40',
                    'input_border': '#6C757D',
                    'input_focus': '#4A9BC7',
                    
                    # 表格色
                    'table_header': '#495057',
                    'table_row_even': '#343A40',
                    'table_row_odd': '#2B3035',
                    'table_hover': '#1A365D',
                    
                    # 状态栏色
                    'status_bg': '#343A40',
                    'status_text': '#CED4DA',
                }
            }
        }
        
        self.current_theme = 'light'
        self.config_file = os.path.join(os.path.dirname(__file__), '../resources/theme_config.json')
        self.callbacks = []
        
        # 加载保存的主题设置
        self.load_theme_config()
    
    def get_color(self, color_name: str) -> str:
        """获取当前主题的颜色值"""
        return self.themes[self.current_theme]['colors'].get(color_name, '#000000')
    
    def get_theme_colors(self) -> Dict[str, str]:
        """获取当前主题的所有颜色"""
        return self.themes[self.current_theme]['colors'].copy()
    
    def get_available_themes(self) -> Dict[str, str]:
        """获取可用主题列表"""
        return {theme_id: theme_data['name'] for theme_id, theme_data in self.themes.items()}
    
    def set_theme(self, theme_name: str):
        """切换主题"""
        if theme_name in self.themes:
            old_theme = self.current_theme
            self.current_theme = theme_name
            self.save_theme_config()
            
            # 通知所有注册的回调函数
            for callback in self.callbacks:
                try:
                    callback(old_theme, theme_name)
                except Exception as e:
                    print(f"主题切换回调错误: {e}")
    
    def register_theme_change_callback(self, callback):
        """注册主题切换回调函数"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def unregister_theme_change_callback(self, callback):
        """注销主题切换回调函数"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def apply_theme_to_widget(self, widget, widget_type='default'):
        """将当前主题应用到指定控件"""
        colors = self.get_theme_colors()
        
        try:
            if widget_type == 'frame':
                widget.configure(bg=colors['bg_primary'])
            elif widget_type == 'label':
                widget.configure(
                    bg=colors['bg_primary'],
                    fg=colors['text_primary']
                )
            elif widget_type == 'button':
                widget.configure(
                    bg=colors['btn_primary'],
                    fg=colors['white'],
                    activebackground=colors['btn_primary_hover'],
                    activeforeground=colors['white']
                )
            elif widget_type == 'entry':
                widget.configure(
                    bg=colors['input_bg'],
                    fg=colors['text_primary'],
                    insertbackground=colors['text_primary'],
                    selectbackground=colors['primary'],
                    selectforeground=colors['white']
                )
            elif widget_type == 'text':
                widget.configure(
                    bg=colors['input_bg'],
                    fg=colors['text_primary'],
                    insertbackground=colors['text_primary'],
                    selectbackground=colors['primary'],
                    selectforeground=colors['white']
                )
            elif widget_type == 'listbox':
                widget.configure(
                    bg=colors['input_bg'],
                    fg=colors['text_primary'],
                    selectbackground=colors['primary'],
                    selectforeground=colors['white']
                )
        except Exception as e:
            print(f"应用主题到控件时出错: {e}")
    
    def get_ttk_style_config(self) -> Dict[str, Any]:
        """获取TTK样式配置"""
        colors = self.get_theme_colors()
        
        return {
            'TFrame': {
                'configure': {'background': colors['bg_primary']}
            },
            'TLabel': {
                'configure': {
                    'background': colors['bg_primary'],
                    'foreground': colors['text_primary']
                }
            },
            'TButton': {
                'configure': {
                    'background': colors['btn_primary'],
                    'foreground': colors['white'],
                    'borderwidth': 0,
                    'focuscolor': 'none'
                },
                'map': {
                    'background': [
                        ('active', colors['btn_primary_hover']),
                        ('pressed', colors['btn_primary_dark'])
                    ]
                }
            },
            'TEntry': {
                'configure': {
                    'fieldbackground': colors['input_bg'],
                    'foreground': colors['text_primary'],
                    'bordercolor': colors['input_border'],
                    'insertcolor': colors['text_primary']
                },
                'map': {
                    'bordercolor': [('focus', colors['input_focus'])]
                }
            },
            'Treeview': {
                'configure': {
                    'background': colors['table_row_even'],
                    'foreground': colors['text_primary'],
                    'fieldbackground': colors['table_row_even']
                },
                'map': {
                    'background': [('selected', colors['primary'])],
                    'foreground': [('selected', colors['white'])]
                }
            },
            'Treeview.Heading': {
                'configure': {
                    'background': colors['table_header'],
                    'foreground': colors['text_primary'],
                    'relief': 'flat'
                }
            }
        }
    
    def save_theme_config(self):
        """保存主题配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            config = {
                'current_theme': self.current_theme,
                'version': '1.0'
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存主题配置失败: {e}")
    
    def load_theme_config(self):
        """从文件加载主题配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    theme = config.get('current_theme', 'light')
                    if theme in self.themes:
                        self.current_theme = theme
        except Exception as e:
            print(f"加载主题配置失败: {e}")
            self.current_theme = 'light'

# 全局主题管理器实例
theme_manager = ThemeManager() 