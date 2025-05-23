"""
日志服务模块

提供日志管理相关的服务功能。
"""

import os
import glob
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path


class LogService:
    """日志服务类"""
    
    def __init__(self):
        self.log_dir = "logs"
        self.current_log_file = None
        self.log_listeners = []
        self.status_callback = None
        
        # 确保日志目录存在
        os.makedirs(self.log_dir, exist_ok=True)
        
    def set_callbacks(self, status_callback=None):
        """设置回调函数"""
        self.status_callback = status_callback
        
    def _update_status(self, message):
        """更新状态"""
        if self.status_callback:
            self.status_callback(message)
    
    def add_log_listener(self, callback):
        """添加日志监听器"""
        if callback not in self.log_listeners:
            self.log_listeners.append(callback)
    
    def remove_log_listener(self, callback):
        """移除日志监听器"""
        if callback in self.log_listeners:
            self.log_listeners.remove(callback)
    
    def notify_log_listeners(self, log_entry):
        """通知所有日志监听器"""
        for callback in self.log_listeners:
            try:
                callback(log_entry)
            except:
                pass
    
    def get_log_files(self):
        """获取所有日志文件"""
        try:
            log_pattern = os.path.join(self.log_dir, "*.log")
            log_files = glob.glob(log_pattern)
            
            # 按修改时间排序（最新的在前）
            log_files.sort(key=os.path.getmtime, reverse=True)
            
            return log_files
            
        except Exception as e:
            self._update_status(f"获取日志文件失败: {str(e)}")
            return []
    
    def read_log_file(self, file_path, lines=None):
        """读取日志文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if lines is None:
                    content = f.read()
                else:
                    # 读取最后N行
                    all_lines = f.readlines()
                    content = ''.join(all_lines[-lines:]) if all_lines else ""
            
            return content
            
        except Exception as e:
            self._update_status(f"读取日志文件失败: {str(e)}")
            return ""
    
    def get_recent_logs(self, lines=100):
        """获取最近的日志条目"""
        try:
            log_files = self.get_log_files()
            if not log_files:
                return []
            
            # 从最新的日志文件开始读取
            recent_logs = []
            remaining_lines = lines
            
            for log_file in log_files:
                if remaining_lines <= 0:
                    break
                    
                content = self.read_log_file(log_file, remaining_lines)
                if content:
                    lines_in_file = content.strip().split('\n')
                    recent_logs.extend(lines_in_file)
                    remaining_lines -= len(lines_in_file)
            
            # 只返回所需的行数
            return recent_logs[:lines]
            
        except Exception as e:
            self._update_status(f"获取最近日志失败: {str(e)}")
            return []
    
    def filter_logs_by_level(self, logs, level):
        """按日志级别过滤"""
        if level.upper() == "ALL":
            return logs
        
        filtered_logs = []
        level_keywords = {
            "DEBUG": ["DEBUG"],
            "INFO": ["INFO"],
            "WARNING": ["WARNING", "WARN"],
            "ERROR": ["ERROR"],
            "CRITICAL": ["CRITICAL", "FATAL"]
        }
        
        keywords = level_keywords.get(level.upper(), [])
        
        for log in logs:
            for keyword in keywords:
                if keyword in log.upper():
                    filtered_logs.append(log)
                    break
        
        return filtered_logs
    
    def search_logs(self, keyword, log_files=None):
        """在日志中搜索关键词"""
        try:
            if log_files is None:
                log_files = self.get_log_files()
            
            search_results = []
            
            for log_file in log_files:
                content = self.read_log_file(log_file)
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    if keyword.lower() in line.lower():
                        search_results.append({
                            'file': log_file,
                            'line_number': line_num,
                            'content': line.strip(),
                            'timestamp': self._extract_timestamp(line)
                        })
            
            return search_results
            
        except Exception as e:
            self._update_status(f"搜索日志失败: {str(e)}")
            return []
    
    def _extract_timestamp(self, log_line):
        """从日志行中提取时间戳"""
        try:
            # 假设日志格式为：YYYY-MM-DD HH:MM:SS - ...
            if ' - ' in log_line:
                timestamp_str = log_line.split(' - ')[0]
                return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except:
            pass
        
        return None
    
    def clear_old_logs(self, days=7):
        """清理旧日志文件"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            log_files = self.get_log_files()
            
            deleted_count = 0
            
            for log_file in log_files:
                file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                
                if file_time < cutoff_date:
                    os.remove(log_file)
                    deleted_count += 1
            
            self._update_status(f"已清理 {deleted_count} 个旧日志文件")
            return deleted_count
            
        except Exception as e:
            self._update_status(f"清理日志失败: {str(e)}")
            return 0
    
    def export_logs(self, file_path, start_date=None, end_date=None, level=None):
        """导出日志"""
        try:
            log_files = self.get_log_files()
            
            with open(file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(f"# 日志导出文件\n")
                output_file.write(f"# 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                output_file.write(f"# 日志级别: {level or 'ALL'}\n")
                output_file.write("# " + "="*50 + "\n\n")
                
                for log_file in log_files:
                    content = self.read_log_file(log_file)
                    lines = content.split('\n')
                    
                    # 应用过滤条件
                    if level:
                        lines = self.filter_logs_by_level(lines, level)
                    
                    if start_date or end_date:
                        lines = self._filter_logs_by_date(lines, start_date, end_date)
                    
                    if lines:
                        output_file.write(f"\n# 来源文件: {log_file}\n")
                        output_file.write("-" * 50 + "\n")
                        for line in lines:
                            if line.strip():
                                output_file.write(line + '\n')
            
            return True, "日志导出成功"
            
        except Exception as e:
            return False, f"日志导出失败: {str(e)}"
    
    def _filter_logs_by_date(self, logs, start_date, end_date):
        """按日期过滤日志"""
        filtered_logs = []
        
        for log in logs:
            timestamp = self._extract_timestamp(log)
            
            if timestamp:
                if start_date and timestamp < start_date:
                    continue
                if end_date and timestamp > end_date:
                    continue
            
            filtered_logs.append(log)
        
        return filtered_logs
    
    def get_log_statistics(self):
        """获取日志统计信息"""
        try:
            log_files = self.get_log_files()
            
            total_files = len(log_files)
            total_size = 0
            total_lines = 0
            
            level_counts = {
                'DEBUG': 0,
                'INFO': 0,
                'WARNING': 0,
                'ERROR': 0,
                'CRITICAL': 0
            }
            
            for log_file in log_files:
                # 文件大小
                total_size += os.path.getsize(log_file)
                
                # 行数和级别统计
                content = self.read_log_file(log_file)
                lines = content.split('\n')
                total_lines += len([line for line in lines if line.strip()])
                
                # 统计各级别日志数量
                for line in lines:
                    line_upper = line.upper()
                    for level in level_counts:
                        if level in line_upper:
                            level_counts[level] += 1
                            break
            
            return {
                'total_files': total_files,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_lines': total_lines,
                'level_counts': level_counts,
                'oldest_log': log_files[-1] if log_files else None,
                'newest_log': log_files[0] if log_files else None
            }
            
        except Exception as e:
            self._update_status(f"获取日志统计失败: {str(e)}")
            return {} 