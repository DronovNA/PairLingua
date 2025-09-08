// Application data
const WORD_PAIRS = [
  {id: 1, spanish: "hola", russian: "привет", level: "A1", audio: true},
  {id: 2, spanish: "gracias", russian: "спасибо", level: "A1", audio: true},
  {id: 3, spanish: "casa", russian: "дом", level: "A1", audio: false},
  {id: 4, spanish: "agua", russian: "вода", level: "A1", audio: true},
  {id: 5, spanish: "familia", russian: "семья", level: "A1", audio: false},
  {id: 6, spanish: "hermano", russian: "брат", level: "A2", audio: true},
  {id: 7, spanish: "escuela", russian: "школа", level: "A2", audio: false},
  {id: 8, spanish: "trabajo", russian: "работа", level: "A2", audio: true},
  {id: 9, spanish: "feliz", russian: "счастливый", level: "B1", audio: false},
  {id: 10, spanish: "conocer", russian: "знать", level: "B1", audio: true}
];

const ACHIEVEMENTS = [
  {id: 1, title: "Первые шаги", description: "Завершите первый урок", icon: "🌱", earned: true},
  {id: 2, title: "Неделя изучения", description: "Учитесь 7 дней подряд", icon: "🔥", earned: true},
  {id: 3, title: "100 слов", description: "Выучите 100 слов", icon: "💯", earned: false},
  {id: 4, title: "Мастер точности", description: "90% точности в 50 ответах", icon: "🎯", earned: false}
];

const USER_STATS = {
  streak: 7,
  points: 2450,
  accuracy: 85.2,
  cardsLearned: 124,
  cardsReview: 15,
  level: "A2",
  weeklyData: [
    {day: "Пн", reviews: 25, correct: 22},
    {day: "Вт", reviews: 18, correct: 16},
    {day: "Ср", reviews: 32, correct: 28},
    {day: "Чт", reviews: 15, correct: 13},
    {day: "Пт", reviews: 28, correct: 25},
    {day: "Сб", reviews: 22, correct: 19},
    {day: "Вс", reviews: 20, correct: 17}
  ]
};

const DEMO_USER = {
  email: "demo@pairlingua.com",
  name: "Демо пользователь",
  avatar: "🌟",
  joinDate: "2024-01-15"
};

// Game State
let gameState = {
  currentMode: 'matching',
  currentPairs: [],
  selectedSpanish: null,
  selectedCard: null,
  isProcessing: false,
  currentQuestion: null,
  score: 0,
  streak: 0
};

// DOM Elements
let elements = {};

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    initializeElements();
    setupEventListeners();
    updateUserStats();
    
    // Show login page initially
    showPage('loginPage');
});

function initializeElements() {
    elements = {
        // Pages
        loginPage: document.getElementById('loginPage'),
        mainApp: document.getElementById('mainApp'),
        
        // Navigation
        sidebar: document.getElementById('sidebar'),
        mobileMenuToggle: document.getElementById('mobileMenuToggle'),
        navItems: document.querySelectorAll('.nav-item'),
        
        // Login
        loginForm: document.getElementById('loginForm'),
        demoBtn: document.getElementById('demoBtn'),
        emailInput: document.getElementById('email'),
        passwordInput: document.getElementById('password'),
        
        // User info
        userName: document.getElementById('userName'),
        headerStreak: document.getElementById('headerStreak'),
        headerPoints: document.getElementById('headerPoints'),
        
        // Stats
        streakValue: document.getElementById('streakValue'),
        accuracyValue: document.getElementById('accuracyValue'),
        pointsValue: document.getElementById('pointsValue'),
        cardsLeftValue: document.getElementById('cardsLeftValue'),
        
        // Game modes
        modeButtons: document.querySelectorAll('.mode-btn'),
        gameArea: document.querySelector('.game-area'),
        
        // Matching mode
        spanishWords: document.getElementById('spanishWords'),
        russianWords: document.getElementById('russianWords'),
        
        // Choice mode
        questionWord: document.getElementById('questionWord'),
        choicesList: document.getElementById('choicesList'),
        
        // Typing mode
        typingQuestionWord: document.getElementById('typingQuestionWord'),
        typingInput: document.getElementById('typingInput'),
        checkAnswerBtn: document.getElementById('checkAnswerBtn'),
        
        // Controls
        skipBtn: document.getElementById('skipBtn'),
        nextBtn: document.getElementById('nextBtn'),
        
        // Success message
        successMessage: document.getElementById('successMessage'),
        successText: document.getElementById('successText'),
        
        // Charts
        weeklyChart: document.getElementById('weeklyChart'),
        accuracyChart: document.getElementById('accuracyChart'),
        
        // Achievements
        achievementsList: document.getElementById('achievementsList'),
        
        // Logout
        logoutBtn: document.getElementById('logoutBtn')
    };
    
    console.log('Elements initialized:', Object.keys(elements).length);
}

