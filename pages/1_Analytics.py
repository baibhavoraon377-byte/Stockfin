"""
Advanced Analytics page  ·  pages/1_Analytics.py
DO NOT call st.set_page_config() here — it lives only in app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import time
import warnings

warnings.filterwarnings("ignore")

# ── Page-level CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
:root{--bg-base:#0d0f14;--bg-card:rgba(19, 22, 30, 0.55);--bg-elevated:rgba(28, 32, 48, 0.55);
    --border:rgba(255,255,255,.08);--border-active:rgba(255,255,255,.18);
    --accent-blue:#4f8fff;--accent-violet:#7c6ff7;--accent-green:#22d98a;
    --accent-red:#f05252;--accent-amber:#f5a623;
    --text-primary:#f0f2f8;--text-secondary:#8892a4;--text-muted:#4e5669;
    --radius-sm:8px;--radius-md:14px;--radius-lg:20px;}
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
/* Match Dashboard layout — content auto-fits when sidebar collapses */
header{background:transparent!important;backdrop-filter:none!important;border:none!important;}
header[data-testid="stHeader"]{background:transparent!important;border-bottom:none!important;}
.block-container{padding-left:3rem!important;padding-right:3rem!important;padding-top:1.5rem!important;padding-bottom:2rem!important; max-width: 100% !important;}
[data-testid="stMain"]{flex:1 1 auto!important;min-width:0!important;width:100%!important;transition:width .3s ease, flex .3s ease!important;}
#MainMenu,footer{visibility:hidden;}
[data-testid="stSidebarNav"]{display:none!important;}
[data-testid="stAppDeployButton"]{display:none!important;}
h1,h2,h3{font-family:'Syne',sans-serif!important;color:var(--text-primary)!important;}
.stMarkdown p{color:var(--text-secondary);font-size:.84rem;}
.analytics-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-lg);
    padding:1.2rem 1.4rem;margin-bottom:.8rem;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
    box-shadow:0 4px 30px rgba(0,0,0,0.1);
    transition:border-color .25s ease, box-shadow .25s ease, transform .25s ease;
    animation: slideUpFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
    will-change:transform, box-shadow; position:relative; z-index:0;}
.analytics-card h4{font-family:'Syne',sans-serif;font-size:.72rem;font-weight:600;letter-spacing:.08em;
    text-transform:uppercase;color:var(--text-secondary);margin-bottom:.6rem;}
.analytics-card table td{padding:.28rem .4rem;font-size:.82rem;color:var(--text-secondary);}
.analytics-card table td:last-child{color:var(--text-primary);}
/* KPI cards — matches analytics-card but compact */
.analytics-kpi-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-md);
    padding:1rem 1.2rem;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
    box-shadow:0 4px 30px rgba(0,0,0,0.1);
    transition:border-color .25s ease, box-shadow .25s ease, transform .25s ease;
    animation: slideUpFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
    will-change:transform, box-shadow; position:relative; z-index:0;}
.analytics-kpi-card:hover{
    border-color:rgba(79,143,255,0.6) !important;
    box-shadow:0 0 30px rgba(79,143,255,0.25), 0 10px 40px rgba(0,0,0,0.4) !important;
    transform:translateY(-4px); z-index:10;}
.analytics-kpi-card .kpi-label{font-family:'DM Sans',sans-serif;font-size:.68rem;font-weight:600;
    letter-spacing:.09em;text-transform:uppercase;color:var(--text-secondary);margin-bottom:.35rem;}
.analytics-kpi-card .kpi-value{font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;
    color:var(--text-primary);line-height:1.15;}
.analytics-kpi-card .kpi-delta{font-family:'DM Sans',sans-serif;font-size:.78rem;font-weight:600;margin-top:.25rem;}
.metric-box{background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius-md);
    padding:1rem;text-align:center;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
    box-shadow:0 4px 30px rgba(0,0,0,0.1);
    transition:border-color .25s ease, box-shadow .25s ease, transform .25s ease;
    will-change:transform, box-shadow; position:relative; z-index:0;}
.metric-box h4{font-size:.68rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
    color:var(--text-secondary);margin:0 0 .4rem;}
.metric-box h2{font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:700;color:var(--text-primary);margin:0;}
.insight-text{background:rgba(245,166,35,.07);border-left:3px solid #f5a623;
    border-radius:0 var(--radius-sm) var(--radius-sm) 0;padding:.8rem 1rem;font-size:.82rem;color:#8892a4;}
.nav-group{font-size:.62rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;
    color:var(--text-muted)!important;padding:.5rem .4rem .2rem;}
.nav-item{display:flex;align-items:center;gap:9px;padding:.5rem .8rem;border-radius:var(--radius-sm);
    font-size:.83rem;font-weight:500;color:var(--text-secondary)!important;cursor:pointer;margin:2px 0;}
.nav-item:hover{background:rgba(255,255,255,.05);}
.nav-item.active{background:rgba(79,143,255,.15);color:var(--accent-blue)!important;font-weight:600;}
.stButton>button{background:var(--bg-elevated)!important;border:1px solid var(--border-active)!important;
    color:var(--text-secondary)!important;border-radius:var(--radius-sm)!important;
    font-size:.8rem!important;transition:all .15s!important;}
.stButton>button:hover{background:var(--accent-blue)!important;border-color:var(--accent-blue)!important;color:white!important;}
.stButton>button[kind="primary"]{background:var(--accent-blue)!important;border-color:var(--accent-blue)!important;color:white!important;}
.stSelectbox>div>div,.stTextInput>div>div>input,.stMultiSelect>div>div>div{background:var(--bg-elevated)!important;
    border:1px solid var(--border)!important;border-radius:var(--radius-sm)!important;color:white!important;}
span[data-baseweb="tag"] {background-color:rgba(79,143,255,0.2)!important;border:1px solid var(--accent-blue)!important;}
span[data-baseweb="tag"] * {color:white!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--bg-card)!important;border-radius:var(--radius-md)!important;
    gap:4px;padding:4px;border:1px solid var(--border)!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--text-secondary)!important;
    border-radius:var(--radius-sm)!important;font-size:.8rem!important;padding:6px 14px!important;}
.stTabs [aria-selected="true"]{background:var(--bg-elevated)!important;color:var(--text-primary)!important;font-weight:600!important;}
div[data-testid="stMetric"]{background:var(--bg-card);border:1px solid var(--border);
    border-radius:var(--radius-md);padding:.8rem 1rem;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);box-shadow:0 4px 30px rgba(0,0,0,0.1);}
div[data-testid="stMetric"] label{color:var(--text-secondary)!important;font-size:.68rem!important;
    letter-spacing:.06em;text-transform:uppercase;}
div[data-testid="stMetric"] [data-testid="stMetricValue"]{font-family:'Syne',sans-serif!important;
    color:var(--text-primary)!important;font-size:1.4rem!important;}
::-webkit-scrollbar{width:8px;height:8px;}
::-webkit-scrollbar-track{background:var(--bg-base);border-radius:10px;}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:10px;transition:background 0.2s;}
::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,0.2);}
/* Ensure Streamlit markdown wrappers don't clip hover shadows */
[data-testid="stMarkdownContainer"]{overflow:visible !important;}
[data-testid="stColumn"]{overflow:visible !important;}
/* ── Hover Glow Effects ── */
.analytics-card:hover{
    border-color:rgba(79,143,255,0.6) !important;
    box-shadow:0 0 30px rgba(79,143,255,0.25), 0 10px 40px rgba(0,0,0,0.4) !important;
    transform:translateY(-4px); z-index:10;}
.metric-box:hover{
    border-color:rgba(124,111,247,0.6) !important;
    box-shadow:0 0 30px rgba(124,111,247,0.25), 0 10px 40px rgba(0,0,0,0.4) !important;
    transform:translateY(-4px); z-index:10;}
div[data-testid="stMetric"]:hover{
    border-color:rgba(79,143,255,0.55) !important;
    box-shadow:0 0 26px rgba(79,143,255,0.2), 0 8px 36px rgba(0,0,0,0.35) !important;
    transform:translateY(-3px);}
div[data-testid="stMetric"]{
    transition:border-color .25s ease, box-shadow .25s ease, transform .25s ease;
    will-change:transform, box-shadow;}
""", unsafe_allow_html=True)

