import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Tuple
import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

@st.cache_resource
def get_yf_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

class StockDataFetcher:
    """Handle all yfinance data fetching operations"""
    
    def __init__(self):
        self.cache_duration = 60  # Cache duration in seconds
        self.rate_limit_delay = 0.5  # Delay between API calls
        
    @st.cache_data(ttl=60)
    def get_live_price(_self, symbol: str) -> Optional[float]:
        """Fetch current live price for a stock"""
        try:
            stock = yf.Ticker(symbol)
            # Try to get real-time data
            current_data = stock.history(period="1d", interval="1m")
            if not current_data.empty:
                price = current_data['Close'].iloc[-1]
            else:
                # Fallback to info
                price = stock.info.get('regularMarketPrice', 
                                      stock.info.get('currentPrice', 
                                                    stock.info.get('previousClose', 0)))
            return price
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
    
    @st.cache_data(ttl=300)
    def get_historical_data(_self, symbol: str, period: str = "1mo", 
                            interval: str = "1d") -> Optional[pd.DataFrame]:
        """Fetch historical stock data"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period, interval=interval)
            if hist.empty:
                return None
            return hist
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    @st.cache_data(ttl=3600)
    def get_company_info(_self, symbol: str) -> Dict:
        """Fetch company information"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'country': info.get('country', 'N/A'),
                'website': info.get('website', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'eps': info.get('trailingEps', 'N/A'),
                'dividend_yield': info.get('dividendYield', 0),
                '52w_high': info.get('fiftyTwoWeekHigh', 0),
                '52w_low': info.get('fiftyTwoWeekLow', 0),
                'avg_volume': info.get('averageVolume', 0),
                'beta': info.get('beta', 1.0),
            }
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            return {}
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict:
        """Fetch data for multiple stocks simultaneously"""
        import concurrent.futures
        stocks_data = {}
        
        def _fetch(symbol):
            return symbol, self.get_stock_summary(symbol)
            
        max_w = min(32, (os.cpu_count() or 1) + 4)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_w) as executor:
            future_to_sym = {executor.submit(_fetch, sym): sym for sym in symbols}
            for future in concurrent.futures.as_completed(future_to_sym):
                sym, data = future.result()
                if data:
                    stocks_data[sym] = data
        return stocks_data
    
    @st.cache_data(ttl=60)
    def get_stock_summary(_self, symbol: str) -> Optional[Dict]:
        """Get comprehensive stock summary"""
        try:
            stock = yf.Ticker(symbol)
            
            # Get 30-day historical data for charts
            hist_30d = stock.history(period="1mo")
            if hist_30d.empty:
                return None
            
            current_price = hist_30d['Close'].iloc[-1]
            
            if len(hist_30d) >= 2:
                prev_close = hist_30d['Close'].iloc[-2]
                change = current_price - prev_close
                change_percent = (change / prev_close) * 100
                day_high = hist_30d['High'].iloc[-1]
                day_low = hist_30d['Low'].iloc[-1]
                volume = hist_30d['Volume'].iloc[-1]
                open_price = hist_30d['Open'].iloc[-1]
            else:
                change = 0
                change_percent = 0
                day_high = current_price
                day_low = current_price
                volume = hist_30d['Volume'].iloc[-1]
                open_price = hist_30d['Open'].iloc[-1]
            
            return {
                'symbol': symbol,
                'price': float(current_price),
                'change': float(change),
                'change_percent': float(change_percent),
                'open': float(open_price),
                'high': float(day_high),
                'low': float(day_low),
                'volume': float(volume),
                'history': hist_30d,
                'info': _self.get_company_info(symbol),
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error getting summary for {symbol}: {e}")
            return None
    
    def get_intraday_data(self, symbol: str, interval: str = "5m") -> Optional[pd.DataFrame]:
        """Fetch intraday data for real-time charts"""
        try:
            stock = yf.Ticker(symbol)
            # Map interval to yfinance format
            interval_map = {
                "1m": "1m",
                "5m": "5m", 
                "15m": "15m",
                "30m": "30m",
                "1h": "60m"
            }
            yf_interval = interval_map.get(interval, "5m")
            data = stock.history(period="1d", interval=yf_interval)
            return data if not data.empty else None
        except Exception as e:
            print(f"Error fetching intraday data: {e}")
            return None
    
    def search_stocks(self, query: str) -> List[Dict]:
        """Search for stocks by ticker or name"""
        try:
            # This is a simple implementation - you can enhance with yfinance Ticker object
            ticker = yf.Ticker(query.upper())
            info = ticker.info
            if info and 'symbol' in info:
                return [{
                    'symbol': info.get('symbol', query),
                    'name': info.get('longName', query),
                    'type': info.get('quoteType', 'EQUITY')
                }]
            return []
        except Exception as e:
            print(f"Error searching for {query}: {e}")
            return []
    
    def get_market_movers(self, move_type: str = "gainers") -> List[Dict]:
        """Get market movers (gainers/losers) - Note: Requires additional API"""
        # This is a placeholder - you might want to use a different API for this
        # For now, return sample data
        sample_movers = {
            "gainers": [
                {"symbol": "NVDA", "change": 8.5, "price": 485.20},
                {"symbol": "TSLA", "change": 5.2, "price": 245.80},
                {"symbol": "META", "change": 3.8, "price": 335.60},
            ],
            "losers": [
                {"symbol": "PYPL", "change": -4.2, "price": 62.30},
                {"symbol": "NFLX", "change": -2.8, "price": 475.50},
                {"symbol": "AMD", "change": -1.9, "price": 145.20},
            ]
        }
        return sample_movers.get(move_type, [])
    
    def get_options_data(self, symbol: str) -> Optional[Dict]:
        """Fetch options data for a stock"""
        try:
            stock = yf.Ticker(symbol)
            expirations = stock.options
            if not expirations:
                return None
            
            # Get nearest expiration
            nearest_exp = expirations[0]
            calls = stock.option_chain(nearest_exp).calls
            puts = stock.option_chain(nearest_exp).puts
            
            return {
                'expirations': expirations,
                'calls': calls,
                'puts': puts,
                'nearest_expiration': nearest_exp
            }
        except Exception as e:
            print(f"Error fetching options: {e}")
            return None


class PortfolioManager:
    """Manage portfolio operations"""
    
    def __init__(self, data_fetcher: StockDataFetcher):
        self.data_fetcher = data_fetcher
        self.portfolio_file = "portfolio_data.json"
    
    def calculate_portfolio_value(self, holdings: List[Dict]) -> Dict:
        """Calculate current portfolio value and metrics"""
        total_value = 0
        total_invested = 0
        holdings_data = []
        
        symbols = [h['symbol'] for h in holdings]
        multi_data = self.data_fetcher.get_multiple_stocks(symbols)
        
        for holding in holdings:
            sym = holding['symbol']
            stock_data = multi_data.get(sym)
            if stock_data:
                current_price = stock_data['price']
                current_value = holding['shares'] * current_price
                invested_value = holding['shares'] * holding['buy_price']
                pnl = current_value - invested_value
                pnl_percent = (pnl / invested_value) * 100 if invested_value > 0 else 0
                
                total_value += current_value
                total_invested += invested_value
                
                holdings_data.append({
                    **holding,
                    'current_price': current_price,
                    'current_value': current_value,
                    'pnl': pnl,
                    'pnl_percent': pnl_percent,
                    'allocation': 0  # Will calculate after total
                })
        
        # Calculate allocations
        for holding in holdings_data:
            holding['allocation'] = (holding['current_value'] / total_value) * 100 if total_value > 0 else 0
        
        total_pnl = total_value - total_invested
        total_pnl_percent = (total_pnl / total_invested) * 100 if total_invested > 0 else 0
        
        return {
            'total_value': total_value,
            'total_invested': total_invested,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'holdings': holdings_data
        }
    
    def get_portfolio_performance_history(self, holdings: List[Dict], days: int = 30) -> pd.DataFrame:
        """Get historical performance of portfolio"""
        import sqlite3
        
        # Connect to SQLite
        conn = sqlite3.connect('portfolio_cache.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_history (
                date TEXT PRIMARY KEY,
                value REAL
            )
        ''')
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        performance = []
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            cursor.execute('SELECT value FROM portfolio_history WHERE date = ?', (date_str,))
            row = cursor.fetchone()
            
            if row:
                value = row[0]
            else:
                # Calculate portfolio value on each date (simplified)
                # In production, you'd need historical prices for each holding
                value = sum(h['shares'] * h['buy_price'] for h in holdings)
                
                # Only cache dates before today to avoid caching incomplete data
                if date.date() < datetime.now().date():
                    cursor.execute('INSERT OR REPLACE INTO portfolio_history (date, value) VALUES (?, ?)', (date_str, value))
                    conn.commit()
            
            performance.append({
                'date': date,
                'value': value
            })
            
        conn.close()
        return pd.DataFrame(performance)


# Create singleton instances
@st.cache_resource
def get_stock_fetcher():
    return StockDataFetcher()

@st.cache_resource
def get_portfolio_manager():
    fetcher = get_stock_fetcher()
    return PortfolioManager(fetcher)