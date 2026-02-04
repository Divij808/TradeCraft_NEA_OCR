# create_db.py
import sqlite3


def create_db(database_name="tradecraft.db"):
    with sqlite3.connect(database_name) as connection:
        create_tradecraft_tables(connection)


def create_db_connection(connection):
    create_tradecraft_tables(connection)


def create_tradecraft_tables(connection):
    # function for creating tables

    sql_statements = [

        """CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            stock_symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            sell_or_buy TEXT NOT NULL,
            live_price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );""",
        """CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hashed TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    code_of_verification TEXT,
    cash REAL NOT NULL DEFAULT 100000.0
)"""

    ]
    cursor = connection.cursor()
    for statement in sql_statements:
        cursor.execute(statement)
    connection.commit()
