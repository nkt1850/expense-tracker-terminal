# Expense Tracker (Terminal + LLM)

Track expenses via terminal using a local LLM (LM Studio).

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup LM Studio**:
   - Open LM Studio app
   - Download a model (e.g., Qwen3, Llama 3.2)
   - Click "Start Server" (local HTTP server at port 1234)

## Running

```bash
python -m bot.cli
```

## Usage

Type naturally to add expenses/income:

```
→ Spent $50 on lunch
→ Got $100 from freelance yesterday
→ Paid $200 for bills
→ Show my expenses
→ What's my balance?
→ help
```

## Project Structure

```
expense-tracker-terminal/
├── bot/
│   ├── cli.py          # Terminal interface
│   ├── llm_client.py  # LM Studio API client
│   └── database.py    # SQLite operations
├── app/
│   ├── app.py         # Streamlit dashboard
│   └── queries.py    # DB queries
├── data/
│   └── expenses.db   # SQLite database
└── requirements.txt
```

## Using Streamlit Dashboard

```bash
streamlit run app/app.py
```

The app will be at http://localhost:8501