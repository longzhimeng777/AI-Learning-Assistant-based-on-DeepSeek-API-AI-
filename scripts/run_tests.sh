#!/bin/bash

# AI学习助手测试脚本

echo "🚀 开始运行AI学习助手测试..."

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "❌ Python未安装，请先安装Python"
    exit 1
fi

# 安装测试依赖
echo "📦 安装测试依赖..."
pip install -r requirements.txt

# 运行代码格式化检查
echo "🔍 运行代码格式化检查..."
black --check .
if [ $? -ne 0 ]; then
    echo "⚠️  代码格式化检查失败，运行 black . 进行格式化"
    black .
fi

# 运行代码检查
echo "🔍 运行代码检查..."
flake8 .
if [ $? -ne 0 ]; then
    echo "❌ 代码检查失败"
    exit 1
fi

# 运行类型检查
echo "🔍 运行类型检查..."
mypy .
if [ $? -ne 0 ]; then
    echo "⚠️  类型检查有警告"
fi

# 运行测试
echo "🧪 运行测试..."
pytest --cov=app --cov-report=html --cov-report=term-missing -v

if [ $? -eq 0 ]; then
    echo "✅ 所有测试通过！"
    echo "📊 测试覆盖率报告已生成在 htmlcov/ 目录"
else
    echo "❌ 测试失败"
    exit 1
fi