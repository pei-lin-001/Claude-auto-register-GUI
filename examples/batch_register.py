#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Claude AI 批量注册示例脚本
该脚本展示如何使用Claude自动注册工具进行批量账号注册
"""

import subprocess
import time
import argparse
import os
import sys
import random

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Claude AI 批量注册工具')
    parser.add_argument('--count', type=int, default=3, help='要注册的账号数量')
    parser.add_argument('--interval', type=int, default=60, help='每次注册之间的等待时间(秒)')
    parser.add_argument('--random_interval', action='store_true', help='随机化等待时间')
    args = parser.parse_args()

    print(f"开始批量注册 Claude AI 账号，计划注册 {args.count} 个账号")
    print(f"每次注册之间将等待 {args.interval} 秒")
    
    success_count = 0
    
    for i in range(args.count):
        print(f"\n开始第 {i+1}/{args.count} 个账号的注册过程...")
        
        # 设置浏览器窗口位置，避免窗口重叠
        x_pos = (i % 3) * 100
        y_pos = (i // 3) * 100
        position_arg = f"--position {x_pos},{y_pos}"
        
        # 运行主程序
        try:
            result = subprocess.run(
                ["python", "../main.py", position_arg], 
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if "注册完成" in result.stdout:
                success_count += 1
                print(f"第 {i+1} 个账号注册成功!")
            else:
                print(f"第 {i+1} 个账号可能注册失败，请检查日志!")
                
        except subprocess.CalledProcessError as e:
            print(f"第 {i+1} 个账号注册失败: {e}")
            print(f"错误输出: {e.stderr}")
        
        # 判断是否继续注册
        if i < args.count - 1:
            wait_time = args.interval
            if args.random_interval:
                # 随机等待时间，基础时间的80%-120%之间
                wait_time = int(args.interval * random.uniform(0.8, 1.2))
            
            print(f"等待 {wait_time} 秒后继续下一个账号注册...")
            time.sleep(wait_time)
    
    print(f"\n批量注册完成!")
    print(f"成功: {success_count}/{args.count}")
    print(f"请查看 logs 目录获取详细日志")


if __name__ == "__main__":
    main() 