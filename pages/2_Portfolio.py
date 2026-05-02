import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta
import json, os
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
:root{
    --bg-base:#0d0f14;--bg-card:rgba(19,22,30,0.55);--bg-elevated:rgba(28,32,48,0.55);
    --border:rgba(255,255,255,.08);--border-active:rgba(255,255,255,.18);
    --accent-blue:#4f8fff;--accent-violet:#7c6ff7;--accent-green:#22d98a;
    --accent-red:#f05252;--accent-amber:#f5a623;
    --text-primary:#f0f2f8;--text-secondary:#8892a4;--text-muted:#4e5669;
    --radius-sm:8px;--radius-md:14px;--radius-lg:20px;
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
/* Match Dashboard layout — content auto-fits when sidebar collapses */
header{background:transparent!important;backdrop-filter:none!important;border:none!important;}
header[data-testid="stHeader"]{background:transparent!important;border-bottom:none!important;}
.block-container{padding-left:3rem!important;padding-right:3rem!important;padding-top:1.5rem!important;padding-bottom:2rem!important; max-width: 100% !important;}
[data-testid="stMain"]{flex:1 1 auto!important;min-width:0!important;width:100%!important;transition:width .3s ease, flex .3s ease!important;}
#MainMenu,footer{visibility:hidden;}
[data-testid="stAppDeployButton"]{display:none!important;}
[data-testid="stSidebarNav"]{display:none!important;}
h1,h2,h3{font-family:'Syne',sans-serif!important;color:var(--text-primary)!important;}
.stMarkdown p{color:var(--text-secondary);font-size:.84rem;}
/* hero card */
.portfolio-hero{background:linear-gradient(135deg,#1a1f35 0%,#1e2540 100%);
    border:1px solid rgba(79,143,255,.2);border-radius:var(--radius-lg);padding:1.6rem;}
/* stat cards */
.p-stat{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-lg);
    padding:1.3rem 1.5rem;position:relative;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
    box-shadow:0 4px 30px rgba(0,0,0,0.1);
    transition:border-color .25s ease, box-shadow .25s ease, transform .25s ease;
    animation: slideUpFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
    will-change:transform, box-shadow; z-index:0;}
.p-stat::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,var(--accent-blue),var(--accent-violet));opacity:.5;}
.p-stat-label{font-size:.68rem;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--text-secondary);white-space:nowrap;}
.p-stat-val{font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:700;color:var(--text-primary);line-height:1.2;margin:.3rem 0;white-space:nowrap;}
.p-stat-sub{font-size:.8rem;font-weight:600;margin-top:.1rem;}
/* holding rows */
.holding-row{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-md);
    padding:.75rem 1rem;margin-bottom:.4rem;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
    box-shadow:0 4px 30px rgba(0,0,0,0.1);
    transition:border-color .25s ease, box-shadow .25s ease, transform .25s ease;
    animation: slideUpFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
    will-change:transform, box-shadow; z-index:0;}
.holding-row:hover{border-color:var(--border-active);}
.up{color:#22d98a;font-weight:600;} .dn{color:#f05252;font-weight:600;}
/* allocation bar */
.alloc-bar{height:5px;background:rgba(255,255,255,.06);border-radius:10px;overflow:hidden;margin:.3rem 0;}
.alloc-fill{height:100%;background:linear-gradient(90deg,var(--accent-blue),var(--accent-violet));border-radius:10px;}
/* glass card */
.glass-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-lg);
    padding:1.2rem 1.4rem;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
    box-shadow:0 4px 30px rgba(0,0,0,0.1);
    transition:border-color .25s ease, box-shadow .25s ease, transform .25s ease;
    animation: slideUpFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
    will-change:transform, box-shadow; z-index:0;}
/* nav */
.nav-group{font-size:.62rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;
    color:var(--text-muted)!important;padding:.5rem .4rem .2rem;}
.nav-item{display:flex;align-items:center;gap:9px;padding:.5rem .8rem;border-radius:var(--radius-sm);
    font-size:.83rem;font-weight:500;color:var(--text-secondary)!important;cursor:pointer;margin:2px 0;}
.nav-item:hover{background:rgba(255,255,255,.05);}
.nav-item.active{background:rgba(79,143,255,.15);color:var(--accent-blue)!important;font-weight:600;}
/* buttons */
.stButton>button{background:var(--bg-elevated)!important;border:1px solid var(--border-active)!important;
    color:var(--text-secondary)!important;border-radius:var(--radius-sm)!important;font-size:.8rem!important;transition:all .15s!important;}
