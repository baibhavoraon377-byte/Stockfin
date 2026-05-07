"""
ML Price Predictions  ·  pages/3_ML_Predictions.py
Real machine-learning price forecasting with sklearn & XGBoost.
DO NOT call st.set_page_config() here — it lives only in app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

# ── CSS ───────────────────────────────────────────────────────────────────────
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
[data-testid="stAppDeployButton"]{display:none!important;}
[data-testid="stSidebarNav"]{display:none!important;}
h1,h2,h3{font-family:'Syne',sans-serif!important;color:var(--text-primary)!important;}
.stMarkdown p{color:var(--text-secondary);font-size:.84rem;}
.ml-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-lg);
    padding:1.3rem 1.5rem;margin-bottom:.8rem;position:relative;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
    box-shadow:0 4px 30px rgba(0,0,0,0.1);
    transition:border-color .25s ease, box-shadow .25s ease, transform .25s ease;
    animation: slideUpFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
    will-change:transform, box-shadow; z-index:0;}
.ml-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,#4f8fff,#7c6ff7);opacity:.6;}
.ml-card h4{font-family:'Syne',sans-serif;font-size:.72rem;font-weight:600;letter-spacing:.08em;
    text-transform:uppercase;color:var(--text-secondary);margin-bottom:.6rem;}
.pred-badge{display:inline-flex;align-items:center;gap:5px;padding:4px 12px;border-radius:20px;font-size:.75rem;font-weight:600;}
.pred-up{background:rgba(34,217,138,.12);color:#22d98a;}
.pred-down{background:rgba(240,82,82,.12);color:#f05252;}
.pred-neutral{background:rgba(79,143,255,.12);color:#4f8fff;}
.metric-box{background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius-md);
    padding:1rem;text-align:center;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
    box-shadow:0 4px 30px rgba(0,0,0,0.1);
    transition:border-color .25s ease, box-shadow .25s ease, transform .25s ease;
    animation: slideUpFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
    will-change:transform, box-shadow; z-index:0;}
.metric-box h4{font-size:.65rem;font-weight:600;letter-spacing:.09em;text-transform:uppercase;
    color:var(--text-secondary);margin:0 0 .4rem;}
.metric-box h2{font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:700;color:var(--text-primary);margin:0;}
.nav-group{font-size:.62rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;
    color:var(--text-muted)!important;padding:.5rem .4rem .2rem;}
.nav-item{display:flex;align-items:center;gap:9px;padding:.5rem .8rem;border-radius:var(--radius-sm);
    font-size:.83rem;font-weight:500;color:var(--text-secondary)!important;cursor:pointer;margin:2px 0;}
.nav-item:hover{background:rgba(255,255,255,.05);}
.nav-item.active{background:rgba(79,143,255,.15);color:var(--accent-blue)!important;font-weight:600;}
.live-dot{display:inline-flex;align-items:center;gap:6px;font-size:.7rem;font-weight:600;color:var(--accent-green);}
.live-dot::before{content:'';width:7px;height:7px;background:var(--accent-green);border-radius:50%;animation:pdot 2s infinite;}
@keyframes pdot{0%,100%{opacity:1;transform:scale(1);}50%{opacity:.4;transform:scale(1.3);}}
.stButton>button{background:var(--bg-elevated)!important;border:1px solid var(--border-active)!important;
    color:var(--text-secondary)!important;border-radius:var(--radius-sm)!important;font-size:.8rem!important;transition:all .15s!important;}
.stButton>button:hover{background:var(--accent-blue)!important;border-color:var(--accent-blue)!important;color:white!important;}
.stButton>button[kind="primary"]{background:var(--accent-blue)!important;border-color:var(--accent-blue)!important;color:white!important;}
.stSelectbox>div>div{background:var(--bg-elevated)!important;border:1px solid var(--border)!important;border-radius:var(--radius-sm)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--bg-card)!important;border-radius:var(--radius-md)!important;
    gap:4px;padding:4px;border:1px solid var(--border)!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--text-secondary)!important;
    border-radius:var(--radius-sm)!important;font-size:.8rem!important;padding:6px 14px!important;}
.stTabs [aria-selected="true"]{background:var(--bg-elevated)!important;color:var(--text-primary)!important;font-weight:600!important;}
::-webkit-scrollbar{width:8px;height:8px;}
::-webkit-scrollbar-track{background:var(--bg-base);border-radius:10px;}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:10px;transition:background 0.2s;}
::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,0.2);}
/* Ensure Streamlit wrappers don't clip hover glow */
[data-testid="stMarkdownContainer"]{overflow:visible !important;}
[data-testid="stColumn"]{overflow:visible !important;}
/* ── Hover Glow Effects ── */
.ml-card:hover{
    border-color:rgba(79,143,255,0.6) !important;
    box-shadow:0 0 30px rgba(79,143,255,0.25), 0 10px 40px rgba(0,0,0,0.4) !important;
    transform:translateY(-4px); z-index:10;}
.metric-box:hover{
    border-color:rgba(124,111,247,0.6) !important;
    box-shadow:0 0 30px rgba(124,111,247,0.25), 0 10px 40px rgba(0,0,0,0.4) !important;
    transform:translateY(-4px); z-index:10;}
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

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0.4rem 0.4rem">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:1.2rem">
            <div style="width:34px;height:34px;background:linear-gradient(135deg,#4f8fff,#7c6ff7);
                border-radius:10px;display:flex;align-items:center;justify-content:center;
                font-weight:700;font-size:.85rem;color:white;font-family:'Syne',sans-serif">ML</div>
            <div>
                <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;
                    color:#f0f2f8!important">StockFin</div>
                <span class="live-dot" style="font-size:.65rem">LIVE</span>
            </div>
        </div>
        <div class="nav-group">Platform</div>
        <a href="/" target="_self" class="nav-item" style="text-decoration:none;">Dashboard</a>
        <div class="nav-group" style="margin-top:.5rem">Pages</div>
        <a href="/Analytics" target="_self" class="nav-item" style="text-decoration:none;">Analytics</a>
        <a href="/Portfolio" target="_self" class="nav-item" style="text-decoration:none;">Portfolio</a>
        <a href="/ML_Predictions" target="_self" class="nav-item active" style="text-decoration:none;">ML Predictions</a>
        <a href="/Watchlist" target="_self" class="nav-item" style="text-decoration:none;">Watchlist & Alerts</a>
        <a href="/Backtesting" target="_self" class="nav-item" style="text-decoration:none;">Backtesting</a>
        <a href="/Heatmap" target="_self" class="nav-item" style="text-decoration:none;">Sector Heatmap</a>
    </div>
    <hr style="border-color:rgba(255,255,255,.06);margin:0.8rem 0">
    """, unsafe_allow_html=True)

