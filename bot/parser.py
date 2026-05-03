import re
from datetime import datetime
from typing import Optional, Tuple, List

def parse_expense_message(message: str) -> Optional[dict]:
    message = message.strip().lower()
    
    patterns = [
        r"(?:spent|spent\s+)?\$?(\d+(?:\.\d{1,2})?)\s*(?:on|for)\s+(.+?)(?:\s+yesterday|\s+last\s+day)?$",
        r"(?:spent|spent\s+)?\$?(\d+(?:\.\d{1,2})?)\s+(?:on|for)\s+(.+?)(?:\s+yesterday|\s+last\s+day)?$",
        r"(?:bought|paid|purchased)\s+(?:for\s+)?\$?(\d+(?:\.\d{1,2})?)\s*(?:on\s+)?(.+?)(?:\s+yesterday)?$",
        r"\$?(\d+(?:\.\d{1,2})?)\s*(?:on|for)\s+(.+)",
        r"(?:spent|paid|bought)\s+(.+?)\s+\$?(\d+(?:\.\d{1,2})?)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            amount = float(match.group(1))
            rest = match.group(2).strip() if match.lastindex >= 2 else ""
            return {
                "amount": amount,
                "raw_text": rest,
                "transaction_type": "expense"
            }
    
    income_patterns = [
        r"(?:received|got|earned|made)\s+(?:\$\d+(?:\.\d{1,2})?|(\d+(?:\.\d{1,2})?))\s*(?:from|with|through)?\s*(.*)",
        r"(?:salary|freelance|wage|payment)\s+(?:of\s+)?\$?(\d+(?:\.\d{1,2})?)",
        r"\$?(\d+(?:\.\d{1,2})?)\s*(?:income|earning|salary)",
    ]
    
    for pattern in income_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            amount = float(match.group(1))
            rest = match.group(2).strip() if match.lastindex >= 2 else ""
            return {
                "amount": amount,
                "raw_text": rest,
                "transaction_type": "income"
            }
    
    return None

def extract_category_and_description(raw_text: str, available_categories: List[str]) -> Tuple[Optional[str], Optional[str]]:
    if not raw_text:
        return None, None
    
    raw_lower = raw_text.lower()
    
    best_category = None
    best_match_len = 0
    
    for cat in available_categories:
        cat_lower = cat.lower()
        if cat_lower in raw_lower:
            start_idx = raw_lower.find(cat_lower)
            match_len = len(cat_lower)
            if match_len > best_match_len:
                best_category = cat
                best_match_len = match_len
    
    if best_category:
        cat_idx = [c.lower() for c in available_categories].index(best_category.lower())
        description = raw_lower.replace(available_categories[cat_idx].lower(), "").strip()
        description = re.sub(r'\s+', ' ', description).strip()
        return best_category, description if description else None
    
    words = raw_text.split()
    description = " ".join(words[:10]) if words else None
    return None, description

def extract_date(message: str) -> Tuple[str, str]:
    today = datetime.now().strftime("%Y-%m-%d")
    
    message_lower = message.lower()
    
    if "yesterday" in message_lower:
        from datetime import timedelta
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d"), "yesterday"
    
    date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', message)
    if date_match:
        year, month, day = date_match.groups()
        try:
            dt = datetime(int(year), int(month), int(day))
            return dt.strftime("%Y-%m-%d"), f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except ValueError:
            pass
    
    date_match = re.search(r'(\d{1,2})/(\d{1,2})(?:\s*/\s*(\d{4}))?', message)
    if date_match:
        if date_match.group(3):
            year = int(date_match.group(3))
        else:
            year = datetime.now().year
        month, day = int(date_match.group(1)), int(date_match.group(2))
        try:
            dt = datetime(year, month, day)
            return dt.strftime("%Y-%m-%d"), f"{year}-{month:02d}-{day:02d}"
        except ValueError:
            pass
    
    return today, "today"

def clean_description(description: str, max_words: int = 30) -> str:
    if not description:
        return ""
    
    words = description.split()
    if len(words) > max_words:
        words = words[:max_words]
    
    return " ".join(words)