#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.database import (
    init_database,
    add_transaction,
    get_transactions,
    get_categories,
    add_category,
    remove_category,
    get_summary,
    get_category_totals,
)
from bot.llm_client import call_llm, is_server_running

def print_header():
    print("\n" + "="*50)
    print("💰 EXPENSE TRACKER (Terminal + LLM)")
    print("Currency: VND (Vietnamese Dong)")
    print("="*50)

def print_help():
    print("""
Commands:
  • Add expense/income: "Spent 50K on lunch" or "Got 100K from freelance"
  • List transactions: "Show my expenses" or "list transactions"
  • Show balance: "What's my balance?"
  • Manage categories: "add category X" or "remove category X"
  • Help: "help"

Examples:
  → Spent 25K on groceries yesterday
  → Got 500K from salary
  → Paid 100K for bills
  → Show my spending this month
""")

def format_currency(value):
    return f"{value:,.0f} VND"

def display_transactions(transactions, title="Transactions"):
    if not transactions:
        print("No transactions found.")
        return
    
    print(f"\n{title}:")
    print("-" * 60)
    for t in transactions:
        emoji = "📈" if t["transaction_type"] == "income" else "📉"
        desc = t["description"] or ""
        print(f"{emoji} {t['date']} | {t['category']:15} | {format_currency(t['amount']):>10} | {desc[:20]}")

def display_summary():
    summary = get_summary()
    print(f"\n📊 SUMMARY")
    print("-" * 40)
    print(f"  Total Income:  {format_currency(summary['total_income'])}")
    print(f"  Total Expense: {format_currency(summary['total_expense'])}")
    print(f"  Balance:     {format_currency(summary['balance'])}")

def display_categories():
    categories = get_categories()
    print(f"\n📁 CATEGORIES: {', '.join(categories)}")

def handle_add(parsed, categories):
    if not parsed.get("amount"):
        return "I couldn't detect an amount. Try: Spent 50K on lunch"
    
    transaction_type = parsed.get("transaction_type", "expense")
    amount = parsed.get("amount")
    category = parsed.get("category")
    description = parsed.get("description", "")
    date = parsed.get("date", "2026-05-03")
    
    if not category:
        cat_list = ", ".join(categories)
        return f"What category? (choose from: {cat_list})"
    
    if category not in categories:
        cat_list = ", ".join(categories)
        return f"Category '{category}' not found. Choose from: {cat_list}"
    
    add_transaction(date, transaction_type, category, description, amount)
    return f"✅ Added {transaction_type}: {format_currency(amount)} for {category} on {date}"

def main():
    init_database()
    
    if not is_server_running():
        print("❌ LM Studio server not running.")
        print("Please start LM Studio, load the Qwen3 model, and click 'Start Server'")
        print("The server should be at http://localhost:1234")
        sys.exit(1)
    
    print_header()
    print("Type your expense/income or 'help' for commands.")
    print("Type 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye! 👋")
                break
            
            parsed = call_llm(user_input)
            
            if not parsed:
                print("Bot: Sorry, I couldn't process that. Try again.")
                continue
            
            action = parsed.get("action")
            categories = get_categories()
            
            if action == "add":
                msg = handle_add(parsed, categories)
                print(f"Bot: {msg}")
                
            elif action == "list":
                t_type = parsed.get("transaction_type")
                transactions = get_transactions(limit=20, transaction_type=t_type)
                display_transactions(transactions, f"{t_type.capitalize() if t_type else 'All'} Transactions")
                
            elif action == "summary":
                display_summary()
                
            elif action == "categories":
                display_categories()
                
            elif action == "help":
                print_help()
                
            else:
                print(f"Bot: {parsed.get('message', 'Unknown command. Type help for usage.')}")
        
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()