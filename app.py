"""
StockFin — Live Market Dashboard
Entry point for the Streamlit multi-page app.
Run with: streamlit run app.py
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import time
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# ── Page config (ONLY in the root app.py, never in pages/) ─────────────────
st.set_page_config(
    page_title="StockFin — Live Dashboard",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Dark premium CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
:root {
    --bg-base:#0d0f14; --bg-card:rgba(19, 22, 30, 0.55); --bg-card-hover:rgba(24, 28, 39, 0.65);
    --bg-elevated:rgba(28, 32, 48, 0.55); --border:rgba(255,255,255,0.08);
    --border-active:rgba(255,255,255,0.18);
    --accent-blue:#4f8fff; --accent-violet:#7c6ff7;
    --accent-green:#22d98a; --accent-red:#f05252; --accent-amber:#f5a623;
    --text-primary:#f0f2f8; --text-secondary:#8892a4; --text-muted:#4e5669;
    --radius-sm:8px; --radius-md:14px; --radius-lg:20px;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;color:var(--text-primary)!important;}
@keyframes meshBg {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.stApp{
    background: radial-gradient(circle at 15% 50%, rgba(79, 143, 255, 0.12), transparent 45%),
                radial-gradient(circle at 85% 30%, rgba(124, 111, 247, 0.12), transparent 45%),
                var(--bg-base) !important;
    background-size: 200% 200% !important;
    animation: meshBg 25s ease infinite !important;
}
@keyframes slideUpFade {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
section[data-testid="stSidebar"]{background:var(--bg-card)!important;border-right:1px solid var(--border)!important;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);}
section[data-testid="stSidebar"] *{color:var(--text-primary)!important;}
#MainMenu,footer{visibility:hidden;}
header{background:transparent!important;}
[data-testid="stAppDeployButton"]{display:none!important;}
[data-testid="stSidebarNav"]{display:none!important;}
h1,h2,h3{font-family:'Syne',sans-serif!important;color:var(--text-primary)!important;}
p,span{color:var(--text-primary);}
.stMarkdown p{color:var(--text-secondary);font-size:.84rem;}
.fin-card,.stat-card,.ticker-card,.glass-card,.metric-card,.alert-item{
    background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-lg);padding:1.3rem 1.5rem;
    backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);box-shadow:0 4px 30px rgba(0,0,0,0.1);
    transition:border-color .25s ease, transform .25s ease, box-shadow .25s ease;
    animation: slideUpFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
}
.stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,var(--accent-blue),var(--accent-violet));opacity:.7;}
.stat-card{position:relative;overflow:hidden;}
.stat-card:hover,.fin-card:hover{border-color:var(--border-active);transform:translateY(-2px);}
.stat-label{font-size:.7rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
    color:var(--text-secondary);margin-bottom:.4rem;}
.stat-value{font-family:'Syne',sans-serif!important;font-size:1.9rem;font-weight:700;
    color:var(--text-primary);line-height:1.1;}
.stat-badge{display:inline-flex;align-items:center;gap:4px;font-size:.7rem;font-weight:600;
    padding:3px 8px;border-radius:20px;margin-top:.4rem;}
.badge-up{background:rgba(34,217,138,.12);color:var(--accent-green);}
.badge-down{background:rgba(240,82,82,.12);color:var(--accent-red);}
.badge-info{background:rgba(79,143,255,.12);color:var(--accent-blue);}
.ticker-card{border-radius:var(--radius-md);text-align:center;padding:.9rem;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);box-shadow:0 4px 30px rgba(0,0,0,0.1);}
.ticker-card:hover{border-color:var(--accent-blue);transform:translateY(-3px);
    box-shadow:0 8px 24px rgba(79,143,255,.12);}
.ticker-sym{font-size:.68rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--text-secondary);}
.ticker-price{font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:700;color:var(--text-primary);margin:.3rem 0;}
.ticker-chg{font-size:.75rem;font-weight:600;}
.up{color:var(--accent-green);} .down{color:var(--accent-red);}
.nav-group{font-size:.62rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;
    color:var(--text-muted)!important;padding:.5rem .4rem .2rem;}
.nav-item{display:flex;align-items:center;gap:9px;padding:.5rem .8rem;border-radius:var(--radius-sm);
    font-size:.83rem;font-weight:500;color:var(--text-secondary)!important;cursor:pointer;transition:background .15s;margin:2px 0;}
.nav-item:hover{background:rgba(255,255,255,.05);}
.nav-item.active{background:rgba(79,143,255,.15);color:var(--accent-blue)!important;font-weight:600;}
.live-dot{display:inline-flex;align-items:center;gap:6px;font-size:.7rem;font-weight:600;color:var(--accent-green);}
.live-dot::before{content:'';width:7px;height:7px;background:var(--accent-green);border-radius:50%;animation:pdot 2s infinite;}
@keyframes pdot{0%,100%{opacity:1;transform:scale(1);}50%{opacity:.4;transform:scale(1.3);}}
.stSelectbox>div>div,.stTextInput>div>div>input,.stNumberInput>div>div>input{
    background:var(--bg-elevated)!important;border:1px solid var(--border)!important;
    border-radius:var(--radius-sm)!important;color:var(--text-primary)!important;font-size:.84rem!important;}
.stButton>button{background:var(--bg-elevated)!important;border:1px solid var(--border-active)!important;
    color:var(--text-secondary)!important;border-radius:var(--radius-sm)!important;
    font-size:.8rem!important;font-weight:500!important;transition:all .15s!important;}
.stButton>button:hover{background:var(--accent-blue)!important;border-color:var(--accent-blue)!important;color:white!important;}
.stButton>button[kind="primary"]{background:var(--accent-blue)!important;border-color:var(--accent-blue)!important;color:white!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--bg-card)!important;border-radius:var(--radius-md)!important;
    gap:4px;padding:4px;border:1px solid var(--border)!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--text-secondary)!important;
    border-radius:var(--radius-sm)!important;font-size:.8rem!important;font-weight:500!important;padding:6px 14px!important;}
.stTabs [aria-selected="true"]{background:var(--bg-elevated)!important;color:var(--text-primary)!important;font-weight:600!important;}
div[data-testid="stMetric"]{background:var(--bg-card);border:1px solid var(--border);
    border-radius:var(--radius-md);padding:.8rem 1rem;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);box-shadow:0 4px 30px rgba(0,0,0,0.1);}
div[data-testid="stMetric"] label{color:var(--text-secondary)!important;font-size:.7rem!important;
    letter-spacing:.06em;text-transform:uppercase;}
div[data-testid="stMetric"] [data-testid="stMetricValue"]{font-family:'Syne',sans-serif!important;
    color:var(--text-primary)!important;font-size:1.5rem!important;}
[data-testid="stDataFrameContainer"]{border:1px solid var(--border)!important;border-radius:var(--radius-md)!important;}
::-webkit-scrollbar{width:8px;height:8px;}
::-webkit-scrollbar-track{background:var(--bg-base);border-radius:10px;}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:10px;transition:background 0.2s;}
::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,0.2);}
/* Skeletons */
.skeleton{background:linear-gradient(90deg,var(--bg-elevated) 25%,var(--bg-card-hover) 50%,var(--bg-elevated) 75%);background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:var(--radius-sm);}
@keyframes shimmer{0%{background-position:200% 0;}100%{background-position:-200% 0;}}
.skeleton-card{height:100px;border-radius:var(--radius-md);margin-bottom:.5rem;}
.glass-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-lg);padding:1.2rem 1.4rem;}
.glass-card h4{font-family:'Syne',sans-serif;font-size:.8rem;font-weight:600;letter-spacing:.07em;
    text-transform:uppercase;color:var(--text-secondary);margin-bottom:.6rem;}
.glass-card table td{padding:.28rem .4rem;font-size:.82rem;color:var(--text-secondary);}
.glass-card table td:last-child{color:var(--text-primary);}
.alert-item{border-left:3px solid;border-radius:0 var(--radius-sm) var(--radius-sm) 0;
    padding:.75rem 1rem;background:var(--bg-elevated)!important;}
.metric-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-md);
    padding:1rem;text-align:center;}
.metric-value{font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:var(--text-primary);margin:.3rem 0;}
.positive{color:var(--accent-green);} .negative{color:var(--accent-red);}
/* Ensure Streamlit markdown wrappers don't clip hover shadows */
[data-testid="stMarkdownContainer"]{overflow:visible !important;}
[data-testid="stColumn"]{overflow:visible !important;}
/* ── Hover Glow Effects ── */
.fin-card,.stat-card,.glass-card,.metric-card,.ticker-card{
    transition:border-color .25s ease, box-shadow .25s ease, transform .25s ease;
    will-change:transform, box-shadow; position:relative; z-index:0;}
.fin-card:hover,.glass-card:hover,.metric-card:hover{
    border-color:rgba(79,143,255,0.6)!important;
    box-shadow:0 0 30px rgba(79,143,255,0.25),0 10px 40px rgba(0,0,0,0.4)!important;
    transform:translateY(-4px); z-index:10;}
.stat-card:hover{
    border-color:rgba(124,111,247,0.6)!important;
    box-shadow:0 0 30px rgba(124,111,247,0.25),0 10px 40px rgba(0,0,0,0.4)!important;
    transform:translateY(-4px); z-index:10;}
.ticker-card:hover{
    border-color:rgba(79,143,255,0.65)!important;
    box-shadow:0 0 34px rgba(79,143,255,0.28),0 10px 40px rgba(0,0,0,0.4)!important;
    transform:translateY(-5px); z-index:10;}
</style>
""", unsafe_allow_html=True)


