import { useState, useEffect } from 'react'
import {
  Folder,
  File,
  ChevronRight,
  ChevronDown,
  RefreshCw,
} from 'lucide-react'
import axios from 'axios'

interface FileItem {
  name: string
  path: string
  is_dir: boolean
  size: number | null
}

export default function FileExplorer() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [currentPath, setCurrentPath] = useState('')
  const [loading, setLoading] = useState(true)
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set())

  useEffect(() => {
    loadFiles(currentPath)
  }, [currentPath])

  const loadFiles = async (path: string) => {
    setLoading(true)
    try {
      const response = await axios.get(
        `/api/workspace/files?path=${encodeURIComponent(path)}`
      )
      if (response.data.code === 0) {
        setFiles(response.data.data.items)
      }
    } catch (error) {
      console.error('加载文件列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleDir = (path: string) => {
    setExpandedDirs((prev) => {
      const next = new Set(prev)
      if (next.has(path)) {
        next.delete(path)
      } else {
        next.add(path)
      }
      return next
    })
  }

  const handleClick = (file: FileItem) => {
    if (file.is_dir) {
      toggleDir(file.path)
      setCurrentPath(file.path)
    }
  }

  return (
    <div className="h-full overflow-auto">
      <div className="flex items-center justify-between p-2 border-b border-gray-700">
        <span className="text-sm font-medium">文件浏览器</span>
        <button
          onClick={() => loadFiles(currentPath)}
          className="text-gray-400 hover:text-white"
        >
          <RefreshCw size={14} />
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-4">
          <RefreshCw className="animate-spin" size={16} />
        </div>
      ) : (
        <div className="p-2">
          {files.map((file) => (
            <div
              key={file.path}
              onClick={() => handleClick(file)}
              className="flex items-center gap-2 px-2 py-1 rounded hover:bg-gray-700 cursor-pointer"
            >
              {file.is_dir ? (
                <>
                  {expandedDirs.has(file.path) ? (
                    <ChevronDown size={14} className="text-gray-400" />
                  ) : (
                    <ChevronRight size={14} className="text-gray-400" />
                  )}
                  <Folder size={14} className="text-yellow-400" />
                </>
              ) : (
                <>
                  <span className="w-3.5" />
                  <File size={14} className="text-blue-400" />
                </>
              )}
              <span className="text-sm truncate">{file.name}</span>
              {!file.is_dir && file.size !== null && (
                <span className="text-xs text-gray-500 ml-auto">
                  {formatSize(file.size)}
                </span>
              )}
            </div>
          ))}

          {files.length === 0 && (
            <div className="text-center text-gray-500 py-4">空文件夹</div>
          )}
        </div>
      )}
    </div>
  )
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
