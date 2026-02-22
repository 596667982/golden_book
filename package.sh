#!/bin/bash

# Golden Book 项目打包脚本
# 用于将项目打包以便传输到另一台 Mac

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_NAME="golden-book"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="${PROJECT_NAME}_${TIMESTAMP}.tar.gz"

print_info "开始打包项目..."
print_info "项目目录: $SCRIPT_DIR"

cd "$SCRIPT_DIR/.."

# 创建排除文件列表
EXCLUDE_PATTERNS=(
    "venv"
    "node_modules"
    "__pycache__"
    "*.pyc"
    ".DS_Store"
    "*.log"
    ".git"
    "app.db"
    "uploads"
    "*.tar.gz"
)

# 构建 tar 排除参数
EXCLUDE_ARGS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude='$pattern'"
done

# 打包项目
print_info "正在打包（排除 venv, node_modules, 数据库等）..."
eval tar -czf "$ARCHIVE_NAME" $EXCLUDE_ARGS "$PROJECT_NAME/"

# 获取文件大小
FILE_SIZE=$(du -h "$ARCHIVE_NAME" | cut -f1)

print_info "=========================================="
print_info "打包完成！"
print_info "=========================================="
echo ""
print_info "压缩包: $SCRIPT_DIR/../$ARCHIVE_NAME"
print_info "文件大小: $FILE_SIZE"
echo ""
print_info "传输到目标 Mac 后，执行以下命令："
echo "  tar -xzf $ARCHIVE_NAME"
echo "  cd $PROJECT_NAME"
echo "  chmod +x deploy.sh start.sh stop.sh"
echo "  ./deploy.sh"
echo ""
print_warning "注意: 数据库文件和上传的文件未包含在压缩包中"
print_warning "如需迁移数据，请单独复制 backend/app.db 和 backend/uploads/ 目录"
