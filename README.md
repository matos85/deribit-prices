# Deribit Price Tracker

Сервис периодически забирает index price валют `btc_usd` и `eth_usd` с биржи [Deribit](https://docs.deribit.com/), сохраняет их в PostgreSQL и отдаёт через HTTP API на FastAPI.

## Возможности

- Celery Beat раз в минуту запрашивает `public/get_index_price` для `btc_usd` и `eth_usd`
- В БД пишутся `ticker`, `price`, UNIX `timestamp`
- Read-only API:
  - `GET /prices?ticker=btc_usd` — все сохранённые точки
  - `GET /prices/latest?ticker=btc_usd` — последняя цена
  - `GET /prices/history?ticker=btc_usd&date_from=1700000000&date_to=1700000120` — срез по дате

Интерактивная документация: [http://localhost:8000/docs](http://localhost:8000/docs)

## Архитектура

```
Celery Beat → Celery Worker → DeribitClient (aiohttp) → Deribit API
                     ↓
              PriceRepository → PostgreSQL
                     ↑
                  FastAPI
```

Слои:

| Слой | Назначение |
|------|------------|
| `app/api` | HTTP-роуты, Pydantic-схемы, зависимости FastAPI |
| `app/domain` | SQLAlchemy-модель и репозиторий |
| `app/infrastructure` | БД, HTTP-клиент Deribit |
| `app/workers` | Celery app и периодическая задача |
| `app/core` | Конфигурация (`Settings`) |

## Требования

На любом компьютере достаточно:

- Docker Engine (или Docker Desktop)
- Docker Compose v2 (`docker compose`)
- доступ в интернет (образы Docker + API Deribit)

Python/PostgreSQL/Redis на хосте **не нужны**.

## Запуск на другом компьютере (только Docker)

1. Скопируйте папку проекта или клонируйте репозиторий.
2. В каталоге проекта выполните:

```bash
cd deribit-prices
docker compose up --build -d
```

3. Откройте API: [http://localhost:8000/docs](http://localhost:8000/docs)

Подымаются ровно два контейнера:

| Сервис | Содержимое |
|--------|------------|
| `app` | FastAPI + Celery worker + Celery beat + Redis |
| `db` | PostgreSQL 16 |

Наружу открыт только порт `8000`. PostgreSQL доступен приложению по внутренней сети Docker (`db:5432`).

Первый тик цен появится в течение ~1 минуты после старта.

Полезные команды:

```bash
# логи
docker compose logs -f app

# статус
docker compose ps

# остановка
docker compose down

# остановка со сбросом БД
docker compose down -v
```

Если порт `8000` занят, поменяйте проброс в `docker-compose.yml`, например `"8001:8000"`.
## Переменные окружения

Скопируйте `.env.example` в `.env` при локальном запуске.

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | SQLAlchemy DSN PostgreSQL | `postgresql+psycopg2://deribit:deribit@localhost:5432/deribit_prices` |
| `REDIS_URL` | Broker/backend Celery | `redis://localhost:6379/0` |
| `DERIBIT_BASE_URL` | Базовый URL Deribit API | `https://www.deribit.com/api/v2` |
| `TICKERS` | Список тикеров через запятую | `btc_usd,eth_usd` |
| `FETCH_INTERVAL_SECONDS` | Интервал Celery Beat | `60` |

## Примеры API

```bash
# Все цены BTC
curl "http://localhost:8000/prices?ticker=btc_usd"

# Последняя цена ETH
curl "http://localhost:8000/prices/latest?ticker=eth_usd"

# История по диапазону UNIX timestamp
curl "http://localhost:8000/prices/history?ticker=btc_usd&date_from=1700000000&date_to=1700003600"
```

Пример ответа:

```json
{
  "ticker": "btc_usd",
  "price": "65123.45000000",
  "timestamp": 1700000060
}
```

У каждого метода обязателен query-параметр `ticker`.

## Локальный запуск без Docker

1. Поднимите PostgreSQL и Redis.
2. Создайте виртуальное окружение и установите зависимости:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

3. Запустите процессы в отдельных терминалах:

```bash
uvicorn app.main:app --reload --port 8000
celery -A app.workers.celery_app.celery_app worker --loglevel=INFO
celery -A app.workers.celery_app.celery_app beat --loglevel=INFO
```

## Тесты

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Тесты используют in-memory SQLite и моки HTTP (`aioresponses`), внешние сервисы не нужны.