# ── Stock catalogue ───────────────────────────────────────────────────────────
STOCK_CATALOGUE = {
    "Apple (AAPL)":               "AAPL",
    "Microsoft (MSFT)":           "MSFT",
    "NVIDIA (NVDA)":              "NVDA",
    "Alphabet / Google (GOOGL)":  "GOOGL",
    "Meta Platforms (META)":      "META",
    "Amazon (AMZN)":              "AMZN",
    "Tesla (TSLA)":               "TSLA",
    "Netflix (NFLX)":             "NFLX",
    "AMD (AMD)":                  "AMD",
    "Intel (INTC)":               "INTC",
    "Qualcomm (QCOM)":            "QCOM",
    "Broadcom (AVGO)":            "AVGO",
    "Salesforce (CRM)":           "CRM",
    "Oracle (ORCL)":              "ORCL",
    "Adobe (ADBE)":               "ADBE",
    "Shopify (SHOP)":             "SHOP",
    "Palantir (PLTR)":            "PLTR",
    "JPMorgan Chase (JPM)":       "JPM",
    "Goldman Sachs (GS)":         "GS",
    "Visa (V)":                   "V",
    "Mastercard (MA)":            "MA",
    "Johnson & Johnson (JNJ)":    "JNJ",
    "UnitedHealth (UNH)":         "UNH",
    "Pfizer (PFE)":               "PFE",
    "Eli Lilly (LLY)":            "LLY",
    "Walmart (WMT)":              "WMT",
    "Coca-Cola (KO)":             "KO",
    "S&P 500 ETF (SPY)":          "SPY",
    "NASDAQ ETF (QQQ)":           "QQQ",
    "Bitcoin (BTC-USD)":          "BTC-USD",
    "Infosys (INFY)":             "INFY",
    "Wipro (WIT)":                "WIT",
    "HDFC Bank (HDB)":            "HDB",
    "Tata Motors (TTM)":          "TTM",
}
SYMBOL_TO_NAME = {v: k for k, v in STOCK_CATALOGUE.items()}

