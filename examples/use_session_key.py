#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
示例脚本：如何使用已保存的SessionKey访问Claude AI
"""

import requests
import json
import os
import sys

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read_session_key(file_path):
    """读取保存的SessionKey"""
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
        return None


def send_message_to_claude(session_key, message, conversation_id=None):
    """
    使用SessionKey向Claude发送消息
    
    Args:
        session_key: Claude的SessionKey
        message: 要发送的消息内容
        conversation_id: 可选，现有会话ID
        
    Returns:
        响应JSON或错误信息
    """
    # API端点
    base_url = "https://claude.ai/api"
    
    # 设置请求头
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": f"sessionKey={session_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # 创建新会话（如果未提供会话ID）
    if not conversation_id:
        try:
            # 获取组织ID
            org_response = requests.get(f"{base_url}/organizations", headers=headers)
            org_response.raise_for_status()
            org_data = org_response.json()
            if len(org_data) == 0:
                return {"error": "无法获取组织ID"}
            
            organization_id = org_data[0]["uuid"]
            
            # 创建新会话
            create_data = {
                "name": "",
                "organization_id": organization_id
            }
            create_response = requests.post(
                f"{base_url}/organizations/{organization_id}/chat_conversations",
                headers=headers,
                json=create_data
            )
            create_response.raise_for_status()
            conversation_id = create_response.json()["uuid"]
            
        except requests.RequestException as e:
            return {"error": f"创建会话失败: {str(e)}"}
    
    # 发送消息
    try:
        message_data = {
            "attachments": [],
            "completion": {
                "prompt": "",
                "timezone": "Asia/Shanghai",
                "model": "claude-3-opus-20240229"
            },
            "organization_id": organization_id,
            "conversation_id": conversation_id,
            "text": message
        }
        
        message_response = requests.post(
            f"{base_url}/append_message",
            headers=headers,
            json=message_data,
            stream=True
        )
        message_response.raise_for_status()
        
        # 读取流式响应
        full_response = ""
        for line in message_response.iter_lines():
            if line:
                try:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        json_str = decoded_line[6:]  # 去除 "data: " 前缀
                        if json_str != "[DONE]":
                            chunk = json.loads(json_str)
                            if "completion" in chunk:
                                full_response += chunk["completion"]
                except Exception as e:
                    print(f"解析响应出错: {e}")
        
        return {
            "conversation_id": conversation_id,
            "response": full_response
        }
        
    except requests.RequestException as e:
        return {"error": f"发送消息失败: {str(e)}"}


def main():
    # 读取SessionKey
    session_key_file = "../sessionKey.txt"  # 根据实际情况调整路径
    session_key = read_session_key(session_key_file)
    
    if not session_key:
        print("无法读取SessionKey，请先运行注册程序生成SessionKey")
        return
    
    print("成功读取SessionKey!")
    
    # 发送消息示例
    message = "你好，Claude! 请简单介绍一下你自己。"
    print(f"\n发送消息: '{message}'")
    
    result = send_message_to_claude(session_key, message)
    
    if "error" in result:
        print(f"错误: {result['error']}")
    else:
        print("\nClaude的回复:")
        print("="*50)
        print(result["response"])
        print("="*50)
        print(f"\n会话ID: {result['conversation_id']}")
        print("\n你可以使用此会话ID继续对话")


if __name__ == "__main__":
    main() 