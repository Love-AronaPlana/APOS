#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS API 测试文件
"""

import requests
import json
import time

# API 基础地址
BASE_URL = "http://localhost:8880/api"

def test_health():
    """测试健康检查接口"""
    print("🏥 测试健康检查接口...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_tools():
    """测试工具列表接口"""
    print("\n🔧 测试工具列表接口...")
    try:
        response = requests.get(f"{BASE_URL}/tools")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"工具数量: {len(data.get('tools', []))}")
        for tool in data.get('tools', []):
            print(f"  - {tool['name']}: {tool['description']}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 获取工具列表失败: {e}")
        return False

def test_chat():
    """测试聊天接口"""
    print("\n💬 测试聊天接口...")
    try:
        # 测试简单计算
        message = "请帮我计算 2 + 3 * 4 的结果"
        payload = {
            "message": message,
            "session_id": "test_session"
        }
        
        print(f"发送消息: {message}")
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"响应: {data.get('response', '')}")
            print(f"迭代次数: {data.get('iterations', 0)}")
            print(f"状态: {data.get('status', '')}")
        else:
            print(f"错误: {data.get('error', '')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 聊天测试失败: {e}")
        return False

def test_history():
    """测试历史记录接口"""
    print("\n📚 测试历史记录接口...")
    try:
        session_id = "test_session"
        response = requests.get(f"{BASE_URL}/history/{session_id}")
        print(f"状态码: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            history = data.get('history', [])
            print(f"历史记录数量: {len(history)}")
            for i, msg in enumerate(history[-3:]):  # 显示最后3条
                print(f"  {i+1}. [{msg['role']}] {msg['content'][:50]}...")
        else:
            print(f"错误: {data.get('error', '')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 历史记录测试失败: {e}")
        return False

def test_clear_history():
    """测试清除历史记录接口"""
    print("\n🗑️ 测试清除历史记录接口...")
    try:
        session_id = "test_session"
        response = requests.delete(f"{BASE_URL}/clear/{session_id}")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {data.get('message', '')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 清除历史记录测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始 APOS API 测试")
    print("=" * 50)
    
    tests = [
        ("健康检查", test_health),
        ("工具列表", test_tools),
        ("聊天功能", test_chat),
        ("历史记录", test_history),
        ("清除历史", test_clear_history),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)  # 间隔1秒
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(tests)} 个测试通过")
    
    if passed == len(tests):
        print("🎉 所有测试通过！APOS API 运行正常")
    else:
        print("⚠️ 部分测试失败，请检查服务状态")

if __name__ == "__main__":
    main()

