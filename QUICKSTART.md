# Golden Book - 快速参考

## 🚀 快速开始

### 首次部署
```bash
./deploy.sh
```

### 启动服务
```bash
./start.sh
```

### 停止服务
```bash
./stop.sh
```

## 📦 部署到新 Mac

### 1. 打包项目
```bash
./package.sh
```

### 2. 传输文件
- 使用 AirDrop
- 使用 U 盘
- 使用 `scp golden-book_*.tar.gz user@target-mac:~/`

### 3. 在目标 Mac 上部署
```bash
tar -xzf golden-book_*.tar.gz
cd golden-book
chmod +x *.sh
./deploy.sh
```

## 🌐 访问地址

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 📝 手动启动（不使用脚本）

### 后端
```bash
cd backend
venv/bin/uvicorn main:app --reload
```

### 前端
```bash
cd frontend
npm run dev
```

## 🔧 常用命令

### 后端
```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 运行测试
pytest

# 查看日志
tail -f /tmp/golden-book-backend.log
```

### 前端
```bash
# 安装依赖
cd frontend
npm install

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 🐛 故障排除

### 端口被占用
```bash
# 查找并停止占用端口的进程
lsof -ti:8000 | xargs kill
lsof -ti:5173 | xargs kill
```

### 重新安装依赖
```bash
# 后端
cd backend
rm -rf venv
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# 前端
cd frontend
rm -rf node_modules
npm install
```

### 查看后端日志
```bash
tail -f /tmp/golden-book-backend.log
```

## 📚 文档

- **CLAUDE.md** - 项目架构和开发指南
- **DEPLOYMENT.md** - 详细部署说明
- **README.md** - 项目简介

## ⚙️ 环境变量

创建 `backend/.env` 文件配置 AI API：
```bash
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
```

## 📋 系统要求

- macOS
- Python 3.13+
- Node.js 16+
- 500MB+ 磁盘空间
