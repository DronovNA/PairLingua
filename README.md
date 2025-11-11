# PairLingua - Interactive Spanish-Russian Language Learning App

PairLingua is a modern, interactive web application for learning Spanish through Russian translations using spaced repetition algorithms and gamification.

## 🎯 Features

- **Spaced Repetition Learning**: Uses SM-2 algorithm for optimal retention
- **Interactive Exercises**: Matching, multiple choice, and typing exercises
- **Gamification**: Points, streaks, achievements, and leaderboards
- **Progress Tracking**: Detailed statistics and learning analytics
- **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile
- **Real-time Updates**: Instant feedback and progress updates

## 🏗️ Architecture

- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Reverse Proxy**: Nginx
- **Containerization**: Docker + Docker Compose

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pairlingua.git
   cd pairlingua
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Wait for services to be ready** (about 30-60 seconds)

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Demo Account

- Email: `demo@pairlingua.com`
- Password: `demo123`

## 📁 Project Structure

```
pairlingua/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── alembic/            # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── store/          # Redux store
│   │   └── types/          # TypeScript types
│   ├── Dockerfile
│   └── package.json
├── nginx/                   # Nginx configuration
├── scripts/                 # Database scripts
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 Development

### Backend Development

1. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

3. **Start development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Development

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

### Database Management

- **Create migration**: `alembic revision --autogenerate -m "Description"`
- **Apply migrations**: `alembic upgrade head`
- **Rollback migration**: `alembic downgrade -1`

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### End-to-End Tests
```bash
npm run test:e2e
```

## 📊 API Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

- **Authentication**
  - `POST /api/v1/auth/register` - Register new user
  - `POST /api/v1/auth/login` - Login user
  - `POST /api/v1/auth/refresh` - Refresh tokens

- **Study**
  - `GET /api/v1/study/cards/due` - Get cards due for review
  - `POST /api/v1/study/cards/review` - Submit review results

- **User**
  - `GET /api/v1/users/me` - Get current user profile
  - `GET /api/v1/users/me/stats` - Get user statistics

## 🏆 Learning Algorithm

PairLingua uses the **SM-2 (SuperMemo 2)** spaced repetition algorithm:

1. **Quality Scale (0-5)**:
   - 0: Complete blackout
   - 1: Incorrect response; correct one remembered
   - 2: Incorrect response; correct one seemed easy
   - 3: Correct response recalled with serious difficulty
   - 4: Correct response after hesitation
   - 5: Perfect response

2. **Adaptive Intervals**: Cards are scheduled for review at increasing intervals based on performance

3. **Ease Factor**: Each card has a difficulty factor that adjusts based on response quality

## 🎮 Game Elements

- **Points System**: Earn points for correct answers
- **Streak Tracking**: Maintain daily study streaks
- **Achievements**: Unlock badges for milestones
- **Leaderboards**: Compete with other learners
- **Progress Visualization**: Charts and statistics

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with salt
- **CORS Protection**: Configurable origins
- **Rate Limiting**: API endpoint protection
- **Input Validation**: Server-side data validation

## 📱 Mobile Support

- Responsive design for all screen sizes
- Touch-friendly interface
- PWA (Progressive Web App) support
- Offline functionality (coming soon)

## 🌍 Internationalization

- Multi-language interface (Russian, Spanish, English)
- RTL language support
- Locale-specific formatting

## 📈 Monitoring & Analytics

- Health check endpoints
- Performance metrics
- Error tracking
- User analytics

## 🚀 Deployment

### Production Deployment

1. **Set production environment variables**
2. **Build Docker images**
3. **Deploy with Docker Compose or Kubernetes**
4. **Set up SSL certificates**
5. **Configure domain and DNS**

### Environment Variables

See `.env.example` for all available configuration options.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Documentation: [Wiki](https://github.com/yourusername/pairlingua/wiki)
- Issues: [GitHub Issues](https://github.com/yourusername/pairlingua/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/pairlingua/discussions)

## 🙏 Acknowledgments

- SuperMemo for the SM-2 algorithm
- OpenAI for language processing inspiration
- The open-source community for amazing tools and libraries

---

**PairLingua** - Making language learning interactive, effective, and fun! 🎉
