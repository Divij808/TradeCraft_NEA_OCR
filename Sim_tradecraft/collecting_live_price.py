import yfinance as yf
import feedparser
import json
from datetime import datetime
from urllib.parse import quote
import re


def get_current_price(symbol):
    """Fetch the current stock price for a given symbol"""
    try:
        ticker = yf.Ticker(symbol)
        todays_data = ticker.history(period='1d')

        if not todays_data.empty:
            return todays_data['Close'].iloc[-1]
    except Exception as e:
        print(f"Error fetching price for {symbol}: {str(e)}")
    return None


def fetch_stock_news(symbol, max_articles=5):
    """
    Fetch news for a specific stock symbol from Yahoo Finance RSS feed
    """
    try:
        rss_url = f"https://finance.yahoo.com/rss/headline?s={quote(symbol)}"
        feed = feedparser.parse(rss_url)

        articles = []
        for entry in feed.entries[:max_articles]:
            pub_date = entry.get('published', '')
            try:
                date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = pub_date

            description = entry.get('summary', 'No description available')
            description = re.sub('<[^<]+?>', '', description)

            article = {
                'title': entry.get('title', 'No title'),
                'description': description[:200] + '...' if len(description) > 200 else description,
                'link': entry.get('link', '#'),
                'date': formatted_date,
                'source': 'Yahoo Finance',
                'symbol': symbol
            }
            articles.append(article)

        return articles
    except Exception as e:
        print(f"Error fetching news for {symbol}: {str(e)}")
        return []


def fetch_all_stocks_news(symbols, articles_per_stock=3):
    """Fetch news for multiple stock symbols"""
    all_news = []

    for symbol in symbols:
        news = fetch_stock_news(symbol, articles_per_stock)
        all_news.extend(news)

    all_news.sort(key=lambda x: x['date'], reverse=True)
    return all_news


def load_companies_from_json(json_file='Companies.json'):
    """Load company data from Companies.json file"""
    try:
        with open(json_file, 'r') as f:
            companies = json.load(f)
            return companies
    except FileNotFoundError:
        print(f"Error: {json_file} not found")
        return []
    except Exception as e:
        print(f"Error loading companies: {str(e)}")
        return []


def update_live_prices_in_json(json_file='Companies.json', output_file='Companies.json'):
    """
    Update live prices in Companies.json and save to a new file
    """
    companies = load_companies_from_json(json_file)

    if not companies:
        print("No companies loaded")
        return



    for company in companies:
        symbol = company['symbol']
        print(f"Fetching price for {symbol}...", end=' ')

        current_price = get_current_price(symbol)
        if current_price:
            company['live_price'] = round(current_price, 2)
            print(f"✓ ${current_price:.2f}")
        else:
            print(f"✗ Failed")

    # Save updated data
    try:
        with open(output_file, 'w') as f:
            json.dump(companies, f, indent=2)
        print(f"\n✓ Updated prices saved to {output_file}")
    except Exception as e:
        print(f"\n✗ Error saving file: {str(e)}")

    return companies



# ---------- LOAD JSON ----------
with open("Companies.json", "r", encoding="utf-8") as file:
    stocks = json.load(file)


# ---------- NORMALIZE TEXT ----------
def normalize(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())


# ---------- FIND LIVE PRICE ----------
def get_live_price(company_name):
    query = normalize(company_name)

    for stock in stocks:
        name = normalize(stock["name"])
        symbol = normalize(stock["symbol"])


        if query in name or query == symbol:
            return {
                "name": stock["name"],
                "symbol": stock["symbol"],
                "live_price": stock["live_price"],
                "image": stock["image"]
            }

    return None


# ---------- TEXT INPUT ----------
def live_price(symbol):
    result = get_live_price(symbol)

    price = result['live_price']
    return price


