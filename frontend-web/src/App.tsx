import { useState } from 'react'
import Chat from './components/Chat'
import Settings from './components/Settings'
import MemoryView from './components/MemoryView'
import History from './components/History'
import Sidebar from './components/Sidebar'

type View = 'chat' | 'settings' | 'memory' | 'history'

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
            <div className="text-sm text-gray-400">
              AI 编程助手 v0.1.0
            </div>
          </div>
        </header>
        
        {/* 内容区 */}
        <div className="flex-1 overflow-auto">
          {currentView === 'chat' && <Chat onSwitchView={(view) => setCurrentView(view as View)} />}
          {currentView === 'settings' && <Settings />}
          {currentView === 'memory' && <MemoryView />}
          {currentView === 'history' && <History />}
        </div>
      </main>
    </div>
  )
}

export default App
