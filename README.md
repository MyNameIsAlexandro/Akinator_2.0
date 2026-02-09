# Akinator 2.0

Telegram-бот, угадывающий персонажей (реальных и вымышленных) с помощью байесовского вывода и LLM.

## Architecture

- **Candidate Engine** — векторный поиск (FAISS) по базе сущностей
- **Scoring Engine** — байесовское обновление вероятностей по ответам пользователя
- **Question Policy** — выбор вопроса с максимальным information gain
- **LLM Client** — генерация вопросов, объяснений, извлечение атрибутов (OpenAI API)
- **Telegram Bot** — интерфейс на aiogram с inline-кнопками

## Tech Stack

- Python 3.11+
- aiogram 3.x (Telegram Bot API)
- SQLite (entity storage)
- FAISS (vector similarity search)
- OpenAI API (embeddings + LLM)

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Set environment variables
export TELEGRAM_BOT_TOKEN="your-token"
export OPENAI_API_KEY="your-key"

# Run tests
pytest

# Start bot
python -m akinator
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Data Model](docs/DATA_MODEL.md)
- [Game Logic](docs/GAME_LOGIC.md)
- [Telegram UX](docs/TELEGRAM_UX.md)

## License

MIT
