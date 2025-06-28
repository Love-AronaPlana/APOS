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

    def __init__(self, server_params, tool_name, description, input_schema, transport='stdio', url=None):
        self.server_params = server_params
        self.tool_name = tool_name
        self.description = description
        self.input_schema = input_schema
        self.transport = transport
        self.url = url
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
        if self.transport == 'stdio':
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
        elif self.transport == 'streamable-http':
            import requests
            import json
            from requests.exceptions import RequestException

            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "callTool",
                "params": {
                    "name": self.tool_name,
                    "arguments": parameters
                }
            }

            try:
                resp = requests.post(
                    self.url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    stream=True,
                    timeout=30
                )
                resp.raise_for_status()

                result = []
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                        if 'error' in msg:
                            return {"success": False, "error": msg['error'].get('message', '未知错误')}
                        if 'result' in msg:
                            result.append(str(msg['result']))
                    except json.JSONDecodeError:
                        self.logger.warning(f"无法解析响应行: {line}")
                        continue

                if not result:
                    return {"success": False, "error": "未收到有效的响应数据"}
                
                return {"success": True, "result": "\n".join(result)}
            except RequestException as e:
                return {"success": False, "error": f"HTTP请求失败: {str(e)}"}
            except Exception as e:
                return {"success": False, "error": f"处理响应失败: {str(e)}"}
        else:
            return {"success": False, "error": f"不支持的传输方式: {self.transport}"}
