.PHONY: help install test lint format type-check docker-build docker-run clean

# 默认目标
help:
	@echo "AI学习助手 - 开发命令"
	@echo ""
	@echo "命令:"
	@echo "  install     安装依赖"
	@echo "  test       运行测试"
	@echo "  lint       代码检查"
	@echo "  format     代码格式化"
	@echo "  type-check 类型检查"
	@echo "  run        运行应用"
	@echo "  docker-build 构建Docker镜像"
	@echo "  docker-run  运行Docker容器"
	@echo "  clean      清理临时文件"

# 安装依赖
install:
	pip install -r requirements.txt

# 运行测试
test:
	pytest --cov=app --cov-report=html --cov-report=term-missing -v

# 代码检查
lint:
	flake8 .

# 代码格式化
format:
	black .
	isort .

# 类型检查
type-check:
	mypy .

# 运行应用
run:
	python app.py

# 构建Docker镜像
docker-build:
	docker build -t ai-learning-assistant .

# 运行Docker容器
docker-run:
	docker run -p 5000:5000 --env-file .env ai-learning-assistant

# 清理临时文件
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/ .pytest_cache/ .mypy_cache/ build/ dist/ *.egg-info/

# 开发环境设置
dev-setup: install format
	@echo "开发环境设置完成！"
	@echo "请确保已创建.env文件并配置DeepSeek API密钥"

# 完整的质量检查
quality-check: lint type-check test
	@echo "✅ 所有质量检查通过！"