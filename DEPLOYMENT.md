# 部署指南

本文档说明如何将 Golden Book 项目部署到新的 Mac 上。

## 快速开始

### 方法一：使用自动化脚本（推荐）

1. **在源 Mac 上打包项目**
   ```bash
   ./package.sh
   ```
   这会创建一个 `golden-book_YYYYMMDD_HHMMSS.tar.gz` 压缩包

2. **传输到目标 Mac**
   - 使用 AirDrop
   - 使用 U 盘
   - 使用网络共享
   - 使用 scp: `scp golden-book_*.tar.gz user@target-mac:~/`

3. **在目标 Mac 上解压并部署**
   ```bash
   tar -xzf golden-book_*.tar.gz
   cd golden-book
   chmod +x deploy.sh start.sh stop.sh package.sh
   ./deploy.sh
   ```

### 方法二：使用 Git（如果项目在 Git 仓库中）

1. **在源 Mac 上推送代码**
   ```bash
   git add .
   git commit -m "Update project"
   git push origin main
   ```

2. **在目标 Mac 上克隆并部署**
   ```bash
   git clone <repository-url>
   cd golden-book
   chmod +x deploy.sh start.sh stop.sh package.sh
   ./deploy.sh
   ```

## 脚本说明

### deploy.sh - 自动化部署脚本
完整的部署流程，包括：
- 检查系统依赖（Python 3.13+, Node.js）
- 创建 Python 虚拟环境
- 安装后端依赖
- 安装前端依赖
- 可选：立即启动服务

**使用方法：**
```bash
./deploy.sh
```

### start.sh - 启动服务
启动后端和前端开发服务器

**使用方法：**
```bash
./start.sh
```

服务地址：
- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### stop.sh - 停止服务
停止所有运行中的服务

**使用方法：**
```bash
./stop.sh
```

### package.sh - 打包项目
将项目打包为压缩文件，自动排除不必要的文件（venv, node_modules, 数据库等）

**使用方法：**
```bash
./package.sh
```

## 系统要求

- macOS
- Python 3.13 或更高版本
- Node.js 和 npm
- 至少 500MB 可用磁盘空间

## 数据迁移（可选）

如果需要迁移现有数据：

1. **复制数据库文件**
   ```bash
   # 在源 Mac 上
   cp backend/app.db /path/to/backup/

   # 在目标 Mac 上
   cp /path/to/backup/app.db backend/
   ```

2. **复制上传的文件**
   ```bash
   # 在源 Mac 上
   tar -czf uploads.tar.gz backend/uploads/

   # 在目标 Mac 上
   tar -xzf uploads.tar.gz -C backend/
   ```

## 环境变量配置

如果使用 AI 功能，需要配置 API keys：

```bash
cd backend
cat > .env << EOF
# OpenAI API（可选）
OPENAI_API_KEY=your-openai-key-here

# Anthropic API（可选）
ANTHROPIC_API_KEY=your-anthropic-key-here

# 自定义配置（可选）
DATABASE_URL=sqlite+aiosqlite:///./app.db
UPLOAD_DIR=uploads
EOF
```

## 故障排除

### Python 版本问题
如果 Python 版本低于 3.13，可能会遇到兼容性问题。建议使用 Homebrew 安装最新版本：
```bash
brew install python@3.13
```

### 端口被占用
如果端口 8000 或 5173 被占用：
```bash
# 查找占用端口的进程
lsof -ti:8000
lsof -ti:5173

# 停止进程
kill <PID>
```

### 依赖安装失败
如果遇到依赖安装问题：
```bash
# 清理并重新安装后端依赖
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 清理并重新安装前端依赖
cd ../frontend
rm -rf node_modules package-lock.json
npm install
```

### 查看日志
后端日志位置：`/tmp/golden-book-backend.log`
```bash
tail -f /tmp/golden-book-backend.log
```

## 手动启动（不使用脚本）

如果需要手动控制启动过程：

**后端：**
```bash
cd backend
source venv/bin/activate  # 或使用 venv/bin/uvicorn
uvicorn main:app --reload
```

**前端：**
```bash
cd frontend
npm run dev
```

## 生产环境部署

对于生产环境，建议：

1. 使用 Gunicorn 或 uWSGI 运行后端
2. 构建前端静态文件：`npm run build`
3. 使用 Nginx 作为反向代理
4. 配置 HTTPS
5. 使用 PostgreSQL 替代 SQLite

详细的生产环境部署指南请参考项目文档。