function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Login
    if (elements.loginForm) {
        elements.loginForm.addEventListener('submit', handleLogin);
    }
    if (elements.demoBtn) {
        elements.demoBtn.addEventListener('click', handleDemoLogin);
    }
    
    // Navigation
    if (elements.navItems) {
        elements.navItems.forEach(item => {
            item.addEventListener('click', handleNavigation);
        });
    }
    
    // Mobile menu
    if (elements.mobileMenuToggle) {
        elements.mobileMenuToggle.addEventListener('click', toggleMobileMenu);
    }
    
    // Game modes
    if (elements.modeButtons) {
        elements.modeButtons.forEach(btn => {
            btn.addEventListener('click', handleModeChange);
        });
    }
    
    // Game controls
    if (elements.skipBtn) elements.skipBtn.addEventListener('click', handleSkip);
    if (elements.nextBtn) elements.nextBtn.addEventListener('click', handleNext);
    if (elements.checkAnswerBtn) elements.checkAnswerBtn.addEventListener('click', checkTypingAnswer);
    
    // Typing input
    if (elements.typingInput) {
        elements.typingInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                checkTypingAnswer();
            }
        });
    }
    
    // Logout
    if (elements.logoutBtn) {
        elements.logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Audio buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('audio-btn')) {
            playAudio();
        }
    });
    
    console.log('Event listeners set up');
}

// Page Management
function showPage(pageId) {
    console.log('Switching to page:', pageId);
    
    // Hide all pages
    const allPages = document.querySelectorAll('.page');
    allPages.forEach(page => {
        page.classList.remove('active');
    });
    
    // Show target page
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');
        console.log('Page switched successfully to:', pageId);
    } else {
        console.error('Page not found:', pageId);
    }
}

function showContentPage(pageId) {
    console.log('Switching to content page:', pageId);
    
    // Hide all content pages
    document.querySelectorAll('.content-page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show target content page
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');
        console.log('Content page switched successfully to:', pageId);
        
        // Initialize page-specific content
        if (pageId === 'statisticsPage') {
            setTimeout(initializeCharts, 100);
        } else if (pageId === 'achievementsPage') {
            renderAchievements();
        }
    } else {
        console.error('Content page not found:', pageId);
    }
}

// Authentication
function handleLogin(e) {
    e.preventDefault();
    console.log('Login form submitted');
    
    const email = elements.emailInput.value.trim();
    const password = elements.passwordInput.value.trim();
    
    console.log('Login attempt:', email);
    
    // Allow any email/password combination for demo purposes
    if (email && password) {
        loginUser();
    } else {
        showSuccessMessage('Пожалуйста, заполните все поля', 'error');
    }
}

function handleDemoLogin(e) {
    e.preventDefault();
    console.log('Demo login clicked');
    
    // Auto-fill demo credentials
    elements.emailInput.value = DEMO_USER.email;
    elements.passwordInput.value = 'demo123';
    
    // Login immediately
    loginUser();
}

function loginUser() {
    console.log('Logging in user...');
    
    // Switch to main app
    showPage('mainApp');
    showContentPage('studyPage');
    
    // Update user interface
    updateUserInfo();
    generateNewRound();
    
    // Show welcome message
    setTimeout(() => {
        showSuccessMessage('Добро пожаловать в PairLingua!', 'success');
    }, 500);
    
    console.log('User logged in successfully');
}

function handleLogout() {
    console.log('Logging out user...');
    
    showPage('loginPage');
    elements.emailInput.value = '';
    elements.passwordInput.value = '';
    resetGame();
    
    showSuccessMessage('Вы успешно вышли из системы', 'info');
}

