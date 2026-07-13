import { useState, useEffect } from 'react'
import { Folder, RefreshCw } from 'lucide-react'
import axios from 'axios'

interface WorkspaceData {
  path: string
  name: string
  exists: boolean
}

export default function WorkspaceInfo() {
  const [workspace, setWorkspace] = useState<WorkspaceData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadWorkspace()
  }, [])

  const loadWorkspace = async () => {
    try {
      const response = await axios.get('/api/workspace/info')
      if (response.data.code === 0) {
        setWorkspace(response.data.data)
      }
    } catch (error) {
      console.error('加载工作区信息失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-3 flex items-center gap-2">
        <RefreshCw className="animate-spin" size={16} />
        <span className="text-sm text-gray-400">加载工作区...</span>
      </div>
    )
  }

  if (!workspace) {
    return (
      <div className="bg-red-900/50 rounded-lg p-3">
        <span className="text-sm text-red-400">无法获取工作区信息</span>
      </div>
    )
  }

  return (
    <div className="bg-gray-800 rounded-lg p-3">
      <div className="flex items-center gap-2">
        <Folder size={16} className="text-yellow-400" />
        <span className="text-sm font-medium">工作区</span>
      </div>
      <div className="mt-2">
        <div className="text-xs text-gray-400">名称</div>
        <div className="text-sm font-mono bg-gray-700 rounded px-2 py-1">
          {workspace.name}
        </div>
      </div>
      <div className="mt-2">
        <div className="text-xs text-gray-400">路径</div>
        <div className="text-xs font-mono bg-gray-700 rounded px-2 py-1 break-all">
          {workspace.path}
        </div>
      </div>
      <div className="mt-2">
        <span
          className={`text-xs px-2 py-1 rounded ${
            workspace.exists
              ? 'bg-green-900/50 text-green-400'
              : 'bg-red-900/50 text-red-400'
          }`}
        >
          {workspace.exists ? '✓ 有效' : '✗ 不存在'}
        </span>
      </div>
    </div>
  )
}
