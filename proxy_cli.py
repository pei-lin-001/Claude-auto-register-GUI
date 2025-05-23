#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代理管理命令行工具
提供代理使用次数管理、统计查看等功能
"""

import os
import sys
import argparse
import json
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.proxy_manager import ProxyManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def show_statistics(proxy_manager):
    """显示代理统计信息"""
    stats = proxy_manager.get_proxy_statistics()
    
    print("\n=== 代理统计信息 ===")
    print(f"总代理数量: {stats['total_proxies']}")
    print(f"活跃代理数量: {stats['active_proxies']}")
    print(f"已耗尽代理数量: {stats['exhausted_proxies']}")
    
    print("\n=== 详细统计 ===")
    for proxy_type, type_stats in stats['usage_details'].items():
        print(f"{proxy_type}:")
        print(f"  总计: {type_stats['total']} 个")
        print(f"  活跃: {type_stats['active']} 个")
        print(f"  已注释: {type_stats['commented']} 个")

def show_usage_details(proxy_manager):
    """显示详细的使用次数信息"""
    print("\n=== 代理使用次数详情 ===")
    
    if not proxy_manager.usage_data:
        print("暂无使用记录")
        return
    
    # 按使用次数排序
    sorted_usage = sorted(
        proxy_manager.usage_data.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    for proxy, count in sorted_usage:
        status = "已耗尽" if count >= proxy_manager.max_usage_count else "可用"
        print(f"{proxy}: {count}/{proxy_manager.max_usage_count} 次 ({status})")

def reset_usage_count(proxy_manager, proxy_string=None):
    """重置代理使用次数"""
    if proxy_string:
        if proxy_string in proxy_manager.usage_data:
            old_count = proxy_manager.usage_data[proxy_string]
            proxy_manager.usage_data[proxy_string] = 0
            proxy_manager._save_usage_data()
            print(f"已重置代理 {proxy_string} 的使用次数 (从 {old_count} 重置为 0)")
        else:
            print(f"未找到代理 {proxy_string} 的使用记录")
    else:
        # 重置所有代理的使用次数
        count = len(proxy_manager.usage_data)
        proxy_manager.usage_data.clear()
        proxy_manager._save_usage_data()
        print(f"已重置所有 {count} 个代理的使用次数")

def uncomment_proxy(proxy_manager, proxy_string):
    """取消注释指定的代理"""
    found = False
    
    for proxy_type, file_path in proxy_manager.proxy_files_map.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    lines = file.readlines()
                
                modified = False
                for i, line in enumerate(lines):
                    # 检查是否是被注释的目标代理
                    stripped_line = line.strip()
                    if stripped_line == f"# {proxy_string}" or stripped_line == f"#{proxy_string}":
                        # 保持原有的换行符格式
                        if line.endswith('\n'):
                            lines[i] = f"{proxy_string}\n"
                        else:
                            lines[i] = proxy_string
                        modified = True
                        found = True
                        break
                
                if modified:
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.writelines(lines)
                    print(f"已取消注释代理: {proxy_string} (文件: {file_path})")
                    
                    # 重置使用次数
                    if proxy_string in proxy_manager.usage_data:
                        proxy_manager.usage_data[proxy_string] = 0
                        proxy_manager._save_usage_data()
                        print(f"已重置代理 {proxy_string} 的使用次数")
                    
                    return True
                    
            except Exception as e:
                logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
    
    if not found:
        print(f"未找到被注释的代理: {proxy_string}")
    
    return False

def list_proxy_files(proxy_manager):
    """列出所有代理文件的内容"""
    print("\n=== 代理文件内容 ===")
    
    for proxy_type, file_path in proxy_manager.proxy_files_map.items():
        if os.path.exists(file_path):
            print(f"\n{proxy_type} ({file_path}):")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        for line_num, line in enumerate(lines, 1):
                            line = line.rstrip()
                            if line:
                                status = "已注释" if line.startswith('#') else "活跃"
                                usage_count = 0
                                clean_proxy = line.lstrip('# ')
                                if clean_proxy in proxy_manager.usage_data:
                                    usage_count = proxy_manager.usage_data[clean_proxy]
                                print(f"  {line_num}: {line} ({status}, 使用次数: {usage_count})")
                    else:
                        print("  (空文件)")
            except Exception as e:
                print(f"  读取文件出错: {str(e)}")
        else:
            print(f"\n{proxy_type}: 文件不存在")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='代理管理命令行工具')
    parser.add_argument('--max-usage', type=int, default=3, help='设置代理最大使用次数 (默认: 3)')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 统计信息命令
    subparsers.add_parser('stats', help='显示代理统计信息')
    
    # 使用详情命令
    subparsers.add_parser('usage', help='显示代理使用次数详情')
    
    # 重置使用次数命令
    reset_parser = subparsers.add_parser('reset', help='重置代理使用次数')
    reset_parser.add_argument('--proxy', help='指定要重置的代理 (不指定则重置所有)')
    
    # 取消注释命令
    uncomment_parser = subparsers.add_parser('uncomment', help='取消注释指定的代理')
    uncomment_parser.add_argument('proxy', help='要取消注释的代理')
    
    # 列出文件命令
    subparsers.add_parser('list', help='列出所有代理文件内容')
    
    # 测试命令
    subparsers.add_parser('test', help='运行代理管理器测试')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建代理管理器
    proxy_manager = ProxyManager(max_usage_count=args.max_usage)
    
    # 执行相应命令
    if args.command == 'stats':
        show_statistics(proxy_manager)
    
    elif args.command == 'usage':
        show_usage_details(proxy_manager)
    
    elif args.command == 'reset':
        reset_usage_count(proxy_manager, args.proxy)
    
    elif args.command == 'uncomment':
        uncomment_proxy(proxy_manager, args.proxy)
    
    elif args.command == 'list':
        list_proxy_files(proxy_manager)
    
    elif args.command == 'test':
        # 运行测试
        print("测试功能暂时不可用 - 测试文件已被移除")
        print("您可以使用以下命令来测试代理管理器的基本功能:")
        print("  python proxy_cli.py stats    # 查看统计信息")
        print("  python proxy_cli.py list     # 列出代理文件")
        print("  python proxy_cli.py usage    # 查看使用详情")

if __name__ == "__main__":
    main() 