// Navigation
function handleNavigation(e) {
    e.preventDefault();
    console.log('Navigation clicked:', e.currentTarget.dataset.page);
    
    const pageId = e.currentTarget.dataset.page + 'Page';
    
    // Update active nav item
    elements.navItems.forEach(item => item.classList.remove('active'));
    e.currentTarget.classList.add('active');
    
    // Show corresponding page
    showContentPage(pageId);
    
    // Close mobile menu if open
    if (elements.sidebar) {
        elements.sidebar.classList.remove('mobile-open');
    }
}

function toggleMobileMenu() {
    console.log('Mobile menu toggled');
    if (elements.sidebar) {
        elements.sidebar.classList.toggle('mobile-open');
    }
}

// User Interface Updates
function updateUserInfo() {
    if (elements.userName) {
        elements.userName.textContent = DEMO_USER.name;
    }
}

function updateUserStats() {
    if (elements.headerStreak) elements.headerStreak.textContent = USER_STATS.streak;
    if (elements.headerPoints) elements.headerPoints.textContent = USER_STATS.points;
    if (elements.streakValue) elements.streakValue.textContent = USER_STATS.streak;
    if (elements.accuracyValue) elements.accuracyValue.textContent = USER_STATS.accuracy + '%';
    if (elements.pointsValue) elements.pointsValue.textContent = USER_STATS.points;
    if (elements.cardsLeftValue) elements.cardsLeftValue.textContent = USER_STATS.cardsReview;
}

// Game Mode Management
function handleModeChange(e) {
    const mode = e.currentTarget.dataset.mode;
    console.log('Game mode changed to:', mode);
    
    // Update active mode button
    elements.modeButtons.forEach(btn => btn.classList.remove('active'));
    e.currentTarget.classList.add('active');
    
    // Update game state
    gameState.currentMode = mode;
    
    // Show corresponding game mode
    document.querySelectorAll('.game-mode-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const targetMode = document.getElementById(mode + 'Mode');
    if (targetMode) {
        targetMode.classList.add('active');
    }
    
    // Generate new content for the mode
    generateNewRound();
}

// Game Logic
function generateNewRound() {
    console.log('Generating new round for mode:', gameState.currentMode);
    
    gameState.currentPairs = getRandomPairs(WORD_PAIRS, 5);
    
    switch(gameState.currentMode) {
        case 'matching':
            renderMatchingMode();
            break;
        case 'choice':
            renderChoiceMode();
            break;
        case 'typing':
            renderTypingMode();
            break;
    }
}

function getRandomPairs(pairs, count) {
    const shuffled = [...pairs].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, Math.min(count, pairs.length));
}

// Matching Mode
function renderMatchingMode() {
    console.log('Rendering matching mode');
    
    if (!elements.spanishWords || !elements.russianWords) {
        console.error('Matching mode elements not found');
        return;
    }
    
    const spanishWords = gameState.currentPairs.map(pair => pair.spanish);
    const russianWords = [...gameState.currentPairs.map(pair => pair.russian)]
        .sort(() => Math.random() - 0.5);

    elements.spanishWords.innerHTML = '';
    elements.russianWords.innerHTML = '';

    spanishWords.forEach(word => {
        const card = createWordCard(word, 'spanish');
        elements.spanishWords.appendChild(card);
    });

    russianWords.forEach(word => {
        const card = createWordCard(word, 'russian');
        elements.russianWords.appendChild(card);
    });
    
    resetGameState();
}

function createWordCard(word, type) {
    const card = document.createElement('div');
    card.className = 'word-card';
    card.textContent = word;
    card.dataset.word = word;
    card.dataset.type = type;
    
    card.addEventListener('click', () => handleCardClick(card, word, type));
    
    return card;
}

function handleCardClick(card, word, type) {
    if (gameState.isProcessing) return;
    
    console.log('Card clicked:', word, type);
    
    if (type === 'spanish') {
        selectSpanishWord(card, word);
    } else if (type === 'russian' && gameState.selectedSpanish) {
        checkMatch(gameState.selectedSpanish, word);
    }
}

function selectSpanishWord(card, word) {
    console.log('Spanish word selected:', word);
    
    // Remove previous selection
    if (gameState.selectedCard) {
        gameState.selectedCard.classList.remove('selected');
    }
    
    // Select new word
    card.classList.add('selected');
    gameState.selectedSpanish = word;
    gameState.selectedCard = card;
}

