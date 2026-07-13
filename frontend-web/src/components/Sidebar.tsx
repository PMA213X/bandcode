import {
  MessageSquare,
  Settings,
  Brain,
  History,
  HelpCircle,
  FlaskConical,
  FolderOpen,
} from 'lucide-react'
import WorkspaceInfo from './WorkspaceInfo'

type View =
  | 'chat'
  | 'settings'
  | 'memory'
  | 'history'
  | 'model-test'
  | 'files'

interface SidebarProps {
  currentView: View
  onViewChange: (view: View) => void
}

const menuItems = [
  { id: 'chat' as View, icon: MessageSquare, label: '对话', shortcut: '1' },
  { id: 'settings' as View, icon: Settings, label: '设置', shortcut: '2' },
  { id: 'memory' as View, icon: Brain, label: '记忆', shortcut: '3' },
  { id: 'history' as View, icon: History, label: '历史', shortcut: '4' },
  {
    id: 'model-test' as View,
    icon: FlaskConical,
    label: '测试',
    shortcut: '5',
  },
  { id: 'files' as View, icon: FolderOpen, label: '文件', shortcut: '6' },
]

export default function Sidebar({ currentView, onViewChange }: SidebarProps) {
  return (
    <aside className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
      {/* 菜单按钮区 */}
      <div className="flex flex-col items-center py-4 gap-2">
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
      </div>

      {/* 底部区域 */}
      <div className="mt-auto p-3 space-y-3">
        <WorkspaceInfo />

        <button
          className="w-full flex items-center justify-center gap-2 py-2 rounded-lg text-gray-400 hover:bg-gray-700 hover:text-white"
          title="帮助"
        >
          <HelpCircle size={16} />
          <span className="text-xs">帮助</span>
        </button>
      </div>
    </aside>
  )
}
