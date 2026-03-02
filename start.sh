#!/bin/bash

# Golden Book 服务启动脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 检查是否已部署
if [ ! -d "$SCRIPT_DIR/backend/venv" ]; then
    print_error "项目未部署，请先运行 ./deploy.sh"
    exit 1
fi

if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    print_error "前端依赖未安装，请先运行 ./deploy.sh"
    exit 1
fi

print_info "启动 Golden Book 服务..."

# 检查端口是否被占用
if lsof -ti:8000 > /dev/null 2>&1; then
    print_error "端口 8000 已被占用，请先停止占用该端口的进程"
    exit 1
fi

if lsof -ti:5173 > /dev/null 2>&1; then
    print_error "端口 5173 已被占用，请先停止占用该端口的进程"
    exit 1
fi

# 启动后端
cd "$SCRIPT_DIR/backend"
print_info "启动后端服务器..."
venv/bin/uvicorn main:app --reload > /tmp/golden-book-backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/golden-book-backend.pid

# 等待后端启动
sleep 3

# 检查后端是否启动成功
if curl -s http://127.0.0.1:8000/api/health > /dev/null 2>&1; then
    print_info "后端启动成功 (PID: $BACKEND_PID)"
    print_info "后端日志: /tmp/golden-book-backend.log"
else
    print_error "后端启动失败，请查看日志: /tmp/golden-book-backend.log"
    cat /tmp/golden-book-backend.log
    exit 1
fi

# 启动前端
cd "$SCRIPT_DIR/frontend"
print_info "启动前端开发服务器..."
print_info "=========================================="
print_info "服务已启动！"
print_info "=========================================="
echo ""
print_info "访问地址："
echo "  前端: http://localhost:5173"
echo "  后端 API: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"
echo ""
print_info "停止服务: ./stop.sh"
echo ""

npm run dev -- --host 0.0.0.0
