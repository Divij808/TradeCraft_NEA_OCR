import sys
import subprocess


def ensure_packages():
    packages = [
        "flask",
        "feedparser",
        "yfinance",
        "sqlite3"
    ]

    for pkg in packages:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", pkg
            ])


ensure_packages()
