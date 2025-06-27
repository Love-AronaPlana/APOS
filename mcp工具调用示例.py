import asyncio
import os
import json
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """
    使用 mcp.py 库连接到 MCP 服务器并与之交互的主函数。（类型安全最终版）
    """
    print("🚀 正在启动并连接到 MCP 文件服务器...")

    server_params = StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-filesystem",
            "C:\\Users\\Gavin\\Desktop",
            "E:\\",
        ],
    )

    async with AsyncExitStack() as stack:
        try:
            # 1. 连接服务器
            stdio_transport = await stack.enter_async_context(
                stdio_client(server_params)
            )
            _stdio, write = stdio_transport

            # 2. 创建会话
            session = await stack.enter_async_context(ClientSession(_stdio, write))
            await session.initialize()
            print("✅ 服务器连接成功，会话已建立！")

            # 3. 获取工具列表 (并显示参数)
            print("\n" + "=" * 20 + " 1. 发现工具 " + "=" * 20)
            list_tools_response = await session.list_tools()

            print("\n🔍 服务器提供的工具详细信息:")
            for tool in list_tools_response.tools:
                print(f"\n  ▶ 工具名称: {tool.name}")
                print(f"    功能描述: {tool.description}")
                print(f"    参数说明 (inputSchema): {tool.inputSchema}")

            # 4. 调用 'list_directory' 工具
            print("\n" + "=" * 20 + " 2. 调用 'list_directory' 工具 " + "=" * 20)
            target_directory = "C:\\Users\\Gavin\\Desktop"
            target_directory = os.path.normpath(target_directory)

            print(f"正在请求目录 '{target_directory}' 的内容...")
            call_tool_response = await session.call_tool(
                name="list_directory", arguments={"path": target_directory}
            )

            # 5. 查看结果
            print("\n" + "=" * 20 + " 3. 查看结果 " + "=" * 20)

            # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ #
            #                                                                 #
            #                  这 是 最 终 的 彻 底 修 复                     #
            #                                                                 #
            # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ #
            if not call_tool_response.isError:
                print(f"\n📂 目录 '{target_directory}' 下的内容获取成功:")
                print("--------------------------------------------------")

                # 遍历所有返回的内容块 (一个响应里可能有多个)
                for content_block in call_tool_response.content:
                    # 使用 hasattr 进行安全检查，看这个内容块有没有 .text 属性
                    if hasattr(content_block, "text"):
                        # 如果有，说明是文本内容，直接打印
                        print(content_block.text)
                    else:
                        # 如果没有，说明是图片等其他类型，打印提示信息
                        print(
                            f"[收到非文本内容，类型为: {type(content_block).__name__}]"
                        )

                print("--------------------------------------------------")

            else:
                # 错误信息也同样做安全检查
                error_text = ""
                if call_tool_response.content and hasattr(
                    call_tool_response.content[0], "text"
                ):
                    error_text = call_tool_response.content[0].text
                print(f"\n❌ 工具执行失败: {error_text}")
            # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ #
            #                                                                 #
            # =============================================================== #
            # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ #

        except Exception as e:
            print(f"\n❌ 发生严重错误: {e}")
            import traceback

            traceback.print_exc()

    print("\n🛑 会话已关闭，程序结束。")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断。")
