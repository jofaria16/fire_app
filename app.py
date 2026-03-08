import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf
import numpy as np

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="FARIA | QUANT TERMINAL v9.0", page_icon="📈", layout="wide")

# --- 2. CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;800&display=swap');
    
    .stApp { background-color: #05070A; color: #E8EAF0; font-family: 'DM Sans', sans-serif; }
    
    .main-header { text-align: center; padding: 24px 0 16px; border-bottom: 1px solid #1A1F2E; margin-bottom: 28px; }
    .logo-f  { font-size: 28px; font-weight: 800; color: #FFFFFF; font-family: 'Space Mono', monospace; letter-spacing: -1px; }
    .logo-q  { font-size: 28px; font-weight: 400; color: #00C8FF; font-family: 'Space Mono', monospace; }
    .logo-v  { font-size: 11px; color: #404860; letter-spacing: 4px; margin-top: 4px; }
    
    .metric-card { background: #0B0E14; padding: 16px 20px; border-radius: 10px; border: 1px solid #1A1F2E; margin-bottom: 12px; transition: border-color 0.2s; }
    .metric-card:hover { border-color: #2A3048; }
    .metric-row { display: flex; justify-content: space-between; align-items: center; padding: 7px 0; border-bottom: 1px solid #12161F; font-size: 13px; }
    .metric-row:last-child { border-bottom: none; }
    
    .verdict-bar { padding: 14px 20px; border-radius: 8px; text-align: center; font-weight: 800; font-size: 18px; margin: 16px 0; letter-spacing: 2px; font-family: 'Space Mono', monospace; }
    
    .sector-badge { display: inline-block; background: #12161F; border: 1px solid #252B3B; padding: 3px 10px; border-radius: 20px; font-size: 11px; color: #7888AA; margin-left: 8px; text-transform: uppercase; letter-spacing: 1px; }
    
    .dcf-box { background: #0B0E14; border: 1px solid #1A2535; border-radius: 10px; padding: 16px 20px; margin-top: 12px; }
    .dcf-title { font-size: 11px; color: #4A5570; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 12px; font-family: 'Space Mono', monospace; }
    .dcf-row { display: flex; justify-content: space-between; padding: 5px 0; font-size: 13px; color: #8898BB; }
    .dcf-row span:last-child { color: #C8D8F8; font-family: 'Space Mono', monospace; }
    
    div.stButton > button { 
        width: 100% !important; 
        background: linear-gradient(90deg, #0050CC, #0090FF) !important; 
        color: white !important; font-weight: 700; border-radius: 6px; border: none; height: 2.8em;
        font-family: 'Space Mono', monospace; letter-spacing: 1px;
        transition: opacity 0.2s;
    }
    div.stButton > button:hover { opacity: 0.85; }
    
    .stTextInput input, .stNumberInput input, .stSelectbox select { 
        background-color: #0B0E14 !important; color: #E8EAF0 !important; 
        border: 1px solid #252B3B !important; border-radius: 6px !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    .stTabs [data-baseweb="tab-list"] { background: #0B0E14; border-radius: 8px; border: 1px solid #1A1F2E; }
    .stTabs [data-baseweb="tab"] { color: #606880; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #00C8FF !important; }

    /* Remove default streamlit padding */
    .block-container { padding-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATABASE ---
if not os.path.exists("dados"):
    os.makedirs("dados")

def save_db(df, name):
    df.to_csv(f"dados/{name}.csv", index=False)

def load_db(name):
    path = f"dados/{name}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        if not df.empty and "Mês" in df.columns:
            try:
                df['tmp_dt'] = pd.to_datetime(df['Mês'], format='%b %y', errors='coerce')
                df = df.sort_values('tmp_dt', ascending=False).drop(columns=['tmp_dt'])
            except:
                pass
        return df
    return pd.DataFrame()

def get_months():
    m_names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    curr_y = datetime.now().year % 100
    return [f"{m} {curr_y}" for m in m_names[::-1]] + [f"{m} {curr_y-1}" for m in m_names[::-1]]

# --- 4. SECTOR DETECTION ---
SECTOR_CONFIG = {
    "Technology": {
        "method": "dcf",
        "discount_rate": 0.10,
        "terminal_growth": 0.03,
        "growth_cap": 0.25,
        "label": "DCF (High-Growth Tech)",
        "color": "#00C8FF"
    },
    "Communication Services": {
        "method": "dcf",
        "discount_rate": 0.10,
        "terminal_growth": 0.025,
        "growth_cap": 0.20,
        "label": "DCF (Media/Comms)",
        "color": "#00C8FF"
    },
    "Consumer Cyclical": {
        "method": "ev_ebitda",
        "target_multiple": 14,
        "label": "EV/EBITDA (Consumer)",
        "color": "#FFB347"
    },
    "Consumer Defensive": {
        "method": "pe_relative",
        "fair_pe": 22,
        "label": "P/E Relativo (Defensivo)",
        "color": "#98FF98"
    },
    "Healthcare": {
        "method": "dcf",
        "discount_rate": 0.09,
        "terminal_growth": 0.025,
        "growth_cap": 0.18,
        "label": "DCF (Healthcare)",
        "color": "#FF9ECD"
    },
    "Financial Services": {
        "method": "pb_roe",
        "label": "P/B + ROE (Financeiras)",
        "color": "#FFD700"
    },
    "Industrials": {
        "method": "ev_ebitda",
        "target_multiple": 11,
        "label": "EV/EBITDA (Industriais)",
        "color": "#B0C4DE"
    },
    "Basic Materials": {
        "method": "ev_ebitda",
        "target_multiple": 8,
        "label": "EV/EBITDA (Materiais)",
        "color": "#DEB887"
    },
    "Energy": {
        "method": "ev_ebitda",
        "target_multiple": 7,
        "label": "EV/EBITDA (Energia)",
        "color": "#FFA07A"
    },
    "Real Estate": {
        "method": "nav",
        "label": "NAV/FFO (REIT)",
        "color": "#9370DB"
    },
    "Utilities": {
        "method": "ddm",
        "label": "DDM (Utilities/Dividendo)",
        "color": "#7EC8E3"
    },
    "default": {
        "method": "dcf",
        "discount_rate": 0.10,
        "terminal_growth": 0.025,
        "growth_cap": 0.15,
        "label": "DCF (Geral)",
        "color": "#A0A8C0"
    }
}

# --- 5. INTRINSIC VALUE ENGINE (SECTOR-ADJUSTED) ---
def get_sector_config(sector):
    return SECTOR_CONFIG.get(sector, SECTOR_CONFIG["default"])

def safe_get(d, *keys, default=0):
    """Try multiple keys, return first non-None/non-zero value"""
    for key in keys:
        val = d.get(key)
        if val is not None and val != 0 and not (isinstance(val, float) and np.isnan(val)):
            return val
    return default

def calculate_intrinsic_value(info, sector):
    cfg = get_sector_config(sector)
    method = cfg["method"]
    shares = safe_get(info, 'sharesOutstanding', default=1)
    price = safe_get(info, 'currentPrice', 'previousClose', default=1)

    result = {
        "method_label": cfg["label"],
        "color": cfg["color"],
        "value": 0,
        "components": {}
    }

    try:
        # ── DCF (Technology, Healthcare, Comms) ──────────────────────────────
        if method == "dcf":
            dr  = cfg.get("discount_rate", 0.10)
            tg  = cfg.get("terminal_growth", 0.025)
            cap = cfg.get("growth_cap", 0.15)

            # FCF: try freeCashflow first, then operating - capex
            fcf = safe_get(info, 'freeCashflow', default=0)
            if fcf <= 0:
                ocf  = safe_get(info, 'operatingCashflow', default=0)
                capx = abs(safe_get(info, 'capitalExpenditures', default=0))
                fcf  = ocf - capx

            if fcf <= 0:
                # last resort: use net income as proxy
                fcf = safe_get(info, 'netIncomeToCommon', default=0)

            if fcf <= 0 or shares <= 0:
                return result

            rev_g = safe_get(info, 'revenueGrowth', default=0.05)
            eps_g = safe_get(info, 'earningsGrowth', default=0.05)
            g = min(max((rev_g + eps_g) / 2, 0.03), cap)

            pv_cfs = sum([(fcf * (1 + g)**i) / (1 + dr)**i for i in range(1, 6)])
            fcf_5  = fcf * (1 + g)**5
            tv     = (fcf_5 * (1 + tg)) / (dr - tg)
            pv_tv  = tv / (1 + dr)**5

            iv = (pv_cfs + pv_tv) / shares
            result["value"] = iv
            result["components"] = {
                "FCF Base": f"${fcf/1e9:.2f}B",
                "Taxa Crescimento": f"{g*100:.1f}%",
                "Taxa Desconto": f"{dr*100:.0f}%",
                "Terminal Growth": f"{tg*100:.1f}%",
                "PV Fluxos (5a)": f"${pv_cfs/1e9:.1f}B",
                "PV Terminal": f"${pv_tv/1e9:.1f}B"
            }

        # ── EV/EBITDA (Consumer, Industrial, Energy, Materials) ──────────────
        elif method == "ev_ebitda":
            ebitda = safe_get(info, 'ebitda', default=0)
            debt   = safe_get(info, 'totalDebt', default=0)
            cash   = safe_get(info, 'totalCash', 'cashAndCashEquivalents', default=0)
            target = cfg.get("target_multiple", 12)

            if ebitda <= 0 or shares <= 0:
                return result

            ev_implied = ebitda * target
            equity     = ev_implied - debt + cash
            iv         = equity / shares

            result["value"] = iv
            result["components"] = {
                "EBITDA": f"${ebitda/1e9:.2f}B",
                "Múltiplo Alvo": f"{target}x",
                "EV Implícito": f"${ev_implied/1e9:.1f}B",
                "Dívida Líquida": f"${(debt-cash)/1e9:.1f}B"
            }

        # ── P/E Relativo (Consumer Defensive) ────────────────────────────────
        elif method == "pe_relative":
            eps       = safe_get(info, 'trailingEps', 'forwardEps', default=0)
            fair_pe   = cfg.get("fair_pe", 20)
            # adjust fair PE for growth
            rev_g     = safe_get(info, 'revenueGrowth', default=0.05)
            adj_pe    = fair_pe * (1 + rev_g)

            if eps <= 0:
                return result

            iv = eps * adj_pe
            result["value"] = iv
            result["components"] = {
                "EPS (TTM)": f"${eps:.2f}",
                "P/E Justo": f"{fair_pe}x",
                "Ajuste Crescimento": f"+{rev_g*100:.1f}%",
                "P/E Ajustado": f"{adj_pe:.1f}x"
            }

        # ── P/B + ROE (Financeiras) ───────────────────────────────────────────
        elif method == "pb_roe":
            roe   = safe_get(info, 'returnOnEquity', default=0.10)
            bvps  = safe_get(info, 'bookValue', default=0)
            dr    = 0.10
            # Graham formula for banks: fair P/B = ROE / cost of equity
            fair_pb = max(roe / dr, 0.5)
            iv      = bvps * fair_pb

            result["value"] = iv
            result["components"] = {
                "Book Value/Share": f"${bvps:.2f}",
                "ROE": f"{roe*100:.1f}%",
                "Custo Capital": "10%",
                "P/B Justo": f"{fair_pb:.2f}x"
            }

        # ── DDM (Utilities) ───────────────────────────────────────────────────
        elif method == "ddm":
            div_rate  = safe_get(info, 'dividendRate', default=0)
            div_yield = safe_get(info, 'dividendYield', default=0)
            dr        = 0.07
            g         = 0.025  # utilities grow slowly

            if div_rate <= 0:
                # estimate from yield
                div_rate = price * div_yield if div_yield > 0 else 0

            if div_rate <= 0:
                return result

            # Gordon Growth Model: P = D1 / (r - g)
            d1 = div_rate * (1 + g)
            iv = d1 / (dr - g)
            result["value"] = iv
            result["components"] = {
                "Dividendo Anual": f"${div_rate:.2f}",
                "Taxa Crescimento Div": f"{g*100:.1f}%",
                "Taxa Desconto": f"{dr*100:.0f}%",
                "D1": f"${d1:.2f}"
            }

        # ── NAV/FFO (REIT) ────────────────────────────────────────────────────
        elif method == "nav":
            # Use P/FFO proxy (FFO ≈ net income + depreciation for REITs)
            ni    = safe_get(info, 'netIncomeToCommon', default=0)
            dep   = safe_get(info, 'totalAssets', default=0) * 0.02  # rough depreciation
            ffo   = ni + dep
            if ffo <= 0 or shares <= 0:
                return result

            ffo_per_share = ffo / shares
            fair_p_ffo    = 16  # typical REIT fair multiple
            iv            = ffo_per_share * fair_p_ffo
            result["value"] = iv
            result["components"] = {
                "FFO Estimado": f"${ffo/1e6:.0f}M",
                "FFO/Share": f"${ffo_per_share:.2f}",
                "P/FFO Justo": "16x"
            }

    except Exception as e:
        result["components"]["Erro"] = str(e)

    return result

# --- 6. SAFE TICKER FETCH ---
def fetch_ticker_data(ticker_symbol):
    """Robust ticker data fetch with multiple fallbacks"""
    try:
        stock = yf.Ticker(ticker_symbol)
        
        # Force a real data fetch — .info can be lazy
        info = stock.info
        
        # Validate we actually got data (not just empty dict)
        if not info or len(info) < 5:
            return None, None, "Dados insuficientes retornados pelo Yahoo Finance."
        
        # Check essential fields exist
        name = info.get('longName') or info.get('shortName') or info.get('symbol')
        if not name:
            return None, None, f"Ticker '{ticker_symbol}' não reconhecido."
        
        # Try to get current price with multiple fallbacks
        price = (info.get('currentPrice') or 
                 info.get('regularMarketPrice') or 
                 info.get('previousClose') or 
                 info.get('navPrice') or 0)
        
        if price == 0:
            # Try getting price from history
            hist = stock.history(period="2d")
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
                info['currentPrice'] = price

        if price == 0:
            return None, None, f"Não foi possível obter cotação para '{ticker_symbol}'."
        
        return stock, info, None

    except Exception as e:
        err_str = str(e).lower()
        if "404" in err_str or "no data" in err_str:
            return None, None, f"Ticker '{ticker_symbol}' não encontrado no Yahoo Finance."
        return None, None, f"Erro ao carregar dados: {str(e)}"

# --- 7. AUTH ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown('<div class="main-header"><span class="logo-f">F</span><span class="logo-q">|QUANT</span><div class="logo-v">TERMINAL v9.0</div></div>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<br>", unsafe_allow_html=True)
        pwd = st.text_input("ACCESS KEY", type="password", placeholder="••••")
        if st.button("UNLOCK"):
            if pwd == "1214":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Chave incorreta.")
    st.stop()

# --- 8. MAIN INTERFACE ---
st.markdown('<div class="main-header"><span class="logo-f">F</span><span class="logo-q">|QUANT</span><div class="logo-v">TERMINAL v9.0</div></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🏛️  PATRIMÓNIO", "💰  FLUXO", "🔬  ANALYTICS"])

# ════════════════════════════════════════════════════════
# TAB 1 — PATRIMÓNIO
# ════════════════════════════════════════════════════════
with tab1:
    df_p = load_db("patrimonio")
    
    total_recente = df_p["Total"].iloc[0] if not df_p.empty else 0
    total_anterior = df_p["Total"].iloc[1] if len(df_p) > 1 else total_recente
    delta = total_recente - total_anterior
    delta_pct = (delta / total_anterior * 100) if total_anterior > 0 else 0
    delta_sign = "+" if delta >= 0 else ""
    delta_color = "#00FF85" if delta >= 0 else "#FF5252"
    
    col_total, col_delta = st.columns([3, 1])
    with col_total:
        st.markdown(f"<h1 style='text-align:center; color:#00FF85; font-family:Space Mono,monospace; font-size:2.8em; margin:0;'>{total_recente:,.2f} €</h1>", unsafe_allow_html=True)
    with col_delta:
        st.markdown(f"<div style='text-align:center; color:{delta_color}; font-family:Space Mono,monospace; font-size:1.1em; padding-top:18px;'>{delta_sign}{delta:,.0f}€<br><small>{delta_sign}{delta_pct:.1f}%</small></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("➕  ADICIONAR REGISTO"):
        m = st.selectbox("Mês", get_months(), key="m1")
        c1, c2 = st.columns(2)
        v1 = c1.number_input("Trading 212 (€)", min_value=0.0, format="%.2f")
        v2 = c2.number_input("IBKR (€)", min_value=0.0, format="%.2f")
        v3 = c1.number_input("Crypto (€)", min_value=0.0, format="%.2f")
        v4 = c2.number_input("Outros / PPR (€)", min_value=0.0, format="%.2f")
        if st.button("GRAVAR PATRIMÓNIO"):
            new_row = pd.DataFrame([{"Mês": m, "T212": v1, "IBKR": v2, "CRY": v3, "PPR": v4, "Total": v1+v2+v3+v4}])
            save_db(pd.concat([df_p, new_row], ignore_index=True), "patrimonio")
            st.success("Gravado!")
            st.rerun()
    
    for i, r in df_p.iterrows():
        cols = st.columns([4, 1])
        with cols[0]:
            breakdown = f'T212: {r.get("T212",0):,.0f}€ &nbsp;|&nbsp; IBKR: {r.get("IBKR",0):,.0f}€ &nbsp;|&nbsp; CRY: {r.get("CRY",0):,.0f}€ &nbsp;|&nbsp; PPR: {r.get("PPR",0):,.0f}€'
            st.markdown(f'''<div class="metric-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-family:Space Mono,monospace;">{r["Mês"]}</b>
                    <span style="color:#00FF85; font-size:1.2em; font-weight:700; font-family:Space Mono,monospace;">{r["Total"]:,.2f} €</span>
                </div>
                <div style="font-size:11px; color:#606880; margin-top:6px;">{breakdown}</div>
            </div>''', unsafe_allow_html=True)
        with cols[1]:
            if st.button("🗑", key=f"delp_{i}"):
                save_db(df_p.drop(i).reset_index(drop=True), "patrimonio")
                st.rerun()

# ════════════════════════════════════════════════════════
# TAB 2 — FLUXO
# ════════════════════════════════════════════════════════
with tab2:
    df_f = load_db("poupanca")
    
    if not df_f.empty:
        total_ent = df_f["Entradas"].sum()
        total_sai = df_f["Saidas"].sum()
        total_net = total_ent - total_sai
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Entradas", f"{total_ent:,.0f} €")
        c2.metric("Total Saídas", f"{total_sai:,.0f} €")
        c3.metric("Total Poupado", f"{total_net:,.0f} €", delta=f"{(total_net/total_ent*100):.1f}% taxa" if total_ent > 0 else "")

    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("➕  REGISTAR ENTRADAS/SAÍDAS"):
        mf  = st.selectbox("Mês", get_months(), key="m2")
        ent = st.number_input("Entradas (Salário, etc.) €", min_value=0.0, format="%.2f")
        sai = st.number_input("Saídas (Despesas, etc.) €", min_value=0.0, format="%.2f")
        if st.button("GRAVAR FLUXO"):
            new_f = pd.DataFrame([{"Mês": mf, "Entradas": ent, "Saidas": sai}])
            save_db(pd.concat([df_f, new_f], ignore_index=True), "poupanca")
            st.success("Gravado!")
            st.rerun()

    for i, r in df_f.iterrows():
        net = r['Entradas'] - r['Saidas']
        taxa = (net / r['Entradas'] * 100) if r['Entradas'] > 0 else 0
        net_color = "#00FF85" if net >= 0 else "#FF5252"
        cols = st.columns([4, 1])
        with cols[0]:
            st.markdown(f'''<div class="metric-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-family:Space Mono,monospace;">{r["Mês"]}</b>
                    <span style="color:{net_color}; font-weight:700; font-family:Space Mono,monospace;">+{net:,.2f} €</span>
                </div>
                <div style="font-size:11px; color:#606880; margin-top:6px;">
                    Entradas: {r["Entradas"]:,.0f}€ &nbsp;|&nbsp; Saídas: {r["Saidas"]:,.0f}€ &nbsp;|&nbsp; Taxa Poupança: {taxa:.1f}%
                </div>
            </div>''', unsafe_allow_html=True)
        with cols[1]:
            if st.button("🗑", key=f"delf_{i}"):
                save_db(df_f.drop(i).reset_index(drop=True), "poupanca")
                st.rerun()

# ════════════════════════════════════════════════════════
# TAB 3 — ANALYTICS v9
# ════════════════════════════════════════════════════════
with tab3:
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        ticker_in = st.text_input("", placeholder="SCAN TICKER  (ex: AAPL · GOOGL · NVDA · EDP.LS)", label_visibility="collapsed").strip().upper()
    with col_btn:
        scan_btn = st.button("SCAN")

    if ticker_in and scan_btn or (ticker_in and 'last_ticker' in st.session_state and st.session_state.last_ticker == ticker_in):
        st.session_state.last_ticker = ticker_in
        
        with st.spinner(f"Fetching {ticker_in}..."):
            stock, info, error = fetch_ticker_data(ticker_in)

        if error:
            st.error(f"❌  {error}")
        else:
            sector   = info.get('sector', 'default') or 'default'
            industry = info.get('industry', '')
            name     = info.get('longName') or info.get('shortName', ticker_in)
            price    = safe_get(info, 'currentPrice', 'regularMarketPrice', 'previousClose', default=1)
            currency = info.get('currency', 'USD')
            exchange = info.get('exchange', '')
            
            # Header
            st.markdown(f"""
                <div style="margin-bottom:16px;">
                    <span style="font-size:1.5em; font-weight:800;">{name}</span>
                    <span class="sector-badge">{sector}</span>
                    <span class="sector-badge">{industry[:30] if industry else ''}</span>
                    <div style="font-size:12px; color:#505870; margin-top:4px; font-family:Space Mono,monospace;">{ticker_in} · {exchange} · {currency}</div>
                </div>
            """, unsafe_allow_html=True)

            # Key metrics
            rev_g     = safe_get(info, 'revenueGrowth', default=0)
            eps_g     = safe_get(info, 'earningsGrowth', default=0)
            margin    = safe_get(info, 'profitMargins', default=0)
            roe       = safe_get(info, 'returnOnEquity', default=0)
            cfo       = safe_get(info, 'operatingCashflow', default=0)
            ni        = safe_get(info, 'netIncomeToCommon', default=1)
            debt_ebit = safe_get(info, 'debtToEbitda', default=0)
            beta      = safe_get(info, 'beta', default=1.0)
            pe_ttm    = safe_get(info, 'trailingPE', default=0)
            pe_fwd    = safe_get(info, 'forwardPE', default=0)
            ev_ebitda = safe_get(info, 'enterpriseToEbitda', default=0)

            # ── CHECKLIST ──
            col_l, col_r = st.columns(2)
            score = 0

            with col_l:
                st.markdown('<div class="dcf-box"><div class="dcf-title">📈 Crescimento & Rentabilidade</div>', unsafe_allow_html=True)
                checks_l = [
                    ("Receita > 7% a.a.",    rev_g > 0.07,  f"{rev_g*100:.1f}%"),
                    ("EPS Growth > 9%",       eps_g > 0.09,  f"{eps_g*100:.1f}%"),
                    ("Margem Líquida > 10%",  margin > 0.10, f"{margin*100:.1f}%"),
                ]
                for label, passed, val in checks_l:
                    score += 1 if passed else 0
                    icon   = "✅" if passed else "❌"
                    color  = "#00FF85" if passed else "#FF5252"
                    st.markdown(f'<div class="metric-row"><span>{label}</span><span style="color:{color}; font-family:Space Mono,monospace;">{val} {icon}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_r:
                st.markdown('<div class="dcf-box"><div class="dcf-title">💎 Qualidade & Balanço</div>', unsafe_allow_html=True)
                cfo_ni = cfo / ni if ni != 0 else 0
                checks_r = [
                    ("ROE > 15%",            roe > 0.15,         f"{roe*100:.1f}%"),
                    ("CFO / Net Income > 90%", cfo_ni > 0.90,    f"{cfo_ni*100:.1f}%"),
                    ("Dívida/EBITDA < 3x",   0 < debt_ebit < 3,  f"{debt_ebit:.2f}x"),
                ]
                for label, passed, val in checks_r:
                    score += 1 if passed else 0
                    icon   = "✅" if passed else "❌"
                    color  = "#00FF85" if passed else "#FF5252"
                    st.markdown(f'<div class="metric-row"><span>{label}</span><span style="color:{color}; font-family:Space Mono,monospace;">{val} {icon}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # ── VALUATION (SECTOR-ADJUSTED) ──
            iv_result = calculate_intrinsic_value(info, sector)
            iv        = iv_result["value"]
            upside    = ((iv / price) - 1) * 100 if price > 0 and iv > 0 else 0

            # Verdict
            if iv > 0:
                if score >= 5 and upside > 15:
                    verdict, vcolor = "✦  APPROVED", "#00FF85"
                elif score >= 3 and upside > -10:
                    verdict, vcolor = "◈  WATCHLIST", "#FFD700"
                else:
                    verdict, vcolor = "✕  REJECTED", "#FF5252"
            else:
                verdict, vcolor = "⚠  DADOS INSUFICIENTES", "#888"

            st.markdown(f'<div class="verdict-bar" style="background:{vcolor}22; color:{vcolor}; border:1px solid {vcolor}44;">{verdict} &nbsp; ({score}/6)</div>', unsafe_allow_html=True)

            # ── PRICE vs IV ──
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Preço Atual", f"{price:.2f} {currency}")
            if iv > 0:
                m2.metric(f"Valor Intrínseco", f"{iv:.2f} {currency}", delta=f"{upside:+.1f}%")
            else:
                m2.metric("Valor Intrínseco", "N/A")
            m3.metric("P/E TTM", f"{pe_ttm:.1f}x" if pe_ttm > 0 else "N/A")
            m4.metric("EV/EBITDA", f"{ev_ebitda:.1f}x" if ev_ebitda > 0 else "N/A")

            # ── VALUATION BREAKDOWN ──
            cfg = get_sector_config(sector)
            st.markdown(f'''
                <div class="dcf-box" style="margin-top:16px;">
                    <div class="dcf-title">🔢 Metodologia: {iv_result["method_label"]}</div>
            ''', unsafe_allow_html=True)
            for k, v in iv_result["components"].items():
                st.markdown(f'<div class="dcf-row"><span>{k}</span><span>{v}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # ── EXTRA METRICS ──
            with st.expander("📊 Métricas Adicionais"):
                extras = {
                    "Beta": f"{beta:.2f}",
                    "Market Cap": f"${info.get('marketCap', 0)/1e9:.1f}B" if info.get('marketCap') else "N/A",
                    "P/E Forward": f"{pe_fwd:.1f}x" if pe_fwd > 0 else "N/A",
                    "P/S Ratio": f"{info.get('priceToSalesTrailing12Months', 0):.1f}x" if info.get('priceToSalesTrailing12Months') else "N/A",
                    "P/B Ratio": f"{info.get('priceToBook', 0):.1f}x" if info.get('priceToBook') else "N/A",
                    "Dividend Yield": f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "N/A",
                    "52W High": f"{info.get('fiftyTwoWeekHigh', 0):.2f}" if info.get('fiftyTwoWeekHigh') else "N/A",
                    "52W Low": f"{info.get('fiftyTwoWeekLow', 0):.2f}" if info.get('fiftyTwoWeekLow') else "N/A",
                    "Analistas (Preço Alvo)": f"{info.get('targetMeanPrice', 0):.2f}" if info.get('targetMeanPrice') else "N/A",
                    "Recomendação": info.get('recommendationKey', 'N/A').upper(),
                }
                col1, col2 = st.columns(2)
                items = list(extras.items())
                for j, (k, v) in enumerate(items):
                    (col1 if j % 2 == 0 else col2).markdown(
                        f'<div class="metric-row"><span style="color:#606880;">{k}</span><span style="font-family:Space Mono,monospace;">{v}</span></div>',
                        unsafe_allow_html=True
                    )

    elif ticker_in and not scan_btn:
        st.session_state.last_ticker = ticker_in

st.markdown("<br><center style='color:#252B3B; font-size:10px; font-family:Space Mono,monospace;'>FARIA QUANT TERMINAL v9.0  ·  FOR PERSONAL USE ONLY</center>", unsafe_allow_html=True)
