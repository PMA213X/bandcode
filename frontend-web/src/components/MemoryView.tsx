import React, { useState, useEffect } from 'react'
import { RefreshCw, Search, Globe, Folder, List, MessageSquare, Camera } from 'lucide-react'
import axios from 'axios'

const LAYERS = [
  { id: 'global', name: '全局', icon: Globe },
  { id: 'project', name: '项目', icon: Folder },
  { id: 'task', name: '任务', icon: List },
  { id: 'session', name: '会话', icon: MessageSquare },
  { id: 'checkpoint', name: '快照', icon: Camera },
]

export default function MemoryView() {
  const [activeLayer, setActiveLayer] = useState('global')
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadMemory(activeLayer)
  }, [activeLayer])

  const loadMemory = async (layer: string) => {
    setLoading(true)
    try {
      const response = await axios.get(`/api/memory?layer=${layer}`)
      if (response.data.code === 0) {
        setContent(response.data.data.content || '暂无内容')
      }
    } catch (error) {
      console.error('加载 Memory 失败:', error)
      setContent('加载失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    setLoading(true)
    try {
      const response = await axios.get(`/api/memory/search?query=${encodeURIComponent(searchQuery)}`)
      if (response.data.code === 0) {
        setContent(JSON.stringify(response.data.data, null, 2))
      }
    } catch (error) {
      console.error('搜索失败:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-full">
      {/* 左侧层级选择 */}
      <div className="w-48 border-r border-gray-700 p-4">
        <h3 className="text-sm font-semibold text-gray-400 mb-4">Memory 层级</h3>
        <nav className="space-y-1">
          {LAYERS.map((layer) => {
            const Icon = layer.icon
            return (
              <button
                key={layer.id}
                onClick={() => setActiveLayer(layer.id)}
                className={`w-full text-left px-3 py-2 rounded-md text-sm flex items-center gap-2 ${
                  activeLayer === layer.id
                    ? 'bg-cyan-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                <Icon size={16} />
                {layer.name}
              </button>
            )
          })}
        </nav>
        
        {/* 搜索框 */}
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-gray-400 mb-2">搜索</h3>
          <div className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="搜索记忆..."
              className="input text-sm"
            />
          </div>
        </div>
      </div>
      
      {/* 右侧内容 */}
      <div className="flex-1 p-6 overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">Memory 浏览器</h2>
          <button
            onClick={() => loadMemory(activeLayer)}
            className="btn-primary flex items-center gap-2"
          >
            <RefreshCw size={16} />
            刷新
          </button>
        </div>
        
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="animate-spin" size={24} />
          </div>
        ) : (
          <div className="terminal">
            <pre className="whitespace-pre-wrap text-sm">{content}</pre>
          </div>
        )}
      </div>
    </div>
  )
}
