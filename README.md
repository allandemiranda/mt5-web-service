# MetaTrader 5 (MT5) Web Service

A production-grade, asynchronous Web Backend API written in Python using FastAPI, providing a complete REST API wrapper around the official **[MetaTrader 5 (MQL5) Python Integration](https://www.mql5.com/en/docs/python_metatrader5)**.

---

## Features

- **Lifecycle Integration**: MT5 connection is initialized immediately upon service startup using FastAPI lifespan context management.
- **Persistent Connection**: MT5 connection is kept persistent during the app lifecycle and only cleanly shutdown on server stop.
- **Auto-Reconnection & Health Monitor**: Continuously monitors MT5 terminal heartbeat and reconnects using exponential backoff if disconnected.
- **Centralized HTTP 503 Handling**: All MT5-dependent endpoints automatically return `HTTP 503 Service Unavailable` when the connection is down, and immediately resume `200 OK` once reconnected.
- **Thread-Safe Architecture**: MT5 C-extension calls are executed safely in worker threads without blocking FastAPI's async event loop.
- **100% MQL5 API Coverage**: Terminal, Account, Symbols, Depth of Market (DOM), Candlestick Rates (OHLCV), Ticks, Orders, Positions, Trade Calculations, and Historical Deals/Orders.
- **Interactive OpenAPI Documentation**: Auto-generated Swagger UI and ReDoc.

---

## Architecture Overview

```
Client (HTTP/REST) 
       │
       ▼
 FastAPI Router (/api/v1/*)
       │
 ┌─────┴─────────────────────────┐
 │ require_mt5_connection (503)  │
 └─────┬─────────────────────────┘
       ▼
 MT5 Service Layer (asyncio.to_thread)
       │
 ┌─────┴─────────────────────────┐
 │ MT5 Python C-Extension (IPC)  │
 └─────┬─────────────────────────┘
       ▼
 MetaTrader 5 Terminal (terminal64.exe)
```

---

## Project Structure

```
mt5-web-service/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── app/
│   ├── __init__.py
│   ├── config.py                # Pydantic Settings & environment variables
│   ├── main.py                  # FastAPI initialization & lifespan lifecycle
│   ├── core/
│   │   ├── __init__.py
│   │   ├── constants.py         # MT5 Enums & Timeframe mappings
│   │   ├── exceptions.py        # Custom exceptions and exception handlers
│   │   ├── logging.py           # Structured logging setup
│   │   └── mt5_manager.py       # Connection lifecycle, heartbeat & auto-reconnect
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py            # API response envelopes
│   │   ├── account.py           # Account schemas
│   │   ├── terminal.py          # Terminal info & version schemas
│   │   ├── symbols.py           # Symbol info & tick schemas
│   │   ├── market_book.py       # DOM depth schemas
│   │   ├── rates.py             # OHLCV rate bar schemas
│   │   ├── ticks.py             # Tick schemas
│   │   ├── orders.py            # Trade requests & result schemas
│   │   ├── positions.py         # Position schemas & close requests
│   │   └── history.py           # History query & deal schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── mt5_service.py       # Safe MT5 API execution & type serialization
│   └── api/
│       ├── __init__.py
│       ├── dependencies.py      # require_mt5_connection dependency (HTTP 503)
│       └── v1/
│           ├── __init__.py
│           ├── router.py        # Centralized v1 router
│           ├── health.py        # Health & status endpoint
│           ├── terminal.py      # Terminal info endpoints
│           ├── account.py       # Account endpoints
│           ├── symbols.py       # Symbols & tick data endpoints
│           ├── market_book.py   # DOM depth of market endpoints
│           ├── rates.py         # Historical OHLCV endpoints
│           ├── ticks.py         # Ticks history endpoints
│           ├── orders.py        # Active orders & trade dispatch
│           ├── positions.py     # Open positions & close handler
│           └── history.py       # Historical deals & orders
└── tests/
    ├── __init__.py
    ├── conftest.py              # Mock fixtures & AsyncClient test client
    └── test_health_and_reconnection.py
```

---

## Configuration & Environment Variables

Create `.env` based on `.env.example`:

```env
# Application Settings
APP_NAME="MT5 Web Service"
DEBUG=false
HOST=0.0.0.0
PORT=8000

# MT5 Terminal & Account
MT5_LOGIN=12345678
MT5_PASSWORD=YourPassword
MT5_SERVER=YourBroker-Server
# Optional custom path to terminal64.exe (leave blank for default installation)
MT5_PATH=
MT5_PORTABLE=false
MT5_TIMEOUT=60000

# Reconnection & Heartbeat
MT5_HEARTBEAT_INTERVAL=5.0
MT5_RETRY_BASE_DELAY=2.0
MT5_RETRY_MAX_DELAY=30.0
MT5_RETRY_BACKOFF_FACTOR=1.5
```

---

## Installation & Running

### Requirements
- Windows 10/11 or Windows Server (64-bit)
- Python 3.10+ (64-bit)
- MetaTrader 5 Terminal (64-bit) installed and logged in

### Setup
```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
copy .env.example .env

# 4. Start the server
python -m app.main
```

The server starts at `http://localhost:8000`.
Interactive API documentation is available at `http://localhost:8000/docs`.

---

## API Endpoints Summary

| Category | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Health** | `GET` | `/api/v1/health` | Health & connection diagnostics (Always accessible) |
| **Terminal** | `GET` | `/api/v1/terminal/version` | Terminal build and version |
| **Terminal** | `GET` | `/api/v1/terminal/info` | Terminal state & configuration |
| **Terminal** | `GET` | `/api/v1/terminal/last-error` | Last MT5 error code & message |
| **Account** | `GET` | `/api/v1/account` | Current account balances & equity |
| **Symbols** | `GET` | `/api/v1/symbols/total` | Count of available instruments |
| **Symbols** | `GET` | `/api/v1/symbols` | List symbols (with optional group filter) |
| **Symbols** | `GET` | `/api/v1/symbols/{symbol}` | Instrument specification |
| **Symbols** | `GET` | `/api/v1/symbols/{symbol}/tick` | Current tick prices |
| **Symbols** | `POST` | `/api/v1/symbols/{symbol}/select`| Select symbol in MarketWatch |
| **DOM** | `POST` | `/api/v1/market-book/{symbol}/subscribe` | Subscribe to depth of market |
| **DOM** | `GET` | `/api/v1/market-book/{symbol}` | Get current depth of market records |
| **DOM** | `DELETE`| `/api/v1/market-book/{symbol}/unsubscribe` | Unsubscribe from DOM |
| **Rates** | `GET` | `/api/v1/rates/from` | OHLCV bars starting from date |
| **Rates** | `GET` | `/api/v1/rates/from-pos` | OHLCV bars starting from index |
| **Rates** | `GET` | `/api/v1/rates/range` | OHLCV bars in date range |
| **Ticks** | `GET` | `/api/v1/ticks/from` | Ticks starting from date |
| **Ticks** | `GET` | `/api/v1/ticks/range` | Ticks in date range |
| **Orders** | `GET` | `/api/v1/orders/total` | Total active orders |
| **Orders** | `GET` | `/api/v1/orders` | List active orders |
| **Orders** | `POST` | `/api/v1/orders/check` | Validate order parameters |
| **Orders** | `POST` | `/api/v1/orders/send` | Send trade order to broker |
| **Orders** | `POST` | `/api/v1/orders/calc-margin` | Calculate required margin |
| **Orders** | `POST` | `/api/v1/orders/calc-profit` | Calculate expected profit |
| **Positions** | `GET` | `/api/v1/positions/total` | Total open positions |
| **Positions** | `GET` | `/api/v1/positions` | List open positions |
| **Positions** | `POST` | `/api/v1/positions/{ticket}/close` | Close open position by ticket |
| **History** | `GET` | `/api/v1/history/orders/total` | Total historical orders count |
| **History** | `GET` | `/api/v1/history/orders` | Historical orders |
| **History** | `GET` | `/api/v1/history/deals/total` | Total historical deals count |
| **History** | `GET` | `/api/v1/history/deals` | Historical deals |

---

## Running Automated Tests

```bash
pytest tests/ -v
```
