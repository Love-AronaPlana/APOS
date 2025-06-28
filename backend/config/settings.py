#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS 配置文件
"""

import os
from dotenv import load_dotenv

# 加载环境变量
# 使用绝对路径加载.env文件
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))


class Config:
    """应用配置类"""

    # Flask 配置
    SECRET_KEY = os.environ.get("SECRET_KEY") or "apos-secret-key-2024"
    DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

    # OpenAI API 配置
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_API_MODEL = os.environ.get("OPENAI_API_MODEL", "gpt-3.5-turbo")

    # 日志配置
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # 历史记录配置
    MAX_HISTORY_LENGTH = int(os.environ.get("MAX_HISTORY_LENGTH", "100"))

    @classmethod
    def validate_config(cls):
        """验证配置"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY 环境变量未设置")

        else:
            print(f"✅ 配置验证通过")
            print(f"🔑 API Key: {cls.OPENAI_API_KEY[:10]}...")
            print(f"🌐 API Base: {cls.OPENAI_API_BASE}")
            print(f"🤖 Model: {cls.OPENAI_API_MODEL}")
