import { useState } from 'react'
import Chat from './components/Chat'
import Settings from './components/Settings'
import MemoryView from './components/MemoryView'
import History from './components/History'
import ModelTest from './components/ModelTest'
import FileExplorer from './components/FileExplorer'
import Sidebar from './components/Sidebar'

type View =
  | 'chat'
  | 'settings'
  | 'memory'
  | 'history'
  | 'model-test'
  | 'files'

function App() {
  const [currentView, setCurrentView] = useState<View>('chat')

  return (
    <div className="flex h-screen bg-gray-900">
      {/* 侧边栏 */}
      <Sidebar currentView={currentView} onViewChange={setCurrentView} />

      {/* 主内容区 */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* 标题栏 */}
        <header className="bg-gray-800 border-b border-gray-700 px-4 py-3">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-cyan-400">BandCode</h1>
            <div className="text-sm text-gray-400">AI 编程助手 v0.1.0</div>
          </div>
        </header>

        {/* 内容区 — 用 CSS display 控制显隐，避免组件卸载丢失状态 */}
        <div className="flex-1 overflow-auto">
          <div style={{ display: currentView === 'chat' ? 'flex' : 'none', flexDirection: 'column', height: '100%' }}>
            <Chat onSwitchView={(view) => setCurrentView(view as View)} />
          </div>
          <div style={{ display: currentView === 'settings' ? 'block' : 'none', height: '100%' }}>
            <Settings />
          </div>
          <div style={{ display: currentView === 'memory' ? 'block' : 'none', height: '100%' }}>
            <MemoryView />
          </div>
          <div style={{ display: currentView === 'history' ? 'block' : 'none', height: '100%' }}>
            <History />
          </div>
          <div style={{ display: currentView === 'model-test' ? 'block' : 'none', height: '100%' }}>
            <ModelTest />
          </div>
          <div style={{ display: currentView === 'files' ? 'block' : 'none', height: '100%' }}>
            <FileExplorer />
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