# ── Data helpers ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def get_live_stock_data(symbol: str, period: str = "1mo") -> dict | None:
    try:
        stock = yf.Ticker(symbol)
        fi = stock.fast_info

        # ── Most accurate live price (priority order) ──────────────────────
        current_price = None
        try:
            current_price = float(fi.last_price)
        except Exception:
            pass
        if not current_price:
            info = stock.info
            current_price = (
                info.get("regularMarketPrice")
                or info.get("currentPrice")
                or info.get("previousClose")
                or 0.0
            )
        current_price = float(current_price)

        # ── Previous close for correct change calculation ──────────────────
        prev_close = None
        try:
            prev_close = float(fi.previous_close)
        except Exception:
            pass
        if not prev_close:
            try:
                prev_close = float(stock.info.get("previousClose") or current_price)
            except Exception:
                prev_close = current_price

        # ── Historical bars for chart ──────────────────────────────────────
        hist = stock.history(period=period, prepost=True)
        if hist.empty:
            return None

        change = current_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0.0

        return {
            "symbol":         symbol,
            "price":          current_price,
            "open":           float(hist["Open"].iloc[-1]),
            "high":           float(hist["High"].iloc[-1]),
            "low":            float(hist["Low"].iloc[-1]),
            "volume":         float(hist["Volume"].iloc[-1]),
            "prev_close":     prev_close,
            "change":         change,
            "change_percent": change_pct,
            "history":        hist,
            "info":           stock.info,
        }
    except Exception as exc:
        st.warning(f"Could not fetch {symbol}: {exc}")
        return None


@st.cache_data(ttl=300)
def get_multiple_stocks(symbols: tuple, period: str = "1mo") -> dict:
    import concurrent.futures
    import os
    result = {}
    
    def _fetch(sym):
        return sym, get_live_stock_data(sym, period)
        
    max_w = min(32, (os.cpu_count() or 1) + 4)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_w) as executor:
        future_to_sym = {executor.submit(_fetch, sym): sym for sym in symbols}
        for future in concurrent.futures.as_completed(future_to_sym):
            sym, data = future.result()
            if data:
                result[sym] = data
    return result


@st.cache_data(ttl=60)
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    delta = df["Close"].diff()
    gain  = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss  = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["RSI"]      = (100 - (100 / (1 + rs))).fillna(50)
    df["BB_Middle"] = df["Close"].rolling(20).mean()
    bb_std          = df["Close"].rolling(20).std()
    df["BB_Upper"]  = df["BB_Middle"] + bb_std * 2
    df["BB_Lower"]  = df["BB_Middle"] - bb_std * 2
    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"]   = exp1 - exp2
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    return df


