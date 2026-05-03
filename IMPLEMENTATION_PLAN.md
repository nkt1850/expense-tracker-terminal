# Expense Tracker - Implementation Plan

## Project Overview

A local expense tracking system with:
- **Input:** CLI + LLM (LM Studio) for natural language expense entry
- **Storage:** SQLite database
- **Dashboard:** Streamlit web app
- **Mobile:** iOS Swift app (future phase)

---

## Current Architecture

```
┌──────────────┐     ┌──────────────┐     ┌─────────────┐
│ CLI (LLM)   │────▶│ SQLite DB  │◀────│ Streamlit │
│ Terminal    │     │            │     │ Dashboard│
└──────────────┘     └──────────────┘     └─────────────┘
```

---

## Future Phase: iOS Mobile App

### Architecture

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│ iPhone    │────▶│  Python API   │────▶│ SQLite DB │
│ (Swift)   │     │  Server      │     │          │
│ App       │     │  (Flask)    │     │          │
└───────────┘     └──────┬──────┘     └─────────────┘
                          │
                    ┌─────▼─────┐
                    │ Streamlit │
                    │ (Web)   │
                    └─────────┘
```

### Components Needed

1. **Python API Server (Flask/FastAPI)**
   - POST `/transactions` - Add expense/income
   - GET `/transactions` - List with filters
   - GET `/summary` - Totals
   - GET `/categories` - Category list
   - POST `/categories` - Add/remove category

2. **LM Studio Configuration**
   - Enable "Serve on Local Network" (bind to 0.0.0.0)
   - Or use LM Mini Connect relay for remote

3. **iOS Swift App**
   - Screen 1: Add expense (natural language input)
   - Screen 2: Dashboard (charts via SwiftUI Charts or WebView)
   - Call LLM for parsing (same system prompt as CLI)

4. **Streamlit Updates**
   - Update to use API server instead of direct SQLite

### Network Options

| Option | Pros | Cons |
|--------|------|------|
| Local WiFi only | Simple, no relay | Must be on same network |
| LM Mini Connect | Works anywhere | Extra app to install |
| Tailscale/LM Link | Secure, company features | More setup |

---

## Implementation Roadmap

### Phase 1: Current (Done)
- [x] CLI with LLM integration
- [x] SQLite database
- [x] Streamlit dashboard
- [x] VND currency support

### Phase 2: Mobile (Planned)
- [ ] Python API server
- [ ] LM Studio LAN configuration
- [ ] iOS Swift app
- [ ] Streamlit via API

---

## Technical Details

### Database Schema

```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    transaction_type TEXT CHECK(transaction_type IN ('expense', 'income')),
    category TEXT NOT NULL,
    description TEXT,
    amount REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Default Categories
Food, Transport, Entertainment, Shopping, Bills, Salary, Freelance, Other

### Currency
VND (Vietnamese Dong)
- "50K" = 50,000 VND
- "1M" = 1,000,000 VND

### LLM System Prompt
See `bot/llm_client.py` for the expense parsing prompt.

---

## File Structure

```
expense-tracker-terminal/
├── bot/
│   ├── cli.py              # Terminal interface
│   ├── llm_client.py      # LM Studio API client
│   └── database.py        # SQLite operations
├── app/
│   ├── app.py            # Streamlit dashboard
│   └── queries.py       # DB queries
├── data/
│   └── expenses.db     # SQLite database
├── requirements.txt
└── README.md
```

---

## Running the App

### CLI (Terminal + LLM)
```bash
cd ~/Desktop/expense-tracker-terminal
source venv/bin/activate
python -m bot.cli
```

### Streamlit Dashboard
```bash
streamlit run app/app.py
```

### LM Studio
- Open LM Studio app
- Load model (Qwen3 recommended)
- Start Server (Developer tab)# iOS Mobile Implementation
