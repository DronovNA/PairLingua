# Создаем Frontend файлы

# Frontend package.json
package_json = """{
  "name": "pairlingua-frontend",
  "version": "1.0.0",
  "description": "Interactive Spanish-Russian language learning frontend",
  "private": true,
  "dependencies": {
    "@reduxjs/toolkit": "^1.9.7",
    "@types/node": "^20.8.7",
    "@types/react": "^18.2.31",
    "@types/react-dom": "^18.2.14",
    "axios": "^1.5.1",
    "framer-motion": "^10.16.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-dnd": "^16.0.1",
    "react-dnd-html5-backend": "^16.0.1",
    "react-hook-form": "^7.47.0",
    "react-hot-toast": "^2.4.1",
    "react-query": "^3.39.3",
    "react-router-dom": "^6.17.0",
    "react-scripts": "5.0.1",
    "react-redux": "^8.1.3",
    "tailwindcss": "^3.3.5",
    "typescript": "^4.9.5",
    "web-vitals": "^3.5.0",
    "@headlessui/react": "^1.7.17",
    "@heroicons/react": "^2.0.18",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "date-fns": "^2.30.0",
    "clsx": "^2.0.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject",
    "lint": "eslint src --ext .ts,.tsx",
    "lint:fix": "eslint src --ext .ts,.tsx --fix"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.1.4",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^14.5.1",
    "@types/jest": "^29.5.6",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31"
  },
  "proxy": "http://localhost:8000"
}
"""

# TypeScript config
tsconfig_json = """{
  "compilerOptions": {
    "target": "es5",
    "lib": [
      "dom",
      "dom.iterable",
      "es6"
    ],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "baseUrl": "src",
    "paths": {
      "@/*": ["*"],
      "@/components/*": ["components/*"],
      "@/hooks/*": ["hooks/*"],
      "@/services/*": ["services/*"],
      "@/store/*": ["store/*"],
      "@/types/*": ["types/*"],
      "@/utils/*": ["utils/*"]
    }
  },
  "include": [
    "src"
  ],
  "exclude": [
    "node_modules"
  ]
}
"""

# Tailwind config
tailwind_config = """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        secondary: {
          50: '#fdf2f8',
          100: '#fce7f3',
          200: '#fbcfe8',
          300: '#f9a8d4',
          400: '#f472b6',
          500: '#ec4899',
          600: '#db2777',
          700: '#be185d',
          800: '#9d174d',
          900: '#831843',
        },
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        }
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'bounce-gentle': 'bounceGentle 0.6s ease-in-out',
        'pulse-soft': 'pulseSoft 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceGentle: {
          '0%, 20%, 53%, 80%, 100%': { transform: 'translate3d(0,0,0)' },
          '40%, 43%': { transform: 'translate3d(0,-15px,0)' },
          '70%': { transform: 'translate3d(0,-7px,0)' },
          '90%': { transform: 'translate3d(0,-2px,0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
"""

# Frontend Dockerfile
frontend_dockerfile = """# Multi-stage build for React app
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy build files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
"""

# Main index.html
index_html = """<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#0ea5e9" />
    <meta name="description" content="Изучайте испанский язык интерактивно с PairLingua" />
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://pairlingua.com/" />
    <meta property="og:title" content="PairLingua - Изучение испанского языка" />
    <meta property="og:description" content="Интерактивное изучение испанского языка с алгоритмом spaced repetition" />
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image" />
    <meta property="twitter:title" content="PairLingua - Изучение испанского языка" />
    <meta property="twitter:description" content="Интерактивное изучение испанского языка с алгоритмом spaced repetition" />
    
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <title>PairLingua - Изучение испанского языка</title>
    
    <!-- Prevent FOUC (Flash of Unstyled Content) -->
    <style>
      body {
        visibility: hidden;
        opacity: 0;
        transition: opacity 0.3s;
      }
      .app-loaded {
        visibility: visible !important;
        opacity: 1 !important;
      }
    </style>
  </head>
  <body class="bg-gray-50 font-sans">
    <noscript>
      <div style="text-align: center; padding: 2rem; font-family: system-ui;">
        <h1>JavaScript Required</h1>
        <p>PairLingua requires JavaScript to function properly.</p>
        <p>Please enable JavaScript in your browser settings.</p>
      </div>
    </noscript>
    
    <!-- Loading spinner -->
    <div id="initial-loader" class="fixed inset-0 bg-white z-50 flex items-center justify-center">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p class="mt-4 text-gray-600">Загрузка PairLingua...</p>
      </div>
    </div>
    
    <div id="root"></div>
    
    <!-- PWA Installation Prompt -->
    <div id="pwa-install-prompt" class="hidden fixed bottom-4 left-4 right-4 bg-primary-600 text-white p-4 rounded-lg shadow-lg z-40">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <svg class="h-6 w-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
          </svg>
          <span class="text-sm font-medium">Установить PairLingua на устройство</span>
        </div>
        <div class="flex space-x-2">
          <button id="pwa-install-btn" class="bg-white text-primary-600 px-3 py-1 rounded text-sm font-medium">
            Установить
          </button>
          <button id="pwa-dismiss-btn" class="text-primary-200 hover:text-white">
            <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <script>
      // Remove loading spinner when page loads
      window.addEventListener('load', function() {
        document.body.classList.add('app-loaded');
        const loader = document.getElementById('initial-loader');
        if (loader) {
          loader.style.display = 'none';
        }
      });
      
      // PWA Installation
      let deferredPrompt;
      
      window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        const installPrompt = document.getElementById('pwa-install-prompt');
        const installBtn = document.getElementById('pwa-install-btn');
        const dismissBtn = document.getElementById('pwa-dismiss-btn');
        
        if (!localStorage.getItem('pwa-dismissed')) {
          installPrompt.classList.remove('hidden');
        }
        
        installBtn.addEventListener('click', () => {
          installPrompt.classList.add('hidden');
          deferredPrompt.prompt();
          deferredPrompt.userChoice.then((choiceResult) => {
            deferredPrompt = null;
          });
        });
        
        dismissBtn.addEventListener('click', () => {
          installPrompt.classList.add('hidden');
          localStorage.setItem('pwa-dismissed', 'true');
        });
      });
    </script>
  </body>
</html>
"""

