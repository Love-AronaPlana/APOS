import asyncio
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # 从 .env 文件加载环境变量


class MCPClient:
    def __init__(self):
        # 初始化会话和客户端对象
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    # 方法将在这里定义

    async def connect_to_server(self, server_script_path: str):
        """连接到 MCP 服务器"""
        print(f"[DEBUG] 正在连接服务器，脚本路径: {server_script_path}")
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("服务器脚本必须是 .py 或 .js 文件")
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "C:\\Users\\Gavin",
                "C:\\Users\\Gavin\\Desktop",
            ],
            env=None,
        )
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        print(f"[DEBUG] 成功创建 stdio 传输")
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        print(f"[DEBUG] 正在初始化会话...")
        await self.session.initialize()
        print(f"[DEBUG] 会话初始化成功")

    async def process_query(self, query: str) -> str:
        """使用 Claude 和可用工具处理查询"""
        print(f"[DEBUG] 处理查询: {query}")
        messages = [{"role": "user", "content": query}]
        print(f"[DEBUG] 获取可用工具列表...")
        response = await self.session.list_tools()
        print(f"[DEBUG] 获取到 {len(response.tools)} 个可用工具")

        # 添加工具详细信息输出
        print("\n[DEBUG] 可用工具详细信息:")
        for i, tool in enumerate(response.tools, 1):
            print(f"  {i}. {tool.name}")
            print(f"     描述: {tool.description}")
            print(f"     输入参数: {tool.inputSchema}")
            print("     --------------------")

        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]
        # 调用 Claude API 处理初始查询
        print(f"[DEBUG] 调用 Claude API，模型: claude-3-5-sonnet-20241022")
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools,
        )
        print(
            f"[DEBUG] 收到 Claude 响应，内容类型: {[c.type for c in response.content]}"
        )
        # 处理响应，并执行工具调用
        final_text = []
        assistant_message_content = []
        for content in response.content:
            if content.type == "text":
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input
                # 执行工具调用
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[调用工具 {tool_name} 参数: {tool_args}]")
                assistant_message_content.append(content)
                messages.append(
                    {"role": "assistant", "content": assistant_message_content}
                )
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": result.content,
                            }
                        ],
                    }
                )
                # 获取 Claude 的后续响应
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools,
                )
                final_text.append(response.content[0].text)
        return "\n".join(final_text)

    async def chat_loop(self):
        """运行交互式聊天"""
        print("[DEBUG] 进入聊天循环")
        print("\nMCP 客户端已启动!")
        print("请输入查询，或输入 'quit' 退出。")
        while True:
            try:
                query = input("\n输入查询: ").strip()
                print(f"[DEBUG] 用户输入: {query}")
                if query.lower() == "quit":
                    print("[DEBUG] 检测到退出命令")
                    break
                response = await self.process_query(query)
                print(f"[DEBUG] 最终响应内容: {response}")
            except Exception as e:
                print(f"[DEBUG] 捕获异常: {str(e)}")
                print("\n" + response)
            except Exception as e:
                print(f"\n错误: {str(e)}")


async def main():
    print("正在启动 MCP 客户端...")
    client = MCPClient()
    print("正在连接服务器...")
    await client.connect_to_server("path/to/your/server_script.js")
    print("服务器连接成功，启动聊天循环...")
    await client.chat_loop()


if __name__ == "__main__":
    asyncio.run(main())
