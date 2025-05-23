import json
import os
from typing import Dict, Any, Optional
from tkinter import filedialog, messagebox
import shutil
from datetime import datetime

class GUIConfigManager:
    """GUI配置管理器 - 支持配置导入导出"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(__file__), '../resources')
        self.config_file = os.path.join(self.config_dir, 'gui_config.json')
        self.backup_dir = os.path.join(self.config_dir, 'backups')
        
        # 默认配置
        self.default_config = {
            'version': '1.0',
            'window': {
                'width': 1200,
                'height': 800,
                'x': 100,
                'y': 100,
                'maximized': False,
                'always_on_top': False
            },
            'theme': {
                'current': 'light',
                'auto_detect': False
            },
            'general': {
                'language': 'zh_CN',
                'show_splash': True,
                'minimize_to_tray': True,
                'close_to_tray': True,
                'auto_save': True,
                'auto_save_interval': 300  # 5分钟
            },
            'hotkeys': {
                'show_hide_window': 'Ctrl+Shift+C',
                'start_stop': 'F5',
                'emergency_stop': 'Ctrl+Alt+S',
                'open_logs': 'Ctrl+L',
                'open_config': 'Ctrl+Comma'
            },
            'dashboard': {
                'refresh_interval': 5,
                'show_charts': True,
                'chart_history_days': 7
            },
            'proxy_manager': {
                'auto_test_on_add': True,
                'test_timeout': 10,
                'batch_test_size': 5
            },
            'batch_register': {
                'default_batch_size': 3,
                'retry_failed': True,
                'max_retries': 3,
                'delay_between_accounts': 30
            },
            'logs': {
                'max_lines': 1000,
                'auto_scroll': True,
                'word_wrap': True,
                'show_timestamps': True
            }
        }
        
        self.config = self.default_config.copy()
        self.load_config()
    
    def get(self, key_path: str, default=None) -> Any:
        """获取配置值，支持嵌套路径，如 'window.width'"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """设置配置值，支持嵌套路径"""
        keys = key_path.split('.')
        config = self.config
        
        # 导航到最后一级的父节点
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # 设置值
        config[keys[-1]] = value
        
        # 自动保存
        if self.get('general.auto_save', True):
            self.save_config()
    
    def update_section(self, section: str, values: Dict[str, Any]):
        """更新配置节"""
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section].update(values)
        
        if self.get('general.auto_save', True):
            self.save_config()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取配置节"""
        return self.config.get(section, {}).copy()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    
                # 合并配置，保持默认配置的完整性
                self.config = self._merge_config(self.default_config, loaded_config)
            else:
                # 首次运行，使用默认配置
                self.config = self.default_config.copy()
                self.save_config()
                
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.config = self.default_config.copy()
    
    def save_config(self):
        """保存配置文件"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def export_config(self, filepath: Optional[str] = None) -> str:
        """导出配置到文件"""
        if filepath is None:
            filepath = filedialog.asksaveasfilename(
                title="导出配置",
                defaultextension=".json",
                filetypes=[
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ],
                initialname=f"claude_gui_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
        
        if not filepath:
            return ""
        
        try:
            # 创建导出配置，包含版本信息和导出时间
            export_data = {
                'export_info': {
                    'version': self.config.get('version', '1.0'),
                    'export_time': datetime.now().isoformat(),
                    'app_name': 'Claude Auto Register GUI'
                },
                'config': self.config
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("导出成功", f"配置已成功导出到:\n{filepath}")
            return filepath
            
        except Exception as e:
            messagebox.showerror("导出失败", f"导出配置失败:\n{str(e)}")
            return ""
    
    def import_config(self, filepath: Optional[str] = None) -> bool:
        """从文件导入配置"""
        if filepath is None:
            filepath = filedialog.askopenfilename(
                title="导入配置",
                filetypes=[
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )
        
        if not filepath or not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 检查导入数据格式
            if 'config' in import_data:
                # 新格式，包含导出信息
                imported_config = import_data['config']
                export_info = import_data.get('export_info', {})
                
                # 显示导入信息
                info_msg = f"准备导入配置:\n"
                if 'export_time' in export_info:
                    info_msg += f"导出时间: {export_info['export_time']}\n"
                if 'app_name' in export_info:
                    info_msg += f"应用: {export_info['app_name']}\n"
                info_msg += f"\n是否继续导入？"
                
                if not messagebox.askyesno("确认导入", info_msg):
                    return False
            else:
                # 旧格式，直接作为配置
                imported_config = import_data
            
            # 备份当前配置
            self.create_backup()
            
            # 合并导入的配置
            self.config = self._merge_config(self.default_config, imported_config)
            
            # 保存配置
            self.save_config()
            
            messagebox.showinfo("导入成功", "配置已成功导入并保存")
            return True
            
        except Exception as e:
            messagebox.showerror("导入失败", f"导入配置失败:\n{str(e)}")
            return False
    
    def reset_to_default(self):
        """重置为默认配置"""
        if messagebox.askyesno("确认重置", "确定要重置所有配置为默认值吗？\n此操作无法撤销。"):
            # 备份当前配置
            self.create_backup()
            
            # 重置配置
            self.config = self.default_config.copy()
            self.save_config()
            
            messagebox.showinfo("重置成功", "配置已重置为默认值")
            return True
        return False
    
    def create_backup(self) -> str:
        """创建配置备份"""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            
            backup_filename = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            shutil.copy2(self.config_file, backup_path)
            
            # 只保留最近10个备份
            self._cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            print(f"创建备份失败: {e}")
            return ""
    
    def list_backups(self) -> list:
        """列出所有备份文件"""
        try:
            if not os.path.exists(self.backup_dir):
                return []
            
            backups = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('config_backup_') and filename.endswith('.json'):
                    filepath = os.path.join(self.backup_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    backups.append({
                        'filename': filename,
                        'filepath': filepath,
                        'modified_time': datetime.fromtimestamp(mtime),
                        'size': os.path.getsize(filepath)
                    })
            
            # 按修改时间倒序排列
            backups.sort(key=lambda x: x['modified_time'], reverse=True)
            return backups
            
        except Exception as e:
            print(f"列出备份失败: {e}")
            return []
    
    def restore_backup(self, backup_filepath: str) -> bool:
        """从备份恢复配置"""
        try:
            if not os.path.exists(backup_filepath):
                messagebox.showerror("错误", "备份文件不存在")
                return False
            
            # 确认恢复
            backup_name = os.path.basename(backup_filepath)
            if not messagebox.askyesno("确认恢复", f"确定要从备份恢复配置吗？\n备份文件: {backup_name}\n\n当前配置将被覆盖。"):
                return False
            
            # 恢复配置
            shutil.copy2(backup_filepath, self.config_file)
            self.load_config()
            
            messagebox.showinfo("恢复成功", "配置已从备份恢复")
            return True
            
        except Exception as e:
            messagebox.showerror("恢复失败", f"从备份恢复配置失败:\n{str(e)}")
            return False
    
    def _merge_config(self, default: dict, loaded: dict) -> dict:
        """合并配置，保持默认配置的结构"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _cleanup_old_backups(self, keep_count: int = 10):
        """清理旧备份，只保留指定数量"""
        try:
            backups = self.list_backups()
            
            if len(backups) > keep_count:
                # 删除多余的旧备份
                for backup in backups[keep_count:]:
                    os.remove(backup['filepath'])
                    
        except Exception as e:
            print(f"清理旧备份失败: {e}")

# 全局配置管理器实例
gui_config = GUIConfigManager() 