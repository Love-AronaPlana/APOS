#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具包装器模块
"""

from mcp import ClientSession
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack
import asyncio
from utils.logger import get_logger


class MCPToolWrapper:
    """MCP 工具包装器"""

    def __init__(self, server_params, tool_name, description, input_schema):
        self.server_params = server_params
        self.tool_name = tool_name
        self.description = description
        self.input_schema = input_schema
        self.logger = get_logger(f"MCPToolWrapper.{tool_name}")

    def get_description(self):
        """获取工具描述"""
        return self.description

    def get_parameters(self):
        """获取工具参数定义"""
        return self.input_schema

    def execute(self, parameters):
        """执行 MCP 工具"""
        try:
            # 异步执行工具调用
            result = asyncio.run(self._async_execute(parameters))
            return result
        except Exception as e:
            self.logger.error(f"❌ MCP 工具执行失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _async_execute(self, parameters):
        """异步执行 MCP 工具"""
        async with AsyncExitStack() as stack:
            stdio_transport = await stack.enter_async_context(
                stdio_client(self.server_params)
            )
            _stdio, write = stdio_transport

            session = await stack.enter_async_context(ClientSession(_stdio, write))
            await session.initialize()

            # 调用工具
            response = await session.call_tool(
                name=self.tool_name, arguments=parameters
            )

            # 处理响应
            if response.isError:
                error_msg = response.content[0].text if response.content else "未知错误"
                return {"success": False, "error": error_msg}

            # 提取文本内容
            result = []
            for content_block in response.content:
                if hasattr(content_block, "text"):
                    result.append(content_block.text)
                else:
                    result.append(f"[非文本内容: {type(content_block).__name__}]")

            return {"success": True, "result": "\n".join(result)}
