import { useState, useEffect } from 'react'
import { Play, CheckCircle, XCircle, RefreshCw, Settings } from 'lucide-react'
import axios from 'axios'

interface ModelInfo {
  default_model: string
  base_url: string
  planner_model: string
  simple_coder_model: string
  complex_coder_model: string
  tester_model: string
}

export default function ModelTest() {
  const [testing, setTesting] = useState(false)
  const [result, setResult] = useState<{ success: boolean; message: string; latency?: number; model?: string } | null>(null)
  const [testMessage, setTestMessage] = useState('你好，请简单介绍一下自己。')
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null)
  const [loadingInfo, setLoadingInfo] = useState(true)

  useEffect(() => {
    loadModelInfo()
  }, [])

  const loadModelInfo = async () => {
    try {
      const response = await axios.get('/api/test/model/info')
      if (response.data.code === 0) {
        setModelInfo(response.data.data)
      }
    } catch (error) {
      console.error('加载模型信息失败:', error)
    } finally {
      setLoadingInfo(false)
    }
  }

  const handleTest = async () => {
    setTesting(true)
    setResult(null)
    
    const startTime = Date.now()
    
    try {
      const response = await axios.post('/api/test/model', { message: testMessage })
      const latency = Date.now() - startTime
      
      if (response.data.code === 0) {
        setResult({
          success: true,
          message: response.data.data.response,
          latency,
          model: response.data.data.model,
        })
      } else {
        setResult({
          success: false,
          message: response.data.message || '测试失败',
          latency,
        })
      }
    } catch (error: any) {
      setResult({
        success: false,
        message: error.response?.data?.message || error.message || '连接失败',
      })
    } finally {
      setTesting(false)
    }
  }

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-6">模型测试</h2>
      
      {/* 模型信息 */}
      <div className="bg-gray-800 rounded-lg p-4 mb-4">
        <div className="flex items-center gap-2 mb-3">
          <Settings size={16} className="text-gray-400" />
          <h3 className="font-semibold text-gray-300">当前模型配置</h3>
        </div>
        {loadingInfo ? (
          <div className="flex items-center gap-2 text-gray-400">
            <RefreshCw className="animate-spin" size={14} />
            加载中...
          </div>
        ) : modelInfo ? (
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="text-gray-400">默认模型:</div>
            <div className="text-white">{modelInfo.default_model || '未配置'}</div>
            <div className="text-gray-400">Base URL:</div>
            <div className="text-white truncate">{modelInfo.base_url || '未配置'}</div>
            <div className="text-gray-400">Planner:</div>
            <div className="text-white">{modelInfo.planner_model || '未配置'}</div>
            <div className="text-gray-400">ComplexCoder:</div>
            <div className="text-white">{modelInfo.complex_coder_model || '未配置'}</div>
            <div className="text-gray-400">SimpleCoder:</div>
            <div className="text-white">{modelInfo.simple_coder_model || '未配置'}</div>
            <div className="text-gray-400">Tester:</div>
            <div className="text-white">{modelInfo.tester_model || '未配置'}</div>
          </div>
        ) : (
          <div className="text-red-400 text-sm">无法加载模型信息</div>
        )}
      </div>
      
      {/* 测试消息输入 */}
      <div className="bg-gray-800 rounded-lg p-4 mb-4">
        <label className="block text-sm text-gray-400 mb-2">测试消息</label>
        <textarea
          value={testMessage}
          onChange={(e) => setTestMessage(e.target.value)}
          className="w-full bg-gray-700 text-white rounded p-3 h-24 resize-none focus:outline-none focus:ring-2 focus:ring-cyan-500"
          placeholder="输入测试消息..."
        />
      </div>
      
      {/* 测试按钮 */}
      <button
        onClick={handleTest}
        disabled={testing || !testMessage.trim()}
        className="btn-primary flex items-center gap-2 disabled:opacity-50"
      >
        {testing ? (
          <>
            <RefreshCw className="animate-spin" size={16} />
            测试中...
          </>
        ) : (
          <>
            <Play size={16} />
            开始测试
          </>
        )}
      </button>
      
      {/* 测试结果 */}
      {result && (
        <div className={`mt-4 rounded-lg p-4 ${result.success ? 'bg-green-900/50' : 'bg-red-900/50'}`}>
          <div className="flex items-center gap-2 mb-2">
            {result.success ? (
              <CheckCircle className="text-green-400" size={20} />
            ) : (
              <XCircle className="text-red-400" size={20} />
            )}
            <span className="font-semibold">
              {result.success ? '测试成功' : '测试失败'}
            </span>
            {result.latency && (
              <span className="text-sm text-gray-400">({result.latency}ms)</span>
            )}
            {result.model && (
              <span className="text-sm text-gray-400">模型: {result.model}</span>
            )}
          </div>
          <div className="whitespace-pre-wrap text-sm mt-2 p-3 bg-gray-800 rounded">
            {result.message}
          </div>
        </div>
      )}
      
      {/* 测试说明 */}
      <div className="mt-6 bg-gray-800 rounded-lg p-4">
        <h3 className="font-semibold mb-2">测试说明</h3>
        <ul className="text-sm text-gray-400 space-y-1">
          <li>• 测试会发送一条消息给 AI 模型</li>
          <li>• 检查模型是否能正常响应</li>
          <li>• 显示响应时间和内容</li>
          <li>• 如果失败，请检查 API 配置</li>
        </ul>
      </div>
    </div>
  )
}
