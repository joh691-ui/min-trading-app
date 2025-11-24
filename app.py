import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

# --- SID-KONFIGURATION ---
st.set_page_config(page_title="Skapa S&P500-portfölj", page_icon="🚀", layout="centered")

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
    "MMM",
"AOS",
"ABT",
"ABBV",
"ACN",
"ADBE",
"AMD",
"AES",
"AFL",
"A",
"APD",
"ABNB",
"AKAM",
"ALB",
"ARE",
"ALGN",
"ALLE",
"LNT",
"ALL",
"GOOGL",
"GOOG",
"MO",
"AMZN",
"AMCR",
"AEE",
"AEP",
"AXP",
"AIG",
"AMT",
"AWK",
"AMP",
"AME",
"AMGN",
"APH",
"ADI",
"AON",
"APA",
"APO",
"AAPL",
"AMAT",
"APTV",
"ACGL",
"ADM",
"ANET",
"AJG",
"AIZ",
"T",
"ATO",
"ADSK",
"ADP",
"AZO",
"AVB",
"AVY",
"AXON",
"BKR",
"BALL",
"BAC",
"BK",
"BAX",
"BDX",
"BRK-B",
"BBY",
"BIIB",
"TECH",
"BLK",
"BX",
"XYZ",
"BKNG",
"BXP",
"BSX",
"BMY",
"AVGO",
"BR",
"BRO",
"BF-B",
"BLDR",
"BG",
"CHRW",
"CDNS",
"CZR",
"CPT",
"CPB",
"COF",
"CAH",
"KMX",
"CCL",
"CARR",
"CAT",
"CBOE",
"CBRE",
"CDW",
"COR",
"CNC",
"CNP",
"CF",
"CRL",
"SCHW",
"CHTR",
"CVX",
"CMG",
"CB",
"CHD",
"CINF",
"CTAS",
"CSCO",
"C",
"CFG",
"CME",
"CMS",
"CTSH",
"COIN",
"CL",
"CMCSA",
"CAG",
"COP",
"ED",
"STZ",
"CEG",
"CPRT",
"GLW",
"CPAY",
"CTVA",
"CSGP",
"COST",
"CTRA",
"CRWD",
"CCI",
"CSX",
"CMI",
"CVS",
"DHI",
"DHR",
"DRI",
"DDOG",
"DVA",
"DAY",
"DECK",
"DE",
"DELL",
"DAL",
"DVN",
"DXCM",
"FANG",
"DLR",
"DG",
"DLTR",
"D",
"DPZ",
"DASH",
"DOV",
"DOW",
"DTE",
"DUK",
"DD",
"EMN",
"ETN",
"EBAY",
"ECL",
"EIX",
"EW",
"EA",
"ELV",
"LLY",
"EMR",
"ENPH",
"ETR",
"EOG",
"EPAM",
"EQT",
"EFX",
"EQIX",
"EQR",
"ERIE",
"ESS",
"EL",
"EG",
"EVRG",
"ES",
"EXC",
"EXE",
"EXPE",
"EXPD",
"EXR",
"XOM",
"FFIV",
"FDS",
"FICO",
"FAST",
"FRT",
"FDX",
"FIS",
"FITB",
"FSLR",
"FE",
"FI",
"F",
"FTNT",
"FTV",
"FOXA",
"FOX",
"BEN",
"FCX",
"GRMN",
"IT",
"GE",
"GEHC",
"GEV",
"GEN",
"GNRC",
"GD",
"GIS",
"GM",
"GPC",
"GILD",
"GPN",
"GL",
"GDDY",
"GS",
"HAL",
"HAS",
"HCA",
"DOC",
"HSIC",
"HPE",
"HLT",
"HOLX",
"HD",
"HON",
"HRL",
"HST",
"HWM",
"HPQ",
"HUBB",
"HUM",
"HBAN",
"HII",
"IEX",
"IDXX",
"ITW",
"INCY",
"IR",
"PODD",
"INTC",
"ICE",
"IBM",
"IFF",
"IP",
"INTU",
"ISRG",
"IVZ",
"INVH",
"IQV",
"IRM",
"JBHT",
"JBL",
"JKHY",
"J",
"JNJ",
"JCI",
"JPM",
"K",
"KVUE",
"KDP",
"KEY",
"KEYS",
"KMB",
"KIM",
"KMI",
"KKR",
"KLAC",
"KR",
"LHX",
"LH",
"LRCX",
"LW",
"LVS",
"LDOS",
"LEN",
"LII",
"LIN",
"LYV",
"LKQ",
"LMT",
"L",
"LOW",
"LULU",
"LYB",
"MTB",
"MPC",
"MKTX",
"MAR",
"MMC",
"MLM",
"MAS",
"MA",
"MTCH",
"MKC",
"MCD",
"MCK",
"MDT",
"MRK",
"META",
"MET",
"MTD",
"MGM",
"MCHP",
"MU",
"MSFT",
"MAA",
"MRNA",
"MHK",
"MOH",
"TAP",
"MDLZ",
"MPWR",
"MNST",
"MCO",
"MS",
"MOS",
"MSI",
"MSCI",
"NDAQ",
"NTAP",
"NFLX",
"NEM",
"NWSA",
"NWS",
"NEE",
"NKE",
"NI",
"NDSN",
"NSC",
"NTRS",
"NOC",
"NCLH",
"NRG",
"NUE",
"NVDA",
"NVR",
"NXPI",
"OXY",
"ODFL",
"OMC",
"ON",
"OKE",
"ORCL",
"ORLY",
"OTIS",
"PCAR",
"PKG",
"PLTR",
"PANW",
"PSKY",
"PH",
"PAYX",
"PAYC",
"PYPL",
"PNR",
"PEP",
"PFE",
"PCG",
"PM",
"PSX",
"PNW",
"POOL",
"PPG",
"PPL",
"PFG",
"PG",
"PGR",
"PLD",
"PRU",
"PTC",
"PEG",
"PSA",
"PHM",
"QCOM",
"PWR",
"DGX",
"RL",
"RJF",
"O",
"REG",
"REGN",
"RF",
"RSG",
"RMD",
"RVTY",
"ROK",
"ROL",
"ROP",
"ROST",
"RCL",
"RTX",
"SPGI",
"CRM",
"SBAC",
"SLB",
"STX",
"SRE",
"NOW",
"SPG",
"SWKS",
"SW",
"SNA",
"SOLV",
"SO",
"LUV",
"SWK",
"SBUX",
"STT",
"STLD",
"STE",
"SYK",
"SMCI",
"SYF",
"SNPS",
"SYY",
"TROW",
"TTWO",
"TPR",
"TRGP",
"TGT",
"TEL",
"TDY",
"TER",
"TSLA",
"TXN",
"TXT",
"BA",
"CI",
"CLX",
"KO",
"COO",
"HIG",
"HSY",
"IPG",
"SJM",
"KHC",
"PNC",
"SHW",
"TTD",
"DIS",
"WMB",
"TMO",
"TJX",
"TKO",
"TMUS",
"TSCO",
"TT",
"TDG",
"TRV",
"TRMB",
"TFC",
"TYL",
"TSN",
"USB",
"UBER",
"UDR",
"ULTA",
"UNP",
"UAL",
"UPS",
"URI",
"UNH",
"UHS",
"VLO",
"V",
"VTR",
"VLTO",
"VRSN",
"VRSK",
"VZ",
"VRTX",
"VTRS",
"VICI",
"VST",
"VMC",
"WRB",
"GWW",
"WAB",
"WMT",
"WBD",
"WM",
"WAT",
"WEC",
"WFC",
"WELL",
"WST",
"WDC",
"WY",
"WSM",
"WTW",
"WDAY",
"WYNN",
"XEL",
"XYL",
"YUM",
"ZBRA",
"ZBH",
"ZTS"
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
