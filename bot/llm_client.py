import requests
import json
from typing import Optional

LMSTUDIO_URL = "http://localhost:1234/v1/chat/completions"

SYSTEM_PROMPT = """You are an expense tracker assistant. Your job is to parse user natural language input about expenses or income and extract structured information.

Categories: Food, Transport, Entertainment, Shopping, Bills, Salary, Freelance, Other

Currency: VND (Vietnamese Dong) - always use VND, not USD

Rules:
- Amount must be positive number in VND
- If no date is given, use today's date (2026-05-03)
- If user says "yesterday", use 2026-05-02
- Description max 30 words
- Determine transaction type (expense/income) from context
- Parse input amounts as VND (e.g., "50K" = 50000, "100K" = 100000, "1M" = 1000000)

Response format (JSON only):
{
  "action": "add" or "list" or "categories" or "summary" or "help" or "unknown",
  "transaction_type": "expense" or "income" or null,
  "amount": number or null,
  "category": string or null,
  "description": string or null,
  "date": "YYYY-MM-DD" or null,
  "message": string or null (for help/acknowledgment)
}

Examples:
- "Spent 50K on lunch" → {"action": "add", "transaction_type": "expense", "amount": 50000, "category": null, "description": "lunch", "date": "2026-05-03"}
- "Paid 100K for food" → {"action": "add", "transaction_type": "expense", "amount": 100000, "category": "Food", "description": "", "date": "2026-05-03"}
- "Got 1M from freelance yesterday" → {"action": "add", "transaction_type": "income", "amount": 1000000, "category": "Freelance", "description": "", "date": "2026-05-02"}
- "Got salary 5M" → {"action": "add", "transaction_type": "income", "amount": 5000000, "category": "Salary", "description": "", "date": "2026-05-03"}
- "Show my expenses" → {"action": "list", "transaction_type": "expense", "amount": null, "category": null, "description": null, "date": null}
- "What's my balance?" → {"action": "summary", "transaction_type": null, "amount": null, "category": null, "description": null, "date": null}
- "How do I use this?" → {"action": "help", "transaction_type": null, "amount": null, "category": null, "description": null, "date": null}
"""

def call_llm(user_message: str) -> Optional[dict]:
    try:
        response = requests.post(
            LMSTUDIO_URL,
            json={
                "model": "local-model",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.1,
                "max_tokens": 500
            },
            timeout=120
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        
        return None
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return None

def is_server_running() -> bool:
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=2)
        return response.status_code == 200
    except:
        return False