// AI学习助手前端JavaScript代码

class AILearningAssistant {
    constructor() {
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.loading = document.getElementById('loading');
        this.settingsPanel = document.getElementById('settingsPanel');
        this.settingsToggle = document.getElementById('settingsToggle');
        this.temperatureSlider = document.getElementById('temperature');
        this.temperatureValue = document.getElementById('temperatureValue');
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.setupAutoResize();
        this.updateTemperatureValue();
    }
    
    bindEvents() {
        // 发送消息事件
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // 设置面板切换
        this.settingsToggle.addEventListener('click', () => {
            this.settingsPanel.classList.toggle('active');
        });
        
        // 温度滑块事件
        this.temperatureSlider.addEventListener('input', () => {
            this.updateTemperatureValue();
        });
    }
    
    setupAutoResize() {
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });
    }
    
    updateTemperatureValue() {
        this.temperatureValue.textContent = this.temperatureSlider.value;
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // 清空输入框
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        
        // 添加用户消息
        this.addMessage(message, 'user');
        
        // 显示加载动画
        this.showLoading();
        
        try {
            // 创建超时控制器
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 60000); // 60秒超时
            
            // 发送请求到后端API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    max_tokens: document.getElementById('maxTokens').value,
                    temperature: this.temperatureSlider.value
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }
            
            // 添加AI回复
            this.addMessage(data.reply, 'assistant');
            
        } catch (error) {
            console.error('Failed to send message:', error);
            let errorMessage = 'An error occurred while processing the request';
            
            if (error.name === 'AbortError') {
                errorMessage = 'Request timed out, please try again later';
            } else if (error.message.includes('网络')) {
                errorMessage = 'Network connection failed, please check your connection';
            } else if (error.message.includes('超时')) {
                errorMessage = 'Request timed out, please try again later';
            } else if (error.message.includes('频率')) {
                errorMessage = 'Too many requests, please try again later';
            } else {
                errorMessage = error.message;
            }
            
            this.addMessage(`抱歉，发生了错误：${errorMessage}`, 'assistant');
        } finally {
            this.hideLoading();
        }
    }
    
    addMessage(content, sender) {
        // 如果是第一条消息，移除欢迎消息
        if (this.messagesContainer.querySelector('.welcome-message')) {
            this.messagesContainer.innerHTML = '';
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // 处理Markdown格式的回复（简单实现）
        const formattedContent = this.formatMessage(content);
        messageContent.innerHTML = formattedContent;
        
        if (sender === 'user') {
            messageDiv.appendChild(messageContent);
            messageDiv.appendChild(avatar);
        } else {
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
        }
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // 简单的Markdown格式化
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // 粗体
            .replace(/\*(.*?)\*/g, '<em>$1</em>')              // 斜体
            .replace(/`(.*?)`/g, '<code>$1</code>')            // 行内代码
            .replace(/\n/g, '<br>')                           // 换行
            .replace(/^#\s+(.*)$/gm, '<h3>$1</h3>')           // 标题
            .replace(/^-\s+(.*)$/gm, '<li>$1</li>')           // 列表项
            .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');        // 列表
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    showLoading() {
        this.sendButton.disabled = true;
        this.loading.classList.add('active');
    }
    
    hideLoading() {
        this.sendButton.disabled = false;
        this.loading.classList.remove('active');
    }
}

// 设置建议问题
function setSuggestion(question) {
    document.getElementById('messageInput').value = question;
    document.getElementById('messageInput').focus();
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new AILearningAssistant();
});

// 健康检查
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (!data.deepseek_configured) {
            console.warn('DeepSeek API not configured');
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
}

// 页面加载时执行健康检查
window.addEventListener('load', checkHealth);