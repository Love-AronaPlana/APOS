#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS 历史记录管理器
"""

from typing import Dict, List, Any
from datetime import datetime
import os
import json
import uuid
from config.settings import Config
from utils.logger import get_logger

class HistoryManager:
    """历史记录管理器"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
        self.max_length = Config.MAX_HISTORY_LENGTH
        self.sessions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sessions')
        os.makedirs(self.sessions_dir, exist_ok=True)
        self._load_all_sessions()
        
        self.logger.info("📚 历史记录管理器初始化完成")
    
    def _save_session(self, session_id: str):
        """保存会话到文件"""
        if session_id not in self.sessions:
            return
        
        file_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.sessions[session_id], f, ensure_ascii=False, indent=2)
            self.logger.info(f"💾 会话已保存: {session_id} -> {file_path}")
        except Exception as e:
            self.logger.error(f"❌ 保存会话失败: {str(e)}")
    
    def _load_session(self, session_id: str) -> List[Dict[str, Any]]:
        """从文件加载会话"""
        file_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"❌ 加载会话失败: {str(e)}")
            return []
    
    def _load_all_sessions(self):
        """加载所有会话"""
        if not os.path.exists(self.sessions_dir):
            return
        
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith('.json'):
                session_id = filename[:-5]
                self.sessions[session_id] = self._load_session(session_id)
        
        self.logger.info(f"📥 已加载 {len(self.sessions)} 个会话")
    
    def create_new_session(self) -> str:
        """创建新会话并返回会话ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        self._save_session(session_id)
        self.logger.info(f"✨ 创建新会话: {session_id}")
        return session_id
    
    def delete_session(self, session_id: str):
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            
        file_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                self.logger.info(f"🗑️ 删除会话文件: {file_path}")
            except Exception as e:
                self.logger.error(f"❌ 删除会话文件失败: {str(e)}")
    
    def add_message(self, session_id: str, role: str, content: Any):
        """添加消息到历史记录"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        self.sessions[session_id].append(message)
        
        # 限制历史记录长度
        if len(self.sessions[session_id]) > self.max_length:
            # 保留系统消息，删除最旧的用户/助手消息
            system_messages = [msg for msg in self.sessions[session_id] if msg['role'] == 'system']
            other_messages = [msg for msg in self.sessions[session_id] if msg['role'] != 'system']
            
            # 保留最新的消息
            other_messages = other_messages[-(self.max_length - len(system_messages)):]
            
            self.sessions[session_id] = system_messages + other_messages
        
        self.logger.info(f"📝 添加消息 - 会话: {session_id}, 角色: {role}, 长度: {len(str(content))}")
        self.logger.debug(f"💬 消息内容: {content}")
        
        # 保存会话到文件
        self._save_session(session_id)
    
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """获取历史记录"""
        if session_id not in self.sessions:
            return []
        
        history = self.sessions[session_id].copy()
        self.logger.info(f"📖 获取历史记录 - 会话: {session_id}, 消息数量: {len(history)}")
        
        return history
    
    def get_last_assistant_message(self, session_id: str) -> str:
        """获取最后一条助手消息"""
        if session_id not in self.sessions:
            return ""
        
        # 从后往前查找最后一条助手消息
        for message in reversed(self.sessions[session_id]):
            if message['role'] == 'assistant':
                return message['content']
        
        return ""
    
    def clear_history(self, session_id: str):
        """清除历史记录"""
        if session_id in self.sessions:
            self.sessions[session_id] = []
            self._save_session(session_id)
            self.logger.info(f"🗑️ 清除历史记录 - 会话: {session_id}")
    
    def get_all_sessions(self) -> List[str]:
        """获取所有会话ID"""
        return list(self.sessions.keys())
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """获取会话信息"""
        if session_id not in self.sessions:
            return {}
        
        messages = self.sessions[session_id]
        
        return {
            'session_id': session_id,
            'message_count': len(messages),
            'created_at': messages[0]['timestamp'] if messages else None,
            'last_updated': messages[-1]['timestamp'] if messages else None
        }