# ── Plotly dark layout ────────────────────────────────────────────────────────
DARK_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(19,22,30,0)",
    plot_bgcolor="rgba(28,32,48,0.5)",
    font=dict(family="DM Sans", color="#8892a4", size=11),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)",
               tickfont=dict(size=10, color="#4e5669")),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)",
               tickfont=dict(size=10, color="#4e5669")),
    legend=dict(bgcolor="rgba(19,22,30,0.75)", bordercolor="rgba(255,255,255,0.08)",
                borderwidth=1, font=dict(color="#8892a4", size=10)),
    hoverlabel=dict(
        bgcolor="rgba(13,15,20,0.96)",
        bordercolor="rgba(79,143,255,0.5)",
        font=dict(family="DM Sans", size=12, color="#f0f2f8"),
    ),
    margin=dict(l=8, r=8, t=36, b=8),
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0.4rem 0.4rem">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:1.2rem">
            <div style="width:34px;height:34px;background:linear-gradient(135deg,#4f8fff,#7c6ff7);
                border-radius:10px;display:flex;align-items:center;justify-content:center;
                font-weight:700;font-size:.85rem;color:white;font-family:'Syne',sans-serif">S</div>
            <div>
                <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;
                    color:#f0f2f8!important">StockFin</div>
                <span class="live-dot" style="font-size:.65rem">LIVE</span>
            </div>
        </div>
        <div class="nav-group">Platform</div>
        <a href="/" target="_self" class="nav-item active" style="text-decoration:none;">Dashboard</a>
        <div class="nav-group" style="margin-top:.5rem">Pages</div>
        <a href="/Analytics" target="_self" class="nav-item" style="text-decoration:none;">Analytics</a>
        <a href="/Portfolio" target="_self" class="nav-item" style="text-decoration:none;">Portfolio</a>
        <a href="/ML_Predictions" target="_self" class="nav-item" style="text-decoration:none;">ML Predictions</a>
        <a href="/Watchlist" target="_self" class="nav-item" style="text-decoration:none;">Watchlist & Alerts</a>
        <a href="/Backtesting" target="_self" class="nav-item" style="text-decoration:none;">Backtesting</a>
        <a href="/Heatmap" target="_self" class="nav-item" style="text-decoration:none;">Sector Heatmap</a>
    </div>
    <hr style="border-color:rgba(255,255,255,.06);margin:0.8rem 0">
    """, unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size:.7rem;font-weight:600;letter-spacing:.1em;'
        'text-transform:uppercase;color:#4e5669;padding:.3rem .4rem .1rem">Select Stocks</div>',
        unsafe_allow_html=True,
    )

    # Checkboxes using full company names
    selected_stocks: list[str] = []
    for name, sym in STOCK_CATALOGUE.items():
        # Only show first 12 in sidebar checkboxes to avoid overflow
        if list(STOCK_CATALOGUE.keys()).index(name) >= 12:
            break
        if st.checkbox(name, value=(sym in ["AAPL", "TSLA", "MSFT"])):
            selected_stocks.append(sym)

    st.markdown(
        '<hr style="border-color:rgba(255,255,255,.06);margin:.8rem 0">',
        unsafe_allow_html=True,
    )
    chart_period = st.selectbox("Chart Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=0)
    total_value  = st.number_input("Initial Investment ($)", value=10_000, step=1_000, min_value=0)

    st.markdown(
        '<hr style="border-color:rgba(255,255,255,.06);margin:.8rem 0">',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:.72rem;color:#4e5669;padding:.2rem .4rem">'
        "Data · Yahoo Finance · Refreshes ~60 s</div>",
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
hc1, hc2, hc3 = st.columns([3, 1.4, 0.8])
with hc1:
    st.markdown("""
    <div style="padding:.8rem 0 .2rem">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:.5rem">
            <div style="width:40px;height:40px;background:linear-gradient(135deg,#4f8fff,#7c6ff7);
                border-radius:12px;display:flex;align-items:center;justify-content:center;
                font-weight:800;font-size:1rem;color:white;font-family:'Syne',sans-serif;
                box-shadow:0 4px 16px rgba(79,143,255,.3);flex-shrink:0">S</div>
            <div>
                <div style="font-family:'Syne',sans-serif;font-size:1.7rem;font-weight:800;
                    color:#f0f2f8;line-height:1">StockFin</div>
                <div style="font-size:.82rem;color:#8892a4;margin-top:.2rem">
                    Live Market Dashboard &nbsp;·&nbsp; Real-time analytics</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with hc2:
    now = datetime.now().strftime("%b %d, %Y  %H:%M")
    st.markdown(f"""
    <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:10px;
        padding:.55rem 1rem;text-align:center;margin-top:.8rem">
        <div style="font-size:.65rem;color:#4e5669;text-transform:uppercase;
            letter-spacing:.07em">Last Update</div>
        <div style="font-size:.82rem;font-weight:600;color:#f0f2f8">{now}</div>
    </div>
    """, unsafe_allow_html=True)
