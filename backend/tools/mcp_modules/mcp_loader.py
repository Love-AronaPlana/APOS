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
                    asyncio.run(self._load_all_servers(mcp_servers))

                except Exception as e:
                    self.logger.error(f"❌ 加载 MCP 配置失败 {filename}: {str(e)}")

    async def _load_all_servers(self, mcp_servers):
        """异步加载所有MCP服务器"""
        tasks = []
        for server_name, server_config in mcp_servers.items():
            # 检查是否启用该服务器
            if not server_config.get('enabled', True):
                self.logger.info(f"⏭️ 跳过禁用的 MCP 服务器: {server_name}")
                continue
            
            self.logger.info(f"📡 连接 MCP 服务器: {server_name}")

            # 获取传输方式和URL
            transport = server_config.get('transport', 'stdio')
            url = server_config.get('url')

            # 根据传输方式创建服务器参数
            if transport == 'stdio':
                server_params = StdioServerParameters(
                    command=server_config.get("command"),
                    args=server_config.get("args", []),
                    env=server_config.get("env", {}),
                )
            else:
                server_params = None

            tasks.append(self._get_mcp_server_tools(server_name, transport, url, server_params))

        # 并行获取所有服务器的工具列表
        results = await asyncio.gather(*tasks)

        # 处理所有结果并注册工具
        for result in results:
            if result:
                server_name, server_info, tools = result
                for tool in tools:
                    tool_name = f"mcp_{server_name}_{tool.name}"
                    transport = server_info.get('transport', 'stdio')
                    url = server_info.get('url')
                    server_params = server_info.get('server_params')
                    tool_instance = MCPToolWrapper(
                        server_params=server_params,
                        tool_name=tool.name,
                        description=tool.description,
                        input_schema=tool.inputSchema,
                        transport=transport,
                        url=url
                    )

                    self.tool_manager.tools[tool_name] = tool_instance
                    self.tool_manager.tool_descriptions[tool_name] = (
                        tool.description
                    )
                    self.logger.info(f"✅ 注册 MCP 工具: {tool_name}")

    async def _get_mcp_server_tools(self, server_name, transport, url, server_params):
        """异步获取MCP服务器提供的工具列表"""
        if transport == 'stdio':
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
                    return (server_name, {'transport': transport, 'server_params': server_params}, list_tools_response.tools)

                except Exception as e:
                    self.logger.error(f"❌ 获取 MCP 工具列表失败: {str(e)}")
                    return None
        elif transport == 'streamable-http':
            import requests
            import json
            from requests.exceptions import RequestException

            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "listTools",
                    "params": {}
                }
                self.logger.info(f"📡 连接 HTTP MCP 服务器: {url}")
                resp = requests.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    stream=True,
                    timeout=30
                )
                resp.raise_for_status()

                tools = []
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                        if 'error' in msg:
                            self.logger.error(f"❌ 服务器返回错误: {msg['error']}")
                            return None
                        if 'result' in msg and 'tools' in msg['result']:
                            tools = msg['result']['tools']
                            break
                    except json.JSONDecodeError:
                        self.logger.warning(f"无法解析响应行: {line}")
                        continue

                if not tools:
                    self.logger.warning(f"⚠️ 未从服务器获取到工具列表: {url}")
                    return None

                return (server_name, {'transport': transport, 'url': url}, tools)
            except RequestException as e:
                self.logger.error(f"❌ HTTP 请求失败: {str(e)}")
                return None
            except Exception as e:
                self.logger.error(f"❌ 获取 HTTP MCP 工具列表失败: {str(e)}")
                return None
        else:
            self.logger.error(f"❌ 不支持的传输方式: {transport}")
            return None

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
