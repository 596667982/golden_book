#!/bin/bash

# Golden Book 自动化部署脚本
# 用于在新的 Mac 上快速部署项目

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

print_info "开始部署 Golden Book 项目..."
print_info "项目目录: $SCRIPT_DIR"

# 1. 检查系统依赖
print_info "检查系统依赖..."
check_command python3
check_command npm

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.13"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_warning "Python 版本为 $PYTHON_VERSION，建议使用 Python 3.13 或更高版本"
fi

# 2. 部署后端
print_info "开始部署后端..."
cd "$SCRIPT_DIR/backend"

# 清理旧的虚拟环境（如果存在）
if [ -d "venv" ]; then
    print_warning "检测到旧的虚拟环境，正在删除..."
    rm -rf venv
fi

# 创建虚拟环境
print_info "创建 Python 虚拟环境..."
python3 -m venv venv

# 激活虚拟环境并安装依赖
print_info "安装 Python 依赖..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

print_info "后端依赖安装完成"

# 检查数据库文件
if [ ! -f "app.db" ]; then
    print_info "数据库文件不存在，首次启动时会自动创建"
fi

# 检查 uploads 目录
if [ ! -d "uploads" ]; then
    print_info "创建 uploads 目录..."
    mkdir -p uploads
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    print_warning ".env 文件不存在，如需配置 AI API，请创建 .env 文件"
    print_info "示例: echo 'OPENAI_API_KEY=your-key-here' > .env"
fi

deactivate

# 3. 部署前端
print_info "开始部署前端..."
cd "$SCRIPT_DIR/frontend"

# 清理旧的 node_modules（如果需要）
if [ -d "node_modules" ]; then
    print_info "检测到已存在的 node_modules，跳过清理"
else
    print_info "安装前端依赖..."
fi

npm install

print_info "前端依赖安装完成"

# 4. 完成部署
cd "$SCRIPT_DIR"
print_info "=========================================="
print_info "部署完成！"
print_info "=========================================="
echo ""
print_info "启动后端服务器："
echo "  cd backend"
echo "  venv/bin/uvicorn main:app --reload"
echo ""
print_info "启动前端开发服务器："
echo "  cd frontend"
echo "  npm run dev"
echo ""
print_info "访问应用："
echo "  前端: http://localhost:5173"
echo "  后端 API: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"
echo ""

# 询问是否立即启动服务
read -p "是否现在启动服务？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "启动服务..."

    # 启动后端（后台运行）
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
    else
        print_error "后端启动失败，请查看日志: /tmp/golden-book-backend.log"
        exit 1
    fi

    # 启动前端
    cd "$SCRIPT_DIR/frontend"
    print_info "启动前端开发服务器..."
    npm run dev
else
    print_info "稍后可以手动启动服务"
fi
