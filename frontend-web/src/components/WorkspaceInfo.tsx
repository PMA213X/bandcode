import { useState, useEffect } from 'react'
import { Folder, RefreshCw, Edit3, Check, X } from 'lucide-react'
import axios from 'axios'

interface WorkspaceData {
  path: string
  name: string
  exists: boolean
}

export default function WorkspaceInfo() {
  const [workspace, setWorkspace] = useState<WorkspaceData | null>(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [editPath, setEditPath] = useState('')
  const [saving, setSaving] = useState(false)

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

  const handleSave = async () => {
    if (!editPath.trim()) return
    setSaving(true)
    try {
      const response = await axios.post('/api/workspace/update', { path: editPath })
      if (response.data.code === 0) {
        setWorkspace(response.data.data)
        setEditing(false)
      } else {
        alert(response.data.message)
      }
    } catch (error: any) {
      alert(error.response?.data?.message || '更新失败')
    } finally {
      setSaving(false)
    }
  }

  const startEdit = () => {
    setEditPath(workspace?.path || '')
    setEditing(true)
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
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Folder size={16} className="text-yellow-400" />
          <span className="text-sm font-medium">工作区</span>
        </div>
        {!editing && (
          <button onClick={startEdit} className="text-gray-400 hover:text-white" title="修改工作区">
            <Edit3 size={14} />
          </button>
        )}
      </div>

      {editing ? (
        <div className="mt-2 space-y-2">
          <input
            type="text"
            value={editPath}
            onChange={(e) => setEditPath(e.target.value)}
            className="w-full text-xs font-mono bg-gray-700 rounded px-2 py-1.5 text-white outline-none focus:ring-1 focus:ring-cyan-500"
            placeholder="输入新的工作区路径"
            onKeyDown={(e) => { if (e.key === 'Enter') handleSave() }}
          />
          <div className="flex gap-1">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex-1 flex items-center justify-center gap-1 text-xs bg-cyan-600 hover:bg-cyan-500 rounded px-2 py-1 disabled:opacity-50"
            >
              <Check size={12} /> {saving ? '保存中...' : '确认'}
            </button>
            <button
              onClick={() => setEditing(false)}
              className="flex-1 flex items-center justify-center gap-1 text-xs bg-gray-600 hover:bg-gray-500 rounded px-2 py-1"
            >
              <X size={12} /> 取消
            </button>
          </div>
        </div>
      ) : (
        <>
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
        </>
      )}
    </div>
  )
}