with hc3:
    st.markdown("<div style='margin-top:.8rem'>", unsafe_allow_html=True)
    if st.button("Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

# ── Guard: no stocks selected ─────────────────────────────────────────────────
if not selected_stocks:
    st.markdown("""
    <div class="fin-card" style="text-align:center;padding:3rem">
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:#f0f2f8">
            Select stocks from the sidebar to get started
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

placeholder = st.empty()
with placeholder.container():
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:.82rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#4e5669;margin-bottom:.6rem">Loading Market Overview...</div>
    <div style="display:flex;gap:1rem;margin-bottom:1rem;flex-wrap:wrap;">
        <div class="skeleton skeleton-card" style="flex:1;min-width:200px;height:110px"></div>
        <div class="skeleton skeleton-card" style="flex:1;min-width:200px;height:110px"></div>
        <div class="skeleton skeleton-card" style="flex:1;min-width:200px;height:110px"></div>
        <div class="skeleton skeleton-card" style="flex:1;min-width:200px;height:110px"></div>
    </div>
    <div style="font-family:'Syne',sans-serif;font-size:.82rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#4e5669;margin-bottom:.6rem">Loading Detailed Analysis...</div>
    <div class="skeleton skeleton-card" style="width:100%;height:500px"></div>
    """, unsafe_allow_html=True)

stocks_data = get_multiple_stocks(tuple(selected_stocks), chart_period)

placeholder.empty()

if not stocks_data:
    st.error("No stock data could be fetched. Check your internet connection and try again.")
    st.stop()

# ── Ticker grid ───────────────────────────────────────────────────────────────
st.markdown(
    "<div style=\"font-family:'Syne',sans-serif;font-size:.82rem;font-weight:600;"
    "letter-spacing:.08em;text-transform:uppercase;color:#4e5669;margin-bottom:.6rem\">"
    "Market Overview</div>",
    unsafe_allow_html=True,
)

cards_html = ["<div style='display:flex; gap: 1rem; flex-wrap: wrap;'>"]
for idx, (sym, data) in enumerate(list(stocks_data.items())[:8]):
    display_name = SYMBOL_TO_NAME.get(sym, sym)
    up = data["change"] >= 0
    cards_html.append(f"""
    <div class="ticker-card" data-ticker="{sym}" data-prev-close="{data['prev_close']}" style="flex: 1; min-width: 200px;">
        <div class="ticker-sym">{sym}</div>
        <div style="font-size:.65rem;color:#4e5669;margin-bottom:.2rem">{display_name[:22]}</div>
        <div class="ticker-price count-up" id="price-{sym}">${data['price']:.2f}</div>
        <div class="ticker-chg {'up' if up else 'down'} count-up" id="chg-{sym}">
            {'▲' if up else '▼'} {abs(data['change_percent']):.2f}%
        </div>
    </div>
    """)
cards_html.append("</div>")
st.markdown("\n".join(cards_html), unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Detailed analysis ─────────────────────────────────────────────────────────
st.markdown(
    "<div style=\"font-family:'Syne',sans-serif;font-size:.82rem;font-weight:600;"
    "letter-spacing:.08em;text-transform:uppercase;color:#4e5669;margin-bottom:.6rem\">"
    "Detailed Analysis</div>",
    unsafe_allow_html=True,
)

# Selectbox with full company names, returns symbol
sym_keys  = list(stocks_data.keys())
sym_names = [SYMBOL_TO_NAME.get(s, s) for s in sym_keys]
sel_idx   = st.selectbox(
    "Select stock to analyse",
    range(len(sym_keys)),
    format_func=lambda i: f"{sym_keys[i]}  —  {sym_names[i]}",
    label_visibility="collapsed",
)
selected_symbol = sym_keys[sel_idx]

if selected_symbol and selected_symbol in stocks_data:
    data = stocks_data[selected_symbol]
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Price Chart", "Indicators", "Company Info", "Alerts"]
    )

    # ── Price Chart ──────────────────────────────────────────────────────────
    with tab1:
        hist = calculate_indicators(data["history"])

        # Tighter vertical_spacing and row_heights for compact look
        fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True,
            vertical_spacing=0.06,
            row_heights=[0.60, 0.18, 0.22],
            subplot_titles=("Price & Moving Averages", "Volume", "RSI (14)"),
        )
        fig.add_trace(
            go.Candlestick(
                x=hist.index, open=hist["Open"], high=hist["High"],
                low=hist["Low"], close=hist["Close"],
                increasing_line_color="#22d98a", decreasing_line_color="#f05252",
                name="Price",
            ), row=1, col=1,
        )
        for col_name, label, color in [
            ("MA20",     "MA20", "#f5a623"),
            ("MA50",     "MA50", "#7c6ff7"),
            ("BB_Upper", "BB+",  "rgba(255,255,255,.25)"),
            ("BB_Lower", "BB-",  "rgba(255,255,255,.25)"),
        ]:
            fig.add_trace(
                go.Scatter(
                    x=hist.index, y=hist[col_name], name=label,
                    line=dict(color=color, width=1,
                              dash="dot" if "BB" in col_name else "solid"),
                ), row=1, col=1,
            )
        bar_colors = [
            "#22d98a" if hist["Close"].iloc[i] >= hist["Open"].iloc[i] else "#f05252"
            for i in range(len(hist))
        ]
        fig.add_trace(
            go.Bar(x=hist.index, y=hist["Volume"], name="Volume",
                   marker_color=bar_colors, opacity=0.7), row=2, col=1,
        )
        fig.add_trace(
            go.Scatter(x=hist.index, y=hist["RSI"], name="RSI",
                       line=dict(color="#4f8fff", width=1.5)), row=3, col=1,
        )
        fig.add_hline(y=70, line_dash="dot", line_color="#f05252", opacity=0.5, row=3, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="#22d98a", opacity=0.5, row=3, col=1)
        fig.update_layout(
            height=680, showlegend=True, xaxis_rangeslider_visible=False,
            title=f"{selected_symbol} — {SYMBOL_TO_NAME.get(selected_symbol, '')}",
            title_font=dict(family="Syne", size=13, color="#f0f2f8"),
            **DARK_LAYOUT,
        )
        # Tighten subplot title font
        for ann in fig.layout.annotations:
            ann.font.size = 10
            ann.font.color = "#8892a4"
        # Polish candlestick tooltips
        fig.update_traces(
            selector=dict(type="candlestick"),
            hovertext="",
            hovertemplate=(
                "<b>%{x|%d %b %Y}</b><br>"
                "Open: <b>$%{open:.2f}</b><br>"
                "High: <b style='color:#22d98a'>$%{high:.2f}</b><br>"
                "Low: <b style='color:#f05252'>$%{low:.2f}</b><br>"
                "Close: <b>$%{close:.2f}</b><extra></extra>"
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Indicators ───────────────────────────────────────────────────────────
    with tab2:
        hist = calculate_indicators(data["history"])
        latest_rsi = float(hist["RSI"].iloc[-1])
        rsi_status = "Overbought" if latest_rsi > 70 else "Oversold" if latest_rsi < 30 else "Neutral"
        rsi_color  = "#f05252" if latest_rsi > 70 else "#22d98a" if latest_rsi < 30 else "#f5a623"
        macd_val   = float(hist["MACD"].iloc[-1])
        signal_val = float(hist["Signal"].iloc[-1])
        macd_bull  = macd_val > signal_val
        latest_close = float(hist["Close"].iloc[-1])
        week52_high  = data["info"].get("fiftyTwoWeekHigh", latest_close)
        week52_low   = data["info"].get("fiftyTwoWeekLow", latest_close)

        ic1, ic2 = st.columns(2)
        with ic1:
            st.markdown(f"""
            <div class="glass-card">
                <h4>Key Statistics</h4>
                <table style="width:100%">
                    <tr><td>Current Price</td><td><strong>${data['price']:.2f}</strong></td></tr>
                    <tr><td>Day Open</td><td>${data['open']:.2f}</td></tr>
                    <tr><td>Day High</td><td><span style='color:#22d98a'>${data['high']:.2f}</span></td></tr>
                    <tr><td>Day Low</td><td><span style='color:#f05252'>${data['low']:.2f}</span></td></tr>
                    <tr><td>Volume</td><td>{data['volume']:,.0f}</td></tr>
                    <tr><td>MA 20</td><td>${hist['MA20'].iloc[-1]:.2f}</td></tr>
                    <tr><td>MA 50</td><td>${hist['MA50'].iloc[-1]:.2f}</td></tr>
                    <tr><td>BB Upper</td><td>${hist['BB_Upper'].iloc[-1]:.2f}</td></tr>
                    <tr><td>BB Lower</td><td>${hist['BB_Lower'].iloc[-1]:.2f}</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        with ic2:
            # ── RSI Gauge Chart ──────────────────────────────────────────────
            fig_rsi = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=latest_rsi,
                title=dict(text=f"RSI (14) — <b style='color:{rsi_color}'>{rsi_status}</b>",
                           font=dict(family="Syne", size=13, color="#f0f2f8")),
                number=dict(font=dict(family="Syne", size=28, color=rsi_color),
                            suffix=""),
                delta=dict(reference=50, relative=False,
                           font=dict(size=12),
                           increasing=dict(color="#f05252"),
                           decreasing=dict(color="#22d98a")),
                gauge=dict(
                    axis=dict(range=[0, 100], tickwidth=1,
                              tickfont=dict(color="#4e5669", size=9),
                              tickvals=[0, 30, 50, 70, 100]),
                    bar=dict(color=rsi_color, thickness=0.28),
                    bgcolor="rgba(28,32,48,0.0)",
                    borderwidth=0,
                    steps=[
                        dict(range=[0, 30],   color="rgba(34,217,138,0.12)"),
                        dict(range=[30, 70],  color="rgba(245,166,35,0.08)"),
                        dict(range=[70, 100], color="rgba(240,82,82,0.12)"),
                    ],
                    threshold=dict(
                        line=dict(color="rgba(255,255,255,0.3)", width=2),
                        thickness=0.75, value=latest_rsi,
                    ),
                ),
            ))
            fig_rsi.update_layout(
                height=230,
                paper_bgcolor="rgba(19,22,30,0)",
                font=dict(family="DM Sans", color="#8892a4"),
                margin=dict(l=20, r=20, t=50, b=10),
                hoverlabel=dict(bgcolor="rgba(13,15,20,0.95)",
                                bordercolor="rgba(79,143,255,0.5)",
                                font=dict(family="DM Sans", size=12, color="#f0f2f8")),
            )
            st.plotly_chart(fig_rsi, use_container_width=True)

            # ── 52W Price Bullet Chart ───────────────────────────────────────
            pos_pct = ((latest_close - week52_low) / (week52_high - week52_low) * 100
                       if week52_high != week52_low else 50)
            fig_bullet = go.Figure(go.Indicator(
                mode="gauge+number",
                value=pos_pct,
                title=dict(text="52-Week Position (%)",
                           font=dict(family="Syne", size=11, color="#8892a4")),
                number=dict(font=dict(family="Syne", size=20, color="#f0f2f8"),
                            suffix="%", valueformat=".1f"),
                gauge=dict(
                    shape="bullet",
                    axis=dict(range=[0, 100],
                              tickfont=dict(color="#4e5669", size=9)),
                    bar=dict(color="#4f8fff", thickness=0.45),
                    bgcolor="rgba(28,32,48,0.0)",
                    borderwidth=0,
                    steps=[
                        dict(range=[0, 33],  color="rgba(240,82,82,0.15)"),
                        dict(range=[33, 66], color="rgba(245,166,35,0.10)"),
                        dict(range=[66, 100],color="rgba(34,217,138,0.12)"),
                    ],
                    threshold=dict(
                        line=dict(color="#22d98a", width=2),
                        thickness=0.8, value=pos_pct,
                    ),
                ),
            ))
            fig_bullet.update_layout(
                height=130,
                paper_bgcolor="rgba(19,22,30,0)",
                font=dict(family="DM Sans", color="#8892a4"),
                margin=dict(l=20, r=20, t=36, b=10),
            )
            st.plotly_chart(fig_bullet, use_container_width=True)

            # MACD badge
            macd_color = "#22d98a" if macd_bull else "#f05252"
            macd_label = "Bullish" if macd_bull else "Bearish"
            st.markdown(f"""
            <div style='background:rgba(19,22,30,0.6);border:1px solid rgba(255,255,255,0.08);
                border-radius:12px;padding:.8rem 1rem;display:flex;justify-content:space-between;align-items:center'>
                <span style='font-size:.75rem;color:#8892a4;font-weight:600;letter-spacing:.06em;text-transform:uppercase'>MACD Signal</span>
                <span style='font-family:Syne,sans-serif;font-size:.9rem;font-weight:700;color:{macd_color}'>
                    {'▲' if macd_bull else '▼'} {macd_label} &nbsp;
                    <span style='font-size:.75rem;font-weight:400;color:#4e5669'>
                        MACD {macd_val:+.3f} / Sig {signal_val:+.3f}</span>
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

        fig2 = go.Figure()
        for col_name, label, color in [
            ("Close",  "Close Price", "#4f8fff"),
            ("MA20",   "MA20",        "#f5a623"),
            ("MA50",   "MA50",        "#7c6ff7"),
        ]:
            fig2.add_trace(
                go.Scatter(x=hist.index, y=hist[col_name], name=label,
                           line=dict(color=color, width=1.8 if col_name == "Close" else 1.2))
            )
        fig2.update_layout(
            height=300, title="Price vs Moving Averages",
            title_font=dict(family="Syne", size=13, color="#f0f2f8"), **DARK_LAYOUT,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Company Info ─────────────────────────────────────────────────────────
    with tab3:
        info = data["info"]
        ci1, ci2 = st.columns(2)
        with ci1:
            st.markdown(f"""
            <div class="glass-card">
                <h4>Company Profile</h4>
                <table style="width:100%">
                    <tr><td>Name</td><td>{info.get('longName','N/A')}</td></tr>
                    <tr><td>Sector</td><td>{info.get('sector','N/A')}</td></tr>
                    <tr><td>Industry</td><td>{info.get('industry','N/A')}</td></tr>
                    <tr><td>Country</td><td>{info.get('country','N/A')}</td></tr>
                    <tr><td>Website</td>
                        <td><a href="{info.get('website','#')}" target="_blank"
                            style="color:#4f8fff">{info.get('website','N/A')}</a></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        with ci2:
            st.markdown(f"""
            <div class="glass-card">
                <h4>Financial Metrics</h4>
                <table style="width:100%">
                    <tr><td>Market Cap</td><td>${info.get('marketCap',0):,.0f}</td></tr>
                    <tr><td>P/E Ratio</td><td>{info.get('trailingPE','N/A')}</td></tr>
                    <tr><td>52W High</td><td>${info.get('fiftyTwoWeekHigh',0):.2f}</td></tr>
                    <tr><td>52W Low</td><td>${info.get('fiftyTwoWeekLow',0):.2f}</td></tr>
                    <tr><td>Dividend Yield</td>
                        <td>{(info.get('dividendYield') or 0) * 100:.2f}%</td></tr>
                    <tr><td>Beta</td><td>{info.get('beta','N/A')}</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

    # ── Alerts ───────────────────────────────────────────────────────────────
    with tab4:
        hist = calculate_indicators(data["history"])
        latest_rsi = float(hist["RSI"].iloc[-1])
        avg_vol    = float(hist["Volume"].rolling(20).mean().iloc[-1])
        alerts: list[tuple[str, str]] = []

        if data["change_percent"] > 3:
            alerts.append((f"{selected_symbol} surged <strong>+{data['change_percent']:.2f}%</strong> today", "#f5a623"))
        elif data["change_percent"] < -3:
            alerts.append((f"{selected_symbol} dropped <strong>{data['change_percent']:.2f}%</strong> today", "#f05252"))
        if latest_rsi > 70:
            alerts.append((f"RSI overbought — <strong>{latest_rsi:.1f}</strong>", "#f05252"))
        elif latest_rsi < 30:
            alerts.append((f"RSI oversold — <strong>{latest_rsi:.1f}</strong>", "#22d98a"))
        if avg_vol and data["volume"] > avg_vol * 1.5:
            alerts.append((f"Unusual volume — <strong>{data['volume']:,.0f}</strong>", "#4f8fff"))

        if alerts:
            for msg, color in alerts:
                st.markdown(f"""
                <div style="background:rgba(19,22,30,1);border:1px solid {color}33;
                    border-left:3px solid {color};border-radius:0 8px 8px 0;
                    padding:.8rem 1rem;font-size:.83rem;color:#8892a4;margin-bottom:.5rem">
                    {msg}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(34,217,138,.07);border:1px solid rgba(34,217,138,.2);
                border-radius:14px;padding:1rem;font-size:.83rem;color:#22d98a">
                No significant alerts at this time
            </div>
            """, unsafe_allow_html=True)

        st.markdown(
            "<div style='margin-top:1rem;font-size:.72rem;font-weight:600;letter-spacing:.08em;"
            "text-transform:uppercase;color:#4e5669;margin-bottom:.5rem'>Headlines</div>",
            unsafe_allow_html=True,
        )
        for headline in [
            f"{selected_symbol} shows momentum in latest session",
            f"Analysts revise {selected_symbol} price target upward",
            f"Institutional activity noted in {selected_symbol}",
            f"Technical indicators signal trend continuation for {selected_symbol}",
        ]:
            st.markdown(
                f"<div style='padding:.4rem 0;font-size:.82rem;color:#8892a4;"
                f"border-bottom:1px solid rgba(255,255,255,.05)'>→ {headline}</div>",
                unsafe_allow_html=True,
            )

# ── Portfolio summary strip ───────────────────────────────────────────────────
st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
st.markdown('<hr style="border-color:rgba(255,255,255,.06)">', unsafe_allow_html=True)
st.markdown(
    "<div style=\"font-family:'Syne',sans-serif;font-size:.82rem;font-weight:600;"
    "letter-spacing:.08em;text-transform:uppercase;color:#4e5669;margin-bottom:.7rem\">"
    "Portfolio Summary</div>",
    unsafe_allow_html=True,
)

portfolio_value = float(total_value)
for sym, d in stocks_data.items():
    if d and d["open"]:
        alloc = total_value / max(len(stocks_data), 1)
        portfolio_value = portfolio_value - alloc + alloc * d["price"] / d["open"]
pct_return = ((portfolio_value - total_value) / total_value * 100) if total_value else 0.0

ps1, ps2, ps3, ps4 = st.columns(4)
for col, title, value in [
    (ps1, "Total Value",  f"${portfolio_value:,.2f}"),
    (ps2, "Total Return", f"{pct_return:+.2f}%"),
    (ps3, "Holdings",     str(len(stocks_data))),
    (ps4, "Risk Score",   "Medium"),
]:
    with col:
        color = "#22d98a" if "+" in value else "#f05252" if value.startswith("-") else "#f0f2f8"
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">{title}</div>
            <div class="stat-value count-up" style="color:{color};font-size:1.6rem">{value}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1.5rem 0 .5rem;font-size:.75rem;color:#4e5669">
    Data provided by Yahoo Finance &nbsp;·&nbsp; For educational purposes only
    &nbsp;·&nbsp; Not financial advice
</div>
""", unsafe_allow_html=True)

import streamlit.components.v1 as components
components.html("""
<script>
    const parentDoc = window.parent.document;
    if (!parentDoc.window_count_up_initialized) {
        parentDoc.window_count_up_initialized = true;
        
        function animateValue(el) {
            if (el.classList.contains('counted')) return;
            el.classList.add('counted');
            const text = el.innerText.trim();
            const match = text.match(/^([^\\d\\-\\+]*)([\\+\\-]?\\d[\\d,]*(?:\\.\\d+)?)(.*)$/);
            if(match) {
                const prefix = match[1];
                const numStr = match[2].replace(/,/g, '');
                const suffix = match[3];
                const target = parseFloat(numStr);
                if(isNaN(target)) return;
                const decimals = numStr.includes('.') ? numStr.split('.')[1].length : 0;
                
                let start = 0;
                const duration = 1200; // ms
                const startTime = performance.now();
                
                const update = (currentTime) => {
                    const elapsed = currentTime - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
                    const current = start + (target - start) * ease;
                    
                    let currentStr = current.toFixed(decimals).toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",");
                    el.innerText = prefix + currentStr + suffix;
                    
                    if(progress < 1) {
                        requestAnimationFrame(update);
                    } else {
                        el.innerText = text;
                    }
                };
                requestAnimationFrame(update);
            }
        }

        parentDoc.querySelectorAll('.count-up').forEach(animateValue);
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) {
                        if (node.classList && node.classList.contains('count-up')) animateValue(node);
                        const children = node.querySelectorAll('.count-up');
                        children.forEach(animateValue);
                    }
                });
            });
        });
        observer.observe(parentDoc.body, { childList: true, subtree: true });
    } else {
        // Trigger for newly added elements if observer missed them before connection
        parentDoc.querySelectorAll('.count-up:not(.counted)').forEach(el => {
            if(parentDoc.defaultView && typeof parentDoc.defaultView.animateValue === 'function') {
                parentDoc.defaultView.animateValue(el);
            } else {
                // simple fallback if function not exported
                el.classList.add('counted');
            }
        });
    }
