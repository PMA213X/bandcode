import { useState, useEffect } from 'react'
import { MessageSquare, Trash2, RefreshCw } from 'lucide-react'
import axios from 'axios'

interface Session {
  session_id: string
  created_at: string
  message_count: number
  last_message?: string
}

export default function History() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedSession, setSelectedSession] = useState<string | null>(null)
  const [messages, setMessages] = useState<any[]>([])

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      const response = await axios.get('/api/chat/history')
      if (response.data.code === 0) {
        setSessions(response.data.data.sessions || [])
      }
    } catch (error) {
      console.error('加载历史失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadSessionMessages = async (sessionId: string) => {
    try {
      const response = await axios.get(`/api/chat/history?session_id=${sessionId}`)
      if (response.data.code === 0) {
        setMessages(response.data.data.messages || [])
        setSelectedSession(sessionId)
      }
    } catch (error) {
      console.error('加载消息失败:', error)
    }
  }

  const deleteSession = async (sessionId: string) => {
    if (!confirm('确定删除此会话？')) return
    try {
      await axios.delete(`/api/chat/history?session_id=${sessionId}`)
      setSessions(prev => prev.filter(s => s.session_id !== sessionId))
      if (selectedSession === sessionId) {
        setSelectedSession(null)
        setMessages([])
      }
    } catch (error) {
      console.error('删除失败:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <RefreshCw className="animate-spin" size={24} />
      </div>
    )
  }

  return (
    <div className="flex h-full">
      {/* 左侧会话列表 */}
      <div className="w-64 border-r border-gray-700 p-4 overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-gray-400">历史会话</h3>
          <button onClick={loadSessions} className="text-gray-400 hover:text-white">
            <RefreshCw size={16} />
          </button>
        </div>

        <div className="space-y-2">
          {sessions.map((session) => (
            <div
              key={session.session_id}
              onClick={() => loadSessionMessages(session.session_id)}
              className={`p-3 rounded-lg cursor-pointer ${
                selectedSession === session.session_id
                  ? 'bg-cyan-600'
                  : 'bg-gray-800 hover:bg-gray-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <MessageSquare size={16} />
                  <span className="text-sm truncate">
                    {session.last_message || '新会话'}
                  </span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteSession(session.session_id)
                  }}
                  className="text-gray-400 hover:text-red-400"
                >
                  <Trash2 size={14} />
                </button>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {new Date(session.created_at).toLocaleString()}
              </div>
            </div>
          ))}

          {sessions.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              暂无历史会话
            </div>
          )}
        </div>
      </div>

      {/* 右侧消息详情 */}
      <div className="flex-1 p-4 overflow-auto">
        {selectedSession ? (
          <div className="space-y-4">
            <h3 className="text-lg font-bold">会话详情</h3>
            {messages.map((msg, index) => (
              <div key={index} className="bg-gray-800 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-2">
                  {msg.role === 'user' ? '用户' : 'AI'}
                </div>
                <div className="whitespace-pre-wrap">{msg.content}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            选择一个会话查看详情
          </div>
        )}
      </div>
    </div>
  )
}
