#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS 主应用文件
"""

from flask import Flask
from flask_cors import CORS
from config.settings import Config
from core.api import api_bp
from utils.logger import setup_logger
import os


def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(Config)

    # 启用 CORS
    CORS(app, origins="*")

    # 设置日志
    setup_logger()

    # 提前初始化工具管理器以加载MCP服务器
    from tools.tool_manager import ToolManager
    ToolManager()

    # 注册蓝图
    app.register_blueprint(api_bp, url_prefix="/api")

    return app


if __name__ == "__main__":
    app = create_app()
    print("🚀 APOS 后端服务启动中...")
    print(f"📡 API 地址: http://0.0.0.0:8880")
    print(f"📋 API 文档: http://0.0.0.0:8880/api/health")
    app.run(host="0.0.0.0", port=8880, debug=False)