# Main CSS
index_css = """/* PairLingua Styles */
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

/* Custom CSS Variables */
:root {
  --color-primary: theme('colors.primary.500');
  --color-secondary: theme('colors.secondary.500');
  --color-success: theme('colors.success.500');
  --color-warning: theme('colors.warning.500');
  --color-error: theme('colors.error.500');
  
  --shadow-soft: 0 2px 4px 0 rgba(0, 0, 0, 0.06);
  --shadow-medium: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-large: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Base Styles */
body {
  font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
  font-variant-numeric: oldstyle-nums;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Custom Components */
.card {
  @apply bg-white rounded-xl shadow-soft border border-gray-100;
}

.card-hover {
  @apply card transition-all duration-200 hover:shadow-medium hover:border-gray-200;
}

.btn-primary {
  @apply bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2;
}

.btn-secondary {
  @apply bg-gray-100 hover:bg-gray-200 text-gray-900 font-medium py-2 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2;
}

.btn-success {
  @apply bg-success-600 hover:bg-success-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-success-500 focus:ring-offset-2;
}

.btn-danger {
  @apply bg-error-600 hover:bg-error-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-error-500 focus:ring-offset-2;
}

.input-field {
  @apply block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 sm:text-sm;
}

.input-error {
  @apply input-field border-error-300 focus:border-error-500 focus:ring-error-500;
}

/* Study Game Components */
.word-card {
  @apply card-hover p-6 cursor-pointer select-none;
}

.word-card-spanish {
  @apply word-card bg-gradient-to-r from-primary-50 to-blue-50 border-primary-200;
}

.word-card-russian {
  @apply word-card bg-gradient-to-r from-secondary-50 to-pink-50 border-secondary-200;
}

.word-card-selected {
  @apply ring-2 ring-primary-500 border-primary-500 shadow-large scale-105;
}

.word-card-matched {
  @apply bg-gradient-to-r from-success-50 to-green-50 border-success-300 ring-2 ring-success-300;
}

.word-card-error {
  @apply bg-gradient-to-r from-error-50 to-red-50 border-error-300 ring-2 ring-error-300;
}

/* Progress Components */
.progress-bar {
  @apply w-full bg-gray-200 rounded-full h-2 overflow-hidden;
}

.progress-fill {
  @apply h-full bg-gradient-to-r from-primary-600 to-blue-600 transition-all duration-500 ease-out;
}

/* Stats Components */
.stat-card {
  @apply card p-6 text-center;
}

.stat-number {
  @apply text-2xl font-bold text-gray-900;
}

.stat-label {
  @apply text-sm text-gray-600 mt-1;
}

/* Animation Utilities */
.animate-bounce-in {
  animation: bounceIn 0.6s ease-out;
}

.animate-shake {
  animation: shake 0.6s ease-in-out;
}

.animate-success-pulse {
  animation: successPulse 0.8s ease-out;
}

@keyframes bounceIn {
  0% { transform: scale(0.3); opacity: 0; }
  50% { transform: scale(1.05); opacity: 1; }
  70% { transform: scale(0.9); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

@keyframes successPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); background-color: theme('colors.success.100'); }
  100% { transform: scale(1); }
}

/* Responsive Design */
@media (max-width: 640px) {
  .word-card {
    @apply p-4 text-sm;
  }
  
  .stat-card {
    @apply p-4;
  }
  
  .stat-number {
    @apply text-lg;
  }
}

/* Dark Mode Support (for future implementation) */
@media (prefers-color-scheme: dark) {
  /* Dark mode styles would go here */
}

/* Accessibility */
.focus-visible {
  @apply outline-none ring-2 ring-primary-500 ring-offset-2;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .card {
    @apply border-2 border-gray-900;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Print styles */
@media print {
  .no-print {
    display: none !important;
  }
  
  body {
    background: white !important;
    color: black !important;
  }
}
"""

# Записываем frontend файлы
with open("pairlingua/frontend/package.json", "w") as f:
    f.write(package_json)

with open("pairlingua/frontend/tsconfig.json", "w") as f:
    f.write(tsconfig_json)

with open("pairlingua/frontend/tailwind.config.js", "w") as f:
    f.write(tailwind_config)

with open("pairlingua/frontend/Dockerfile", "w") as f:
    f.write(frontend_dockerfile)

with open("pairlingua/frontend/public/index.html", "w") as f:
    f.write(index_html)

with open("pairlingua/frontend/src/index.css", "w") as f:
    f.write(index_css)

print("✅ Frontend конфигурация создана")
print("📦 package.json с React 18 и TypeScript")
print("🎨 Tailwind CSS с кастомными стилями")
print("🌐 HTML с PWA поддержкой")
print("⚡ Оптимизированная сборка с Docker")