import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

# --- SID-KONFIGURATION ---
st.set_page_config(page_title="QuantTrader", page_icon="🚀", layout="centered")

# --- CSS FÖR ATT FÅ DET ATT SE UT SOM EN APP PÅ MOBILEN ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold;}
    .reportview-container .main .block-container { max-width: 600px; padding-top: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
</style>
""", unsafe_allow_html=True)

# --- DIN LISTA (Du kan dölja denna i en separat fil om du vill, men här är enklast) ---
DEFAULT_LISTA = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "LLY", "V",
    "UNH", "XOM", "JNJ", "JPM", "PG", "MA", "AVGO", "HD", "CVX", "MRK", "PEP",
    "COST", "KO", "ABBV", "ADBE", "WMT", "MCD", "CSCO", "CRM", "BAC", "ACN",
    "LIN", "AMD", "NFLX", "ORCL", "DIS", "WFC", "TXN", "DHR", "CAT", "NEE",
    "PM", "VZ", "SPGI", "RTX", "HON", "INTC", "UNP", "LOW", "QCOM", "IBM"
]

# --- FUNKTIONER (Cachade för snabbhet) ---

@st.cache_data(ttl=3600) # Sparar data i 1 timme så du slipper ladda om
def get_usd_sek():
    try:
        data = yf.Ticker("SEK=X").history(period="1d")
        return data["Close"].iloc[-1]
    except:
        return 11.0

@st.cache_data(ttl=3600)
def get_names_map(tickers):
    names = {}
    if not tickers: return names
    try:
        txt = " ".join(tickers)
        batch = yf.Tickers(txt)
        for t, obj in batch.tickers.items():
            n = obj.info.get('shortName') or obj.info.get('longName') or t
            n = n.replace(" Corporation", "").replace(" Inc.", "").replace(" Company", "").replace(" Holdings", "")
            names[t] = n
    except:
        pass
    return names

def run_strategy(capital, tickers):
    status_text = st.status("Hämtar marknadsdata...", expanded=True)
    
    start_date = datetime.now() - timedelta(days=730)
    
    # Ladda ner data
    status_text.write("📡 Kontaktar börsen...")
    # Ladda ner allt i en batch (snabbare än chunks på server)
    data = yf.download(tickers, start=start_date, interval="1mo", progress=False, auto_adjust=True)
    
    if isinstance(data.columns, pd.MultiIndex):
        col = "Adj Close" if "Adj Close" in data.columns.levels[0] else "Close"
        prices = data[col]
    else:
        prices = data["Adj Close"]

    # Index
    status_text.write("📊 Kollar marknadstrenden (S&P 500)...")
    spy = yf.download("^GSPC", start=start_date, interval="1mo", progress=False, auto_adjust=True)
    bench_price = spy["Close"].iloc[-1]
    if isinstance(bench_price, pd.Series): bench_price = bench_price.iloc[0]
    
    # Strategi
    status_text.write("🧠 Räknar ut optimal portfölj...")
    momentum = prices.pct_change(periods=11).iloc[-1].dropna()
    winners = momentum.nlargest(10)
    
    returns = prices.pct_change().tail(12)[winners.index]
    inv_vol = 1.0 / returns.std()
    weights = inv_vol / inv_vol.sum()
    
    # Filter
    sma10 = prices.rolling(10).mean().iloc[-1]
    curr = prices.iloc[-1]
    bench_sma = spy["Close"].rolling(10).mean().iloc[-1]
    if isinstance(bench_sma, pd.Series): bench_sma = bench_sma.iloc[0]

    final_weights = weights.copy()
    
    for t in winners.index:
        if curr[t] < sma10[t]:
            final_weights[t] = 0.0
            
    regime = "BULL"
    multiplier = 1.0
    if bench_price < bench_sma:
        final_weights *= 0.5
        regime = "BEAR"
        multiplier = 0.5
        
    status_text.update(label="Klar!", state="complete", expanded=False)
    return final_weights, regime, multiplier

# --- GUI ---

st.title("🚀 QuantTrader")
st.caption(f"Dagens datum: {datetime.now().date()}")

# Input för kapital
with st.container():
    capital = st.number_input("Ditt Kapital (SEK)", value=100000, step=10000)

# Expander för att redigera listan om man vill
with st.expander("⚙️ Inställningar & Aktielista"):
    raw_tickers = st.text_area("S&P 500 Tickers (kommaseparerade)", ", ".join(DEFAULT_LISTA))
    tickers = [x.strip() for x in raw_tickers.split(",") if x.strip()]

if st.button("Kör Analys"):
    usd_rate = get_usd_sek()
    weights, regime, mult = run_strategy(capital, tickers)
    
    # Hämta namn för vinnarna
    active_tickers = list(weights[weights > 0.001].index)
    names_map = get_names_map(active_tickers)
    
    # Topp-metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("USD/SEK", f"{usd_rate:.2f}")
    col2.metric("Trend", regime, delta="Full Gas" if regime=="BULL" else "Halv Fart", delta_color="normal")
    col3.metric("Exp.", f"{mult*100:.0f}%")
    
    st.divider()
    
    # Skapa snygg tabell
    portfolio_data = []
    active = weights[weights > 0.001].sort_values(ascending=False)
    total_invested = 0
    
    for t, w in active.items():
        sek = capital * w
        name = names_map.get(t, t)
        portfolio_data.append({
            "Bolag": name,
            "Ticker": t,
            "Vikt": f"{w*100:.1f}%",
            "Belopp": f"{sek:,.0f} kr"
        })
        total_invested += sek
        
    df_display = pd.DataFrame(portfolio_data)
    
    st.subheader("🛒 Din Köplista")
    if not df_display.empty:
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.warning("Inga aktier uppfyller kraven just nu.")
        
    # Kassa
    cash = capital - total_invested
    st.success(f"💰 **KASSA (Likvider):** {cash:,.0f} kr ({(cash/capital)*100:.1f}%)")
    
    if cash > capital * 0.4:
        st.info("Hög kassa? Marknaden är svag eller dina toppaktier handlas under sina medelvärden.")