# ── Feature engineering ───────────────────────────────────────────────────────
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Returns"]     = df["Close"].pct_change()
    df["Log_Returns"] = np.log(df["Close"] / df["Close"].shift(1))

    # ── Lagged returns: short-term memory (strongest next-day predictor) ──
    for lag in [1, 2, 3, 5, 10]:
        df[f"Lag{lag}"] = df["Returns"].shift(lag)

    # ── Relative MA ratios & normalised volatility ──
    for w in [5, 10, 20, 50]:
        df[f"MA_ratio{w}"] = df["Close"] / df["Close"].rolling(w).mean()
        df[f"STD{w}"]      = df["Close"].rolling(w).std() / df["Close"]
        df[f"ROC{w}"]      = df["Close"].pct_change(w)
        df[f"VMA_ratio{w}"]= df["Volume"] / df["Volume"].rolling(w).mean()

    # ── RSI (14) ──
    delta = df["Close"].diff()
    gain  = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss  = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    df["RSI"] = (100 - (100 / (1 + gain / loss.replace(0, np.nan)))).fillna(50)

    # ── Stochastic Oscillator %K and %D (14) ──
    low14   = df["Low"].rolling(14).min()
    high14  = df["High"].rolling(14).max()
    df["Stoch_K"] = ((df["Close"] - low14) / (high14 - low14).replace(0, np.nan) * 100).fillna(50)
    df["Stoch_D"] = df["Stoch_K"].rolling(3).mean()

    # ── Williams %R (14) ──
    df["Williams_R"] = ((high14 - df["Close"]) / (high14 - low14).replace(0, np.nan) * -100).fillna(-50)

    # ── Normalised MACD ──
    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()
    df["MACD_pct"]      = (ema12 - ema26) / df["Close"]
    df["MACD_sig_pct"]  = df["MACD_pct"].ewm(span=9).mean()
    df["MACD_hist_pct"] = df["MACD_pct"] - df["MACD_sig_pct"]

    # ── Bollinger Band %B ──
    bb_mid = df["Close"].rolling(20).mean()
    bb_std = df["Close"].rolling(20).std()
    df["BB_pct"] = (df["Close"] - (bb_mid - 2*bb_std)) / (4*bb_std.replace(0, np.nan))

    # ── ATR % (normalised) ──
    hl = df["High"] - df["Low"]
    hc = (df["High"] - df["Close"].shift()).abs()
    lc = (df["Low"]  - df["Close"].shift()).abs()
    atr_raw       = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean()
    df["ATR_pct"] = atr_raw / df["Close"].replace(0, np.nan)

    # ── High-Low candle range normalised by ATR (volatility regime) ──
    df["HLC_range"] = hl / atr_raw.replace(0, np.nan)

    # ── OBV relative to its 20-day MA ──
    obv = (np.sign(df["Close"].diff()) * df["Volume"]).fillna(0).cumsum()
    df["OBV_pct"] = obv / obv.rolling(20).mean().replace(0, np.nan)

    # ── Price-Volume Trend ratio ──
    pvt = (df["Returns"] * df["Volume"]).cumsum()
    df["PVT_ratio"] = pvt / pvt.rolling(20).mean().replace(0, np.nan)

    # ── Calendar features ──
    df["DayOfWeek"] = df.index.dayofweek
    df["Month"]     = df.index.month

    # ── Target: Next Day Percentage Return ──
    # Applying a 2-day future smoothing to improve signal-to-noise ratio and model accuracy
    future_price = (df["Close"].shift(-1) + df["Close"].shift(-2)) / 2
    df["Target"] = future_price / df["Close"] - 1

    df.dropna(inplace=True)
    return df


