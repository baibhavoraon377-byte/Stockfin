import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Market Heatmap", page_icon="🗺️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
:root {
    --bg-base:#0d0f14; --bg-card:rgba(19, 22, 30, 0.55);
    --border:rgba(255,255,255,0.08);
    --text-primary:#f0f2f8; --text-secondary:#8892a4;
    --radius-md:14px;
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
::-webkit-scrollbar{width:8px;height:8px;}
::-webkit-scrollbar-track{background:var(--bg-base);border-radius:10px;}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:10px;transition:background 0.2s;}
::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,0.2);}
.stPlotlyChart { animation: slideUpFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) both; }
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

# Sidebar Navigation (matching other pages)
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
                <span class="live-dot" style="font-size:.65rem;color:#22d98a">LIVE</span>
            </div>
        </div>
        <div style="font-size:.62rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#4e5669;padding:.5rem .4rem .2rem">Platform</div>
        <a href="/" target="_self" style="display:flex;align-items:center;gap:9px;padding:.5rem .8rem;border-radius:8px;font-size:.83rem;font-weight:500;color:#8892a4;text-decoration:none;">Dashboard</a>
        <div style="font-size:.62rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#4e5669;padding:.5rem .4rem .2rem;margin-top:.5rem">Pages</div>
        <a href="/Analytics" target="_self" style="display:flex;align-items:center;gap:9px;padding:.5rem .8rem;border-radius:8px;font-size:.83rem;font-weight:500;color:#8892a4;text-decoration:none;">Analytics</a>
        <a href="/Portfolio" target="_self" style="display:flex;align-items:center;gap:9px;padding:.5rem .8rem;border-radius:8px;font-size:.83rem;font-weight:500;color:#8892a4;text-decoration:none;">Portfolio</a>
        <a href="/ML_Predictions" target="_self" style="display:flex;align-items:center;gap:9px;padding:.5rem .8rem;border-radius:8px;font-size:.83rem;font-weight:500;color:#8892a4;text-decoration:none;">ML Predictions</a>
        <a href="/Watchlist" target="_self" style="display:flex;align-items:center;gap:9px;padding:.5rem .8rem;border-radius:8px;font-size:.83rem;font-weight:500;color:#8892a4;text-decoration:none;">Watchlist & Alerts</a>
        <a href="/Backtesting" target="_self" style="display:flex;align-items:center;gap:9px;padding:.5rem .8rem;border-radius:8px;font-size:.83rem;font-weight:500;color:#8892a4;text-decoration:none;">Backtesting</a>
        <a href="/Heatmap" target="_self" style="display:flex;align-items:center;gap:9px;padding:.5rem .8rem;border-radius:8px;font-size:.83rem;font-weight:600;color:#4f8fff;background:rgba(79,143,255,.15);text-decoration:none;">Heatmap</a>
    </div>
    """, unsafe_allow_html=True)


st.markdown("""
<div style="padding:.8rem 0 .2rem">
    <div style="font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;color:#f0f2f8;line-height:1">Market Heatmap</div>
    <div style="font-size:.9rem;color:#8892a4;margin-top:.4rem">S&P 500 sectors visualised by market capitalization and performance</div>
</div>
<hr style="border-color:rgba(255,255,255,.06);margin:1.2rem 0">
""", unsafe_allow_html=True)

# Define top S&P 500 components per sector
SECTORS = {
    "Technology": ["AAPL", "MSFT", "NVDA", "AVGO", "CSCO", "CRM", "ADBE"],
    "Health Care": ["LLY", "UNH", "JNJ", "ABBV", "MRK", "TMO"],
    "Financials": ["JPM", "V", "MA", "BAC", "WFC", "GS", "MS"],
    "Consumer Discretionary": ["AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX"],
    "Communication": ["GOOGL", "META", "NFLX", "DIS", "CMCSA"],
    "Industrials": ["CAT", "GE", "UNP", "BA", "HON", "UPS"],
    "Consumer Staples": ["WMT", "PG", "KO", "PEP", "COST"],
    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG"],
    "Utilities": ["NEE", "DUK", "SO", "SRE", "AEP"],
    "Real Estate": ["PLD", "AMT", "EQIX", "CCI", "PSA"],
    "Materials": ["LIN", "SHW", "FCX", "ECL", "NEM"]
}

@st.cache_data(ttl=300)
def fetch_heatmap_data():
    all_symbols = []
    symbol_to_sector = {}
    for sec, syms in SECTORS.items():
        all_symbols.extend(syms)
        for s in syms:
            symbol_to_sector[s] = sec
            
    try:
        data = yf.download(all_symbols, period="2d", auto_adjust=False)
        closes = data['Close']
        if len(closes) < 2:
            return pd.DataFrame()
            
        latest_close = closes.iloc[-1]
        prev_close = closes.iloc[-2]
        
        records = []
        for sym in all_symbols:
            if sym in latest_close and sym in prev_close and not pd.isna(latest_close[sym]):
                chg_pct = ((latest_close[sym] - prev_close[sym]) / prev_close[sym]) * 100
                tk = yf.Ticker(sym)
                mcap = tk.fast_info.market_cap if hasattr(tk.fast_info, 'market_cap') else 1e9
                
                records.append({
                    "Symbol": sym,
                    "Sector": symbol_to_sector[sym],
                    "Change": chg_pct,
                    "MarketCap": mcap,
                    "Root": "S&P 500"
                })
        return pd.DataFrame(records)
    except Exception as e:
        print(e)
        return pd.DataFrame()

df = fetch_heatmap_data()

if df.empty:
    st.error("Could not load heatmap data. Please try again later.")
else:
    # Color scale from vivid red to bright green
    color_scale = [
        [0.0, "rgb(240,82,82)"],
        [0.5, "rgb(40,45,60)"],
        [1.0, "rgb(34,217,138)"]
    ]
    
    fig = px.treemap(
        df,
        path=["Root", "Sector", "Symbol"],
        values="MarketCap",
        color="Change",
        color_continuous_scale=color_scale,
        color_continuous_midpoint=0,
        custom_data=["Change", "MarketCap"],
        height=750
    )
    
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{customdata[0]:.2f}%",
        textposition="middle center",
        hovertemplate="<b>%{label}</b><br>Sector: %{parent}<br>Change: %{customdata[0]:.2f}%<br>Market Cap: $%{customdata[1]:.2s}<extra></extra>",
        marker=dict(line=dict(width=2, color="#0d0f14"))
    )
    
    fig.update_layout(
        margin=dict(t=10, l=10, r=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", size=14, color="#f0f2f8"),
        coloraxis_colorbar=dict(
            title=dict(text="% Change", font=dict(color="#8892a4")),
            tickfont=dict(color="#8892a4")
        )
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
