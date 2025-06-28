import json
import requests

class MpcClient:
    def __init__(self, url="http://localhost:8900/mcp"):
        self.url = url
        self._id = 0

    def _next_id(self):
        self._id += 1
        return self._id

    def _send(self, method, params=None):
        """发送一个 JSON-RPC 请求，并实时迭代返回的 JSON-RPC 响应流"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params or {}
        }
        # 注意：Streamable HTTP 要求服务器以 chunked 形式持续推送消息
        resp = requests.post(self.url, json=payload, headers={
            "Content-Type": "application/json"
        }, stream=True)
        resp.raise_for_status()

        # 按行读取，每行一个 JSON 对象
        for raw in resp.iter_lines(decode_unicode=True):
            if not raw:
                continue
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            # 这里只简单返回第一条消息；如果是长流，可累积或持续处理
            return msg

    def initialize(self, name="python-mcp-client", version="0.1.0"):
        """初始化 MCP 会话"""
        result = self._send("initialize", {
            "clientName": name,
            "clientVersion": version
        })
        print("initialize →", result)
        return result

    def list_resources(self):
        """列出服务器上暴露的所有资源"""
        result = self._send("listResources")
        print("listResources →", result)
        return result

    def read_resource(self, uri):
        """读取指定资源 URI"""
        result = self._send("readResource", {"uri": uri})
        print(f"readResource('{uri}') →", result)
        return result

    def list_tools(self):
        """列出服务器上暴露的所有工具"""
        result = self._send("listTools")
        print("listTools →", result)
        return result

    def call_tool(self, name, arguments):
        """调用工具"""
        result = self._send("callTool", {
            "name": name,
            "arguments": arguments
        })
        print(f"callTool('{name}', {arguments}) →", result)
        return result

if __name__ == "__main__":
    client = MpcClient("http://localhost:8900/mcp")

    # 1. 初始化
    client.initialize()

    # 2. 查看可用资源 & 工具
    client.list_resources()
    client.list_tools()

    # 3. 读取一个示例资源（假设服务器实现了 greeting://{name}）
    client.read_resource("greeting://Chen")

    # 4. 调用一个示例工具（假设服务器实现了 add 工具）
    client.call_tool("add", {"a": 10, "b": 32})
