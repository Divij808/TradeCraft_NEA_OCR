import feedparser
import json
from datetime import datetime
from urllib.parse import quote
import re


def fetch_stock_news(symbol, max_articles=5):
    """
    Fetch news for a specific stock symbol from Yahoo Finance RSS feed

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        max_articles: Maximum number of articles to return

    Returns:
        List of news articles with title, description, link, date, and source
    """
    try:
        # Yahoo Finance RSS feed URL
        rss_url = f"https://finance.yahoo.com/rss/headline?s={quote(symbol)}"

        # Parse the RSS feed
        feed = feedparser.parse(rss_url)

        articles = []
        for entry in feed.entries[:max_articles]:
            # Extract published date
            pub_date = entry.get('published', '')
            try:
                # Parse date and format it
                date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = pub_date

            # Clean up description (remove HTML tags)
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
    """
    Fetch news for multiple stock symbols

    Args:
        symbols: List of stock ticker symbols
        articles_per_stock: Number of articles to fetch per stock

    Returns:
        List of all news articles sorted by date
    """
    all_news = []

    for symbol in symbols:
        news = fetch_stock_news(symbol, articles_per_stock)
        all_news.extend(news)

    # Sort by date (most recent first)
    all_news.sort(key=lambda x: x['date'], reverse=True)

    return all_news


def get_stock_trend(symbol):
    """
    Get stock trend indicator (simplified version - you can enhance this)
    Returns: 'up', 'down', or 'neutral'

    In a real implementation, you would compare current price with previous price
    For now, this is a placeholder that returns random trends
    """
    import random
    return random.choice(['up', 'down', 'neutral'])


def load_companies_from_json(json_file='Companies.json'):
    """
    Load company symbols from Companies.json file

    Returns:
        List of stock symbols
    """
    try:
        with open(json_file, 'r') as f:
            companies = json.load(f)
            return [company['symbol'] for company in companies]
    except Exception as e:
        print(f"Error loading companies: {str(e)}")
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']  # Default symbols