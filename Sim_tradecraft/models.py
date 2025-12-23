import json
import os
import random
import re
import time
from string import (punctuation, whitespace, digits, ascii_lowercase, ascii_uppercase)

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

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    errors = []
    # Validate strong password
    password = password.strip()
    password_length = len(password)
    if password_length > 8 or password_length < 20:
        errors.append('Invalid Password length. Must be between 8 and 20 characters.')

    validated_chars = {'-', '_', '.', '!', '@', '#', '$', '^', '&', '(', ')'}
    if not any(character in validated_chars for character in password):
        errors.append('Password must contain at least one valid symbol: ' + ''.join(validated_chars))

    if not any(character in digits for character in password):
        errors.append('Password must contain at least one digit.')

    if not any(character in ascii_lowercase for character in password):
        errors.append('Password must contain at least one lowercase letter.')

    if not any(char in ascii_uppercase for char in password):
        errors.append('Password must contain at least one uppercase letter.')

    return errors