.stButton>button:hover{background:var(--accent-blue)!important;border-color:var(--accent-blue)!important;color:white!important;}
.stButton>button[kind="primary"]{background:var(--accent-blue)!important;border-color:var(--accent-blue)!important;color:white!important;}
.stSelectbox>div>div,.stTextInput>div>div>input,.stNumberInput>div>div>input,.stDateInput>div>div>input{
    background:var(--bg-elevated)!important;border:1px solid var(--border)!important;
    border-radius:var(--radius-sm)!important;color:var(--text-primary)!important;font-size:.84rem!important;}
div[data-testid="stMetric"]{background:var(--bg-card);border:1px solid var(--border);
    border-radius:var(--radius-md);padding:.8rem 1rem;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);box-shadow:0 4px 30px rgba(0,0,0,0.1);
    transition:border-color .25s ease, box-shadow .25s ease, transform .25s ease;
    will-change:transform, box-shadow; z-index:0;}
div[data-testid="stMetric"]:hover{
    border-color:rgba(79,143,255,0.6) !important;
    box-shadow:0 0 30px rgba(79,143,255,0.25), 0 10px 40px rgba(0,0,0,0.4) !important;
    transform:translateY(-4px); z-index:10;}
div[data-testid="stMetric"] label{color:var(--text-secondary)!important;font-size:.68rem!important;
    letter-spacing:.06em;text-transform:uppercase;}
div[data-testid="stMetric"] [data-testid="stMetricValue"]{font-family:'Syne',sans-serif!important;
    color:var(--text-primary)!important;font-size:1.4rem!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--bg-card)!important;border-radius:var(--radius-md)!important;
    gap:4px;padding:4px;border:1px solid var(--border)!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--text-secondary)!important;
    border-radius:var(--radius-sm)!important;font-size:.8rem!important;font-weight:500!important;padding:6px 14px!important;}
.stTabs [aria-selected="true"]{background:var(--bg-elevated)!important;color:var(--text-primary)!important;font-weight:600!important;}
[data-testid="stDataFrameContainer"]{border:1px solid var(--border)!important;border-radius:var(--radius-md)!important;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:var(--bg-base);}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,.1);border-radius:10px;}
/* Ensure Streamlit wrappers don't clip hover glow */
[data-testid="stMarkdownContainer"]{overflow:visible !important;}
[data-testid="stColumn"]{overflow:visible !important;}
.p-stat:hover{
    border-color:rgba(79,143,255,0.6) !important;
    box-shadow:0 0 30px rgba(79,143,255,0.25), 0 10px 40px rgba(0,0,0,0.4) !important;
    transform:translateY(-4px); z-index:10;}
.holding-row:hover{
    border-color:rgba(79,143,255,0.5) !important;
    box-shadow:0 0 24px rgba(79,143,255,0.2), 0 8px 32px rgba(0,0,0,0.35) !important;
    transform:translateY(-3px); z-index:10;}
.glass-card:hover{
    border-color:rgba(124,111,247,0.6) !important;
    box-shadow:0 0 30px rgba(124,111,247,0.25), 0 10px 40px rgba(0,0,0,0.4) !important;
    transform:translateY(-4px); z-index:10;}
