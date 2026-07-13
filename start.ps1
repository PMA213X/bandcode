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

# 启动后端（后台）
Write-Host "🚀 启动后端服务 (http://localhost:8000)..." -ForegroundColor Green
Start-Process python -ArgumentList "backend/main.py" -WindowStyle Hidden

# 等待后端启动
Start-Sleep -Seconds 3

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
    if ($frontendProc -and !$frontendProc.HasExited) {
        Stop-Process -Id $frontendProc.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "✅ 服务已停止" -ForegroundColor Green
}
