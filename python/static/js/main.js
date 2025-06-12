// Конфигурация
const config = {
    backendUrl: 'http://localhost:3000'
};

// Функции для работы с формами
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    let isValid = true;
    const inputs = form.querySelectorAll('input[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            showError(input.id + 'Error', 'Это поле обязательно для заполнения');
            isValid = false;
        } else {
            clearError(input.id + 'Error');
        }
    });

    return isValid;
}

function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

function clearError(elementId) {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.style.display = 'none';
    }
}

// Функции для работы с API
async function fetchData(endpoint, options = {}) {
    try {
        const response = await fetch(`${config.backendUrl}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка при выполнении запроса');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function sendData(endpoint, data, options = {}) {
    return fetchData(endpoint, {
        method: 'POST',
        body: JSON.stringify(data),
        ...options
    });
}

// Функция для отображения уведомлений
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'warning': return 'fa-exclamation-triangle';
        default: return 'fa-info-circle';
    }
}

// Функция для загрузки счетов
async function loadAccounts() {
    try {
        const accounts = await fetchData('/accounts');
        const accountsList = document.getElementById('accountsList');
        if (accountsList) {
            accountsList.innerHTML = accounts.map(account => `
                <div class="account-card">
                    <h3>Счет №${account.account_number}</h3>
                    <p>Баланс: ${account.balance} руб.</p>
                    <p>Статус: ${account.status}</p>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading accounts:', error);
    }
}

// Обработчик отправки формы
async function submitForm(event) {
    event.preventDefault();
    
    const form = event.target;
    const formId = form.id;
    
    if (!validateForm(formId)) {
        return;
    }
    
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
        let response;
        if (formId === 'loginForm') {
            response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams(data)
            });
        } else if (formId === 'registerForm') {
            response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams(data)
            });
        }
        
        if (response.ok) {
            const result = await response.json();
            if (formId === 'loginForm') {
                localStorage.setItem('token', result.access_token);
                window.location.href = '/';
            } else {
                showNotification('Регистрация успешна! Теперь вы можете войти.');
                window.location.href = '/login';
            }
        } else {
            const error = await response.json();
            showError(formId === 'loginForm' ? 'emailError' : 'emailError', error.detail || 'Ошибка при отправке формы');
        }
    } catch (error) {
        console.error('Form submission error:', error);
        showError(formId === 'loginForm' ? 'emailError' : 'emailError', 'Ошибка при отправке формы');
    }
}

// Функция проверки паролей при регистрации
function checkPasswords() {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');
    const errorElement = document.getElementById('passwordError');
    
    if (password && confirmPassword && errorElement) {
        if (password.value !== confirmPassword.value) {
            showError('passwordError', 'Пароли не совпадают');
            return false;
        }
        clearError('passwordError');
        return true;
    }
    return true;
}

// Password visibility toggle
document.querySelectorAll('.toggle-password').forEach(button => {
    button.addEventListener('click', function() {
        const input = this.parentElement.querySelector('input');
        const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
        input.setAttribute('type', type);
        this.querySelector('i').classList.toggle('fa-eye');
        this.querySelector('i').classList.toggle('fa-eye-slash');
    });
});

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded');
    
    // Находим формы
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    console.log('Login form:', loginForm);
    console.log('Register form:', registerForm);
    
    // Добавляем обработчики событий
    if (loginForm) {
        loginForm.addEventListener('submit', submitForm);
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', submitForm);
        const confirmPassword = document.getElementById('confirmPassword');
        if (confirmPassword) {
            confirmPassword.addEventListener('input', checkPasswords);
        }
    }
    
    // Загружаем счета, если мы на главной странице
    if (document.getElementById('accountsList')) {
        loadAccounts();
    }

    // Add notification styles
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem;
            border-radius: 5px;
            background: white;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        }

        .notification-content {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .notification.success { border-left: 4px solid #28a745; }
        .notification.error { border-left: 4px solid #dc3545; }
        .notification.warning { border-left: 4px solid #ffc107; }
        .notification.info { border-left: 4px solid #17a2b8; }

        .notification-close {
            background: none;
            border: none;
            color: #666;
            cursor: pointer;
            padding: 0.25rem;
        }

        .notification-close:hover {
            color: #333;
        }

        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        .error-message {
            color: #dc3545;
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }

        input.error {
            border-color: #dc3545;
        }
    `;
    document.head.appendChild(style);
});

async function handleRegister(event) {
    event.preventDefault();
    const form = document.getElementById('registerForm');
    const email = form.email.value.trim();
    const password = form.password.value;
    const confirm_password = form.confirmPassword.value; // snake_case!

    // Валидация на клиенте (можно расширить)
    if (!email || !password || !confirm_password) {
        showNotification('Пожалуйста, заполните все поля', 'error');
        return false;
    }
    if (password !== confirm_password) {
        showNotification('Пароли не совпадают', 'error');
        return false;
    }

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, confirm_password })
        });
        const data = await response.json();
        if (response.ok) {
            showNotification('Регистрация успешна! Проверьте почту для подтверждения.', 'success');
            setTimeout(() => { window.location.href = '/login'; }, 1500);
        } else {
            showNotification(data.detail || 'Ошибка регистрации', 'error');
        }
    } catch (err) {
        showNotification('Ошибка сети при регистрации', 'error');
    }
    return false;
}

async function handleLogin(event) {
    event.preventDefault();
    const form = document.getElementById('loginForm');
    const username = form.email.value.trim();
    const password = form.password.value;
    if (!username || !password) {
        showNotification('Введите email и пароль', 'error');
        return false;
    }
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    try {
        const response = await fetch('/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            showNotification('Вход выполнен!', 'success');
            setTimeout(() => { window.location.href = '/'; }, 1000);
        } else {
            showNotification(data.detail || 'Ошибка входа', 'error');
        }
    } catch (err) {
        showNotification('Ошибка сети при входе', 'error');
    }
    return false;
} 