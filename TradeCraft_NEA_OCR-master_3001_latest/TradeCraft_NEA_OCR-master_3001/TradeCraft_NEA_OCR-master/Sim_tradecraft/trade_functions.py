import datetime
import sqlite3
import yfinance


# Database functions for managing the users cash
# Retrieve the cash amount for a specific user
def collect_cash_of_user(user_identifier):
    # Connect to the SQLite database
    connection = sqlite3.connect('tradecraft.db')
    cash_fetched = connection.execute(
        'SELECT cash FROM users WHERE id=?', (user_identifier,)
    ).fetchone()
    # Check if no cash found for the user
    if cash_fetched is None:
        # User does not exist or no cash record found
        return 0.0
    # sqlite3.Row supports dict-style access
    else:
        # Return the cash as a float
        return float(cash_fetched['cash'])


# Update the cash amount for a specific user
def setting_the_user_cash(new_cash, user_identifier):
    # Connect to the SQLite database
    connection = sqlite3.connect('tradecraft.db')
    # Update the cash value for the user
    connection.execute('UPDATE users SET cash=? WHERE id=?', (round(new_cash, 2), user_identifier))
    connection.commit()


# Function to calculate the total quantity of a specific stock owned by a user
def amount_of_quantity_owned(symbol, user_identifier):
    # Connect to the SQLite database
    with sqlite3.connect('tradecraft.db') as connection:
        cursor = connection.cursor()
        # Execute SQL query to calculate the total quantity owned
        cursor.execute(
            """
            SELECT COALESCE(
                SUM(CASE 
                    WHEN side = 'BUY' THEN qty 
                    ELSE -qty 
                END),
                0
            )
            FROM transactions
            WHERE user_id = ? AND symbol = ?
            """,
            (user_identifier, symbol)
        )
        # Fetch the result
        owned_quantity = cursor.fetchone()[0]
        return owned_quantity

# Function to record a transaction in the database
def record_transaction(user_identifier, symbol_entered, qty, side):
    # Get the current price of the stock
    price_found = yfinance.Ticker(symbol_entered).info.get('currentPrice')
    local_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with sqlite3.connect('tradecraft.db') as connection:
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO transactions(user_id, symbol, qty, side, price, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
            (user_identifier, symbol_entered, qty, side.upper(), price_found, local_time)
        )
        connection.commit()


def cash_update(user_identifier, side, symbol_entered, qty):
    price_found = yfinance.Ticker(symbol_entered).info.get('currentPrice')
    owned_quantity = amount_of_quantity_owned(symbol_entered, user_identifier)
    if side.lower() == "sell":
        if qty <= 0:
            return "Enter a valid number of shares."
        elif qty > 0:
            if symbol_entered is None:
                return "Invalid stock symbol. If you are 100% sure you symbol is valid! There may be a technical issue on our side. Try after a minute again"
            elif symbol_entered is not None:
                if price_found is None:
                    return "Invalid stock symbol. If you are 100% sure you symbol is valid! There may be a technical issue on our side. Try after a minute again"
            elif owned_quantity < qty:
                return "You do not own enough shares to sell."

            else:
                current_cash_via_database = collect_cash_of_user(user_identifier)
                new_cash = current_cash_via_database + price_found * qty
                setting_the_user_cash(new_cash, user_identifier)
                record_transaction(user_identifier, symbol_entered, qty, side)
                return "Success"

    elif side.lower() == "buy":

        current_cash_via_database = collect_cash_of_user(user_identifier)
        if price_found is None:
            return "Invalid stock symbol. If you are 100% sure you symbol is valid! There may be a technical issue on our side. Try after a minute again"
        if current_cash_via_database < (price_found * qty):
            return "Insufficient funds."
        elif price_found * qty <= current_cash_via_database:
            new_cash = current_cash_via_database - price_found * qty
            setting_the_user_cash(new_cash, user_identifier)
            record_transaction(user_identifier, symbol_entered, qty, side)
            return "Success"

    return "Error occurred during cash update."


def recent_transactions(user_identifier):
    with sqlite3.connect('tradecraft.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC",
                       (user_identifier,))
        transactions = cursor.fetchall()
        return transactions
