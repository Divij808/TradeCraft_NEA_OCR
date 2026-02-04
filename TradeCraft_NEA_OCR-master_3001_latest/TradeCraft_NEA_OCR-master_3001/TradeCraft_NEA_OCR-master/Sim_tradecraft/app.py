# Main project file for TradeCraft.
# Imports
import datetime
import sqlite3

import yfinance

from models import COMPANIES, validate_password, validate_email, company_image

from flask import Flask, render_template, session, redirect, url_for, jsonify, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
# Custom module used to create and initialize the database.
from create_db import create_db
from news_fetcher import (
    fetch_stock_news,
    fetch_all_stocks_news,
    load_companies_from_json,
    get_stock_trend)
from trade_functions import collect_cash_of_user, cash_update, recent_transactions
from verification import send_verification_email, generateOTP

# Create database and tables if they don't exist.
create_db()

# Flask setup - initialize the app once.
app = Flask(__name__)
app.secret_key = 'your_secret_key'


# ------------------- Routes ------------------- #
# Home Route
@app.route('/')
def home():
    # Render the email check page as the landing screen.
    return render_template('check_email.html')


# Email Route
@app.route('/email', methods=['GET', 'POST'])
def email():
    # Handle email submission and OTP delivery.
    if request.method == 'POST':
        # Get email from form
        email_entered: str = request.form.get('email', '').strip()

        # Check if email is empty BEFORE database query
        if not email_entered:
            flash("Please enter an email address.", "error")
            return redirect(url_for('email'))

        # Query to check if email exists in database
        with sqlite3.connect('tradecrafts.db') as conn:
            cursor = conn.cursor()
            result = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        # Check if email exists in database
        if result is None:

            flash("Email not found. Please sign up.", "error")
            return redirect(url_for('signup'))
        else:
            # Email exists, generate OTP and send verification email
            OTP = str(generateOTP())
            # Compose email message
            message = """\
            Subject: TradeCraft_Login

            Paste this into the browser to login to TradeCraft.io http://127.0.0.1:5000/login

            verification code: """ + OTP + "\n\nThis code is valid for 5 minutes."
            # Send verification email
            send_verification_email(email, message)
            # Update OTP in the database
            try:
                # Update OTP in the database
                with sqlite3.connect('tradecraft.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE users SET code_of_verification = ? WHERE email = ?",
                        (OTP, email)
                    )

                    conn.commit()
            # Handle database errors
            except sqlite3.Error as e:
                # Log the error
                print("Database error:", e)
            # Notify user to check their email
            flash("Check your email for verification link and code of verification.", "success")
    # Render the email check page
    return render_template('check_email.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
# Login route to handle user authentication
# Handles both GET and POST requests
def login():
    # Process login form submission
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username', '').strip()
        password_input = request.form.get('password', '')
        email_input = request.form.get('email', '').strip()
        verification_code_input = str(request.form.get('v-code', '').strip())
        # Query database for user information
        with sqlite3.connect('tradecrafts.db') as conn:

            cursor = conn.cursor()
            result = cursor.execute(
                "SELECT id, password_hash, email, verification_code FROM users WHERE username = ?",
                (username,)
            ).fetchone()
        # Validate user credentials
        if result and check_password_hash(result[1], password_input) and email_input == result[
            2] and verification_code_input == result[3]:
            # Successful login, set session variables
            session['user_id'] = result[0]
            session['username'] = username
            session['email'] = email_input
            session['v-code'] = result[3]
            #  Redirect to news page after successful login
            flash("Login successful!", "success")
            return redirect(url_for('news'))
        # Invalid credentials, redirect back to login page
        else:

            flash("Invalid credentials", "error")
            return redirect(url_for('login'))
    # Render login page for GET requests
    return render_template('login.html')

#
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email_entered = request.form.get('email', '').strip()

        # Validate inputs
        if not username or not password or not email_entered:
            flash('All fields are required.', "error")
            return redirect(url_for('signup'))

        # Validate email format
        if not validate_email(email_entered):
            flash('Invalid email format.', "error")
            return redirect(url_for('signup'))

        # Validate password strength
        if not validate_password(password):
            flash('Password does not meet requirements.', "error")
            return redirect(url_for('signup'))

        try:
            with sqlite3.connect('tradecrafts.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users(username, password_hash, email, cash) VALUES (?, ?, ?, ?)',
                    (username, generate_password_hash(password), email_entered, 10000.0)
                )
                conn.commit()
                flash('Account created. You can now log in.', "success")
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', "error")
            return redirect(url_for('signup'))

    return render_template('signup.html')


@app.route('/settings', methods=['GET', 'POST'])
def Settings():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    return render_template('Settings.html')


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email_entered = request.form.get('email', '').strip()
        new_password = request.form.get('password', '')

        # Validate inputs
        if not email_entered or not new_password:
            flash('All fields are required.', "error")
            return redirect(url_for('forgot'))

        # Validate email format
        if not validate_email(email_entered):
            flash('Invalid email format.', "error")
            return redirect(url_for('forgot'))

        # Validate password strength
        if not validate_password(new_password):
            flash('Password does not meet requirements.', "error")
            return redirect(url_for('forgot'))

        try:
            with sqlite3.connect('tradecrafts.db') as conn:
                cursor = conn.cursor()

                # Check if email exists
                result = cursor.execute('SELECT id FROM users WHERE email = ?', (email_entered,)).fetchone()

                if result is None:
                    flash('Email not found. Please check and try again.', "error")
                    return redirect(url_for('forgot'))

                # Update password
                new_password_hash = generate_password_hash(new_password)
                cursor.execute(
                    'UPDATE users SET password_hash = ? WHERE email = ?',
                    (new_password_hash, email_entered)
                )
                conn.commit()

                flash('Password reset successful! You can now log in with your new password.', "success")
                return redirect(url_for('home'))  # Redirects to check_email page

        except sqlite3.Error as e:
            flash(f"A database error occurred: {e}", "error")
            return redirect(url_for('forgot'))

    return render_template('forgot_password.html')


# Trade route
@app.route('/trading', methods=['GET', 'POST'])
def trade():
    # Ensure user is logged in
    if 'user_identification' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))

    # Handle form submission
    if request.method == 'POST':
        symbol_entered = (request.form.get('symbol') or '').upper().strip()
        side = (request.form.get('side') or 'BUY').upper()
        quantity_entered = int(request.form.get('qty') or '0')

        message = cash_update(quantity_entered, session['user_id'], side, symbol_entered)
        flash(message)
    # Fetch transactions for the logged-in user
    transactions = recent_transactions(session['user_id'])
    # Display transaction history

    headings = ("ID", "User ID", "Symbol", "Quantity", "Side", "Price", "Timestamp")

    return render_template('trade.html', headings=headings, data=transactions, current_price=transactions['live_price'])


