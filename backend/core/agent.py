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

class APOSAgent:
    """APOS Agent 主类"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.llm_client = LLMClient()
        self.history_manager = HistoryManager()
        self.tool_manager = ToolManager()
        
        self.logger.info("🤖 APOS Agent 初始化完成")
    
    def process_message(self, user_message: str, session_id: str = 'default') -> Dict[str, Any]:
        """处理用户消息"""
        self.logger.info(f"🔄 开始处理消息 - 会话: {session_id}")
        
        try:
            # 添加用户消息到历史记录
            self.history_manager.add_message(session_id, 'user', user_message)
            
            # 获取历史记录
            history = self.history_manager.get_history(session_id)
            
            # 构建系统提示词
            system_prompt = self._build_system_prompt()
            
            # 开始对话循环
            max_iterations = 10  # 最大迭代次数
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                self.logger.info(f"🔄 第 {iteration} 次迭代")
                
                # 调用 LLM
                response = self.llm_client.chat(system_prompt, history)
                
                # 添加助手响应到历史记录
                self.history_manager.add_message(session_id, 'assistant', response)
                
                # 检查是否需要调用工具
                tool_call = self._extract_tool_call(response)
                
                if tool_call:
                    self.logger.info(f"🔧 检测到工具调用: {tool_call['tool']}")
                    
                    # 执行工具
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
                
                # 检查是否任务完成
                if self._is_task_completed(response):
                    self.logger.info("✅ 任务完成")
                    break
            
            # 获取最终响应
            final_response = self.history_manager.get_last_assistant_message(session_id)
            
            return {
                'response': final_response,
                'session_id': session_id,
                'iterations': iteration,
                'status': 'completed' if iteration < max_iterations else 'max_iterations_reached'
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
        tools_info = self.tool_manager.get_tools_description()
        
        return f"""你是 APOS，一个通用型 AI Agent，能够帮助用户完成各种复杂任务。

你的工作流程：
1. 理解用户的需求
2. 分析需要使用哪些工具来完成任务
3. 按步骤调用工具来完成任务
4. 每次只能调用一个工具
5. 根据工具执行结果决定下一步操作
6. 完成任务后给出总结

工具调用格式：
当你需要调用工具时，请使用以下 XML 格式：
<tool_call>
{{
    "tool": "工具名称",
    "parameters": {{
        "参数名": "参数值"
    }}
}}
</tool_call>

可用工具：
{tools_info}

重要规则：
- 每次对话只能调用一个工具
- 必须严格按照 XML 格式调用工具
- 工具调用后等待执行结果再继续
- 任务完成后说明"任务已完成"

请根据用户的需求，逐步使用工具来完成任务。"""
    
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
    
    def _is_task_completed(self, response: str) -> bool:
        """检查任务是否完成"""
        completion_keywords = [
            "任务已完成", "任务完成", "完成了", "已完成",
            "task completed", "finished", "done"
        ]
        
        response_lower = response.lower()
        for keyword in completion_keywords:
            if keyword.lower() in response_lower:
                return True
        
        return False
    
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """获取历史记录"""
        return self.history_manager.get_history(session_id)
    
    def clear_history(self, session_id: str):
        """清除历史记录"""
        self.history_manager.clear_history(session_id)
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        return self.tool_manager.get_available_tools()

