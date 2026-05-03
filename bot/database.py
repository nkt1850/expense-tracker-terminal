import sqlite3
import os
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "expenses.db"

def get_connection():
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            transaction_type TEXT NOT NULL CHECK(transaction_type IN ('expense', 'income')),
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    
    DEFAULT_CATEGORIES = [
        "Food", "Transport", "Entertainment", "Shopping", 
        "Bills", "Salary", "Freelance", "Other"
    ]
    for cat in DEFAULT_CATEGORIES:
        try:
            c.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

def add_transaction(date: str, transaction_type: str, category: str, description: str, amount: float):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO transactions (date, transaction_type, category, description, amount)
        VALUES (?, ?, ?, ?, ?)
    """, (date, transaction_type, category, description, amount))
    conn.commit()
    conn.close()

def get_transactions(limit: int = 100, transaction_type: str = None, category: str = None):
    conn = get_connection()
    c = conn.cursor()
    
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    
    if transaction_type:
        query += " AND transaction_type = ?"
        params.append(transaction_type)
    if category:
        query += " AND category = ?"
        params.append(category)
    
    query += " ORDER BY date DESC, id DESC LIMIT ?"
    params.append(limit)
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_categories():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM categories ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def add_category(name: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def remove_category(name: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM categories WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def get_summary():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT 
            SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END) as total_expense
        FROM transactions
    """)
    row = c.fetchone()
    conn.close()
    return {
        "total_income": row["total_income"] or 0,
        "total_expense": row["total_expense"] or 0,
        "balance": (row["total_income"] or 0) - (row["total_expense"] or 0)
    }

def get_category_totals():
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