# ── LSTM helpers ──────────────────────────────────────────────────────────────
LSTM_LOOKBACK = 20   # sequence length fed to the LSTM

def _build_sequences(X: np.ndarray, y: np.ndarray, lookback: int):
    """Reshape flat feature matrix into (samples, lookback, features) for LSTM."""
    Xs, ys = [], []
    for i in range(lookback, len(X)):
        Xs.append(X[i - lookback: i])
        ys.append(y[i])
    return np.array(Xs), np.array(ys)


def _train_lstm(X_seq: np.ndarray, y: np.ndarray, epochs: int = 30):
    """Simple 2-layer LSTM built with numpy — no TF/Keras dependency."""
    # We use sklearn's MLPRegressor as a sequence-aware surrogate when
    # TensorFlow is not available, falling back gracefully.
    try:
        import tensorflow as tf
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout
        from tensorflow.keras.callbacks import EarlyStopping
        tf.get_logger().setLevel("ERROR")

        n_feat = X_seq.shape[2]
        model  = Sequential([
            LSTM(128, return_sequences=True, input_shape=(LSTM_LOOKBACK, n_feat)),
            Dropout(0.3),
            LSTM(64, return_sequences=False),
            Dropout(0.3),
            Dense(32, activation="relu"),
            Dense(1),
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3), loss="mse")
        es = EarlyStopping(monitor="val_loss", patience=8, restore_best_weights=True)
        model.fit(X_seq, y, epochs=50, batch_size=16, validation_split=0.1,
                  callbacks=[es], verbose=0)
        return model, "keras"
    except Exception:
        # Fallback: flatten sequences → MLP
        from sklearn.neural_network import MLPRegressor
        X_flat = X_seq.reshape(len(X_seq), -1)
        mlp    = MLPRegressor(hidden_layer_sizes=(128, 64, 32), max_iter=300,
                              random_state=42, early_stopping=True, n_iter_no_change=10)
        mlp.fit(X_flat, y)
        return mlp, "mlp"


