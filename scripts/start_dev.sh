#!/bin/bash

# AI学习助手开发环境启动脚本

echo "🚀 启动AI学习助手开发环境..."

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "❌ Python未安装，请先安装Python"
    exit 1
fi

# 检查是否安装了依赖
if [ ! -f "venv" ] && [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python -m venv venv
    source venv/bin/activate
    
    echo "📦 安装依赖..."
    pip install -r requirements.txt
else
    echo "📦 激活虚拟环境..."
    source venv/bin/activate
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到.env文件，复制.env.example..."
    cp .env.example .env
    echo "📝 请编辑.env文件，添加你的DeepSeek API密钥"
fi

# 启动应用
echo "🌐 启动AI学习助手..."
echo "📱 应用将在 http://localhost:5000 运行"
echo "🔧 开发模式已启用，代码更改将自动重载"

python app.py