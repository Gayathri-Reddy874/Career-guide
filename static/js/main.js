// static/js/main.js

// Global helper functions
window.showToast = function(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

// Format currency
window.formatSalary = function(salary) {
    if (!salary) return 'N/A';
    if (typeof salary === 'string' && salary.includes('-')) {
        return salary;
    }
    return `${salary} LPA`;
};

// Format match score
window.formatMatchScore = function(score) {
    return `${Math.round(score)}%`;
};

// Get match score class
window.getMatchClass = function(score) {
    if (score >= 80) return 'high-match';
    if (score >= 60) return 'medium-match';
    return 'low-match';
};

// Debounce function for search
window.debounce = function(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// Escape HTML to prevent XSS
window.escapeHtml = function(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
};

// Format date
window.formatDate = function(date) {
    return new Date(date).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
};

// Generate random ID
window.generateId = function() {
    return Math.random().toString(36).substr(2, 9);
};

// Local storage helpers
window.storage = {
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            return defaultValue;
        }
    },
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            return false;
        }
    },
    remove: function(key) {
        localStorage.removeItem(key);
    },
    clear: function() {
        localStorage.clear();
    }
};

// Career comparison helpers
window.compareManager = {
    add: function(careerId, careerName) {
        let compareList = storage.get('compareList', []);
        if (compareList.length >= 3) {
            showToast('You can compare up to 3 careers at a time', 'error');
            return false;
        }
        if (!compareList.includes(careerId)) {
            compareList.push(careerId);
            storage.set('compareList', compareList);
            showToast(`${careerName} added to comparison`, 'success');
            return true;
        }
        showToast('Career already in comparison list', 'info');
        return false;
    },
    remove: function(careerId) {
        let compareList = storage.get('compareList', []);
        compareList = compareList.filter(id => id !== careerId);
        storage.set('compareList', compareList);
        return compareList;
    },
    get: function() {
        return storage.get('compareList', []);
    },
    clear: function() {
        storage.remove('compareList');
    },
    count: function() {
        return storage.get('compareList', []).length;
    }
};

// Saved careers helpers
window.savedManager = {
    add: function(careerId, careerName) {
        let saved = storage.get('savedCareers', []);
        if (!saved.includes(careerId)) {
            saved.push(careerId);
            storage.set('savedCareers', saved);
            showToast(`${careerName} saved to your profile`, 'success');
            return true;
        }
        showToast('Career already saved', 'info');
        return false;
    },
    remove: function(careerId) {
        let saved = storage.get('savedCareers', []);
        saved = saved.filter(id => id !== careerId);
        storage.set('savedCareers', saved);
        return saved;
    },
    get: function() {
        return storage.get('savedCareers', []);
    },
    isSaved: function(careerId) {
        return storage.get('savedCareers', []).includes(careerId);
    }
};

// Search functionality
window.initSearch = function() {
    const searchInput = document.getElementById('globalSearch');
    if (!searchInput) return;
    
    const searchResults = document.createElement('div');
    searchResults.className = 'search-results';
    searchInput.parentNode.appendChild(searchResults);
    
    const performSearch = debounce(async (query) => {
        if (query.length < 2) {
            searchResults.style.display = 'none';
            return;
        }
        
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            
            if (results.length === 0) {
                searchResults.innerHTML = '<div class="search-result-item">No careers found</div>';
            } else {
                searchResults.innerHTML = results.map(career => `
                    <a href="/career/${career.Career_ID}" class="search-result-item">
                        <strong>${escapeHtml(career.Career_Name)}</strong>
                        <span class="search-result-category">${escapeHtml(career.Category)}</span>
                    </a>
                `).join('');
            }
            searchResults.style.display = 'block';
        } catch (error) {
            console.error('Search error:', error);
        }
    }, 300);
    
    searchInput.addEventListener('input', (e) => {
        performSearch(e.target.value);
    });
    
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
};

// Mobile menu
window.initMobileMenu = function() {
    const menuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');
    const overlay = document.getElementById('mobileOverlay');
    
    if (!menuBtn) return;
    
    menuBtn.addEventListener('click', () => {
        navLinks.classList.add('active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    });
    
    if (overlay) {
        overlay.addEventListener('click', () => {
            navLinks.classList.remove('active');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && navLinks.classList.contains('active')) {
            navLinks.classList.remove('active');
            if (overlay) overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
};

// Scroll animations
window.initScrollAnimations = function() {
    const elements = document.querySelectorAll('.fade-in-up, .slide-up');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    elements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s ease-out';
        observer.observe(el);
    });
};

// Smooth scroll
window.initSmoothScroll = function() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
};

// Lazy load images
window.initLazyLoad = function() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initSearch();
    initMobileMenu();
    initScrollAnimations();
    initSmoothScroll();
    initLazyLoad();
    
    // Update compare count badge if exists
    const compareCount = compareManager.count();
    const compareBadge = document.getElementById('compareCount');
    if (compareBadge && compareCount > 0) {
        compareBadge.textContent = compareCount;
        compareBadge.style.display = 'inline';
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showToast,
        formatSalary,
        formatMatchScore,
        getMatchClass,
        storage,
        compareManager,
        savedManager
    };
}