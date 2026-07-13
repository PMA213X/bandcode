import { MessageSquare, Settings, Brain, History, HelpCircle } from 'lucide-react'

type View = 'chat' | 'settings' | 'memory' | 'history'

interface SidebarProps {
  currentView: View
  onViewChange: (view: View) => void
}

const menuItems = [
  { id: 'chat' as View, icon: MessageSquare, label: '对话', shortcut: '1' },
  { id: 'settings' as View, icon: Settings, label: '设置', shortcut: '2' },
  { id: 'memory' as View, icon: Brain, label: '记忆', shortcut: '3' },
  { id: 'history' as View, icon: History, label: '历史', shortcut: '4' },
]

export default function Sidebar({ currentView, onViewChange }: SidebarProps) {
  return (
    <aside className="w-16 bg-gray-800 border-r border-gray-700 flex flex-col items-center py-4 gap-2">
      {menuItems.map((item) => {
        const Icon = item.icon
        const isActive = currentView === item.id
        return (
          <button
            key={item.id}
            onClick={() => onViewChange(item.id)}
            className={`w-12 h-12 flex items-center justify-center rounded-lg transition-colors ${
              isActive 
                ? 'bg-cyan-600 text-white' 
                : 'text-gray-400 hover:bg-gray-700 hover:text-white'
            }`}
            title={`${item.label} (${item.shortcut})`}
          >
            <Icon size={20} />
          </button>
        )
      })}
      
      <div className="flex-1" />
      
      <button
        className="w-12 h-12 flex items-center justify-center rounded-lg text-gray-400 hover:bg-gray-700 hover:text-white"
        title="帮助"
      >
        <HelpCircle size={20} />
      </button>
    </aside>
  )
}
