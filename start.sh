#!/bin/bash

# 云志选 - 启动脚本

echo "🚀 启动云志选系统..."
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    exit 1
fi

# 启动后端
echo "📦 启动后端服务..."
cd backend
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
echo "✅ 后端依赖安装完成"

# 后台启动后端
python main.py &
BACKEND_PID=$!
echo "✅ 后端已启动 (PID: $BACKEND_PID)"
echo "   地址: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "⚠️ Node.js未安装，跳过前端启动"
    echo "   后端服务已启动，可单独使用API"
    wait $BACKEND_PID
    exit 0
fi

# 启动前端
echo "🎨 启动前端..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi
echo "✅ 前端依赖安装完成"
echo "✅ 启动前端服务..."
npm start &
FRONTEND_PID=$!
echo "   地址: http://localhost:3000"
echo ""

echo "✨ 云志选系统已启动！"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待信号
wait $BACKEND_PID $FRONTEND_PID
