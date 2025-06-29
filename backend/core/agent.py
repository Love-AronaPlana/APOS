#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS Agent 核心模块
"""

import json
import re
from typing import Dict, List, Any
from core.llm_client import LLMClient
from core.history_manager import HistoryManager
from tools.tool_manager import ToolManager
from utils.logger import get_logger
from .prompts import get_system_prompt
import platform
import getpass
from datetime import datetime

class APOSAgent:
    """APOS Agent 主类"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.llm_client = LLMClient()
        self.history_manager = HistoryManager()
        self.tool_manager = ToolManager()
        self.session_iterations = {}
        
        self.logger.info("🤖 APOS Agent 初始化完成")
    
    def process_message(self, user_message: str, session_id: str = 'default') -> Dict[str, Any]:
        """处理用户消息"""
        self.logger.info(f"🔄 开始处理消息 - 会话: {session_id}")
        
        try:
            # 添加用户消息到历史记录
            if user_message and user_message.strip():
                self.history_manager.add_message(session_id, 'user', user_message)
            
            # 构建系统提示词
            system_prompt = self._build_system_prompt()
            
            # 开始对话循环
            max_iterations = 20  # 最大迭代次数
            # 初始化迭代次数 - 新消息重置计数，工具确认继续计数
            if user_message and user_message.strip():
                self.session_iterations[session_id] = 0
            iteration = self.session_iterations.get(session_id, 0)
            final_response = None
            
            while iteration < max_iterations:
                iteration += 1
                self.session_iterations[session_id] = iteration
                self.logger.info(f"🔄 第 {iteration} 次迭代")
                
                # 获取历史记录
                history = self.history_manager.get_history(session_id)
                
                # 调用 LLM
                response = self.llm_client.chat(system_prompt, history)
                
                # 添加助手响应到历史记录
                self.history_manager.add_message(session_id, 'assistant', response)
                
                # 检查是否任务完成
                if self._is_task_completed(response):
                    self.logger.info("✅ 任务完成")
                    final_response = self._extract_final_answer(response)
                    break
                
                # 检查是否需要调用工具
                tool_call = self._extract_tool_call(response)
                
                if tool_call:
                    self.logger.info(f"🔧 检测到工具调用: {tool_call['tool']}")
                    
                    # 检查是否是MCP工具
                    # 检查是否是MCP工具
                    is_mcp_tool = tool_call['tool'].startswith('mcp_') or hasattr(self.tool_manager.tools[tool_call['tool']], 'is_mcp')

                    if is_mcp_tool:
                        # 需要用户确认，将工具调用请求存储到会话状态
                        self.history_manager.add_message(
                            session_id, 
                            'system', 
                            json.dumps({
                                'type': 'tool_confirmation_required',
                                'tool': tool_call['tool'],
                                'parameters': tool_call['parameters']
                            }, ensure_ascii=False)
                        )

                        # 返回需要确认的状态
                        return {
                            'response': '需要用户确认工具调用',
                            'session_id': session_id,
                            'status': 'waiting_for_confirmation',
                            'tool_call': tool_call
                        }

                    # 非MCP工具直接执行
                    tool_result = self.tool_manager.execute_tool(
                        tool_call['tool'], 
                        tool_call['parameters']
                    )

                    # 添加工具结果到历史记录
                    self.history_manager.add_message(
                        session_id, 
                        'system', 
                        f"工具执行结果: {json.dumps(tool_result, ensure_ascii=False)}"
                    )

                    # 继续下一次迭代
                    continue

                # 如果没有工具调用，也没有最终答案，则直接跳出
                self.logger.warning("🤔 未检测到工具调用或最终答案，提前结束任务。")
                final_response = response # 将当前响应作为最终响应
                break
            
            # 如果循环结束后没有最终响应，则获取最后一条助手消息
            if final_response is None:
                self.logger.warning("🤔 达到最大迭代次数，但未找到最终答案。")
                final_response = self.history_manager.get_last_assistant_message(session_id)
            
            # 任务完成，重置迭代计数
            self.session_iterations[session_id] = 0
            return {
                'response': final_response,
                'session_id': session_id,
                'iterations': iteration,
                'status': 'completed' if final_response and iteration < max_iterations else 'max_iterations_reached'
            }
            
        except Exception as e:
            self.logger.error(f"❌ 处理消息错误: {str(e)}")
            return {
                'error': str(e),
                'session_id': session_id,
                'status': 'error'
            }
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        system_info = {
            'system_version': platform.version(),
            'username': getpass.getuser(),
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        tools_info = self.tool_manager.get_tools_description()
        
        return get_system_prompt(tools_info, system_info)
    
    def _extract_tool_call(self, response: str) -> Dict[str, Any]:
        """从响应中提取工具调用"""
        # 使用正则表达式匹配 XML 格式的工具调用
        pattern = r'<tool_call>\s*(\{.*?\})\s*</tool_call>'
        match = re.search(pattern, response, re.DOTALL)
        
        if match:
            try:
                tool_call_json = match.group(1)
                tool_call = json.loads(tool_call_json)
                self.logger.info(f"🔍 提取到工具调用: {tool_call}")
                return tool_call
            except json.JSONDecodeError as e:
                self.logger.error(f"❌ 工具调用 JSON 解析错误: {e}")
                return None
        
        return None

    def _extract_final_answer(self, response: str) -> str:
        """从响应中提取最终答案"""
        pattern = r'<final_answer>(.*?)</final_answer>'
        match = re.search(pattern, response, re.DOTALL)
        
        if match:
            final_answer = match.group(1).strip()
            self.logger.info(f"🔍 提取到最终答案: {final_answer}")
            return final_answer
        
        # 如果没有找到 final_answer 标签，但任务被标记为完成，则直接返回原始响应
        return response
    
    def _is_task_completed(self, response: str) -> bool:
        """
        检查任务是否完成。

        如果响应中包含 <final_answer> 标签，则认为任务已完成。
        """
        return "<final_answer>" in response
    
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """获取历史记录"""
        return self.history_manager.get_history(session_id)
    
    def clear_history(self, session_id: str):
        """清除历史记录"""
        self.history_manager.clear_history(session_id)
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        return self.tool_manager.get_available_tools()