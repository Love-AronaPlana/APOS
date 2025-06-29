#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APOS 工具管理器
"""

import json
import importlib
import os
from typing import Dict, List, Any, Optional
from utils.logger import get_logger
from mcp import StdioServerParameters
import asyncio


class ToolManager:
    """工具管理器"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.tools: Dict[str, Any] = {}
        self.tool_descriptions: Dict[str, str] = {}

        # 加载内置工具
        self._load_builtin_tools()

        # 加载 MCP 工具
        self._load_mcp_tools()

        self.logger.info(f"🔧 工具管理器初始化完成 - 已加载 {len(self.tools)} 个工具")

    def _load_builtin_tools(self):
        """加载内置工具"""
        builtin_tools = [
            "web_search",
            "file_operations",
            "calculator",
            "weather",
            "time_utils",
        ]

        for tool_name in builtin_tools:
            try:
                module = importlib.import_module(f"tools.builtin.{tool_name}")
                tool_class = getattr(
                    module, f'{tool_name.title().replace("_", "")}Tool'
                )
                tool_instance = tool_class()

                self.tools[tool_name] = tool_instance
                self.tool_descriptions[tool_name] = tool_instance.get_description()

                self.logger.info(f"✅ 加载内置工具: {tool_name}")

            except Exception as e:
                self.logger.error(f"❌ 加载内置工具失败 {tool_name}: {str(e)}")

    def _load_mcp_tools(self):
        """加载 MCP 工具"""
        from .mcp_modules.mcp_loader import MCPLoader

        self.mcp_loader = MCPLoader(self)
        self.mcp_loader.load_mcp_tools()

    async def _get_mcp_server_tools(self, server_params):
        """此方法已迁移至 MCPLoader"""
        pass

    def execute_tool(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行工具"""
        self.logger.info(f"🚀 执行工具: {tool_name}")
        self.logger.debug(f"📋 工具参数: {parameters}")

        if tool_name not in self.tools:
            error_msg = f"工具 '{tool_name}' 不存在"
            self.logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "available_tools": list(self.tools.keys()),
            }

        try:
            tool = self.tools[tool_name]
            result = tool.execute(parameters)

            self.logger.info(f"✅ 工具执行成功: {tool_name}")
            self.logger.debug(f"📤 工具结果: {result}")

            return {"success": True, "result": result, "tool": tool_name}

        except Exception as e:
            error_msg = f"工具执行失败: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg, "tool": tool_name}

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        tools_list = []

        for tool_name, tool in self.tools.items():
            tools_list.append(
                {
                    "name": tool_name,
                    "description": self.tool_descriptions.get(tool_name, ""),
                    "parameters": (
                        tool.get_parameters() if hasattr(tool, "get_parameters") else {}
                    ),
                }
            )

        return tools_list

    def get_tools_description(self) -> str:
        """获取工具描述文本，包含名称、描述和参数说明"""
        descriptions = []
        available_tools = self.get_available_tools()

        for tool_info in available_tools:
            tool_name = tool_info['name']
            description = tool_info['description']
            parameters = tool_info['parameters']
            
            # 格式化参数说明
            param_str = []
            for param, details in parameters.items():
                param_str.append(f"{param}: {details}")
            params_description = "，".join(param_str) if param_str else "无"
            
            descriptions.append(f"- {tool_name}: {description} (调用参数: {params_description})")

        return "\n".join(descriptions)

    def add_mcp_tool(self, config: Dict[str, Any]) -> bool:
        """添加 MCP 工具"""
        return self.mcp_loader.add_mcp_tool(config)
