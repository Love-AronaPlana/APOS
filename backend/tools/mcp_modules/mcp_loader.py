#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具加载器模块
"""

import json
import os
import asyncio
from typing import Dict, List, Any
from utils.logger import get_logger
from mcp import StdioServerParameters
from .mcp_tool import MCPToolWrapper


class MCPLoader:
    """MCP工具加载器"""

    def __init__(self, tool_manager):
        self.logger = get_logger(__name__)
        self.tool_manager = tool_manager
        self.mcp_dir = os.path.join(os.path.dirname(__file__), "..", "mcp")

        # 确保MCP目录存在
        if not os.path.exists(self.mcp_dir):
            os.makedirs(self.mcp_dir)
            self.logger.info("📁 创建 MCP 工具目录")

    def load_mcp_tools(self) -> None:
        """加载所有MCP工具"""
        # 扫描MCP服务器配置文件
        for filename in os.listdir(self.mcp_dir):
            if filename.endswith(".json"):
                try:
                    config_path = os.path.join(self.mcp_dir, filename)
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)

                    # 解析MCP服务器配置
                    mcp_servers = config.get("mcpServers", {})
                    for server_name, server_config in mcp_servers.items():
                        self.logger.info(f"📡 连接 MCP 服务器: {server_name}")

                        # 创建MCP服务器参数
                        server_params = StdioServerParameters(
                            command=server_config.get("command"),
                            args=server_config.get("args", []),
                            env=server_config.get("env", {}),
                        )

                        # 异步连接MCP服务器并获取工具列表
                        tools = asyncio.run(self._get_mcp_server_tools(server_params))

                        # 注册MCP服务器提供的工具
                        for tool in tools:
                            tool_name = f"mcp_{server_name}_{tool.name}"
                            tool_instance = MCPToolWrapper(
                                server_params=server_params,
                                tool_name=tool.name,
                                description=tool.description,
                                input_schema=tool.inputSchema,
                            )

                            self.tool_manager.tools[tool_name] = tool_instance
                            self.tool_manager.tool_descriptions[tool_name] = (
                                tool.description
                            )
                            self.logger.info(f"✅ 注册 MCP 工具: {tool_name}")

                except Exception as e:
                    self.logger.error(f"❌ 加载 MCP 配置失败 {filename}: {str(e)}")

    async def _get_mcp_server_tools(self, server_params):
        """异步获取MCP服务器提供的工具列表"""
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client
        from contextlib import AsyncExitStack

        async with AsyncExitStack() as stack:
            try:
                # 连接服务器
                stdio_transport = await stack.enter_async_context(
                    stdio_client(server_params)
                )
                _stdio, write = stdio_transport

                # 创建会话
                session = await stack.enter_async_context(ClientSession(_stdio, write))
                await session.initialize()

                # 获取工具列表
                list_tools_response = await session.list_tools()
                return list_tools_response.tools

            except Exception as e:
                self.logger.error(f"❌ 获取 MCP 工具列表失败: {str(e)}")
                return []

    def add_mcp_tool(self, config: Dict[str, Any]) -> bool:
        """添加MCP工具"""
        try:
            tool_name = config.get("name")
            if not tool_name:
                raise ValueError("工具名称不能为空")

            # 保存配置文件
            config_path = os.path.join(self.mcp_dir, f"{tool_name}.json")

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            self.logger.info(f"✅ 添加 MCP 工具: {tool_name}")

            # 重新加载工具
            self.load_mcp_tools()

            return True

        except Exception as e:
            self.logger.error(f"❌ 添加 MCP 工具失败: {str(e)}")
            return False
