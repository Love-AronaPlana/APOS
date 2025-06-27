#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS API 路由
"""

from flask import Blueprint, request, jsonify
from core.agent import APOSAgent
from utils.logger import get_logger
import traceback

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 获取日志器
logger = get_logger(__name__)

# 创建 Agent 实例
agent = APOSAgent()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    logger.info("🏥 健康检查请求")
    return jsonify({
        'status': 'ok',
        'message': 'APOS 后端服务运行正常',
        'version': '1.0.0'
    })

@api_bp.route('/chat', methods=['POST'])
def chat():
    """聊天接口"""
    try:
        data = request.get_json()
        logger.info(f"💬 收到聊天请求: {data}")
        
        if not data or 'message' not in data:
            return jsonify({
                'error': '请求数据格式错误，需要包含 message 字段'
            }), 400
        
        # 获取用户消息
        user_message = data['message']
        session_id = data.get('session_id', 'default')
        
        logger.info(f"👤 用户消息: {user_message}")
        logger.info(f"🔑 会话ID: {session_id}")
        
        # 调用 Agent 处理
        response = agent.process_message(user_message, session_id)
        
        logger.info(f"🤖 Agent 响应: {response}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ 聊天接口错误: {str(e)}")
        logger.error(f"📋 错误详情: {traceback.format_exc()}")
        return jsonify({
            'error': f'服务器内部错误: {str(e)}'
        }), 500

@api_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """获取历史记录接口"""
    try:
        logger.info(f"📚 获取历史记录请求: {session_id}")
        
        history = agent.get_history(session_id)
        
        logger.info(f"📖 返回历史记录数量: {len(history)}")
        
        return jsonify({
            'session_id': session_id,
            'history': history
        })
        
    except Exception as e:
        logger.error(f"❌ 获取历史记录错误: {str(e)}")
        return jsonify({
            'error': f'获取历史记录失败: {str(e)}'
        }), 500

@api_bp.route('/clear/<session_id>', methods=['DELETE'])
def clear_history(session_id):
    """清除历史记录接口"""
    try:
        logger.info(f"🗑️ 清除历史记录请求: {session_id}")
        
        agent.clear_history(session_id)
        
        logger.info(f"✅ 历史记录已清除: {session_id}")
        
        return jsonify({
            'message': f'会话 {session_id} 的历史记录已清除'
        })
        
    except Exception as e:
        logger.error(f"❌ 清除历史记录错误: {str(e)}")
        return jsonify({
            'error': f'清除历史记录失败: {str(e)}'
        }), 500

@api_bp.route('/tools', methods=['GET'])
def get_tools():
    """获取可用工具列表接口"""
    try:
        logger.info("🔧 获取工具列表请求")
        
        tools = agent.get_available_tools()
        
        logger.info(f"🛠️ 返回工具数量: {len(tools)}")
        
        return jsonify({
            'tools': tools
        })
        
    except Exception as e:
        logger.error(f"❌ 获取工具列表错误: {str(e)}")
        return jsonify({
            'error': f'获取工具列表失败: {str(e)}'
        }), 500

