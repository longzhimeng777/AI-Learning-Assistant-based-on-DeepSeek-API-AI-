# AI Learning Assistant based on DeepSeek API| AI学习助手

A smart learning assistant powered by the DeepSeek API. | 一个基于 DeepSeek API 的智能学习助手。

- English follows first; Chinese version below. | 先为英文，中文在后。



## English

### Features
- 🤖 DeepSeek AI API integration
- 🎨 Polished web UI
- 🔒 Secure key management
- 🐳 Dockerized deployment
- ✅ Tests and linting
- 🔄 CI/CD workflow

### Tech Stack
- Backend: Python, Flask
- Frontend: HTML, CSS, JavaScript
- AI Service: DeepSeek API
- Deployment: Docker, GitHub Actions

### Quick Start
Requirements: Python 3.8+, DeepSeek API key, Docker (optional)

1) Clone
```bash
git clone <repository-url>
cd ai-learning-assistant
```
2) Install
```bash
pip install -r requirements.txt
```
3) Configure env
```bash
cp .env.example .env
# Edit .env to set DEEPSEEK_API_KEY
```
4) Run (fixed port 8888)
```bash
PORT=8888 HOST=0.0.0.0 python app.py
# Open http://127.0.0.1:8888
```

### Docker
```bash
docker build -t ai-learning-assistant .
docker run -p 8888:8888 --env-file .env -e PORT=8888 -e HOST=0.0.0.0 ai-learning-assistant
```

### Development
```bash
black .
flake8 .
mypy .
pytest
```

### Project Structure
```
ai-learning-assistant/
├── app.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── tests/
├── static/
├── templates/
└── .github/workflows/
```

---

## 中文

### 功能特性
- 🤖 集成 DeepSeek AI API
- 🎨 精美 Web UI
- 🔒 安全密钥管理
- 🐳 Docker 部署
- ✅ 测试与代码检查
- 🔄 CI/CD 工作流

### 技术栈
- 后端：Python, Flask
- 前端：HTML, CSS, JavaScript
- AI 服务：DeepSeek API
- 部署：Docker, GitHub Actions

### 快速开始
环境要求：Python 3.8+、DeepSeek API 密钥、Docker（可选）

1）克隆
```bash
git clone <repository-url>
cd ai-learning-assistant
```
2）安装依赖
```bash
pip install -r requirements.txt
```
3）配置环境变量
```bash
cp .env.example .env
# 编辑 .env，设置 DEEPSEEK_API_KEY
```
4）运行（固定 8888 端口）
```bash
PORT=8888 HOST=0.0.0.0 python app.py
# 打开 http://127.0.0.1:8888
```

### Docker 运行
```bash
docker build -t ai-learning-assistant .
docker run -p 8888:8888 --env-file .env -e PORT=8888 -e HOST=0.0.0.0 ai-learning-assistant
```

### 开发
```bash
black .
flake8 .
mypy .
pytest
```

### 项目结构
```
ai-learning-assistant/
├── app.py              # 主应用文件
├── requirements.txt    # 依赖
├── Dockerfile          # Docker 配置
├── .env.example        # 环境变量示例
├── tests/              # 测试
├── static/             # 静态资源
├── templates/          # 模板
└── .github/workflows/  # CI/CD
```