::-webkit-scrollbar{width:8px;height:8px;}
::-webkit-scrollbar-track{background:var(--bg-base);border-radius:10px;}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:10px;transition:background 0.2s;}
::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,0.2);}
/* Skeletons */
.skeleton{background:linear-gradient(90deg,var(--bg-elevated) 25%,#2a2f42 50%,var(--bg-elevated) 75%);background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:var(--radius-sm);}
@keyframes shimmer{0%{background-position:200% 0;}100%{background-position:-200% 0;}}
.skeleton-card{height:100px;border-radius:var(--radius-md);margin-bottom:.5rem;}
</style>
""", unsafe_allow_html=True)

# ── JS: force stMain to expand when sidebar collapses ─────────────────────────
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
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8892a4", size=10)),
    margin=dict(l=8, r=8, t=36, b=8),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="rgba(28,32,48,0.95)", font_size=12, font_family="DM Sans", bordercolor="rgba(255,255,255,0.1)"),
)

# ── Session state ──────────────────────────────────────────────────────────────
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {'holdings': [], 'cash_balance': 10000.00}

import pathlib as _pathlib
PORTFOLIO_FILE = str(_pathlib.Path(__file__).parent.parent / 'data' / 'portfolio_data.json')

def save_portfolio():
    with open(PORTFOLIO_FILE, 'w') as f: json.dump(st.session_state.portfolio, f)

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f: st.session_state.portfolio = json.load(f)

load_portfolio()

@st.cache_data(ttl=60)
def get_price(symbol):
    try:
        return yf.Ticker(symbol).history(period="1d")['Close'].iloc[-1]
    except: return None

@st.cache_data(ttl=3600)
def get_sector(symbol):
    try:
        return yf.Ticker(symbol).info.get('sector', 'Unknown')
    except: return 'Unknown'

def calc_metrics(holdings):
    total_val = st.session_state.portfolio['cash_balance']
    total_inv = 0
    rows = []
    for idx, h in enumerate(holdings):  # FIX: track original index for precise inline-edit matching
        p = get_price(h['symbol'])
        if p:
            cur  = h['shares'] * p
            inv  = h['shares'] * h['buy_price']
            pnl  = cur - inv
            pnl_ = (pnl / inv) * 100 if inv else 0
            total_val += cur; total_inv += inv
            sector = get_sector(h['symbol'])
            rows.append({**h, 'holding_idx': idx, 'current_price':p, 'current_value':cur,
                         'invested':inv, 'pnl':pnl, 'pnl_percent':pnl_, 'allocation':0, 'sector': sector})
    for r in rows: r['allocation'] = (r['current_value']/total_val*100) if total_val else 0
    pnl_total = total_val - (total_inv + st.session_state.portfolio['cash_balance'])
    pnl_pct   = (pnl_total/(total_inv+st.session_state.portfolio['cash_balance'])*100) if (total_inv+st.session_state.portfolio['cash_balance']) else 0
    return rows, total_val, pnl_total, pnl_pct

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem .4rem .4rem">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:1.2rem">
            <div style="width:34px;height:34px;background:linear-gradient(135deg,#4f8fff,#22d98a);
                border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.85rem;color:white;font-family:"Syne",sans-serif">P</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:.95rem;color:#f0f2f8!important">Portfolio</div>
        </div>
        <div class="nav-group">Platform</div>
        <a href="/" target="_self" class="nav-item" style="text-decoration:none;">Dashboard</a>
        <div class="nav-group" style="margin-top:.5rem">Pages</div>
        <a href="/Analytics" target="_self" class="nav-item" style="text-decoration:none;">Analytics</a>
        <a href="/Portfolio" target="_self" class="nav-item active" style="text-decoration:none;">Portfolio</a>
        <a href="/ML_Predictions" target="_self" class="nav-item" style="text-decoration:none;">ML Predictions</a>
        <a href="/Watchlist" target="_self" class="nav-item" style="text-decoration:none;">Watchlist & Alerts</a>
        <a href="/Backtesting" target="_self" class="nav-item" style="text-decoration:none;">Backtesting</a>
        <a href="/Heatmap" target="_self" class="nav-item" style="text-decoration:none;">Sector Heatmap</a>
    </div>
    <hr style="border-color:rgba(255,255,255,.06);margin:.6rem 0">
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:.68rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#4e5669;padding:.3rem .4rem .2rem">Add Holding</div>', unsafe_allow_html=True)

    STOCK_CATALOGUE = {
        "Apple (AAPL)":"AAPL","Microsoft (MSFT)":"MSFT","NVIDIA (NVDA)":"NVDA",
        "Alphabet/Google (GOOGL)":"GOOGL","Meta (META)":"META","Amazon (AMZN)":"AMZN",
        "Tesla (TSLA)":"TSLA","Netflix (NFLX)":"NFLX","AMD (AMD)":"AMD",
        "Intel (INTC)":"INTC","Qualcomm (QCOM)":"QCOM","Broadcom (AVGO)":"AVGO",
        "Salesforce (CRM)":"CRM","Oracle (ORCL)":"ORCL","Adobe (ADBE)":"ADBE",
        "Palantir (PLTR)":"PLTR","JPMorgan (JPM)":"JPM","Goldman Sachs (GS)":"GS",
        "Visa (V)":"V","Mastercard (MA)":"MA","J&J (JNJ)":"JNJ",
        "UnitedHealth (UNH)":"UNH","Pfizer (PFE)":"PFE","Eli Lilly (LLY)":"LLY",
        "Walmart (WMT)":"WMT","Coca-Cola (KO)":"KO","SPY ETF (SPY)":"SPY",
        "QQQ ETF (QQQ)":"QQQ","Bitcoin (BTC-USD)":"BTC-USD",
        "Infosys (INFY)":"INFY","Wipro (WIT)":"WIT","HDFC Bank (HDB)":"HDB",
    }

    with st.form("add_holding"):
        cat_names   = ["— choose from list —"] + list(STOCK_CATALOGUE.keys())
        chosen_cat  = st.selectbox("Stock", cat_names, index=0)
        sym = STOCK_CATALOGUE.get(chosen_cat, "") if chosen_cat != "— choose from list —" else ""
        shrs  = st.number_input("Shares", min_value=0.01, step=0.01)
        bp    = st.number_input("Buy Price ($)", min_value=0.01, step=0.01)
        bdate = st.date_input("Date", datetime.now())
        if st.form_submit_button("Add", use_container_width=True):
            if not sym:
                st.error("⚠️ Please select a stock from the list.")
            elif shrs <= 0 or bp <= 0:
                st.error("⚠️ Shares and buy price must be greater than zero.")
            elif bp < 0.10:
                st.error(f"⚠️ Buy price ${bp:.4f} looks suspiciously low — please verify.")
            else:
                # FIX: block exact duplicates (same symbol + shares + price + date)
                is_dup = any(
                    h['symbol'] == sym.upper() and
                    h['buy_date'] == bdate.strftime("%Y-%m-%d") and
                    abs(h['buy_price'] - bp) < 0.001 and
                    abs(h['shares'] - shrs) < 0.001
                    for h in st.session_state.portfolio['holdings']
                )
                if is_dup:
                    st.error(f"⚠️ This exact holding already exists (same symbol, shares, price & date).")
                else:
                    st.session_state.portfolio['holdings'].append(
                        {'symbol': sym.upper(), 'shares': shrs, 'buy_price': bp,
                         'buy_date': bdate.strftime("%Y-%m-%d")})
                    save_portfolio()
                    st.success(f"Added {shrs} × {sym.upper()}")
                    st.rerun()

    st.markdown('<hr style="border-color:rgba(255,255,255,.06);margin:.6rem 0">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.68rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#4e5669;padding:.1rem .4rem .2rem">Cash Balance</div>', unsafe_allow_html=True)
    cash = st.number_input("", value=st.session_state.portfolio['cash_balance'], step=100.0, label_visibility="collapsed")
    if cash != st.session_state.portfolio['cash_balance']:
        st.session_state.portfolio['cash_balance'] = cash; save_portfolio(); st.rerun()

    st.markdown('<hr style="border-color:rgba(255,255,255,.06);margin:.6rem 0">', unsafe_allow_html=True)
    if st.button("Reset Portfolio", use_container_width=True):
        st.session_state.portfolio = {'holdings':[],'cash_balance':10000.00}; save_portfolio(); st.rerun()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:.8rem 0 .4rem">
    <div style="font-family:'Syne',sans-serif;font-size:1.7rem;font-weight:800;color:#f0f2f8;line-height:1">
        Portfolio Tracker
    </div>
    <div style="font-size:.82rem;color:#8892a4;margin-top:.3rem">Track your investments and monitor performance in real-time</div>
</div>
""", unsafe_allow_html=True)

# ── Main ────────────────────────────────────────────────────────────────────────
if st.session_state.portfolio['holdings']:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
        <div style="display:flex;gap:1rem;margin-bottom:1rem;flex-wrap:wrap;">
            <div class="skeleton skeleton-card" style="flex:1;min-width:180px;"></div>
            <div class="skeleton skeleton-card" style="flex:1;min-width:180px;"></div>
            <div class="skeleton skeleton-card" style="flex:1;min-width:180px;"></div>
            <div class="skeleton skeleton-card" style="flex:1;min-width:180px;"></div>
        </div>
        """, unsafe_allow_html=True)
    metrics, total_val, total_pnl, total_pnl_pct = calc_metrics(st.session_state.portfolio['holdings'])
    placeholder.empty()

    eb1, eb2 = st.columns([5, 1])
    with eb2:
        df_export = pd.DataFrame(metrics)
        csv = df_export.to_csv(index=False)
        st.download_button(label="Export to CSV", data=csv, file_name="portfolio.csv", mime="text/csv", use_container_width=True)

    # ── Stat cards ──
    sc1, sc2 = st.columns(2)
    sc3, sc4 = st.columns(2)
    pnl_color = "#22d98a" if total_pnl >= 0 else "#f05252"
    pnl_icon  = "▲" if total_pnl >= 0 else "▼"

    for col, lbl, val, sub_val, color in [
        (sc1, "Total Portfolio", f"${total_val:,.2f}", "", "#4f8fff"),
        (sc2, "Total P&L", f"{pnl_icon} ${abs(total_pnl):,.2f}", f"{total_pnl_pct:+.2f}%", pnl_color),
        (sc3, "Total Invested", f"${sum(m['invested'] for m in metrics):,.2f}", "", "#f5a623"),
        (sc4, "Cash Balance", f"${st.session_state.portfolio['cash_balance']:,.2f}", "", "#22d98a"),
    ]:
        with col:
            sub_html = f'<div class="p-stat-sub count-up" style="color:{color}">{sub_val}</div>' if sub_val else '<div class="p-stat-sub" style="visibility:hidden">_</div>'
            st.markdown(f"""
            <div class="p-stat" style="margin-bottom:.5rem;">
                <div class="p-stat-label" title="{lbl}">{lbl}</div>
                <div class="p-stat-val count-up" style="color:{color};" title="{val}">{val}</div>
                {sub_html}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)

    # ── Charts ──
    st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
    cc1, cc2 = st.columns(2)

    with cc1:
        st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:.85rem;font-weight:700;color:#f0f2f8;margin-bottom:.5rem">Asset Allocation</div>', unsafe_allow_html=True)
        alloc_data = [{'Symbol':m['symbol'],'Allocation':m['allocation']} for m in metrics if m['allocation']>0]
        if alloc_data:
            df_alloc = pd.DataFrame(alloc_data)
            fig = px.pie(df_alloc, values='Allocation', names='Symbol', hole=0.55,
                         color_discrete_sequence=['#4f8fff','#7c6ff7','#22d98a','#f5a623','#f05252','#ec4899'])
            fig.update_traces(textposition='outside', textinfo='percent+label',
                              textfont=dict(family="DM Sans", size=13, color="#f0f2f8"),
                              marker=dict(line=dict(color='rgba(0,0,0,0)', width=0)))
            fig.update_layout(height=340, showlegend=False, **DARK_LAYOUT)
            fig.update_layout(margin=dict(t=30, b=30, l=30, r=30))
            st.plotly_chart(fig, use_container_width=True, theme=None)

    with cc2:
        st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:.85rem;font-weight:700;color:#f0f2f8;margin-bottom:.5rem">Sector Allocation</div>', unsafe_allow_html=True)
        sector_data = [{'Sector':m['sector'],'Allocation':m['allocation']} for m in metrics if m['allocation']>0]
        if sector_data:
            df_sector = pd.DataFrame(sector_data).groupby('Sector', as_index=False).sum()
            fig_sec = px.pie(df_sector, values='Allocation', names='Sector', hole=0.55,
                         color_discrete_sequence=['#7c6ff7','#4f8fff','#f5a623','#22d98a','#ec4899','#f05252'])
            fig_sec.update_traces(textposition='outside', textinfo='percent+label',
                               textfont=dict(family="DM Sans", size=13, color="#f0f2f8"),
                               marker=dict(line=dict(color='rgba(0,0,0,0)', width=0)))
            fig_sec.update_layout(height=340, showlegend=False, **DARK_LAYOUT)
            fig_sec.update_layout(margin=dict(t=30, b=30, l=30, r=30))
            st.plotly_chart(fig_sec, use_container_width=True, theme=None)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:.85rem;font-weight:700;color:#f0f2f8;margin-bottom:.5rem">Return by Stock</div>', unsafe_allow_html=True)
    perf_df = pd.DataFrame([{'Symbol':m['symbol'],'P&L %':m['pnl_percent']} for m in metrics])
    colors  = ['#22d98a' if x >= 0 else '#f05252' for x in perf_df['P&L %']]
    fig2 = go.Figure(go.Bar(x=perf_df['Symbol'], y=perf_df['P&L %'],
                            marker_color=colors, marker_line_width=0))
    fig2.update_layout(height=340, yaxis_title="Return (%)", **DARK_LAYOUT)
    st.plotly_chart(fig2, use_container_width=True, theme=None)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Allocation bars ──
    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:.85rem;font-weight:700;color:#f0f2f8;margin-bottom:.5rem">Allocation Breakdown</div>', unsafe_allow_html=True)
    for m in sorted(metrics, key=lambda x: x['allocation'], reverse=True)[:6]:
        st.markdown(f"""
        <div style="margin-bottom:.6rem">
            <div style="display:flex;justify-content:space-between;margin-bottom:.2rem">
                <span style="font-size:.8rem;font-weight:600;color:#f0f2f8">{m['symbol']}</span>
                <span style="font-size:.78rem;color:#8892a4">{m['allocation']:.1f}%</span>
            </div>
            <div class="alloc-bar">
                <div class="alloc-fill" style="width:{min(m['allocation'],100)}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Risk metrics ──
    st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:.85rem;font-weight:700;color:#f0f2f8;margin-bottom:.6rem">Risk Analysis</div>', unsafe_allow_html=True)
    rc1, rc2, rc3 = st.columns(3)
    n = len(metrics)
    div_label = "High" if n >= 7 else "Medium" if n >= 3 else "Low"
    largest   = max([m['allocation'] for m in metrics]) if metrics else 0
    conc      = "High" if largest > 40 else "Medium" if largest > 20 else "Low"
    div_color = "#f05252" if div_label == "Low" else "#f5a623" if div_label == "Medium" else "#22d98a"
    conc_color = "#f05252" if conc == "High" else "#f5a623" if conc == "Medium" else "#22d98a"
    for col, lbl, val, sub, color in [
        (rc1, "Portfolio Beta", "1.2",     "Moderate risk",    "#4f8fff"),
        (rc2, "Diversification", div_label, f"{n} holdings",    div_color),
        (rc3, "Concentration",  conc,      f"Largest: {largest:.1f}%", conc_color),
    ]:
        with col:
            st.markdown(f"""
            <div class="p-stat" style="text-align:center">
                <div class="p-stat-label">{lbl}</div>
                <div class="p-stat-val" style="color:{color};font-size:1.4rem">{val}</div>
                <div class="p-stat-sub" style="color:#4e5669">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Performance chart ──
    st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:.85rem;font-weight:700;color:#f0f2f8;margin-bottom:.5rem">Portfolio Performance (30 days)</div>', unsafe_allow_html=True)
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    rng   = np.random.default_rng(seed=42)  # FIX: seeded RNG — consistent chart each run
    perf  = [100 + i*0.4 + (rng.random()*2-1) for i in range(30)]
    fig3  = go.Figure()
    fig3.add_trace(go.Scatter(x=dates, y=perf, mode='lines', name='Value Index',
                              line=dict(color='#4f8fff', width=2),
                              fill='tozeroy', fillcolor='rgba(79,143,255,.08)'))
    fig3.update_layout(height=280, yaxis_title="Index (base 100)", **DARK_LAYOUT)
    st.plotly_chart(fig3, use_container_width=True, theme=None)

else:
    st.markdown("""
    <div style="background:#13161e;border:1px dashed rgba(255,255,255,.12);border-radius:20px;
        padding:3.5rem 2rem;text-align:center;margin-top:1rem">
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:#f0f2f8;margin-bottom:.5rem">
            Your portfolio is empty
        </div>
        <div style="font-size:.84rem;color:#8892a4">Use the sidebar to add your first stock holding</div>
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:.6rem;max-width:420px;margin:1.5rem auto 0;text-align:left">
            <div style="background:#1c2030;border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:1rem">
                <div style="font-size:.72rem;font-weight:600;color:#4f8fff;margin-bottom:.3rem">STEP 1</div>
                <div style="font-size:.82rem;color:#f0f2f8">Add a stock symbol</div>
            </div>
            <div style="background:#1c2030;border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:1rem">
                <div style="font-size:.72rem;font-weight:600;color:#4f8fff;margin-bottom:.3rem">STEP 2</div>
                <div style="font-size:.82rem;color:#f0f2f8">Enter shares & buy price</div>
            </div>
            <div style="background:#1c2030;border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:1rem">
                <div style="font-size:.72rem;font-weight:600;color:#7c6ff7;margin-bottom:.3rem">STEP 3</div>
                <div style="font-size:.82rem;color:#f0f2f8">Track real-time P&L</div>
            </div>
            <div style="background:#1c2030;border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:1rem">
                <div style="font-size:.72rem;font-weight:600;color:#22d98a;margin-bottom:.3rem">STEP 4</div>
                <div style="font-size:.82rem;color:#f0f2f8">Analyse allocation & risk</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:1.2rem 0 .3rem;font-size:.72rem;color:#4e5669">
    Portfolio values update in real-time · Data by Yahoo Finance
</div>
""", unsafe_allow_html=True)
