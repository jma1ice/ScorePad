function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fa-solid ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="closeNotification(this)">&times;</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'warning': return 'fa-exclamation-triangle';
        default: return 'fa-info-circle';
    }
}

function closeNotification(button) {
    const notification = button.closest('.notification');
    if (notification) {
        notification.remove();
    }
}

function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('error');
            isValid = false;
        } else {
            field.classList.remove('error');
        }
    });
    
    return isValid;
}

async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
        throw new Error(`API request failed: ${response.statusText}`);
    }
    
    return response.json();
}

function saveGameState(gameId, state) {
    localStorage.setItem(`game_${gameId}`, JSON.stringify(state));
}

function loadGameState(gameId) {
    const saved = localStorage.getItem(`game_${gameId}`);
    return saved ? JSON.parse(saved) : null;
}

function clearGameState(gameId) {
    localStorage.removeItem(`game_${gameId}`);
}

function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

function addTouchFeedback() {
    if (!isTouchDevice()) return;
    
    const clickableElements = document.querySelectorAll('.btn, .card-clickable, [onclick]');
    
    clickableElements.forEach(element => {
        element.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
            this.style.opacity = '0.9';
        });
        
        element.addEventListener('touchend', function() {
            setTimeout(() => {
                this.style.transform = '';
                this.style.opacity = '';
            }, 100);
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    addTouchFeedback();
    
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showNotification('Please fill in all required fields', 'error');
            }
        });
    });
    
    const cards = document.querySelectorAll('.card-clickable');
    cards.forEach(card => {
        card.addEventListener('click', function() {
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
});

function formatScore(score) {
    return score > 0 ? `+${score}` : score.toString();
}

function calculateRunningTotal(scores, player) {
    return scores
        .filter(score => score.player === player)
        .reduce((total, score) => total + score.score, 0);
}

function getGameIcon(gameType) {
    const icons = {
        'bridge': 'fa-solid fa-diamond',
        'rummy': 'fa-solid fa-layer-group',
        'canasta': 'fa-solid fa-clone',
        'hearts': 'fa-solid fa-heart',
        'spades': 'fa-solid fa-spade'
    };
    return icons[gameType] || 'fa-solid fa-cards';
}

window.CardGameScorer = {
    showNotification,
    validateForm,
    apiRequest,
    saveGameState,
    loadGameState,
    clearGameState,
    formatScore,
    calculateRunningTotal,
    getGameIcon
};