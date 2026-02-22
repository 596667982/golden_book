#!/bin/bash

# Golden Book 服务停止脚本

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

print_info "停止 Golden Book 服务..."

# 停止后端
if [ -f "/tmp/golden-book-backend.pid" ]; then
    BACKEND_PID=$(cat /tmp/golden-book-backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        print_info "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm /tmp/golden-book-backend.pid
        print_info "后端服务已停止"
    else
        print_warning "后端服务未运行"
        rm /tmp/golden-book-backend.pid
    fi
else
    # 尝试通过端口查找并停止
    BACKEND_PID=$(lsof -ti:8000 2>/dev/null)
    if [ ! -z "$BACKEND_PID" ]; then
        print_info "通过端口找到后端进程 (PID: $BACKEND_PID)，正在停止..."
        kill $BACKEND_PID
        print_info "后端服务已停止"
    else
        print_warning "未找到运行中的后端服务"
    fi
fi

# 停止前端
FRONTEND_PID=$(lsof -ti:5173 2>/dev/null)
if [ ! -z "$FRONTEND_PID" ]; then
    print_info "停止前端服务 (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID
    print_info "前端服务已停止"
else
    print_warning "未找到运行中的前端服务"
fi

print_info "所有服务已停止"