# NEW: API endpoint to get stock price
@app.route('/api/stock-price/<symbol>')
def get_stock_price(symbol):
    """API endpoint to fetch current stock price for a given symbol"""
    try:
        # Normalize the symbol
        symbol = symbol.upper().strip()

        # Validate symbol
        if symbol not in COMPANIES:
            return jsonify({
                'success': False,
                'error': 'Invalid stock symbol'
            }), 404

        # Update prices and fetch the live price

        price = yfinance.Ticker(symbol).info.get('currentPrice')

        if price is not None:
            return jsonify({
                'success': True,
                'symbol': symbol,
                'price': float(price)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Price not available'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/Portfolio', methods=['GET'])
def portfolio():
    # Ensure user is logged in
    cost = 0.0
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Fetch transactions for the logged-in user
    totals = {}
    with sqlite3.connect('tradecraft.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT symbol, qty, side FROM transactions WHERE user_id= ?", (user_id,))
        rows = cursor.fetchall()

    # Calculate net holdings per symbol
    for row in rows:
        symbol = (row['symbol'] or '').upper().strip()
        try:
            qty = int(row['qty'])
        except Exception:
            continue
        side = (row['side'] or 'BUY').upper().strip()
        live_price = yfinance.Ticker(symbol).info.get('currentPrice')
        if side == 'BUY':
            cost = (qty * live_price(symbol)) + cost
            totals[symbol] = totals.get(symbol, 0) + qty
        elif side == 'SELL':
            totals[symbol] = totals.get(symbol, 0) - qty
            cost = (qty * live_price(symbol)) - cost

    # Build portfolio items and compute net worth
    holdings = []
    stock_value = 0.0
    for symbol, qty in totals.items():
        if qty <= 0:
            continue
        price = yfinance.Ticker(symbol).info.get('currentPrice')
        if price is None:
            continue
        company = COMPANIES.get(symbol, {})
        title = company.get('title', symbol)
        logo = company.get('logo', '')
        description = f"{symbol} = {qty} shares"
        holdings.append({
            "title": title,
            "description": description,
            "logo": logo,
            "symbol": symbol,
            "qty": qty,
            "live_price": price
        })
        stock_value += price * qty

    # Get user's cash balance
    cash = 0.0
    with sqlite3.connect('tradecraft.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT cash FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if result and result['cash'] is not None:
            cash = float(result['cash'])

    total_net_worth = (cash + stock_value) - cost

    return render_template(
        "portfolio.html",
        Stock=holdings,
        account_balance=f"{cash:,.2f}",
        stock_value=f"{stock_value:,.2f}",
        net_worth=f"{total_net_worth:,.2f}"
    )


# News Page Route
@app.route('/News')
def news():
    """Display news page - requires login"""
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))

    return render_template('news.html')


# API: Get symbols
@app.route("/api/symbols")
def get_symbols():
    symbols = load_companies_from_json()
    return jsonify({"symbols": symbols})


# API: Get news
@app.route("/api/news")
def get_news():
    symbol = request.args.get("symbol")
    per_page = int(request.args.get("per_page", 20))

    if symbol:
        news = fetch_stock_news(symbol, per_page)
    else:
        symbols = load_companies_from_json()
        news = fetch_all_stocks_news(symbols, articles_per_stock=3)

    # Enrich data for frontend
    for article in news:
        trend = get_stock_trend(article["symbol"])
        article["trend"] = trend
        article["trend_icon"] = {
            "up": "📈",
            "down": "📉",
            "neutral": "➡️"
        }[trend]
        live_price = yfinance.Ticker(symbol).info.get('currentPrice')
        # Fetch live price for the stock
        article["live_price"] = live_price(article["symbol"])
        # fetching and dispalying the logo of the stock
        article["logo"] = (
            company_image(article["symbol"])
        )

    return jsonify({"news": news})


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


@app.get('/api/quote')
def api_quote():
    symbols = (request.args.get('symbols') or '').upper().replace(' ', '')
    live_price = yfinance.Ticker(symbols).info.get('currentPrice')
    out = {}
    for s in symbols.split(','):
        if not s:
            continue
        p = live_price(s)
        if p is not None:
            out[s] = {'symbol': s, 'price': p, 'ts': datetime.datetime.now(datetime.timezone.utc).isoformat() + 'Z'}
    return jsonify({'quotes': out})


@app.route('/rules')
def rules():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    return render_template('rules.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Ensure user is logged in
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        # Determine which form was submitted using the 'action' hidden field
        action_type = request.form.get('action')

        try:
            with sqlite3.connect('tradecrafts.db') as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                if action_type == 'update_username':
                    new_username = request.form.get('new-username', '').strip()
                    if new_username and 3 <= len(new_username) <= 24:
                        cursor.execute("UPDATE users SET username = ? WHERE id = ?",
                                       (new_username, user_id))
                        if cursor.rowcount > 0:
                            conn.commit()
                            session['username'] = new_username
                            flash('Username updated successfully!', 'success')
                        else:
                            flash('User record not found.', 'error')
                    else:
                        flash('Username must be between 3 and 24 characters.', 'error')

                elif action_type == 'update_password':
                    current_password = request.form.get('current-password', '')
                    new_password = request.form.get('new-password', '')

                    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
                    user_record = cursor.fetchone()

                    if user_record and check_password_hash(user_record['password_hash'], current_password):
                        if validate_password(new_password):
                            new_password_hash = generate_password_hash(new_password)
                            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                                           (new_password_hash, user_id))
                            conn.commit()
                            flash('Password updated successfully!', 'success')
                        else:
                            flash('New password does not meet complexity requirements.', 'error')
                    else:
                        flash('Incorrect current password.', 'error')

                elif action_type == 'delete_account':
                    # Delete user transactions first to maintain referential integrity
                    cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
                    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                    if cursor.rowcount > 0:
                        conn.commit()
                        session.clear()
                        flash('Account deleted successfully.', 'info')
                        return redirect(url_for('home'))
                    else:
                        flash('Failed to delete account.', 'error')

                elif action_type == 'update_email':
                    new_email = request.form.get('new-email', '').strip()
                    if new_email and validate_email(new_email):
                        cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
                        if cursor.rowcount > 0:
                            conn.commit()
                            session['email'] = new_email
                            flash('Email updated successfully!', 'success')
                        else:
                            flash('User record not found.', 'error')
                    else:
                        flash('Invalid email format.', 'error')

                else:
                    flash('Invalid action submitted.', 'error')

        except sqlite3.IntegrityError:
            flash('A user with that username or email already exists.', 'error')
        except sqlite3.Error as e:
            flash(f"A database error occurred: {e}", "error")

        return redirect(url_for('profile'))

    # Handle GET request - fetch current user data
    with sqlite3.connect('tradecraft.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT username, email FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()

    username = user_data['username'] if user_data else session.get('username')
    email = user_data['email'] if user_data else session.get('email')

    return render_template('user_info.html', username=username, email=email)


# ONLY ONE if __name__ == '__main__' block at the end
if __name__ == '__main__':
    app.run(debug=True)