function checkMatch(spanishWord, russianWord) {
    console.log('Checking match:', spanishWord, '=', russianWord);
    
    gameState.isProcessing = true;
    
    const correctPair = gameState.currentPairs.find(pair => 
        pair.spanish === spanishWord && pair.russian === russianWord
    );
    
    const spanishCard = gameState.selectedCard;
    const russianCard = document.querySelector(`[data-word="${russianWord}"][data-type="russian"]`);
    
    if (correctPair) {
        console.log('Correct match!');
        handleCorrectAnswer(spanishCard, russianCard);
    } else {
        console.log('Incorrect match');
        handleIncorrectAnswer(spanishCard, russianCard);
    }
}

// Choice Mode
function renderChoiceMode() {
    console.log('Rendering choice mode');
    
    if (!elements.questionWord || !elements.choicesList) {
        console.error('Choice mode elements not found');
        return;
    }
    
    const randomPair = gameState.currentPairs[Math.floor(Math.random() * gameState.currentPairs.length)];
    gameState.currentQuestion = randomPair;
    
    elements.questionWord.textContent = randomPair.spanish;
    
    // Generate choices (1 correct + 3 incorrect)
    const correctAnswer = randomPair.russian;
    const incorrectAnswers = WORD_PAIRS
        .filter(pair => pair.id !== randomPair.id)
        .map(pair => pair.russian)
        .sort(() => Math.random() - 0.5)
        .slice(0, 3);
    
    const allChoices = [correctAnswer, ...incorrectAnswers].sort(() => Math.random() - 0.5);
    
    elements.choicesList.innerHTML = '';
    allChoices.forEach(choice => {
        const btn = document.createElement('button');
        btn.className = 'choice-btn';
        btn.textContent = choice;
        btn.addEventListener('click', () => handleChoiceClick(btn, choice));
        elements.choicesList.appendChild(btn);
    });
    
    resetGameState();
}

