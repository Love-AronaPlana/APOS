import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { Send, Bot, User, Trash2, Settings, Zap, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState('default')
  const [tools, setTools] = useState([])

  // 获取可用工具列表
  useEffect(() => {
    fetchTools()
  }, [])

  const fetchTools = async () => {
    try {
      const response = await fetch('http://localhost:8880/api/tools')
      const data = await response.json()
      setTools(data.tools || [])
    } catch (error) {
      console.error('获取工具列表失败:', error)
    }
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8880/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          session_id: sessionId
        })
      })

      const data = await response.json()

      if (data.error) {
        throw new Error(data.error)
      }

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toLocaleTimeString(),
        iterations: data.iterations,
        status: data.status
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        role: 'error',
        content: `错误: ${error.message}`,
        timestamp: new Date().toLocaleTimeString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const clearHistory = async () => {
    try {
      await fetch(`http://localhost:8880/api/clear/${sessionId}`, {
        method: 'DELETE'
      })
      setMessages([])
    } catch (error) {
      console.error('清除历史记录失败:', error)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const getMessageIcon = (role) => {
    switch (role) {
      case 'user':
        return <User className="w-4 h-4" />
      case 'assistant':
        return <Bot className="w-4 h-4" />
      case 'error':
        return <AlertCircle className="w-4 h-4" />
      default:
        return <Bot className="w-4 h-4" />
    }
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <Badge variant="success" className="ml-2"><CheckCircle className="w-3 h-3 mr-1" />完成</Badge>
      case 'max_iterations_reached':
        return <Badge variant="warning" className="ml-2"><Clock className="w-3 h-3 mr-1" />达到最大迭代</Badge>
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-6 max-w-7xl flex flex-col flex-1">
        {/* 头部 */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">APOS</h1>
              <p className="text-sm text-slate-600 dark:text-slate-400">通用型 AI Agent</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={clearHistory}>
              <Trash2 className="w-4 h-4 mr-2" />
              清除历史
            </Button>
            <Button variant="outline" size="sm">
              <Settings className="w-4 h-4" />
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1">
          {/* 工具面板 */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <Settings className="w-5 h-5 mr-2" />
                  可用工具
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  <div className="space-y-2">
                    {tools.map((tool, index) => (
                      <div key={index} className="tool-card p-3 border rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                        <div className="font-medium text-sm">{tool.name}</div>
                        <div className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                          {tool.description}
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          {/* 聊天区域 */}
          <div className="lg:col-span-3 flex flex-col flex-1">
            <Card className="flex flex-col flex-1">
              <CardHeader>
                <CardTitle className="text-lg">对话</CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col">
                {/* 消息列表 */}
                <ScrollArea className="flex-1 mb-4">
                  <div className="space-y-4">
                    {messages.length === 0 && (
                      <div className="text-center text-slate-500 dark:text-slate-400 py-8">
                        <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>开始与 APOS 对话吧！</p>
                        <p className="text-sm mt-2">我可以帮助您完成各种复杂任务</p>
                      </div>
                    )}
                    {messages.map((message) => (
                      <div key={message.id} className="flex items-start space-x-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          message.role === 'user' 
                            ? 'bg-blue-500 text-white' 
                            : message.role === 'error'
                            ? 'bg-red-500 text-white'
                            : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
                        }`}>
                          {getMessageIcon(message.role)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="font-medium text-sm">
                              {message.role === 'user' ? '用户' : message.role === 'error' ? '错误' : 'APOS'}
                            </span>
                            <span className="text-xs text-slate-500">{message.timestamp}</span>
                            {message.iterations && (
                              <Badge variant="secondary" className="text-xs">
                                {message.iterations} 次迭代
                              </Badge>
                            )}
                            {message.status && getStatusBadge(message.status)}
                          </div>
                          <div className={`prose prose-sm max-w-none ${
                            message.role === 'error' ? 'text-red-600 dark:text-red-400' : ''
                          }`}>
                            <pre className="whitespace-pre-wrap font-sans">{message.content}</pre>
                          </div>
                        </div>
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
                          <Bot className="w-4 h-4 text-slate-700 dark:text-slate-300 animate-pulse" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="font-medium text-sm">APOS</span>
                            <span className="text-xs text-slate-500">正在思考...</span>
                          </div>
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </ScrollArea>

                <Separator className="mb-4" />

                {/* 输入区域 */}
                <div className="flex space-x-2">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="输入您的消息..."
                    disabled={isLoading}
                    className="flex-1"
                  />
                  <Button 
                    onClick={sendMessage} 
                    disabled={isLoading || !inputMessage.trim()}
                    size="icon"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

