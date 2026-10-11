// static/js/quiz.js

class CareerQuiz {
    constructor() {
        this.currentQuestion = 1;
        this.totalQuestions = 8;
        this.answers = {};
        this.init();
    }
    
    init() {
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.submitBtn = document.getElementById('submitBtn');
        this.quizForm = document.getElementById('quizForm');
        
        this.updateProgress();
        this.attachEvents();
        this.loadSavedAnswers();
    }
    
    attachEvents() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.prevQuestion());
        }
        
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.nextQuestion());
        }
        
        if (this.submitBtn) {
            this.submitBtn.addEventListener('click', (e) => this.submitQuiz(e));
        }
        
        // Save answers as user selects
        document.querySelectorAll('.quiz-question input').forEach(input => {
            input.addEventListener('change', () => this.saveCurrentAnswers());
        });
    }
    
    updateProgress() {
        const progress = (this.currentQuestion / this.totalQuestions) * 100;
        if (this.progressBar) {
            this.progressBar.style.width = `${progress}%`;
        }
        if (this.progressText) {
            this.progressText.textContent = `Question ${this.currentQuestion} of ${this.totalQuestions}`;
        }
        
        // Show/hide navigation buttons
        if (this.prevBtn) {
            this.prevBtn.disabled = this.currentQuestion === 1;
        }
        
        if (this.nextBtn && this.submitBtn) {
            if (this.currentQuestion === this.totalQuestions) {
                this.nextBtn.style.display = 'none';
                this.submitBtn.style.display = 'inline-block';
            } else {
                this.nextBtn.style.display = 'inline-block';
                this.submitBtn.style.display = 'none';
            }
        }
    }
    
    showQuestion(questionNum) {
        document.querySelectorAll('.quiz-question').forEach((q, index) => {
            if (index + 1 === questionNum) {
                q.classList.add('active');
            } else {
                q.classList.remove('active');
            }
        });
        
        this.updateProgress();
        
        // Scroll to top of question
        document.querySelector('.quiz-section').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
    
    saveCurrentAnswers() {
        const currentQ = document.querySelector(`.quiz-question[data-question="${this.currentQuestion}"]`);
        if (!currentQ) return;
        
        const inputs = currentQ.querySelectorAll('input');
        const questionAnswers = {};
        
        inputs.forEach(input => {
            if (input.type === 'radio' && input.checked) {
                questionAnswers[input.name] = input.value;
            } else if (input.type === 'checkbox' && input.checked) {
                if (!questionAnswers[input.name]) questionAnswers[input.name] = [];
                questionAnswers[input.name].push(input.value);
            }
        });
        
        Object.assign(this.answers, questionAnswers);
        
        // Save to session storage
        sessionStorage.setItem('quizAnswers', JSON.stringify(this.answers));
    }
    
    loadSavedAnswers() {
        const saved = sessionStorage.getItem('quizAnswers');
        if (saved) {
            try {
                const answers = JSON.parse(saved);
                this.answers = answers;
                
                // Populate inputs
                Object.keys(answers).forEach(name => {
                    const value = answers[name];
                    const inputs = document.querySelectorAll(`input[name="${name}"]`);
                    
                    inputs.forEach(input => {
                        if (Array.isArray(value)) {
                            if (value.includes(input.value)) {
                                input.checked = true;
                            }
                        } else {
                            if (input.value === value) {
                                input.checked = true;
                            }
                        }
                    });
                });
            } catch (e) {
                console.error('Error loading saved answers:', e);
            }
        }
    }
    
    nextQuestion() {
        this.saveCurrentAnswers();
        
        // Validate current question has answer
        const currentQ = document.querySelector(`.quiz-question[data-question="${this.currentQuestion}"]`);
        const hasAnswer = this.hasAnswerForQuestion(currentQ);
        
        if (!hasAnswer) {
            showToast('Please answer this question before continuing', 'error');
            return;
        }
        
        if (this.currentQuestion < this.totalQuestions) {
            this.currentQuestion++;
            this.showQuestion(this.currentQuestion);
        }
    }
    
    prevQuestion() {
        this.saveCurrentAnswers();
        
        if (this.currentQuestion > 1) {
            this.currentQuestion--;
            this.showQuestion(this.currentQuestion);
        }
    }
    
    hasAnswerForQuestion(questionElement) {
        const inputs = questionElement.querySelectorAll('input');
        let answered = false;
        
        inputs.forEach(input => {
            if (input.type === 'radio' && input.checked) {
                answered = true;
            }
            if (input.type === 'checkbox' && input.checked) {
                answered = true;
            }
        });
        
        return answered;
    }
    
    async submitQuiz(event) {
        event.preventDefault();
        
        this.saveCurrentAnswers();
        
        // Validate all questions have answers
        let allAnswered = true;
        document.querySelectorAll('.quiz-question').forEach(q => {
            if (!this.hasAnswerForQuestion(q)) {
                allAnswered = false;
            }
        });
        
        if (!allAnswered) {
            showToast('Please answer all questions before submitting', 'error');
            return;
        }
        
        // Show loading state
        if (this.submitBtn) {
            this.submitBtn.disabled = true;
            this.submitBtn.innerHTML = '<i data-feather="loader"></i> Analyzing...';
            feather.replace();
        }
        
        try {
            const response = await fetch('/api/quiz/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.answers)
            });
            
            const result = await response.json();
            
            if (result.success) {
                sessionStorage.setItem('recommendations', JSON.stringify(result.recommendations));
                window.location.href = '/results';
            } else {
                throw new Error('Failed to get recommendations');
            }
        } catch (error) {
            console.error('Quiz submission error:', error);
            showToast('Something went wrong. Please try again.', 'error');
            
            if (this.submitBtn) {
                this.submitBtn.disabled = false;
                this.submitBtn.innerHTML = 'Get Recommendations';
                feather.replace();
            }
        }
    }
}

// Initialize quiz when page loads
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('quizForm')) {
        new CareerQuiz();
    }
});