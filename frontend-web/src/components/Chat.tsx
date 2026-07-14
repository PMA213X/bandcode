import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User } from 'lucide-react'
import CommandPalette from './CommandPalette'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  agent?: string
  timestamp: Date
}

interface ChatProps {
  onSwitchView?: (view: string) => void
}

export default function Chat({ onSwitchView }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (message?: string) => {
    const text = message ?? input
    if (!text.trim() || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    // 创建助手消息占位
    const assistantId = (Date.now() + 1).toString()
    const assistantMessage: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, assistantMessage])

    try {
      const sessionId = 'default'
      const eventSource = new EventSource(
        `/api/chat/stream?session_id=${sessionId}&project=default&message=${encodeURIComponent(text)}`
      )
      console.log('EventSource created:', eventSource)

      // 忽略中间事件，防止 EventSource 把未知事件类型当错误处理
      const ignoreEvents = ['agent_start', 'constraint_result', 'plan', 'tool_call', 'code', 'test_result', 'review_result', 'memory_update', 'approval_required']
      ignoreEvents.forEach(evt => {
        eventSource.addEventListener(evt, () => {})
      })

      eventSource.addEventListener('text', (event) => {
        console.log('Received text event:', event.data)
        const data = JSON.parse((event as MessageEvent).data)
        setMessages(prev => prev.map(msg =>
          msg.id === assistantId
            ? { ...msg, content: msg.content + data.content }
            : msg
        ))
      })

      eventSource.addEventListener('chat_error', (event) => {
        const data = JSON.parse((event as MessageEvent).data)
        setMessages(prev => prev.map(msg =>
          msg.id === assistantId
            ? { ...msg, content: msg.content || `[错误] ${data.message || '未知错误'}` }
            : msg
        ))
        eventSource.close()
        setLoading(false)
      })

      eventSource.addEventListener('done', () => {
        eventSource.close()
        setLoading(false)
      })

      eventSource.onopen = () => {
        console.log('EventSource opened')
      }
      eventSource.onerror = (error) => {
        console.error('EventSource error:', error)
        eventSource.close()
        setLoading(false)
      }
    } catch (error) {
      console.error('Error:', error)
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    } else if (e.key === '/' && !input) {
      e.preventDefault()
      setCommandPaletteOpen(true)
    }
  }

  const handleCommandMessage = (message: string) => {
    if (message === '/clear') {
      setMessages([])
    } else if (message) {
      handleSend(message)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* 消息列表 */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-20">
            <Bot size={48} className="mx-auto mb-4 opacity-50" />
            <p className="text-lg">输入消息开始对话...</p>
            <p className="text-sm mt-2">使用 / 打开命令面板</p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-cyan-600 flex items-center justify-center">
                <Bot size={16} />
              </div>
            )}

            <div
              className={`max-w-[70%] rounded-lg px-4 py-2 ${
                msg.role === 'user'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-700 text-gray-100'
              }`}
            >
              <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
              <div className="text-xs opacity-50 mt-1">
                {msg.timestamp.toLocaleTimeString()}
              </div>
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
                <User size={16} />
              </div>
            )}
          </div>
        ))}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入框 */}
      <div className="border-t border-gray-700 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入消息... (/ 打开命令面板)"
            className="input flex-1"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={20} />
          </button>
        </div>
      </div>

      {/* 命令面板 */}
      <CommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        onSendMessage={handleCommandMessage}
        onSwitchView={onSwitchView}
      />
    </div>
  )
}
