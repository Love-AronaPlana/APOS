#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS LLM 客户端模块
"""

import openai
from typing import List, Dict, Any
from config.settings import Config
from utils.logger import get_logger

class LLMClient:
    """LLM 客户端类"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # 验证配置
        Config.validate_config()
        
        # 初始化 OpenAI 客户端
        self.client = openai.OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_API_BASE
        )
        
        self.model = Config.OPENAI_API_MODEL
        
        self.logger.info("🔗 LLM 客户端初始化完成")
    
    def chat(self, system_prompt: str, messages: List[Dict[str, Any]]) -> str:
        """发送聊天请求"""
        try:
            # 构建消息列表
            chat_messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # 添加历史消息
            for msg in messages:
                role = msg['role']
                content = msg['content']
                
                # 处理多模态消息
                if isinstance(content, list):
                    # 多模态消息（文本 + 图片）
                    chat_messages.append({
                        "role": role,
                        "content": content
                    })
                else:
                    # 纯文本消息
                    chat_messages.append({
                        "role": role,
                        "content": content
                    })
            
            self.logger.info(f"📤 发送请求到 LLM - 消息数量: {len(chat_messages)}")
            self.logger.debug(f"📋 请求详情: {chat_messages}")
            
            # 发送请求
            response = self.client.chat.completions.create(
                model=self.model,
                messages=chat_messages,
                temperature=0.7,
                max_tokens=4000
            )
            
            # 提取响应内容
            if hasattr(response, 'choices') and len(response.choices) > 0:
                content = response.choices[0].message.content
            else:
                content = str(response)
            
            self.logger.info(f"📥 收到 LLM 响应 - 长度: {len(content)}")
            self.logger.debug(f"📝 响应内容: {content}")
            
            return content
            
        except Exception as e:
            self.logger.error(f"❌ LLM 请求错误: {str(e)}")
            raise e
    
    def create_multimodal_content(self, text: str, image_urls: List[str] = None) -> List[Dict[str, Any]]:
        """创建多模态内容"""
        content = []
        
        # 添加文本内容
        if text:
            content.append({
                "type": "text",
                "text": text
            })
        
        # 添加图片内容
        if image_urls:
            for image_url in image_urls:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                })
        
        return content

