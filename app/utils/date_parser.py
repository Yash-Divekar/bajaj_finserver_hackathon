import re
from dateutil import parser

def extract_month_years(text: str):
    from datetime import datetime

    # Find all substrings that look like month-year or year-month
    # Examples: Jan-24, January 2024, 01/2024, 2024-01, Jan. 2024, 1/24, etc.
    patterns = [
        r"([a-z]{3,9})[\s\-\.\/,]*(\d{2,4})",      # Jan 24, January 2024, Jan-24, Jan.2024
        r"(\d{1,2})[\s\-\.\/,]*([a-z]{3,9})[\s\-\.\/,]*(\d{2,4})",  # 1 Jan 2024, 01-Jan-24
        r"(\d{4})[\s\-\.\/,]*(\d{1,2})",           # 2024-01, 2024/1
        r"(\d{1,2})[\s\-\.\/,]*(\d{2,4})"          # 1/24, 01-2024
    ]

    matches = []
    for pat in patterns:
        matches += re.findall(pat, text, re.IGNORECASE)

    results = set()
    for m in matches:
        # Try to parse each match as a date
        try:
            # Flatten tuple and join with space for parser
            flat = " ".join(m)
            dt = parser.parse(flat, default=parser.parse("2000-01-01"))
            # Only keep if both month and year are present
            if dt.month and dt.year:
                # Format as "Jan-24"
                results.add(dt.strftime("%b-%y"))
        except Exception:
            continue

    return list(results)

def extract_date_range(text):
    date_matches = re.findall(r'\d{1,2}[-/\\]\d{1,2}[-/\\]\d{2,4}', text)
    try:
        return [parser.parse(d).date() for d in date_matches]
    except:
        return []