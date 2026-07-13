import { useState, useEffect } from 'react'
import { RefreshCw } from 'lucide-react'
import axios from 'axios'

interface SettingsData {
  [section: string]: {
    [key: string]: any
  }
}

export default function Settings() {
  const [settings, setSettings] = useState<SettingsData>({})
  const [loading, setLoading] = useState(true)
  const [activeSection, setActiveSection] = useState('模型设置')

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const response = await axios.get('/api/settings')
      if (response.data.code === 0) {
        setSettings(response.data.data)
      }
    } catch (error) {
      console.error('加载设置失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (section: string, key: string, value: any) => {
    try {
      await axios.post('/api/settings', { section, key, value })
      setSettings(prev => ({
        ...prev,
        [section]: { ...prev[section], [key]: value }
      }))
    } catch (error) {
      console.error('保存设置失败:', error)
    }
  }

  const sections = Object.keys(settings)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <RefreshCw className="animate-spin" size={24} />
      </div>
    )
  }

  return (
    <div className="flex h-full">
      {/* 左侧分类 */}
      <div className="w-48 border-r border-gray-700 p-4">
        <h3 className="text-sm font-semibold text-gray-400 mb-4">设置分类</h3>
        <nav className="space-y-1">
          {sections.map((section) => (
            <button
              key={section}
              onClick={() => setActiveSection(section)}
              className={`w-full text-left px-3 py-2 rounded-md text-sm ${
                activeSection === section
                  ? 'bg-cyan-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              {section}
            </button>
          ))}
        </nav>
      </div>
      
      {/* 右侧设置项 */}
      <div className="flex-1 p-6 overflow-auto">
        <h2 className="text-xl font-bold mb-6">{activeSection}</h2>
        
        <div className="space-y-4">
          {Object.entries(settings[activeSection] || {}).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between p-4 bg-gray-800 rounded-lg">
              <div>
                <label className="font-medium">{key}</label>
              </div>
              
              {typeof value === 'boolean' ? (
                <button
                  onClick={() => handleSave(activeSection, key, !value)}
                  className={`px-4 py-2 rounded-md ${
                    value ? 'bg-green-600' : 'bg-gray-600'
                  }`}
                >
                  {value ? '开启' : '关闭'}
                </button>
              ) : (
                <input
                  type="text"
                  defaultValue={String(value || '')}
                  onBlur={(e) => handleSave(activeSection, key, e.target.value)}
                  className="input w-64"
                />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
