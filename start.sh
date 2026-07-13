#!/bin/bash
# BandCode 一键启动脚本 (Linux/Mac)

echo "========================================"
echo "  BandCode - AI 编程助手"
echo "========================================"
echo ""

# 检查 Python
echo "[1/5] 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  ✅ $PYTHON_VERSION"
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "  ✅ $PYTHON_VERSION"
    PYTHON=python
else
    echo "  ❌ Python 未安装，请先安装 Python 3.11+"
    exit 1
fi

# 检查 Node.js
echo "[2/5] 检查 Node.js 环境..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "  ✅ Node.js $NODE_VERSION"
else
    echo "  ❌ Node.js 未安装，请先安装 Node.js 18+"
    exit 1
fi

# 安装后端依赖
echo "[3/5] 安装后端依赖..."
$PYTHON -m pip install -r backend/requirements.txt -q
echo "  ✅ 后端依赖已安装"

# 安装前端依赖
echo "[4/5] 安装前端依赖..."
pushd frontend > /dev/null
if [ ! -d "node_modules" ]; then
    npm install --silent
else
    echo "  ✅ 前端依赖已安装"
fi
popd > /dev/null

# 检查配置文件
echo "[5/5] 检查配置文件..."
if [ ! -f "settings.json" ]; then
    if [ -f "settings.example.json" ]; then
        cp settings.example.json settings.json
        echo "  ✅ 已创建 settings.json（请编辑填入 API Key）"
    else
        echo "  ⚠️ 未找到配置模板"
    fi
else
    echo "  ✅ 配置文件已存在"
fi

echo ""
echo "========================================"
echo "  启动服务..."
echo "========================================"
echo ""

# 启动后端（后台）
echo "🚀 启动后端服务 (http://localhost:8000)..."
$PYTHON backend/main.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "🚀 启动前端 CLI..."
pushd frontend > /dev/null
npm run dev
popd > /dev/null

# 清理后端进程
kill $BACKEND_PID 2>/dev/null
