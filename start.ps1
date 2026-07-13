# BandCode 一键启动脚本 (Windows)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BandCode - AI 编程助手" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
Write-Host "[1/5] 检查 Python 环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python 未安装，请先安装 Python 3.11+" -ForegroundColor Red
    exit 1
}

# 检查 Node.js
Write-Host "[2/5] 检查 Node.js 环境..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✅ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Node.js 未安装，请先安装 Node.js 18+" -ForegroundColor Red
    exit 1
}

# 安装后端依赖
Write-Host "[3/5] 安装后端依赖..." -ForegroundColor Yellow
pip install -r backend/requirements.txt -q
Write-Host "  ✅ 后端依赖已安装" -ForegroundColor Green

# 安装前端依赖
Write-Host "[4/5] 安装前端依赖..." -ForegroundColor Yellow
Push-Location frontend-web
if (-not (Test-Path "node_modules")) {
    npm install --silent
} else {
    Write-Host "  ✅ 前端依赖已安装" -ForegroundColor Green
}
Pop-Location

# 检查配置文件
Write-Host "[5/5] 检查配置文件..." -ForegroundColor Yellow
if (-not (Test-Path "settings.json")) {
    if (Test-Path "settings.example.json") {
        Copy-Item "settings.example.json" "settings.json"
        Write-Host "  ✅ 已创建 settings.json（请编辑填入 API Key）" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ 未找到配置模板" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✅ 配置文件已存在" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  启动服务..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查端口 8000 是否被占用
Write-Host "🔍 检查端口占用..." -ForegroundColor Yellow
$port8000 = netstat -ano | Select-String ":8000\s.*LISTENING"
if ($port8000) {
    $portPid = ($port8000 -split '\s+')[-1]
    Write-Host "  ⚠️ 端口 8000 已被进程 $portPid 占用，正在停止..." -ForegroundColor Yellow
    Stop-Process -Id $portPid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    Write-Host "  ✅ 端口已释放" -ForegroundColor Green
}

# 启动后端（后台）
Write-Host "🚀 启动后端服务 (http://localhost:8000)..." -ForegroundColor Green
$backendProc = Start-Process python -ArgumentList "backend/main.py" -PassThru -WindowStyle Hidden

# 等待后端启动
$maxWait = 15
$waited = 0
$backendReady = $false
while ($waited -lt $maxWait) {
    Start-Sleep -Seconds 1
    $waited++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            break
        }
    } catch {
        # 继续等待
    }
}

if ($backendReady) {
    Write-Host "  ✅ 后端服务已启动" -ForegroundColor Green
} else {
    Write-Host "  ❌ 后端启动超时，请检查日志" -ForegroundColor Red
    if ($backendProc -and !$backendProc.HasExited) {
        Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
    }
    exit 1
}

# 启动前端
Write-Host "🚀 启动前端 (http://localhost:3000)..." -ForegroundColor Green
Push-Location frontend-web
$frontendProc = Start-Process npm -ArgumentList "run","dev" -PassThru -WorkingDirectory (Get-Location) -WindowStyle Hidden

# 等待前端服务器就绪
$maxWait = 30
$waited = 0
while ($waited -lt $maxWait) {
    $listening = netstat -ano | Select-String ":3000\s.*LISTENING"
    if ($listening) { break }
    Start-Sleep -Seconds 1
    $waited++
}

Pop-Location

if ($waited -ge $maxWait) {
    Write-Host "  ⚠️ 前端启动超时，请手动访问 http://localhost:3000" -ForegroundColor Yellow
} else {
    Start-Process "http://localhost:3000"
    Write-Host "  ✅ 前端已启动" -ForegroundColor Green
}

# 保持脚本运行，直到用户按 Ctrl+C 后清理进程
Write-Host ""
Write-Host "按 Ctrl+C 停止所有服务" -ForegroundColor Gray
try {
    while ($true) { Start-Sleep -Seconds 2 }
} finally {
    Write-Host "`n正在停止服务..." -ForegroundColor Yellow
    if ($backendProc -and !$backendProc.HasExited) {
        Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
        Write-Host "  ✅ 后端服务已停止" -ForegroundColor Green
    }
    if ($frontendProc -and !$frontendProc.HasExited) {
        Stop-Process -Id $frontendProc.Id -Force -ErrorAction SilentlyContinue
        Write-Host "  ✅ 前端服务已停止" -ForegroundColor Green
    }
    Write-Host "✅ 所有服务已停止" -ForegroundColor Green
}
