import React, { useState, useEffect, useRef } from 'react'
import { Search, MessageSquare, Globe, Folder, List, Camera, RefreshCw, Trash2, Archive } from 'lucide-react'

interface Command {
  id: string
  name: string
  description: string
  icon: React.ReactNode
  action: () => void
}

interface CommandPaletteProps {
  isOpen: boolean
  onClose: () => void
  onSendMessage: (message: string) => void
  onSwitchView?: (view: string) => void
}

export default function CommandPalette({ isOpen, onClose, onSendMessage, onSwitchView }: CommandPaletteProps) {
  const [search, setSearch] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLDivElement>(null)

  const commands: Command[] = [
    {
      id: 'chat',
      name: '对话',
      description: '开始新的对话',
      icon: <MessageSquare size={16} />,
      action: () => {
        onSendMessage('')
        onClose()
      },
    },
    {
      id: 'memory-global',
      name: '全局记忆',
      description: '查看全局记忆内容',
      icon: <Globe size={16} />,
      action: () => {
        onSwitchView?.('memory')
        onClose()
      },
    },
    {
      id: 'memory-project',
      name: '项目记忆',
      description: '查看项目记忆内容',
      icon: <Folder size={16} />,
      action: () => {
        onSwitchView?.('memory')
        onClose()
      },
    },
    {
      id: 'memory-task',
      name: '任务记忆',
      description: '查看任务记忆内容',
      icon: <List size={16} />,
      action: () => {
        onSwitchView?.('memory')
        onClose()
      },
    },
    {
      id: 'memory-checkpoint',
      name: '检查点',
      description: '查看检查点快照',
      icon: <Camera size={16} />,
      action: () => {
        onSwitchView?.('memory')
        onClose()
      },
    },
    {
      id: 'clear',
      name: '清空对话',
      description: '清空当前对话历史',
      icon: <Trash2 size={16} />,
      action: () => {
        onSendMessage('/clear')
        onClose()
      },
    },
    {
      id: 'compress',
      name: '压缩会话',
      description: '压缩当前会话数据',
      icon: <Archive size={16} />,
      action: () => {
        onSendMessage('/compress')
        onClose()
      },
    },
    {
      id: 'refresh',
      name: '刷新',
      description: '刷新页面数据',
      icon: <RefreshCw size={16} />,
      action: () => {
        window.location.reload()
        onClose()
      },
    },
  ]

  const filteredCommands = commands.filter(
    (cmd) =>
      cmd.name.toLowerCase().includes(search.toLowerCase()) ||
      cmd.description.toLowerCase().includes(search.toLowerCase())
  )

  useEffect(() => {
    if (isOpen) {
      setSearch('')
      setSelectedIndex(0)
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [isOpen])

  useEffect(() => {
    setSelectedIndex(0)
  }, [search])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose()
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex((prev) => Math.min(prev + 1, filteredCommands.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex((prev) => Math.max(prev - 1, 0))
    } else if (e.key === 'Enter') {
      e.preventDefault()
      if (filteredCommands[selectedIndex]) {
        filteredCommands[selectedIndex].action()
      }
    }
  }

  useEffect(() => {
    if (listRef.current) {
      const selectedElement = listRef.current.children[selectedIndex] as HTMLElement
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest' })
      }
    }
  }, [selectedIndex])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-start justify-center pt-[20vh] z-50" onClick={onClose}>
      <div
        className="bg-gray-800 rounded-lg shadow-xl w-full max-w-md overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 搜索框 */}
        <div className="p-3 border-b border-gray-700">
          <div className="flex items-center gap-2 bg-gray-700 rounded-md px-3 py-2">
            <Search size={16} className="text-gray-400" />
            <input
              ref={inputRef}
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入命令..."
              className="bg-transparent flex-1 outline-none text-sm"
            />
          </div>
        </div>

        {/* 命令列表 */}
        <div ref={listRef} className="max-h-64 overflow-y-auto">
          {filteredCommands.length === 0 ? (
            <div className="p-4 text-center text-gray-500 text-sm">未找到匹配的命令</div>
          ) : (
            filteredCommands.map((cmd, index) => (
              <button
                key={cmd.id}
                className={`w-full text-left px-4 py-2 flex items-center gap-3 ${
                  index === selectedIndex ? 'bg-cyan-600 text-white' : 'text-gray-300 hover:bg-gray-700'
                }`}
                onClick={cmd.action}
                onMouseEnter={() => setSelectedIndex(index)}
              >
                <span className={index === selectedIndex ? 'text-white' : 'text-gray-400'}>{cmd.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium">{cmd.name}</div>
                  <div className={`text-xs ${index === selectedIndex ? 'text-cyan-100' : 'text-gray-500'}`}>
                    {cmd.description}
                  </div>
                </div>
              </button>
            ))
          )}
        </div>

        {/* 底部提示 */}
        <div className="p-2 border-t border-gray-700 text-xs text-gray-500 flex justify-between">
          <span>↑↓ 导航</span>
          <span>Enter 选择</span>
          <span>Esc 关闭</span>
        </div>
      </div>
    </div>
  )
}
