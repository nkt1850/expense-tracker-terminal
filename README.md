# Expense Tracker

Discord bot for recording expenses and income, with Streamlit dashboard.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Discord bot token:
```bash
cp .env.example .env
# Edit .env and add your bot token
```

3. Get a Discord bot token:
   - Go to https://discord.com/developers/applications
   - Create an application
   - Go to Bot -> Reset Token
   - Go to OAuth2 -> URL Generator
   - Select scope: `bot`
   - Select permissions: `Send Messages`, `Read Message History`, `Use Slash Commands`
   - Use the generated URL to invite the bot to your server

## Running

### Discord Bot
```bash
cd expense-tracker
python -m bot.main
```

### Streamlit App
```bash
cd expense-tracker
streamlit run app/app.py
```

The app will be available at http://localhost:8501

## Usage

### Discord Commands

- **Add expense**: `@bot spent $50 on lunch`
- **Add income**: `@bot received $100 from freelance`
- **List transactions**: `/list`
- **Add category**: `/add-category Grocery`
- **List categories**: `/categories`
- **Remove category**: `/remove-category Other`
- **Summary**: `/summary`

### Streamlit App

Navigate through tabs:
- Dashboard: Overview with pie charts
- Trends: Line charts and monthly trends
- Categories: Bar charts by category
- Transactions: Filterable table
- Export: Download CSV

## Project Structure

```
expense-tracker/
├── bot/
│   ├── main.py         # Bot entry point
│   ├── cog.py           # Commands
│   ├── parser.py       # NLP parser
│   ├── database.py    # DB operations
│   └── config.py      # Configuration
├── app/
│   ├── app.py         # Streamlit app
│   └── queries.py     # DB queries
├── data/
│   └── expenses.db    # SQLite database
├── requirements.txt
└── .env
```