# ── JS: force stMain to expand when sidebar collapses (matches Dashboard) ─────
import streamlit.components.v1 as _components
_components.html("""
<script>
(function(){
    var doc = window.parent.document;
    function applyFlex(){
        var main = doc.querySelector('[data-testid="stMain"]');
        if(!main){ setTimeout(applyFlex, 200); return; }
        main.style.setProperty('flex','1 1 auto','important');
        main.style.setProperty('min-width','0','important');
        main.style.setProperty('transition','all 0.35s ease','important');
    }
    applyFlex();
    var obs = new MutationObserver(applyFlex);
    obs.observe(doc.body,{attributes:true,subtree:true,
        attributeFilter:['style','class','aria-expanded']});
})();
</script>
""", height=0)

DARK_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(28,32,48,0.5)",
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
    margin=dict(l=8, r=8, t=40, b=8),
)

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

# ── Data helpers ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def fetch_stock_data(symbol: str, period: str = "6mo") -> tuple:
    import random
    retries = 3
    for attempt in range(retries):
        try:
            stock = yf.Ticker(symbol)
            hist  = stock.history(period=period)
            if not hist.empty:
                try:
                    info = stock.info
                except Exception:
                    info = {}
                return hist, info
            # Empty on first try — try 5d fallback then give up
            hist5 = stock.history(period="5d")
            if not hist5.empty:
                try:
                    info = stock.info
                except Exception:
                    info = {}
                return hist5, info
            return None, {}
        except Exception as exc:
            err = str(exc).lower()
            if "too many requests" in err or "rate limit" in err or "429" in err:
                wait = (2 ** attempt) + random.uniform(0.5, 1.5)
                time.sleep(wait)
            else:
                return None, {}
    return None, {}


def calc_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Momentum"] = df["Close"] - df["Close"].shift(10)
    df["ROC"]      = (df["Close"] / df["Close"].shift(10) - 1) * 100
    hl = df["High"] - df["Low"]
    hc = (df["High"] - df["Close"].shift()).abs()
    lc = (df["Low"]  - df["Close"].shift()).abs()
    df["ATR"] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean()
    low_min  = df["Low"].rolling(14).min()
    high_max = df["High"].rolling(14).max()
    denom    = (high_max - low_min).replace(0, np.nan)
    df["Stoch_K"] = (100 * (df["Close"] - low_min) / denom).fillna(50)
    df["Stoch_D"] = df["Stoch_K"].rolling(3).mean()
    df["OBV"]     = (np.sign(df["Close"].diff()) * df["Volume"]).fillna(0).cumsum()
    df["MA20"]    = df["Close"].rolling(20).mean()
    df["MA50"]    = df["Close"].rolling(50).mean()
    delta  = df["Close"].diff()
    gain_  = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss_  = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    df["RSI"]    = (100 - (100 / (1 + gain_ / loss_.replace(0, np.nan)))).fillna(50)
    e1 = df["Close"].ewm(span=12, adjust=False).mean()
    e2 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"]   = e1 - e2
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    price_max = df["High"].max();  price_min = df["Low"].min()
    diff = price_max - price_min
    df["Fib_236"] = price_max - diff * 0.236
    df["Fib_382"] = price_max - diff * 0.382
    df["Fib_500"] = price_max - diff * 0.500
    df["Fib_618"] = price_max - diff * 0.618
    return df


