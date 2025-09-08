import os
import zipfile
from pathlib import Path

# Создаем структуру проекта
project_structure = {
    "pairlingua/": {
        "README.md": "",
        "docker-compose.yml": "",
        ".env.example": "",
        ".gitignore": "",
        "backend/": {
            "Dockerfile": "",
            "requirements.txt": "",
            "alembic.ini": "",
            "app/": {
                "__init__.py": "",
                "main.py": "",
                "core/": {
                    "__init__.py": "",
                    "config.py": "",
                    "database.py": "",
                    "security.py": "",
                    "redis.py": "",
                    "exceptions.py": "",
                },
                "models/": {
                    "__init__.py": "",
                    "user.py": "",
                    "word_pair.py": "",
                    "user_card.py": "",
                    "review.py": "",
                    "session.py": "",
                    "achievement.py": "",
                },
                "schemas/": {
                    "__init__.py": "",
                    "auth.py": "",
                    "user.py": "",
                    "word.py": "",
                    "study.py": "",
                },
                "api/": {
                    "__init__.py": "",
                    "v1/": {
                        "__init__.py": "",
                        "router.py": "",
                        "auth.py": "",
                        "users.py": "",
                        "words.py": "",
                        "study.py": "",
                        "achievements.py": "",
                    }
                },
                "services/": {
                    "__init__.py": "",
                    "auth_service.py": "",
                    "user_service.py": "",
                    "word_service.py": "",
                    "study_service.py": "",
                    "sm2_service.py": "",
                },
                "utils/": {
                    "__init__.py": "",
                    "security.py": "",
                    "email.py": "",
                }
            },
            "alembic/": {
                "versions/": {},
                "env.py": "",
                "script.py.mako": "",
            },
            "tests/": {
                "__init__.py": "",
                "conftest.py": "",
                "test_auth.py": "",
                "test_study.py": "",
            }
        },
        "frontend/": {
            "Dockerfile": "",
            "package.json": "",
            "tsconfig.json": "",
            "tailwind.config.js": "",
            "public/": {
                "index.html": "",
                "favicon.ico": "",
            },
            "src/": {
                "index.tsx": "",
                "App.tsx": "",
                "index.css": "",
                "components/": {
                    "Layout/": {
                        "Header.tsx": "",
                        "Navbar.tsx": "",
                    },
                    "Auth/": {
                        "LoginForm.tsx": "",
                        "RegisterForm.tsx": "",
                    },
                    "Study/": {
                        "GameBoard.tsx": "",
                        "WordCard.tsx": "",
                        "MatchingExercise.tsx": "",
                    },
                    "Profile/": {
                        "ProfilePage.tsx": "",
                        "StatsChart.tsx": "",
                    },
                    "UI/": {
                        "Button.tsx": "",
                        "Input.tsx": "",
                        "Card.tsx": "",
                    }
                },
                "hooks/": {
                    "useAuth.ts": "",
                    "useStudy.ts": "",
                },
                "services/": {
                    "api.ts": "",
                    "auth.ts": "",
                    "study.ts": "",
                },
                "store/": {
                    "index.ts": "",
                    "authSlice.ts": "",
                    "studySlice.ts": "",
                },
                "types/": {
                    "index.ts": "",
                    "auth.ts": "",
                    "study.ts": "",
                },
                "utils/": {
                    "constants.ts": "",
                    "helpers.ts": "",
                }
            }
        },
        "nginx/": {
            "nginx.conf": "",
            "Dockerfile": "",
        },
        "scripts/": {
            "init-db.sql": "",
            "seed-data.sql": "",
            "start.sh": "",
        }
    }
}

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = base_path / name
        if isinstance(content, dict):
            path.mkdir(parents=True, exist_ok=True)
            create_structure(path, content)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()

# Создаем структуру проекта
project_root = Path("pairlingua")
create_structure(Path("."), project_structure)

print("✅ Структура проекта создана")
print("📁 Создано директорий и файлов:", sum(len(str(p).split('/')) for p in Path("pairlingua").rglob("*")))