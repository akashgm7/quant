# QUANT-X: AI Market Scanning & Signal Engine

A production-grade, institutional trading intelligence platform for 24/7 market scanning and confluence-based signal generation.

## 🚀 Getting Started

### 1. Prerequisites
- Docker & Docker Compose
- Telegram Bot Token (from @BotFather)
- Binance API Keys (Optional for scanning, required for private data)

### 2. Configuration
1. Clone the repository.
2. Copy `.env.example` to `.env`.
3. Fill in your `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.

### 3. Launching the System
```bash
docker-compose up --build
```

The system will start:
- **Backend:** `http://localhost:8000`
- **Frontend:** `http://localhost:3000`
- **PostgreSQL:** `localhost:5432`
- **Redis:** `localhost:6379`

## 🛠 Tech Stack
- **Backend:** FastAPI, CCXT, Pandas-TA, SQLAlchemy, Redis.
- **Frontend:** Next.js 14, Tailwind CSS, Framer Motion, Lucide React.
- **Infrastructure:** Docker, PostgreSQL, Redis.

## 📈 Market Logic
The system uses a sophisticated **Confluence Engine**:
1. **Market Structure:** Detects BOS (Break of Structure) and CHoCH (Change of Character) on multiple timeframes.
2. **Liquidity Sweeps:** Identifies institutional stop hunts and wick rejections.
3. **Volume Expansion:** Confirms signals with high-volume relative to average.
4. **Momentum:** Uses RSI and displacement filters.
5. **Risk Management:** Automatic ATR-based Stop Loss and multiple Take Profit targets.

## 🤖 Signal Format
Signals are sent to Telegram with:
- Pair & Direction
- Entry, SL, and TP targets
- Risk/Reward Ratio
- Confidence Score (0-100%)
- Confluence Reasoning

## 📂 Project Structure
- `/backend`: FastAPI core, signal logic, and background scanners.
- `/frontend`: Next.js premium dashboard.
- `docker-compose.yml`: Orchestration for all services.