def calc_risk(df: pd.DataFrame) -> dict:
    r  = df["Close"].pct_change().dropna()
    if len(r) == 0:
        return {
            "Annual Return": 0.0,
            "Annual Volatility": 0.0,
            "Sharpe Ratio": 0.0,
            "Max Drawdown": 0.0,
            "VaR (95%)": 0.0,
            "Sortino Ratio": 0.0,
        }
    ar = r.mean() * 252 * 100
    av = r.std()  * np.sqrt(252) * 100
    sr = ar / av if av else 0.0
    cum  = (1 + r).cumprod()
    mdd  = ((cum - cum.expanding().max()) / cum.expanding().max()).min() * 100
    var_ = float(np.percentile(r, 5)) * 100
    dr   = r[r < 0]
    dd   = dr.std() * np.sqrt(252) * 100 if len(dr) else 0.0
    sor  = ar / dd if dd else 0.0
    return {
        "Annual Return":     ar,
        "Annual Volatility": av,
        "Sharpe Ratio":      sr,
        "Max Drawdown":      mdd,
        "VaR (95%)":         var_,
        "Sortino Ratio":     sor,
    }


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem .4rem .4rem">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:1.2rem">
            <div style="width:34px;height:34px;background:linear-gradient(135deg,#7c6ff7,#4f8fff);
                border-radius:10px;display:flex;align-items:center;justify-content:center;
                font-weight:700;font-size:.85rem;color:white;font-family:'Syne',sans-serif">A</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:.95rem;
                color:#f0f2f8!important">Analytics</div>
        </div>
        <div class="nav-group">Platform</div>
        <a href="/" target="_self" class="nav-item" style="text-decoration:none;">Dashboard</a>
        <div class="nav-group" style="margin-top:.5rem">Pages</div>
        <a href="/Analytics" target="_self" class="nav-item active" style="text-decoration:none;">Analytics</a>
        <a href="/Portfolio" target="_self" class="nav-item" style="text-decoration:none;">Portfolio</a>
        <a href="/ML_Predictions" target="_self" class="nav-item" style="text-decoration:none;">ML Predictions</a>
        <a href="/Watchlist" target="_self" class="nav-item" style="text-decoration:none;">Watchlist & Alerts</a>
        <a href="/Backtesting" target="_self" class="nav-item" style="text-decoration:none;">Backtesting</a>
        <a href="/Heatmap" target="_self" class="nav-item" style="text-decoration:none;">Sector Heatmap</a>
    </div>
    <hr style="border-color:rgba(255,255,255,.06);margin:.6rem 0">
    """, unsafe_allow_html=True)

    # Stock dropdown — full company names
    stock_names  = list(STOCK_CATALOGUE.keys())
    chosen_name  = st.selectbox("Stock", stock_names, index=0)
    stock_symbol = STOCK_CATALOGUE[chosen_name]

    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

    # Compare-with multiselect using short names (tickers)
    tickers = list(STOCK_CATALOGUE.values())
    compare_stocks = st.multiselect(
        "Compare With",
        tickers,
        default=["AAPL", "MSFT"],
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:.8rem 0 .4rem">
    <div style="font-family:'Syne',sans-serif;font-size:1.7rem;font-weight:800;
        color:#f0f2f8;line-height:1">Advanced Stock Analytics</div>
    <div style="font-size:.82rem;color:#8892a4;margin-top:.3rem">
        Deep dive into technical analysis, risk metrics and market insights</div>
</div>
""", unsafe_allow_html=True)

if not stock_symbol:
    st.markdown(
        '<div class="analytics-card" style="text-align:center;padding:2rem;color:#8892a4">'
        "Enter a stock symbol to begin analysis</div>",
        unsafe_allow_html=True,
    )
    st.stop()

with st.spinner(f"Analysing {stock_symbol}…"):
    df, info = fetch_stock_data(stock_symbol, period)

if df is None or df.empty:
    st.error("Could not fetch data. Check the symbol and try again.")
    st.stop()

df    = calc_indicators(df)
risk  = calc_risk(df)
cur_p = float(df["Close"].iloc[-1])
if len(df["Close"]) >= 2:
    prev_p = float(df["Close"].iloc[-2])
    chg    = cur_p - prev_p
    chg_p  = (chg / prev_p) * 100 if prev_p else 0.0
else:
    chg = 0.0
    chg_p = 0.0

