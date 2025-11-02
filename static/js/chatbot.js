// Chatbot JavaScript - Finans Asistanı
class FinansChatbot {
    constructor() {
        this.isTyping = false;
        this.messageHistory = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkHealth();
        this.hideLoadingOverlay();
        this.autoResizeTextarea();
        this.clearChatHistory(); // Clear history on page load
    }

    setupEventListeners() {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const charCount = document.getElementById('charCount');

        // Send button click
        sendButton.addEventListener('click', () => this.sendMessage());

        // Enter key handling
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Character count
        messageInput.addEventListener('input', (e) => {
            const length = e.target.value.length;
            charCount.textContent = length;
            
            // Enable/disable send button
            sendButton.disabled = length === 0;
            
            // Auto-resize textarea
            this.autoResizeTextarea();
        });

        // Focus input on page load
        messageInput.focus();
    }

    autoResizeTextarea() {
        const textarea = document.getElementById('messageInput');
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    async checkHealth() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            const statusIndicator = document.getElementById('statusIndicator');
            const statusText = document.getElementById('statusText');
            
            if (data.status === 'healthy') {
                statusIndicator.className = 'status-indicator connected';
                statusText.textContent = 'Bağlandı';
                
                if (data.data_loaded) {
                    statusText.textContent = 'Veri yüklendi';
                }
            } else {
                statusIndicator.className = 'status-indicator error';
                statusText.textContent = 'Bağlantı hatası';
            }
        } catch (error) {
            console.error('Health check failed:', error);
            const statusIndicator = document.getElementById('statusIndicator');
            const statusText = document.getElementById('statusText');
            statusIndicator.className = 'status-indicator error';
            statusText.textContent = 'Bağlantı hatası';
        }
    }

    hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            setTimeout(() => {
                overlay.style.opacity = '0';
                setTimeout(() => {
                    overlay.style.display = 'none';
                }, 300);
            }, 1000);
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message || this.isTyping) return;

        // Clear input
        messageInput.value = '';
        messageInput.style.height = 'auto';
        document.getElementById('charCount').textContent = '0';
        document.getElementById('sendButton').disabled = true;

        // Add user message to chat
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            if (data.success) {
                // Hide typing indicator
                this.hideTypingIndicator();
                
                // Add bot response
                this.addMessage(data.response, 'bot');
            } else {
                throw new Error(data.error || 'Bilinmeyen hata');
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTypingIndicator();
            this.addMessage(`Üzgünüm, bir hata oluştu: ${error.message}`, 'error');
        }
    }

    addMessage(content, type) {
        // Hide welcome message if this is the first message
        const welcomeMessage = document.getElementById('welcomeMessage');
        const chatMessages = document.getElementById('chatMessages');
        
        if (welcomeMessage && welcomeMessage.style.display !== 'none') {
            welcomeMessage.style.display = 'none';
            chatMessages.style.display = 'block';
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const timestamp = new Date().toLocaleTimeString('tr-TR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        let avatarIcon, avatarText;
        if (type === 'user') {
            avatarIcon = 'fas fa-user';
            avatarText = 'S';
        } else if (type === 'bot') {
            avatarIcon = 'fas fa-robot';
            avatarText = 'F';
        } else {
            avatarIcon = 'fas fa-exclamation-triangle';
            avatarText = '!';
        }

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="${avatarIcon}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${this.formatMessage(content)}</div>
                <span class="message-time">${timestamp}</span>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Add to history
        this.messageHistory.push({ content, type, timestamp });
    }

    formatMessage(content) {
        // Convert line breaks to <br> tags
        return content.replace(/\n/g, '<br>');
    }

    showTypingIndicator() {
        this.isTyping = true;
        const typingIndicator = document.getElementById('typingIndicator');
        typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typingIndicator');
        typingIndicator.style.display = 'none';
    }

    scrollToBottom() {
        const chatContainer = document.querySelector('.chat-container');
        setTimeout(() => {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 100);
    }

    // Function to handle suggested questions
    askQuestion(question) {
        const messageInput = document.getElementById('messageInput');
        messageInput.value = question;
        messageInput.style.height = 'auto';
        document.getElementById('charCount').textContent = question.length;
        document.getElementById('sendButton').disabled = false;
        
        // Focus and send
        messageInput.focus();
        this.sendMessage();
    }

    // Utility function to format currency
    formatCurrency(amount, currency = 'TRY') {
        return new Intl.NumberFormat('tr-TR', {
            style: 'currency',
            currency: currency
        }).format(amount);
    }

    // Utility function to format dates
    formatDate(date) {
        return new Intl.DateTimeFormat('tr-TR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(new Date(date));
    }

    clearChatHistory() {
        // Clear chat messages display
        const chatMessages = document.getElementById('chatMessages');
        const welcomeMessage = document.getElementById('welcomeMessage');
        
        if (chatMessages) {
            chatMessages.innerHTML = '';
            chatMessages.style.display = 'none';
        }
        
        if (welcomeMessage) {
            welcomeMessage.style.display = 'block';
        }
        
        // Reset message history
        this.messageHistory = [];
        
        console.log('Chat history cleared');
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.finansChatbot = new FinansChatbot();
});

// Global function for suggested questions
function askQuestion(question) {
    if (window.finansChatbot) {
        window.finansChatbot.askQuestion(question);
    }
}

// Add some nice animations and interactions
document.addEventListener('DOMContentLoaded', () => {
    // Add hover effects to suggestion buttons
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');
    suggestionBtns.forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            btn.style.transform = 'translateY(-3px) scale(1.02)';
        });
        
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Add smooth scrolling
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.style.scrollBehavior = 'smooth';
    }

    // Add input focus effects
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.addEventListener('focus', () => {
            messageInput.parentElement.style.transform = 'scale(1.02)';
        });
        
        messageInput.addEventListener('blur', () => {
            messageInput.parentElement.style.transform = 'scale(1)';
        });
    }
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to send message
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (window.finansChatbot) {
            window.finansChatbot.sendMessage();
        }
    }
    
    // Escape to clear input
    if (e.key === 'Escape') {
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.value = '';
            messageInput.style.height = 'auto';
            document.getElementById('charCount').textContent = '0';
            document.getElementById('sendButton').disabled = true;
        }
    }
});

// Add some nice loading animations
window.addEventListener('load', () => {
    // Fade in the main content
    const container = document.querySelector('.container');
    if (container) {
        container.style.opacity = '0';
        container.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            container.style.transition = 'all 0.6s ease';
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        }, 100);
    }
});

// Add error handling for network issues
window.addEventListener('online', () => {
    if (window.finansChatbot) {
        window.finansChatbot.checkHealth();
    }
});

window.addEventListener('offline', () => {
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    if (statusIndicator && statusText) {
        statusIndicator.className = 'status-indicator error';
        statusText.textContent = 'İnternet bağlantısı yok';
    }
});
