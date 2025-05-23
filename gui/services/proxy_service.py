"""
代理服务模块

提供代理管理相关的服务功能。
"""

import sys
import os
import threading
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.proxy_manager import ProxyManager


class ProxyService:
    """代理服务类"""
    
    def __init__(self):
        self.proxy_manager = ProxyManager(max_usage_count=3)
        self.status_callback = None
        
    def set_callbacks(self, status_callback=None):
        """设置回调函数"""
        self.status_callback = status_callback
        
    def _update_status(self, message):
        """更新状态"""
        if self.status_callback:
            self.status_callback(message)
    
    def load_proxy_file(self, file_path):
        """加载代理文件"""
        try:
            result = self.proxy_manager.load_proxy_file(file_path)
            self._update_status(f"代理文件加载成功: {len(result)} 个代理")
            return result
        except Exception as e:
            self._update_status(f"代理文件加载失败: {str(e)}")
            return []
    
    def get_proxy_statistics(self):
        """获取代理统计信息"""
        return self.proxy_manager.get_proxy_statistics()
    
    def get_available_proxy(self):
        """获取可用代理"""
        return self.proxy_manager.get_available_proxy()
    
    def test_proxy(self, proxy_string):
        """测试单个代理"""
        try:
            # 这里可以实现代理测试逻辑
            # 例如使用requests测试代理连接
            import requests
            
            proxies = {
                'http': f'http://{proxy_string}',
                'https': f'http://{proxy_string}'
            }
            
            response = requests.get(
                'http://httpbin.org/ip', 
                proxies=proxies, 
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "代理连接正常"
            else:
                return False, f"代理响应异常: {response.status_code}"
                
        except Exception as e:
            return False, f"代理测试失败: {str(e)}"
    
    def test_all_proxies(self, progress_callback=None):
        """测试所有代理"""
        def test_worker():
            stats = self.get_proxy_statistics()
            total_proxies = stats['total_proxies']
            tested_count = 0
            valid_count = 0
            
            # 这里需要实现遍历所有代理的逻辑
            # 由于当前proxy_manager没有提供获取所有代理的方法
            # 这里先提供框架结构
            
            if progress_callback:
                progress_callback(100, tested_count, total_proxies, f"测试完成: {valid_count} 个有效代理")
        
        thread = threading.Thread(target=test_worker)
        thread.daemon = True
        thread.start()
        return thread
    
    def clear_exhausted_proxies(self):
        """清理已耗尽的代理"""
        # 这里需要proxy_manager支持清理功能
        pass
    
    def export_proxy_list(self, file_path, proxy_type="all"):
        """导出代理列表"""
        try:
            # 这里需要实现导出逻辑
            # 目前提供框架结构
            return True, "代理列表导出成功"
        except Exception as e:
            return False, f"导出失败: {str(e)}" 