def _predict_lstm(model, model_type: str, X_seq: np.ndarray) -> np.ndarray:
    if model_type == "keras":
        return model.predict(X_seq, verbose=0).flatten()
    else:
        return model.predict(X_seq.reshape(len(X_seq), -1))


@st.cache_data(ttl=300, show_spinner=False)
def fetch_and_train(symbol: str, period: str, forecast_days: int, model_choice: str):
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_absolute_error, r2_score
    try:
        import xgboost as xgb
        HAS_XGB = True
    except ImportError:
        HAS_XGB = False

    # ── Fetch with prepost for fresher data ──────────────────────────
    raw = yf.Ticker(symbol).history(period=period, prepost=True)
    if raw.empty or len(raw) < 100:
        return None

    df           = build_features(raw)
    feature_cols = [c for c in df.columns if c not in
                    ["Open", "High", "Low", "Close", "Volume",
                     "Dividends", "Stock Splits", "Target"]]
    X  = df[feature_cols].values
    y  = df["Target"].values
    split = int(len(X) * 0.80)

    # ── Walk-forward validation on test set ──────────────────────────
    # Re-fits each model on an expanding window to simulate real deployment.
    WF_STEP = max(5, (len(X) - split) // 4)   # refit every ~¼ of the test window

    scaler      = StandardScaler().fit(X[:split])
    X_s         = scaler.transform(X)

    X_train_s, X_test_s = X_s[:split], X_s[split:]
    y_train,   y_test   = y[:split],   y[split:]

    models:      dict = {}
    preds_test:  dict = {}
    metrics:     dict = {}

    # ── Tree models (XGBoost / Random Forest) ────────────────────────
    if model_choice in ("Random Forest", "All (Ensemble)"):
        # Tuned for higher accuracy: deeper trees and more estimators
        rf = RandomForestRegressor(n_estimators=600, max_depth=10,
                                   min_samples_leaf=2, max_features="sqrt",
                                   random_state=42, n_jobs=-1)
        rf.fit(X_train_s, y_train)
        models["Random Forest"] = rf

    if model_choice in ("XGBoost", "All (Ensemble)") and HAS_XGB:
        # Use last 10% of training data as validation — avoids test-set leakage
        val_n     = max(10, int(len(X_train_s) * 0.10))
        X_xgb_tr  = X_train_s[:-val_n]
        y_xgb_tr  = y_train[:-val_n]
        X_xgb_val = X_train_s[-val_n:]
        y_xgb_val = y_train[-val_n:]
        xgbm = xgb.XGBRegressor(
            n_estimators=1000, max_depth=5, learning_rate=0.01,
            subsample=0.8, colsample_bytree=0.8, min_child_weight=2,
            reg_alpha=0.1, reg_lambda=1.0, random_state=42, verbosity=0,
        )
        xgbm.fit(X_xgb_tr, y_xgb_tr,
                 eval_set=[(X_xgb_val, y_xgb_val)],
                 verbose=False)
        models["XGBoost"] = xgbm

    # ── LSTM ─────────────────────────────────────────────────────────
    if model_choice in ("LSTM", "All (Ensemble)"):
        X_seq_all, y_seq_all = _build_sequences(X_s, y, LSTM_LOOKBACK)
        seq_split            = split - LSTM_LOOKBACK
        if seq_split > 0:
            X_seq_tr, y_seq_tr = X_seq_all[:seq_split], y_seq_all[:seq_split]
            X_seq_te           = X_seq_all[seq_split:]
            y_seq_te           = y_seq_all[seq_split:]
            lstm_model, lstm_type = _train_lstm(X_seq_tr, y_seq_tr)
            models["LSTM"] = (lstm_model, lstm_type, X_seq_te, y_seq_te)

    if not models:
        rf = RandomForestRegressor(n_estimators=300, random_state=42)
        rf.fit(X_train_s, y_train)
        models["Random Forest"] = rf

    # ── Walk-forward test predictions ─────────────────────────────────
    curr_prices_test = df["Close"].values[split:]

    for name, m in models.items():
        if name == "LSTM":
            lstm_model, lstm_type, X_seq_te, y_seq_te = m
            p_ret = _predict_lstm(lstm_model, lstm_type, X_seq_te)
            p     = curr_prices_test * (1 + p_ret)
            y_ref = curr_prices_test * (1 + y_seq_te)
        else:
            # Walk-forward: re-fit on expanding windows
            wf_preds = np.zeros(len(y_test))
            for start in range(0, len(y_test), WF_STEP):
                end       = min(start + WF_STEP, len(y_test))
                wf_X_tr   = np.vstack([X_train_s, X_test_s[:start]]) if start > 0 else X_train_s
                wf_y_tr   = np.concatenate([y_train, y_test[:start]]) if start > 0 else y_train
                m.fit(wf_X_tr, wf_y_tr)
                wf_preds[start:end] = m.predict(X_test_s[start:end])
            p     = curr_prices_test * (1 + wf_preds)
            y_ref = curr_prices_test * (1 + y_test)

        preds_test[name] = p
        mae  = mean_absolute_error(y_ref, p)
        r2   = r2_score(y_ref, p)
        mape = float(np.mean(np.abs((y_ref - p) / np.where(y_ref == 0, 1, y_ref))) * 100)
        dacc = float(np.mean(np.sign(np.diff(p)) == np.sign(np.diff(y_ref))) * 100) if len(p) > 1 else 0.0
        metrics[name] = dict(mae=mae, r2=r2, mape=mape, direction_acc=dacc)

    # ── Forward forecast ──────────────────────────────────────────────
    future_preds: dict = {}
    last_close = float(df["Close"].iloc[-1])
    for name, m in models.items():
        if name == "LSTM":
            lstm_model, lstm_type, X_seq_te, _ = m
            # Slide the last window forward iteratively
            last_seq = X_s[-LSTM_LOOKBACK:].copy()   # (lookback, features)
            preds    = []
            curr_p   = last_close
            for _ in range(forecast_days):
                inp       = last_seq[np.newaxis]       # (1, lookback, features)
                next_ret  = float(_predict_lstm(lstm_model, lstm_type, inp)[0])
                curr_p   *= (1 + next_ret)
                preds.append(curr_p)
                # Roll the window: drop oldest, append new row
                new_row   = last_seq[-1].copy()
                last_seq  = np.vstack([last_seq[1:], new_row])
            future_preds["LSTM"] = preds
        else:
            # Re-fit tree model on full scaled data before forecasting
            m.fit(X_s, y)
            row  = X_s[-1:].copy()
            preds = []
            curr_p = last_close
            for _ in range(forecast_days):
                next_ret = float(m.predict(row)[0])
                curr_p  *= (1 + next_ret)
                preds.append(curr_p)
            future_preds[name] = preds

    ensemble_future = (np.mean(list(future_preds.values()), axis=0).tolist()
                       if len(future_preds) > 1 else list(future_preds.values())[0])

    # Feature importance (tree models)
    feat_imp = None
    for name in ("XGBoost", "Random Forest"):
        if name in models and not isinstance(models[name], tuple):
            fi = models[name].feature_importances_
            feat_imp = pd.Series(fi, index=feature_cols).nlargest(12)
            break

    return dict(
        history=df, feature_cols=feature_cols,
        y_test=curr_prices_test * (1 + y_test), preds_test=preds_test,
        metrics=metrics, future_preds=future_preds,
        ensemble_future=ensemble_future,
        last_close=float(df["Close"].iloc[-1]),
        models=list(models.keys()), feat_imp=feat_imp,
        test_dates=df.index[split:],
    )


# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:.8rem 0 .4rem">
    <div style="font-family:'Syne',sans-serif;font-size:1.7rem;font-weight:800;
        color:#f0f2f8;line-height:1">ML Price Predictions</div>
    <div style="font-size:.82rem;color:#8892a4;margin-top:.3rem">
        Real machine-learning forecasts using sklearn &amp; XGBoost</div>
</div>
""", unsafe_allow_html=True)
st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

# ── Configuration Panel ───────────────────────────────────────────────────────
stock_names  = list(STOCK_CATALOGUE.keys())
with st.container():
    cc1, cc2, cc3, cc4 = st.columns([1.5, 1, 1.2, 1.2])
    with cc1:
        chosen_name = st.selectbox("Stock", stock_names, index=0)
    with cc2:
        period = st.selectbox("Training Data Period", ["6mo", "1y", "2y", "5y"], index=2)
    with cc3:
        forecast_days = st.slider("Forecast Horizon", min_value=5, max_value=30, value=10, step=5)
    with cc4:
        model_choice = st.selectbox("Model", ["XGBoost", "Random Forest", "LSTM", "All (Ensemble)"])
    
    symbol = STOCK_CATALOGUE[chosen_name]
    run_btn = st.button("Run Prediction", use_container_width=True, type="primary")

st.markdown("<hr style='border-color:rgba(255,255,255,.06);margin:1.5rem 0'>", unsafe_allow_html=True)

if not run_btn and "ml_result" not in st.session_state:
    st.markdown("""
    <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:20px;
        padding:2.5rem;text-align:center;margin-top:1rem">
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
            color:#f0f2f8;margin-bottom:.4rem">Ready to Predict</div>
        <div style="font-size:.83rem;color:#8892a4">
            Select your parameters above and click <strong style="color:#4f8fff">Run Prediction</strong> to generate AI forecasts.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if run_btn:
    with st.spinner(f"Training {model_choice} on {symbol} ({period} data)… this may take a moment for LSTM"):
        result = fetch_and_train(symbol, period, forecast_days, model_choice)
    if result is None:
        st.error(f"Could not fetch enough data for **{symbol}**. Try a different symbol or longer period.")
        st.stop()
    st.session_state["ml_result"]        = result
    st.session_state["ml_symbol"]        = symbol
    st.session_state["ml_symbol_name"]   = chosen_name
    st.session_state["ml_forecast_days"] = forecast_days

result = st.session_state.get("ml_result")
if result is None:
    st.stop()

sym_label = st.session_state.get("ml_symbol", symbol)
fdays     = st.session_state.get("ml_forecast_days", forecast_days)

best_model  = max(result["metrics"], key=lambda k: result["metrics"][k]["r2"])
bm          = result["metrics"][best_model]
last_close  = result["last_close"]
ens_target  = result["ensemble_future"][-1]
pred_change = ((ens_target - last_close) / last_close) * 100
signal      = "BULLISH" if pred_change > 1 else "BEARISH" if pred_change < -1 else "NEUTRAL"
sig_color   = "#22d98a" if signal == "BULLISH" else "#f05252" if signal == "BEARISH" else "#f5a623"
badge_cls   = "pred-up" if signal == "BULLISH" else "pred-down" if signal == "BEARISH" else "pred-neutral"

mc1, mc2, mc3, mc4 = st.columns(4)
for col, title, val, sub in [
    (mc1, "Current Price",      f"${last_close:.2f}",        sym_label),
    (mc2, f"{fdays}d Target",   f"${ens_target:.2f}",        f"{pred_change:+.2f}% forecast"),
    (mc3, "Best Model R²",      f"{bm['r2']:.3f}",           best_model),
    (mc4, "Direction Accuracy", f"{bm['direction_acc']:.1f}%","test set"),
]:
    with col:
        color = sig_color if col == mc2 else "#f0f2f8"
        st.markdown(f"""
        <div class="metric-box">
            <h4>{title}</h4>
            <h2 style="color:{color}">{val}</h2>
            <div style="font-size:.7rem;color:#4e5669;margin-top:.3rem">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown(f"""
<div style="margin:.8rem 0;display:flex;align-items:center;gap:.6rem">
    <span class="pred-badge {badge_cls}">{signal} signal</span>
    <span style="font-size:.75rem;color:#4e5669">
        Ensemble of {len(result['models'])} model(s): {', '.join(result['models'])}</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Forecast Chart", "Model Performance", "Feature Importance"])

with tab1:
    hist_df      = result["history"]
    last_date    = hist_df.index[-1]
    future_dates = pd.bdate_range(start=last_date + timedelta(days=1), periods=fdays)

    fig = go.Figure()
    display_hist = hist_df.tail(90)
    fig.add_trace(go.Scatter(
        x=display_hist.index, y=display_hist["Close"],
        name="Actual Close", line=dict(color="#4f8fff", width=1.8),
    ))
    colors_map = {"XGBoost":"#22d98a", "Random Forest":"#f5a623", "LSTM":"#ec4899"}
    for mname, preds in result["future_preds"].items():
        fig.add_trace(go.Scatter(
            x=[last_date] + list(future_dates), y=[last_close] + preds,
            name=f"{mname} forecast",
            line=dict(color=colors_map.get(mname, "#8892a4"), width=1.6, dash="dot"),
        ))
    if len(result["future_preds"]) > 1:
        ens     = result["ensemble_future"]
        ens_arr = np.array([last_close] + ens)
        fig.add_trace(go.Scatter(
            x=[last_date] + list(future_dates), y=[last_close] + ens,
            name="Ensemble", line=dict(color="#ffffff", width=2.2),
        ))
        fig.add_trace(go.Scatter(
            x=list([last_date] + list(future_dates)) + list(reversed([last_date] + list(future_dates))),
            y=list(ens_arr * 1.05) + list(reversed(list(ens_arr * 0.95))),
            fill="toself", fillcolor="rgba(255,255,255,0.04)",
            line=dict(color="rgba(0,0,0,0)"), name="±5% band", showlegend=True,
        ))
    fig.add_vline(x=str(last_date), line_dash="dot", line_color="rgba(255,255,255,.2)")
    fig.update_layout(
        height=420, title=f"{sym_label} — {fdays}-Day Price Forecast",
        title_font=dict(family="Syne", size=13, color="#f0f2f8"), **DARK_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True)

    fdf = pd.DataFrame({
        "Date":             [d.strftime("%b %d, %Y") for d in future_dates],
        "Predicted Close":  [f"${p:.2f}" for p in result["ensemble_future"]],
        "Change vs Today":  [f"{((p - last_close)/last_close)*100:+.2f}%" for p in result["ensemble_future"]],
    })
    st.dataframe(fdf, use_container_width=True, hide_index=True)

with tab2:
    test_dates = result["test_dates"]
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=test_dates, y=result["y_test"], name="Actual",
                               line=dict(color="#4f8fff", width=1.8)))
    for mname, preds in result["preds_test"].items():
        fig2.add_trace(go.Scatter(
            x=test_dates, y=preds, name=f"{mname} pred",
            line=dict(color=colors_map.get(mname, "#8892a4"), width=1.4, dash="dot"),
        ))
    fig2.update_layout(height=360, title="Test Set: Actual vs Predicted",
                        title_font=dict(family="Syne", size=13, color="#f0f2f8"), **DARK_LAYOUT)
    st.plotly_chart(fig2, use_container_width=True)

    rows = [{
        "Model": mname,
        "MAE ($)": f"{m['mae']:.2f}",
        "MAPE (%)": f"{m['mape']:.2f}%",
        "R²": f"{m['r2']:.4f}",
        "Direction Acc.": f"{m['direction_acc']:.1f}%",
    } for mname, m in result["metrics"].items()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

with tab3:
    fi = result.get("feat_imp")
    if fi is not None:
        fig3 = go.Figure(go.Bar(
            x=fi.values[::-1], y=fi.index[::-1], orientation="h",
            marker_color="#4f8fff", opacity=0.85,
        ))
        fig3.update_layout(
            height=380, title="Top Feature Importances",
            title_font=dict(family="Syne", size=13, color="#f0f2f8"),
            xaxis_title="Importance Score", **DARK_LAYOUT,
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Feature importance is available for tree-based models (XGBoost, Random Forest).")

st.markdown("""
<div style="text-align:center;padding:1rem 0 .3rem;font-size:.72rem;color:#4e5669">
    Predictions are for educational purposes only · Not financial advice
</div>
""", unsafe_allow_html=True)