</script>
""", height=0, width=0)

# ── Real-time WebSocket Price Streaming ───────────────────────────────────────
st.components.v1.html("""
<script src="https://cdn.jsdelivr.net/npm/protobufjs@7.2.5/dist/light/protobuf.min.js"></script>
<script>
setTimeout(() => {
    const docs = window.parent.document;
    if (!docs.querySelector('.ticker-card')) return;
    
    let symbols = [];
    docs.querySelectorAll('.ticker-card').forEach(c => {
        let sym = c.getAttribute('data-ticker');
        if(sym) symbols.push(sym);
    });
    
    try {
        if (!window.parent.Yaticker) {
            const root = protobuf.Root.fromJSON({"nested":{"PricingData":{"fields":{"id":{"type":"string","id":1},"price":{"type":"float","id":2},"changePercent":{"type":"float","id":8},"change":{"type":"float","id":12},"previousClose":{"type":"float","id":16}}}}});
            window.parent.Yaticker = root.lookupType("PricingData");
        }
        
        if (window.parent.stockfin_ws && window.parent.stockfin_ws.readyState === WebSocket.OPEN) {
            window.parent.stockfin_ws.send(JSON.stringify({subscribe: symbols}));
            return;
        }

        const ws = new WebSocket('wss://streamer.finance.yahoo.com');
        window.parent.stockfin_ws = ws;
        
        ws.onopen = () => {
            if (symbols.length > 0) {
                ws.send(JSON.stringify({subscribe: symbols}));
            }
        };
        ws.onmessage = (msg) => {
            const Yaticker = window.parent.Yaticker;
            const decoded = Yaticker.decode(new Uint8Array(atob(msg.data).split('').map(c => c.charCodeAt(0))));
            const priceEl = docs.getElementById('price-' + decoded.id);
            const chgEl = docs.getElementById('chg-' + decoded.id);
            const card = docs.querySelector(`.ticker-card[data-ticker="${decoded.id}"]`);
            
            if (priceEl && chgEl && card && decoded.price) {
                const oldPrice = parseFloat(priceEl.innerText.replace('$',''));
                if (oldPrice !== decoded.price) {
                    priceEl.innerText = '$' + decoded.price.toFixed(2);
                    priceEl.style.color = decoded.price > oldPrice ? 'var(--accent-green)' : 'var(--accent-red)';
                    setTimeout(() => { priceEl.style.color = ''; }, 600);
                    
                    const prevClose = parseFloat(card.getAttribute('data-prev-close'));
                    if (prevClose) {
                        const change = decoded.price - prevClose;
                        const pct = (change / prevClose) * 100;
                        const isUp = change >= 0;
                        chgEl.innerText = (isUp ? '▲ ' : '▼ ') + Math.abs(pct).toFixed(2) + '%';
                        chgEl.className = 'ticker-chg ' + (isUp ? 'up' : 'down');
                    }
                }
            }
        };
    } catch(e) { console.error("WebSocket init failed", e); }
}, 800);
</script>
""", height=0, width=0)
