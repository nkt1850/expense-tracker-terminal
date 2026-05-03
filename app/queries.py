import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

DB_PATH = Path(__file__).parent.parent / "data" / "expenses.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    if not DB_PATH.exists():
        from bot.database import init_database as init_db
        init_db()

def get_transactions(filters=None, limit=500):
    init_database()
    conn = get_connection()
    c = conn.cursor()
    
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    
    if filters:
        if filters.get("start_date"):
            query += " AND date >= ?"
            params.append(filters["start_date"])
        if filters.get("end_date"):
            query += " AND date <= ?"
            params.append(filters["end_date"])
        if filters.get("category"):
            query += " AND category = ?"
            params.append(filters["category"])
        if filters.get("transaction_type"):
            query += " AND transaction_type = ?"
            params.append(filters["transaction_type"])
        if filters.get("search"):
            query += " AND (description LIKE ? OR category LIKE ?)"
            search_term = f"%{filters['search']}%"
            params.extend([search_term, search_term])
    
    query += " ORDER BY date DESC, id DESC LIMIT ?"
    params.append(limit)
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_summary():
    init_database()
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""
        SELECT 
            SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END) as total_expense
        FROM transactions
    """)
    row = c.fetchone()
    
    c.execute("""
        SELECT 
            SUM(CASE WHEN transaction_type = 'income' AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now') THEN amount ELSE 0 END) as month_income,
            SUM(CASE WHEN transaction_type = 'expense' AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now') THEN amount ELSE 0 END) as month_expense
        FROM transactions
    """)
    month_row = c.fetchone()
    
    conn.close()
    
    return {
        "total_income": row["total_income"] or 0,
        "total_expense": row["total_expense"] or 0,
        "balance": (row["total_income"] or 0) - (row["total_expense"] or 0),
        "month_income": month_row["month_income"] or 0,
        "month_expense": month_row["month_expense"] or 0,
    }

def get_category_totals():
    init_database()
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""
        SELECT category, transaction_type, SUM(amount) as total
        FROM transactions
        GROUP BY category, transaction_type
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_monthly_totals():
    init_database()
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""
        SELECT strftime('%Y-%m', date) as month, transaction_type, SUM(amount) as total
        FROM transactions
        GROUP BY month, transaction_type
        ORDER BY month
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_categories():
    init_database()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM categories ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def export_csv():
    transactions = get_transactions(limit=10000)
    if not transactions:
        return ""
    
    import csv
    import io
    
    output = io.StringIO()
    fieldnames = ["id", "date", "transaction_type", "category", "description", "amount", "created_at"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for t in transactions:
        writer.writerow({k: t.get(k, "") for k in fieldnames})
    
    return output.getvalue()