# ── Key metrics ───────────────────────────────────────────────────────────────
mc1, mc2, mc3, mc4 = st.columns(4)
chg_color = "#22d98a" if chg_p >= 0 else "#f05252"
chg_arrow = "▲" if chg_p >= 0 else "▼"
for col, lbl, val, delta_html in [
    (mc1, "Current Price", f"${cur_p:.2f}",
     f'<div class="kpi-delta" style="color:{chg_color}">{chg_arrow} {chg_p:+.2f}%</div>'),
    (mc2, "Volume", f"{df['Volume'].iloc[-1]:,.0f}", ""),
    (mc3, "52W High", f"${info.get('fiftyTwoWeekHigh', 0):.2f}", ""),
    (mc4, "52W Low",  f"${info.get('fiftyTwoWeekLow',  0):.2f}", ""),
]:
    with col:
        st.markdown(f"""
        <div class="analytics-kpi-card">
            <div class="kpi-label">{lbl}</div>
            <div class="kpi-value">{val}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

tab1, tab_options, tab2, tab3, tab4, tab5 = st.tabs(
    ["Technical", "Options", "Risk", "Correlation", "Price Levels", "AI Signals"]
)

# ── Tab 1 — Technical ─────────────────────────────────────────────────────────
with tab1:
    st.markdown(
        "<div style=\"font-family:'Syne',sans-serif;font-size:.85rem;font-weight:700;"
        "color:#f0f2f8;margin-bottom:.5rem\">Technical Indicators Dashboard</div>",
        unsafe_allow_html=True,
    )
    show_patterns = st.toggle("🔍 Auto-Detect Chart Patterns (Head & Shoulders, Double Top, Flags)", value=True)
    fig = make_subplots(
        rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.04,
        row_heights=[0.3, 0.2, 0.2, 0.15, 0.15],
        subplot_titles=("Price & MAs", "RSI", "Stochastic", "MACD", "OBV"),
    )
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close",
                             line=dict(color="#4f8fff", width=1.8)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MA20"],  name="MA20",
                             line=dict(color="#f5a623", width=1.2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MA50"],  name="MA50",
                             line=dict(color="#7c6ff7", width=1.2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"],   name="RSI",
                             line=dict(color="#4f8fff", width=1.5)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="#f05252", opacity=.5, row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="#22d98a", opacity=.5, row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["Stoch_K"], name="K",
                             line=dict(color="#4f8fff", width=1.2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["Stoch_D"], name="D",
                             line=dict(color="#f5a623", width=1.2)), row=3, col=1)
    fig.add_hline(y=80, line_dash="dot", line_color="#f05252", opacity=.5, row=3, col=1)
    fig.add_hline(y=20, line_dash="dot", line_color="#22d98a", opacity=.5, row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"],   name="MACD",
                             line=dict(color="#4f8fff", width=1.2)), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["Signal"], name="Signal",
                             line=dict(color="#f5a623", width=1.2)), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["OBV"],    name="OBV",
                             line=dict(color="#22d98a", width=1.2)), row=5, col=1)
    if show_patterns:
        try:
            close_vals = df['Close'].values
            dates = df.index
            
            def get_peaks(arr, distance=7, prominence=0):
                peaks = []
                for i in range(distance, len(arr) - distance):
                    window = arr[i-distance:i+distance+1]
                    if arr[i] == max(window) and (arr[i] - min(window)) >= prominence:
                        if not peaks or i - peaks[-1] >= distance:
                            peaks.append(i)
                return peaks

            prominence = close_vals.mean() * 0.025
            peaks = get_peaks(close_vals, distance=7, prominence=prominence)
            troughs = get_peaks(-close_vals, distance=7, prominence=prominence)
            
            # Double Tops
            for i in range(len(peaks) - 1):
                p1, p2 = peaks[i], peaks[i+1]
                if abs(close_vals[p1] - close_vals[p2]) / close_vals[p1] < 0.03:
                    btwn = [t for t in troughs if p1 < t < p2]
                    if btwn and (close_vals[p1] - close_vals[min(btwn)]) / close_vals[p1] > 0.04:
                        fig.add_shape(type="line", x0=dates[p1], y0=close_vals[p1], x1=dates[p2], y1=close_vals[p2], line=dict(color="#f05252", width=3, dash="dot"), row=1, col=1)
                        fig.add_annotation(x=dates[p2], y=close_vals[p2]*1.03, text="Double Top", showarrow=False, font=dict(color="#f05252", size=11, family="Syne", weight="bold"), row=1, col=1)

            # Head & Shoulders
            for i in range(len(peaks) - 2):
                p1, p2, p3 = peaks[i], peaks[i+1], peaks[i+2]
                if close_vals[p2] > close_vals[p1] and close_vals[p2] > close_vals[p3]:
                    if abs(close_vals[p1] - close_vals[p3]) / close_vals[p1] < 0.04:
                        fig.add_trace(go.Scatter(x=[dates[p1], dates[p2], dates[p3]], y=[close_vals[p1], close_vals[p2], close_vals[p3]], mode="lines+markers", line=dict(color="#f5a623", width=2), name="Head & Shoulders", showlegend=False), row=1, col=1)
                        fig.add_annotation(x=dates[p2], y=close_vals[p2]*1.04, text="Head & Shoulders", showarrow=False, font=dict(color="#f5a623", size=11, family="Syne", weight="bold"), row=1, col=1)

            # Bull Flags
            for i in range(10, len(close_vals) - 10):
                if (close_vals[i] - close_vals[i-10]) / close_vals[i-10] > 0.12:
                    if -0.08 < (close_vals[i+10] - close_vals[i]) / close_vals[i] < 0.02:
                        fig.add_shape(type="rect", x0=dates[i], y0=min(close_vals[i:i+10]), x1=dates[i+10], y1=max(close_vals[i:i+10]), fillcolor="rgba(34,217,138,0.15)", line=dict(color="#22d98a", width=1.5, dash="dot"), row=1, col=1)
                        fig.add_annotation(x=dates[i+5], y=max(close_vals[i:i+10])*1.04, text="Bull Flag", showarrow=False, font=dict(color="#22d98a", size=11, family="Syne", weight="bold"), row=1, col=1)
        except Exception as e:
            pass

    fig.update_layout(
        height=1000, showlegend=True,
        title=f"{stock_symbol} — {chosen_name}",
        title_font=dict(family="Syne", size=13, color="#f0f2f8"), **DARK_LAYOUT,
    )
    for ann in fig.layout.annotations:
        ann.font.size = 10; ann.font.color = "#8892a4"
    st.plotly_chart(fig, use_container_width=True)

    ic1, ic2, ic3, ic4 = st.columns(4)
    rsi_v = float(df["RSI"].iloc[-1])
    rsi_s = "Overbought" if rsi_v > 70 else "Oversold" if rsi_v < 30 else "Neutral"
    rsi_c = "#f05252" if rsi_v > 70 else "#22d98a" if rsi_v < 30 else "#f5a623"
    macd_val = float(df["MACD"].iloc[-1])
    macd_bull = macd_val > float(df["Signal"].iloc[-1])
    for col, lbl, val, sub, sub_color in [
        (ic1, "RSI (14)",  f"{rsi_v:.1f}",                  rsi_s,          rsi_c),
        (ic2, "Stoch K",   f"{df['Stoch_K'].iloc[-1]:.1f}", "",             ""),
        (ic3, "MACD",      f"{macd_val:.4f}",
             "▲ Bullish" if macd_bull else "▼ Bearish",
             "#22d98a" if macd_bull else "#f05252"),
        (ic4, "ATR",       f"${df['ATR'].iloc[-1]:.2f}",    "Volatility",   "#8892a4"),
    ]:
        with col:
            delta_html = f'<div class="kpi-delta" style="color:{sub_color}">{sub}</div>' if sub else ""
            st.markdown(f"""
            <div class="analytics-kpi-card">
                <div class="kpi-label">{lbl}</div>
                <div class="kpi-value">{val}</div>
                {delta_html}
            </div>
            """, unsafe_allow_html=True)

# ── Tab Options ───────────────────────────────────────────────────────────────
with tab_options:
    st.markdown(
        "<div style=\"font-family:'Syne',sans-serif;font-size:.85rem;font-weight:700;"
        "color:#f0f2f8;margin-bottom:.6rem\">Options Chain — Black-Scholes Greeks · Live Data</div>",
        unsafe_allow_html=True,
    )
    import math
    from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

    def norm_cdf(x):
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    def norm_pdf(x):
        return math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)

    def calc_greeks(S, K, T, r, sigma, opt_type):
        if T <= 0 or sigma <= 0: return 0.0, 0.0
        try:
            d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
            d2 = d1 - sigma * math.sqrt(T)
            if opt_type == 'call':
                delta = norm_cdf(d1)
                theta = (- (S * norm_pdf(d1) * sigma) / (2 * math.sqrt(T))
                         - r * K * math.exp(-r * T) * norm_cdf(d2)) / 365.0
            else:
                delta = norm_cdf(d1) - 1.0
                theta = (- (S * norm_pdf(d1) * sigma) / (2 * math.sqrt(T))
                         + r * K * math.exp(-r * T) * norm_cdf(-d2)) / 365.0
            return round(delta, 3), round(theta, 4)
        except Exception:
            return 0.0, 0.0

    _opt_css = {
        ".ag-root-wrapper": {"background-color": "var(--bg-card) !important", "border": "1px solid var(--border) !important", "border-radius": "14px", "overflow": "hidden"},
        ".ag-header": {"background-color": "rgba(255,255,255,0.03) !important", "border-bottom": "1px solid var(--border) !important"},
        ".ag-header-group-cell-label": {"color": "var(--text-primary) !important", "font-weight": "700", "font-family": "'Syne', sans-serif", "font-size": "0.85rem", "justify-content": "center"},
        ".ag-header-cell-label": {"color": "var(--text-secondary) !important", "font-weight": "600", "font-family": "'Syne', sans-serif", "font-size": "0.72rem", "text-transform": "uppercase", "letter-spacing": "0.05em", "justify-content": "center"},
        ".ag-row": {"background-color": "transparent !important", "border-bottom": "1px solid rgba(255,255,255,0.03) !important", "color": "var(--text-primary) !important"},
        ".ag-row-hover": {"background-color": "rgba(255,255,255,0.05) !important"},
        ".ag-cell": {"font-family": "'DM Sans', sans-serif", "font-size": "0.85rem", "display": "flex", "align-items": "center", "justify-content": "center", "border-right": "1px solid rgba(255,255,255,0.02)"},
        ".ag-cell-value": {"color": "var(--text-primary) !important"},
        ".ag-paging-panel": {"background-color": "transparent !important", "border-top": "1px solid var(--border) !important", "color": "var(--text-secondary) !important"},
    }

    try:
        opt_tk    = yf.Ticker(stock_symbol)
        opt_dates = opt_tk.options
        if opt_dates:
            col_exp, col_price = st.columns([2, 1])
            with col_exp:
                sel_date = st.selectbox("Expiration Date", opt_dates, key="opt_date_sel")
            try:
                S_price = float(opt_tk.fast_info.last_price)
            except Exception:
                S_price = float(opt_tk.info.get('regularMarketPrice') or opt_tk.info.get('currentPrice', 0))
            with col_price:
                st.markdown(f"""
                <div style="background:rgba(34,217,138,0.08);border:1px solid rgba(34,217,138,0.2);
                    border-radius:10px;padding:.6rem 1rem;text-align:center;margin-top:1.5rem">
                    <div style="font-size:.65rem;color:#8892a4;font-weight:600;letter-spacing:.08em;text-transform:uppercase">Underlying Price</div>
                    <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:#22d98a">${S_price:.2f}</div>
                </div>""", unsafe_allow_html=True)

            chain  = opt_tk.option_chain(sel_date)
            dt_str = datetime.strptime(sel_date, "%Y-%m-%d").date()
            T_days = max((dt_str - datetime.now().date()).days / 365.0, 0.001)

            if S_price > 0:
                st.markdown('<div style="font-size:0.8rem; font-weight:600; color:var(--text-secondary); margin-bottom:0.3rem">DISPLAY SETTINGS</div>', unsafe_allow_html=True)
                show_all_strikes = st.toggle("Show Deep OTM Strikes", value=False)

                calls = chain.calls[['strike','lastPrice','bid','ask','volume','openInterest','impliedVolatility','inTheMoney']].copy()
                puts  = chain.puts[['strike','lastPrice','bid','ask','volume','openInterest','impliedVolatility','inTheMoney']].copy()
                
                calls.columns = ['Strike', 'C_Last', 'C_Bid', 'C_Ask', 'C_Vol', 'C_OI', 'C_IV', 'C_ITM']
                puts.columns  = ['Strike', 'P_Last', 'P_Bid', 'P_Ask', 'P_Vol', 'P_OI', 'P_IV', 'P_ITM']
                
                df_chain = pd.merge(calls, puts, on='Strike', how='outer').sort_values('Strike').reset_index(drop=True)

                # Trim to Active Zone (±15% of Underlying) unless user wants all
                if not show_all_strikes:
                    lower_bound = S_price * 0.85
                    upper_bound = S_price * 1.15
                    df_chain = df_chain[(df_chain['Strike'] >= lower_bound) & (df_chain['Strike'] <= upper_bound)].reset_index(drop=True)
                
                df_chain['C_IV_pct'] = df_chain['C_IV'] * 100
                df_chain['P_IV_pct'] = df_chain['P_IV'] * 100
                df_chain['C_Delta'] = 0.0; df_chain['C_Theta'] = 0.0
                df_chain['P_Delta'] = 0.0; df_chain['P_Theta'] = 0.0
                
                # Calculate Greeks
                for idx, row in df_chain.iterrows():
                    call_delta, call_theta = calc_greeks(S_price, row['Strike'], T_days, 0.045, row.get('C_IV', 0.0), 'call')
                    put_delta, put_theta = calc_greeks(S_price, row['Strike'], T_days, 0.045, row.get('P_IV', 0.0), 'put')
                    df_chain.at[idx, 'C_Delta'] = call_delta
                    df_chain.at[idx, 'C_Theta'] = call_theta
                    df_chain.at[idx, 'P_Delta'] = put_delta
                    df_chain.at[idx, 'P_Theta'] = put_theta
                
                display = df_chain[['C_OI','C_Vol','C_IV_pct','C_Theta','C_Delta','C_Last','C_Bid','C_Ask', 'C_ITM',
                                    'Strike',
                                    'P_Bid','P_Ask','P_Last','P_Delta','P_Theta','P_IV_pct','P_Vol','P_OI', 'P_ITM']].copy()
                
                gb = GridOptionsBuilder.from_dataframe(display)
                
                call_bg = "function(p){if(p.data.C_ITM===true){return {backgroundColor:'rgba(34,217,138,0.08)'}}; return null;}"
                put_bg  = "function(p){if(p.data.P_ITM===true){return {backgroundColor:'rgba(240,82,82,0.08)'}}; return null;}"
                
                def fmt_num(field, decimals=2, fallback="'—'"): return f"data.{field} != null && !isNaN(data.{field}) ? Number(data.{field}).toFixed({decimals}) : {fallback}"
                def fmt_vol(field): return f"data.{field} != null && !isNaN(data.{field}) ? Number(data.{field}).toLocaleString() : '0'"
                
                # Calls cols
                gb.configure_column("C_OI",     headerName="OI",    valueFormatter=fmt_vol("C_OI"), width=75, minWidth=65, cellStyle=JsCode(call_bg))
                gb.configure_column("C_Vol",    headerName="VOL",   valueFormatter=fmt_vol("C_Vol"), width=75, minWidth=65, cellStyle=JsCode(call_bg))
                gb.configure_column("C_IV_pct", headerName="IV %",  valueFormatter=f"data.C_IV_pct != null && !isNaN(data.C_IV_pct) ? Number(data.C_IV_pct).toFixed(1)+'%' : '—'", width=75, minWidth=65, cellStyle=JsCode(call_bg))
                gb.configure_column("C_Theta",  headerName="Theta", valueFormatter=fmt_num("C_Theta",4), width=80, minWidth=70, cellStyle=JsCode(f"function(p){{ let s = ({call_bg})(p) || {{}}; s.color = '#f5a623'; return s; }}"))
                gb.configure_column("C_Delta",  headerName="Delta", valueFormatter=fmt_num("C_Delta",3), width=80, minWidth=70, cellStyle=JsCode(f"function(p){{ let s = ({call_bg})(p) || {{}}; let v=p.value; s.color=v>0?'#22d98a':v<0?'#f05252':'#8892a4'; return s; }}"))
                gb.configure_column("C_Last",   headerName="LTP",   valueFormatter=fmt_num("C_Last"), width=80, minWidth=75, cellStyle=JsCode(f"function(p){{ let s = ({call_bg})(p) || {{}}; s.color = 'var(--text-primary)'; s.fontWeight='600'; return s; }}"))
                gb.configure_column("C_Bid",    headerName="BID",   valueFormatter=fmt_num("C_Bid"), width=80, minWidth=75, cellStyle=JsCode(call_bg))
                gb.configure_column("C_Ask",    headerName="ASK",   valueFormatter=fmt_num("C_Ask"), width=80, minWidth=75, cellStyle=JsCode(call_bg))
                gb.configure_column("C_ITM",    hide=True)
                
                # Strike (Removed pinned='left' to allow it to be center)
                gb.configure_column("Strike",   headerName="STRIKE", width=95, minWidth=90, cellStyle={'backgroundColor': 'rgba(28,32,48,0.8)', 'color': 'var(--text-primary)', 'fontWeight': '700', 'textAlign': 'center'})
                
                # Puts cols
                gb.configure_column("P_Bid",    headerName="BID",   valueFormatter=fmt_num("P_Bid"), width=80, minWidth=75, cellStyle=JsCode(put_bg))
                gb.configure_column("P_Ask",    headerName="ASK",   valueFormatter=fmt_num("P_Ask"), width=80, minWidth=75, cellStyle=JsCode(put_bg))
                gb.configure_column("P_Last",   headerName="LTP",   valueFormatter=fmt_num("P_Last"), width=80, minWidth=75, cellStyle=JsCode(f"function(p){{ let s = ({put_bg})(p) || {{}}; s.color = 'var(--text-primary)'; s.fontWeight='600'; return s; }}"))
                gb.configure_column("P_Delta",  headerName="Delta", valueFormatter=fmt_num("P_Delta",3), width=80, minWidth=70, cellStyle=JsCode(f"function(p){{ let s = ({put_bg})(p) || {{}}; let v=p.value; s.color=v>0?'#22d98a':v<0?'#f05252':'#8892a4'; return s; }}"))
                gb.configure_column("P_Theta",  headerName="Theta", valueFormatter=fmt_num("P_Theta",4), width=80, minWidth=70, cellStyle=JsCode(f"function(p){{ let s = ({put_bg})(p) || {{}}; s.color = '#f5a623'; return s; }}"))
                gb.configure_column("P_IV_pct", headerName="IV %",  valueFormatter=f"data.P_IV_pct != null && !isNaN(data.P_IV_pct) ? Number(data.P_IV_pct).toFixed(1)+'%' : '—'", width=75, minWidth=65, cellStyle=JsCode(put_bg))
                gb.configure_column("P_Vol",    headerName="VOL",   valueFormatter=fmt_vol("P_Vol"), width=75, minWidth=65, cellStyle=JsCode(put_bg))
                gb.configure_column("P_OI",     headerName="OI",    valueFormatter=fmt_vol("P_OI"), width=75, minWidth=65, cellStyle=JsCode(put_bg))
                gb.configure_column("P_ITM",    hide=True)
                
                gb.configure_grid_options(rowHeight=36)
                gridOpts = gb.build()
                
                # Create Column Groups matching NSE format
                cols = gridOpts['columnDefs']
                c_cols = [c for c in cols if c['field'].startswith('C_')]
                p_cols = [c for c in cols if c['field'].startswith('P_')]
                s_col  = [c for c in cols if c['field'] == 'Strike'][0]
                
                # Make sure Strike column doesn't have pinned attribute cached
                if 'pinned' in s_col:
                    del s_col['pinned']

                gridOpts['columnDefs'] = [
                    {'headerName': 'CALLS', 'children': c_cols},
                    s_col,
                    {'headerName': 'PUTS', 'children': p_cols}
                ]

                from st_aggrid import ColumnsAutoSizeMode

                st.markdown("<div class='animate-enter'>", unsafe_allow_html=True)
                AgGrid(
                    display, 
                    height=550,
                    gridOptions=gridOpts, 
                    allow_unsafe_jscode=True, 
                    theme="alpine", 
                    custom_css=_opt_css, 
                    key='opt_unified_v2',
                    fit_columns_on_grid_load=False,
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW
                )
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("""
                <div style="margin-top:.6rem;font-size:.7rem;color:#4e5669;text-align:right">
                    ✦ Highlighted background = In-The-Money &nbsp;·&nbsp; Greeks via Black-Scholes (r=4.5%)
                </div>""", unsafe_allow_html=True)
            else:
                st.warning("Current stock price unavailable for options calculations.")
        else:
            st.info("No options data available for this symbol.")
    except Exception as e:
        st.warning(f"Failed to load options data: {e}")

# ── Tab 2 — Risk ──────────────────────────────────────────────────────────────
with tab2:
    st.markdown(
        "<div style=\"font-family:'Syne',sans-serif;font-size:.85rem;font-weight:700;"
        "color:#f0f2f8;margin-bottom:.6rem\">Risk Metrics Analysis</div>",
        unsafe_allow_html=True,
    )
    rc1, rc2, rc3 = st.columns(3)
    for col, lbl, val in [
        (rc1, "Annual Return",     f"{risk['Annual Return']:+.2f}%"),
        (rc2, "Annual Volatility", f"{risk['Annual Volatility']:.2f}%"),
        (rc3, "Sharpe Ratio",      f"{risk['Sharpe Ratio']:.2f}"),
    ]:
        col.markdown(
            f'<div class="metric-box"><h4>{lbl}</h4><h2>{val}</h2></div>',
            unsafe_allow_html=True,
        )
    rc4, rc5, rc6 = st.columns(3)
    for col, lbl, val in [
        (rc4, "Max Drawdown",  f"{risk['Max Drawdown']:.2f}%"),
        (rc5, "VaR (95%)",     f"{risk['VaR (95%)']:.2f}%"),
        (rc6, "Sortino Ratio", f"{risk['Sortino Ratio']:.2f}"),
    ]:
        col.markdown(
            f'<div class="metric-box"><h4>{lbl}</h4><h2>{val}</h2></div>',
            unsafe_allow_html=True,
        )

    rs = 0
    rs += 30 if risk["Annual Volatility"] > 40 else 20 if risk["Annual Volatility"] > 25 else 10
    rs += 30 if risk["Max Drawdown"] < -30 else 20 if risk["Max Drawdown"] < -15 else 10
    rs += 20 if risk["Sharpe Ratio"] < 1 else 0
    rl = "High" if rs > 60 else "Medium" if rs > 30 else "Low"
    rc = "#f05252" if rl == "High" else "#f5a623" if rl == "Medium" else "#22d98a"
    st.markdown(f"""
    <div class="insight-text" style="margin-top:.8rem">
        <strong style="color:#f0f2f8">Risk Level: <span style="color:{rc}">{rl}</span></strong><br>
        Overall risk score: {rs}/100 &nbsp;·&nbsp;
        {'High volatility detected' if rl=='High'
         else 'Moderate risk profile' if rl=='Medium'
         else 'Low risk profile'}
    </div>
    """, unsafe_allow_html=True)

    rv = df["Close"].pct_change().rolling(20).std() * np.sqrt(252) * 100
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df.index, y=rv, name="20d Volatility",
        fill="tozeroy", line=dict(color="#f5a623", width=2),
        fillcolor="rgba(245,166,35,.08)",
    ))
    fig2.update_layout(
        height=300, title="Historical Volatility (20-day)",
        title_font=dict(family="Syne", size=13, color="#f0f2f8"), **DARK_LAYOUT,
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Tab 3 — Correlation ───────────────────────────────────────────────────────
with tab3:
    if compare_stocks:
        all_closes: dict[str, pd.Series] = {}
        for sym in list(set(compare_stocks + [stock_symbol])):
            sd, _ = fetch_stock_data(sym, period)
            if sd is not None:
                all_closes[sym] = sd["Close"]
        if len(all_closes) > 1:
            corr = pd.DataFrame(all_closes).corr()
            fig3 = px.imshow(
                corr, text_auto=True,
                color_continuous_scale=["#f05252", "#1c2030", "#4f8fff"],
                zmin=-1, zmax=1, title="Correlation Matrix",
            )
            fig3.update_layout(
                height=400,
                title_font=dict(family="Syne", size=13, color="#f0f2f8"), **DARK_LAYOUT,
            )
            st.plotly_chart(fig3, use_container_width=True)
            for sym in compare_stocks:
                if sym in corr.columns:
                    cv = float(corr.loc[stock_symbol, sym])
                    strength  = "Strong" if abs(cv) > 0.7 else "Moderate" if abs(cv) > 0.3 else "Weak"
                    direction = "positive" if cv > 0 else "negative"
                    st.markdown(
                        f"<div style='font-size:.82rem;color:#8892a4;padding:.3rem 0;"
                        f"border-bottom:1px solid rgba(255,255,255,.05)'>"
                        f"→ <strong style='color:#f0f2f8'>{stock_symbol} vs {sym}</strong>: "
                        f"{cv:.2f} — {strength} {direction} correlation</div>",
                        unsafe_allow_html=True,
                    )
        else:
            st.info("Not enough data to build a correlation matrix.")
    else:
        st.info("Select comparison stocks in the sidebar.")

# ── Tab 4 — Price Levels ──────────────────────────────────────────────────────
with tab4:
    fib  = df[["Fib_236", "Fib_382", "Fib_500", "Fib_618"]].iloc[-1]
    r_hi = float(df["High"].tail(20).max())
    r_lo = float(df["Low"].tail(20).min())
    pos  = ((cur_p - r_lo) / (r_hi - r_lo) * 100) if r_hi != r_lo else 0.0

    fc1, fc2 = st.columns(2)
    fc1.markdown(f"""
    <div class="analytics-card">
        <h4>Fibonacci Retracement</h4>
        <table style="width:100%">
            <tr><td>23.6%</td><td>${fib['Fib_236']:.2f}</td></tr>
            <tr><td>38.2%</td><td>${fib['Fib_382']:.2f}</td></tr>
            <tr><td>50.0%</td><td>${fib['Fib_500']:.2f}</td></tr>
            <tr><td>61.8%</td><td>${fib['Fib_618']:.2f}</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    fc2.markdown(f"""
    <div class="analytics-card">
        <h4>Support &amp; Resistance (20d)</h4>
        <table style="width:100%">
            <tr><td>Resistance</td><td>${r_hi:.2f}</td></tr>
            <tr><td>Support</td><td>${r_lo:.2f}</td></tr>
            <tr><td>Price Position</td><td>{pos:.1f}% of range</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Price",
                              line=dict(color="#4f8fff", width=2)))
    for level, color, label in [
        (fib["Fib_236"], "#f5a623", "23.6%"),
        (fib["Fib_382"], "#f05252", "38.2%"),
        (fib["Fib_500"], "#8892a4", "50.0%"),
        (fib["Fib_618"], "#22d98a", "61.8%"),
    ]:
        fig4.add_hline(
            y=float(level), line_dash="dot", line_color=color, opacity=0.7,
            annotation_text=label, annotation_font=dict(color=color, size=10),
        )
    fig4.update_layout(
        height=400, title="Fibonacci Retracement Levels",
        title_font=dict(family="Syne", size=13, color="#f0f2f8"), **DARK_LAYOUT,
    )
    st.plotly_chart(fig4, use_container_width=True)

# ── Tab 5 — AI Signals ────────────────────────────────────────────────────────
with tab5:
    signals: list[tuple[str, str, float]] = []
    rsi_v = float(df["RSI"].iloc[-1])
    if   rsi_v < 30: signals.append(("BUY",     "RSI oversold",           0.80))
    elif rsi_v > 70: signals.append(("SELL",    "RSI overbought",          0.80))
    else:            signals.append(("NEUTRAL", "RSI neutral",             0.50))

    macd_v = float(df["MACD"].iloc[-1]);  sig_v = float(df["Signal"].iloc[-1])
    if   macd_v > sig_v: signals.append(("BUY",     "MACD bullish crossover",  0.70))
    elif macd_v < sig_v: signals.append(("SELL",    "MACD bearish crossover",  0.70))
    else:                signals.append(("NEUTRAL", "MACD flat",               0.50))

    ma20 = float(df["MA20"].iloc[-1]);  ma50 = float(df["MA50"].iloc[-1])
    if   ma20 > ma50: signals.append(("BUY",     "Golden cross (MA20>MA50)",  0.75))
    elif ma20 < ma50: signals.append(("SELL",    "Death cross (MA20<MA50)",   0.75))
    else:             signals.append(("NEUTRAL", "MAs aligned",               0.50))

    stk = float(df["Stoch_K"].iloc[-1])
    if   stk < 20: signals.append(("BUY",     "Stochastic oversold",   0.65))
    elif stk > 80: signals.append(("SELL",    "Stochastic overbought",  0.65))
    else:          signals.append(("NEUTRAL", "Stochastic neutral",     0.50))

    buys  = sum(1 for s in signals if s[0] == "BUY")
    sells = sum(1 for s in signals if s[0] == "SELL")
    if buys > sells:
        overall, oc = ("STRONG BUY" if buys - sells >= 2 else "BUY"), "#22d98a"
    elif sells > buys:
        overall, oc = ("STRONG SELL" if sells - buys >= 2 else "SELL"), "#f05252"
    else:
        overall, oc = "NEUTRAL", "#f5a623"

    st.markdown(f"""
    <div style="background:rgba(19,22,30,1);border:1px solid {oc}33;
        border-radius:var(--radius-lg);padding:2rem;text-align:center;margin-bottom:.8rem">
        <div style="font-size:.72rem;font-weight:600;letter-spacing:.1em;
            text-transform:uppercase;color:#4e5669;margin-bottom:.4rem">
            Overall Trading Signal</div>
        <div style="font-family:'Syne',sans-serif;font-size:2.8rem;
            font-weight:800;color:{oc};line-height:1">{overall}</div>
        <div style="font-size:.8rem;color:#4e5669;margin-top:.4rem">
            Based on {len(signals)} technical indicators</div>
    </div>
    """, unsafe_allow_html=True)

    for s_type, reason, conf in signals:
        color = "#22d98a" if s_type == "BUY" else "#f05252" if s_type == "SELL" else "#f5a623"
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
            padding:.6rem .8rem;background:#1c2030;border:1px solid rgba(255,255,255,.06);
            border-radius:var(--radius-sm);margin-bottom:.3rem;font-size:.8rem">
            <span style="color:{color};font-weight:600;min-width:90px">{s_type}</span>
            <span style="color:#8892a4;flex:1;padding:0 1rem">{reason}</span>
            <span style="color:#4e5669">{conf*100:.0f}% confidence</span>
        </div>
        """, unsafe_allow_html=True)

    mom  = float(df["Momentum"].tail(5).mean()) if "Momentum" in df.columns else 0.0
    pred = cur_p * (1.02 if mom > 0 else 0.98)
    direction = "upward" if mom > 0 else "downward"
    st.markdown(f"""
    <div class="insight-text" style="margin-top:.8rem">
        <strong style="color:#f0f2f8">AI Price Prediction</strong><br>
        Momentum suggests
        <strong style="color:{'#22d98a' if mom > 0 else '#f05252'}">{direction}</strong> movement.<br>
        Predicted range: <strong>${pred - cur_p*.02:.2f} – ${pred + cur_p*.02:.2f}</strong><br>
        <span style="font-size:.75rem;opacity:.7">Model prediction only — not financial advice.</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:1.2rem 0 .3rem;font-size:.72rem;color:#4e5669">
    Data by Yahoo Finance &nbsp;·&nbsp; For educational purposes only
</div>
""", unsafe_allow_html=True)
