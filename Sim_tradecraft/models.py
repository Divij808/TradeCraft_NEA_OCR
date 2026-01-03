import json
import os
import re
from string import (digits, ascii_lowercase, ascii_uppercase)

base_directory = os.path.dirname(os.path.abspath(__file__))

# Find companies.json file
candidates = [
    os.path.join(base_directory, "data", "companies.json"),
    os.path.join(base_directory, "data", "Companies.json"),
    os.path.join(base_directory, "Companies.json"),
    os.path.join(base_directory, "companies.json"),
]
companies_file = None
for c in candidates:
    if os.path.exists(c):
        companies_file = c
        break

if not companies_file:
    raise FileNotFoundError("companies.json not found")

with open(companies_file, "r") as f:
    raw_companies = json.load(f)

# Normalize
COMPANIES = {}
for c in raw_companies:
    symbol = c.get("symbol")
    if not symbol:
        continue
    COMPANIES[symbol] = {
        "symbol": symbol,
        "title": c.get("name", symbol),
        "logo": c.get("image", ""),
    }


def list_companies():
    return list(COMPANIES.values())

def company_image(symbol):
    with open("Companies.json", "r") as f:
        companies = json.load(f)

    image = next(
        (c["image"] for c in companies if c["symbol"] == symbol),
        None
    )
    return image


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength.
    Returns True if valid, False if invalid.
    """
    password = password.strip()
    password_length = len(password)

    # Check length (between 8 and 20 characters)
    if password_length < 8 or password_length > 20:
        return False

    # Check for at least one valid symbol
    validated_chars = {'-', '_', '.', '!', '@', '#', '$', '^', '&', '(', ')'}
    if not any(character in validated_chars for character in password):
        return False

    # Check for at least one digit
    if not any(character in digits for character in password):
        return False

    # Check for at least one lowercase letter
    if not any(character in ascii_lowercase for character in password):
        return False

    # Check for at least one uppercase letter
    if not any(char in ascii_uppercase for char in password):
        return False

    return True
