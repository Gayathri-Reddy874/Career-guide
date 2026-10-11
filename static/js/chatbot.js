// static/js/chatbot.js

class CareerChatbot {
    constructor() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.input = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.suggestions = document.querySelectorAll('.suggestion-chip');
        this.isTyping = false;
        
        this.init();
    }
    
    init() {
        this.attachEvents();
        this.scrollToBottom();
    }
    
    attachEvents() {
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (this.input) {
            this.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }
        
        if (this.suggestions) {
            this.suggestions.forEach(chip => {
                chip.addEventListener('click', () => {
                    this.sendMessage(chip.textContent);
                });
            });
        }
    }
    
    addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        
        if (!isUser) {
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.innerHTML = '<i data-feather="bot"></i>';
            messageDiv.appendChild(avatar);
        }
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = this.formatMessage(content);
        messageDiv.appendChild(messageContent);
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Refresh icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
    
    formatMessage(content) {
        // Convert markdown-like syntax
        let formatted = content;
        
        // Bold text
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert bullet points
        formatted = formatted.replace(/^•\s+(.*)$/gm, '<li>$1</li>');
        if (formatted.includes('<li>')) {
            formatted = '<ul>' + formatted + '</ul>';
        }
        
        // Convert line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Add emojis based on keywords
        const emojiMap = {
            'salary': '💰',
            'education': '📚',
            'degree': '🎓',
            'skills': '🔧',
            'skill': '🔧',
            'duration': '⏱️',
            'years': '⏱️',
            'recruiters': '🏢',
            'companies': '🏢',
            'outlook': '🔮',
            'growth': '📈',
            'excellent': '🌟',
            'good': '👍',
            'stable': '⚖️'
        };
        
        for (const [keyword, emoji] of Object.entries(emojiMap)) {
            const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
            formatted = formatted.replace(regex, `${emoji} ${keyword}`);
        }
        
        return `<div class="response-text">${formatted}</div>`;
    }
    
    showTypingIndicator() {
        if (this.isTyping) return;
        
        this.isTyping = true;
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i data-feather="bot"></i>
            </div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
        
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
    
    removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
        this.isTyping = false;
    }
    
    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }
    
    async sendMessage(message = null) {
        const text = message || this.input.value.trim();
        
        if (!text) return;
        
        // Clear input
        if (this.input) {
            this.input.value = '';
        }
        
        // Add user message
        this.addMessage(this.escapeHtml(text), true);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            
            const data = await response.json();
            
            this.removeTypingIndicator();
            this.addMessage(data.response, false);
            
        } catch (error) {
            console.error('Chatbot error:', error);
            this.removeTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again later.', false);
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Predefined quick responses
    getQuickResponses() {
        return [
            'What careers are in healthcare?',
            'Tell me about Data Scientist',
            'High salary careers in India',
            'Careers without math',
            'How to become a pilot?',
            'Best careers for the future',
            'What is the salary of a software engineer?',
            'Careers in government sector'
        ];
    }
}

// Initialize chatbot when page loads
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('chatMessages')) {
        new CareerChatbot();
    }
});