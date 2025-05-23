import os
import json
import random
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self, max_usage_count: int = 3):
        """
        代理管理器
        
        Args:
            max_usage_count: 每个代理的最大使用次数，默认为3次
        """
        self.max_usage_count = max_usage_count
        self.usage_file = "proxy_usage.json"
        self.proxypool_dir = "proxypool"
        self.proxy_files_map = {
            "http_ip_port": os.path.join(self.proxypool_dir, "http_ip_port.txt"),
            "http_user_pass": os.path.join(self.proxypool_dir, "http_user_pass.txt"),
            "socks5": os.path.join(self.proxypool_dir, "socks5.txt"),
            "socks5_user_pass": os.path.join(self.proxypool_dir, "socks5_user_pass.txt"),
        }
        self.usage_data = self._load_usage_data()
    
    def _load_usage_data(self) -> Dict:
        """加载代理使用次数数据"""
        try:
            if os.path.exists(self.usage_file):
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载代理使用数据失败: {str(e)}")
        return {}
    
    def _save_usage_data(self):
        """保存代理使用次数数据"""
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"保存代理使用数据失败: {str(e)}")
    
    def _read_proxy_file(self, file_path: str) -> List[str]:
        """读取代理文件，返回未注释的代理列表"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                # 只返回未注释的代理（不以#开头的行）
                active_proxies = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        active_proxies.append(line)
                return active_proxies
        except FileNotFoundError:
            logger.error(f"代理文件未找到: {file_path}")
            return []
        except Exception as e:
            logger.error(f"读取代理文件失败 {file_path}: {str(e)}")
            return []
    
    def _comment_out_proxy(self, file_path: str, proxy_string: str):
        """在代理文件中注释掉指定的代理"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
            
            # 查找并注释掉指定的代理
            modified = False
            for i, line in enumerate(lines):
                if line.strip() == proxy_string:
                    # 保持原有的换行符，只在前面添加注释符号
                    if line.endswith('\n'):
                        lines[i] = f"# {line}"
                    else:
                        lines[i] = f"# {line}\n"
                    modified = True
                    logger.info(f"已注释代理: {proxy_string} (使用次数已达到 {self.max_usage_count} 次)")
                    break
            
            if modified:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.writelines(lines)
                return True
            else:
                logger.warning(f"未找到要注释的代理: {proxy_string}")
                return False
                
        except Exception as e:
            logger.error(f"注释代理失败 {file_path}: {str(e)}")
            return False
    
    def get_available_proxy(self) -> Optional[Dict[str, str]]:
        """获取一个可用的代理"""
        # 获取所有可用的代理类型
        available_proxy_types = []
        for proxy_type, file_path in self.proxy_files_map.items():
            try:
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    available_proxy_types.append(proxy_type)
            except OSError as e:
                logger.error(f"检查代理文件 {file_path} 时出错: {str(e)}")
                continue
        
        if not available_proxy_types:
            logger.warning("代理池中没有找到有效的代理文件，将不使用代理继续")
            return None
        
        # 尝试从每种代理类型中获取可用代理
        remaining_proxy_types = available_proxy_types.copy()
        
        while remaining_proxy_types:
            selected_proxy_type = random.choice(remaining_proxy_types)
            selected_proxy_file = self.proxy_files_map[selected_proxy_type]
            
            proxy_list = self._read_proxy_file(selected_proxy_file)
            
            if proxy_list:
                # 过滤掉已达到使用次数限制的代理
                available_proxies = []
                for proxy in proxy_list:
                    usage_count = self.usage_data.get(proxy, 0)
                    if usage_count < self.max_usage_count:
                        available_proxies.append(proxy)
                
                if available_proxies:
                    selected_proxy_string = random.choice(available_proxies)
                    logger.info(f"选择代理: 类型 '{selected_proxy_type}', 详情: '{selected_proxy_string}'")
                    return {
                        "proxy_string": selected_proxy_string, 
                        "type": selected_proxy_type,
                        "file_path": selected_proxy_file
                    }
                else:
                    logger.warning(f"代理文件 {selected_proxy_file} 中的所有代理都已达到使用次数限制")
                    remaining_proxy_types.remove(selected_proxy_type)
            else:
                logger.warning(f"代理文件 {selected_proxy_file} 为空，尝试其他代理类型")
                remaining_proxy_types.remove(selected_proxy_type)
        
        logger.warning("所有代理文件都为空或无效，将不使用代理继续")
        return None
    
    def record_proxy_usage(self, proxy_string: str, file_path: str):
        """记录代理使用次数，如果达到限制则注释掉"""
        if not proxy_string:
            return
        
        # 增加使用次数
        current_usage = self.usage_data.get(proxy_string, 0)
        new_usage = current_usage + 1
        self.usage_data[proxy_string] = new_usage
        
        logger.info(f"代理 {proxy_string} 使用次数: {new_usage}/{self.max_usage_count}")
        
        # 如果达到最大使用次数，注释掉该代理
        if new_usage >= self.max_usage_count:
            self._comment_out_proxy(file_path, proxy_string)
            logger.info(f"代理 {proxy_string} 已达到最大使用次数 ({self.max_usage_count})，已自动注释")
        
        # 保存使用数据
        self._save_usage_data()
    
    def get_proxy_statistics(self) -> Dict:
        """获取代理使用统计信息"""
        stats = {
            "total_proxies": 0,
            "active_proxies": 0,
            "exhausted_proxies": 0,
            "usage_details": {}
        }
        
        for proxy_type, file_path in self.proxy_files_map.items():
            type_stats = {
                "total": 0,
                "active": 0,
                "commented": 0
            }
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    for line in lines:
                        line = line.strip()
                        if line:
                            type_stats["total"] += 1
                            if line.startswith('#'):
                                type_stats["commented"] += 1
                            else:
                                type_stats["active"] += 1
                                # 检查活跃代理是否已耗尽
                                usage_count = self.usage_data.get(line, 0)
                                if usage_count >= self.max_usage_count:
                                    stats["exhausted_proxies"] += 1
                
                except Exception as e:
                    logger.error(f"读取代理文件统计信息失败 {file_path}: {str(e)}")
                    # 继续处理其他文件，不中断整个统计过程
                    continue
            
            stats["usage_details"][proxy_type] = type_stats
            stats["total_proxies"] += type_stats["total"]
            stats["active_proxies"] += type_stats["active"]
        
        return stats 