function handleChoiceClick(btn, choice) {
    if (gameState.isProcessing) return;
    
    console.log('Choice clicked:', choice);
    
    gameState.isProcessing = true;
    
    // Remove previous selections
    document.querySelectorAll('.choice-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    
    const isCorrect = choice === gameState.currentQuestion.russian;
    
    if (isCorrect) {
        btn.classList.add('correct');
        handleCorrectAnswer();
    } else {
        btn.classList.add('incorrect');
        // Highlight correct answer
        document.querySelectorAll('.choice-btn').forEach(b => {
            if (b.textContent === gameState.currentQuestion.russian) {
                b.classList.add('correct');
            }
        });
        handleIncorrectAnswer();
    }
}

// Typing Mode
function renderTypingMode() {
    console.log('Rendering typing mode');
    
    if (!elements.typingQuestionWord || !elements.typingInput) {
        console.error('Typing mode elements not found');
        return;
    }
    
    const randomPair = gameState.currentPairs[Math.floor(Math.random() * gameState.currentPairs.length)];
    gameState.currentQuestion = randomPair;
    
    elements.typingQuestionWord.textContent = randomPair.spanish;
    elements.typingInput.value = '';
    
    // Focus input after a short delay
    setTimeout(() => {
        elements.typingInput.focus();
    }, 100);
    
    resetGameState();
}

function checkTypingAnswer() {
    if (gameState.isProcessing) return;
    
    const userAnswer = elements.typingInput.value.trim().toLowerCase();
    const correctAnswer = gameState.currentQuestion.russian.toLowerCase();
    
    console.log('Checking typing answer:', userAnswer, 'vs', correctAnswer);
    
    gameState.isProcessing = true;
    
    const isCorrect = userAnswer === correctAnswer;
    
    if (isCorrect) {
        elements.typingInput.classList.add('correct');
        handleCorrectAnswer();
    } else {
        elements.typingInput.classList.add('incorrect');
        showSuccessMessage(`Правильный ответ: ${gameState.currentQuestion.russian}`, 'info');
        handleIncorrectAnswer();
    }
}

// Answer Handling
async function handleCorrectAnswer(spanishCard = null, russianCard = null) {
    gameState.score += 10;
    gameState.streak++;
    
    if (spanishCard && russianCard) {
        spanishCard.classList.add('correct');
        russianCard.classList.add('correct');
    }
    
    showSuccessMessage('Правильно! +10 очков', 'success');
    
    await wait(1500);
    generateNewRound();
    resetGameState();
}

async function handleIncorrectAnswer(spanishCard = null, russianCard = null) {
    gameState.streak = 0;
    
    if (spanishCard && russianCard) {
        spanishCard.classList.add('incorrect');
        russianCard.classList.add('incorrect');
    }
    
    showSuccessMessage('Попробуйте ещё раз!', 'error');
    
    await wait(1500);
    
    if (spanishCard && russianCard) {
        spanishCard.classList.remove('incorrect', 'selected');
        russianCard.classList.remove('incorrect');
        gameState.selectedSpanish = null;
        gameState.selectedCard = null;
    } else {
        generateNewRound();
    }
    
    resetGameState();
}

function resetGameState() {
    gameState.isProcessing = false;
    gameState.selectedSpanish = null;
    gameState.selectedCard = null;
}

function resetGame() {
    gameState = {
        currentMode: 'matching',
        currentPairs: [],
        selectedSpanish: null,
        selectedCard: null,
        isProcessing: false,
        currentQuestion: null,
        score: 0,
        streak: 0
    };
}

// Game Controls
function handleSkip() {
    console.log('Skip clicked');
    generateNewRound();
    showSuccessMessage('Пропущено', 'info');
}

function handleNext() {
    console.log('Next clicked');
    generateNewRound();
}

// Charts
function initializeCharts() {
    console.log('Initializing charts...');
    
    if (elements.weeklyChart && elements.accuracyChart) {
        try {
            createWeeklyChart();
            createAccuracyChart();
        } catch (error) {
            console.error('Error creating charts:', error);
        }
    } else {
        console.error('Chart elements not found');
    }
}

function createWeeklyChart() {
    const ctx = elements.weeklyChart.getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: USER_STATS.weeklyData.map(d => d.day),
            datasets: [{
                label: 'Повторений',
                data: USER_STATS.weeklyData.map(d => d.reviews),
                backgroundColor: '#1FB8CD',
                borderColor: '#1FB8CD',
                borderWidth: 1
            }, {
                label: 'Правильных',
                data: USER_STATS.weeklyData.map(d => d.correct),
                backgroundColor: '#B4413C',
                borderColor: '#B4413C',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

function createAccuracyChart() {
    const ctx = elements.accuracyChart.getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: USER_STATS.weeklyData.map(d => d.day),
            datasets: [{
                label: 'Точность (%)',
                data: USER_STATS.weeklyData.map(d => Math.round((d.correct / d.reviews) * 100)),
                backgroundColor: 'rgba(31, 184, 205, 0.1)',
                borderColor: '#1FB8CD',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

// Achievements
function renderAchievements() {
    console.log('Rendering achievements');
    
    if (!elements.achievementsList) {
        console.error('Achievements list element not found');
        return;
    }
    
    elements.achievementsList.innerHTML = '';
    
    ACHIEVEMENTS.forEach(achievement => {
        const card = document.createElement('div');
        card.className = `achievement-card ${achievement.earned ? 'earned' : ''}`;
        
        card.innerHTML = `
            <span class="achievement-icon">${achievement.icon}</span>
            <h4 class="achievement-title">${achievement.title}</h4>
            <p class="achievement-description">${achievement.description}</p>
        `;
        
        elements.achievementsList.appendChild(card);
    });
}

// Utility Functions
function showSuccessMessage(text, type = 'success') {
    console.log('Showing message:', text, type);
    
    if (elements.successText && elements.successMessage) {
        elements.successText.textContent = text;
        elements.successMessage.classList.remove('hidden');
        
        setTimeout(() => {
            elements.successMessage.classList.add('hidden');
        }, 3000);
    }
}

function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function playAudio() {
    console.log('Playing audio');
    showSuccessMessage('🔊 Аудио воспроизведено', 'info');
}

// Close mobile menu when clicking outside
document.addEventListener('click', function(e) {
    if (elements.sidebar && elements.sidebar.classList.contains('mobile-open')) {
        if (!elements.sidebar.contains(e.target) && 
            elements.mobileMenuToggle && !elements.mobileMenuToggle.contains(e.target)) {
            elements.sidebar.classList.remove('mobile-open');
        }
    }
});