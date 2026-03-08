import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="FARIA | QUANT TERMINAL", page_icon="📈", layout="wide")

# --- 2. STYLE "THE BLACK BOX" ---
st.markdown("""
    <style>
    .stApp { background-color: #05070A; color: #FFFFFF; font-family: 'JetBrains Mono', monospace; }
    .app-logo { text-align: center; padding: 25px 0; border-bottom: 1px solid #1E222D; margin-bottom: 30px; }
    .logo-f { font-size: 32px; font-weight: 900; color: #FFFFFF; }
    .logo-invest { font-size: 32px; font-weight: 200; color: #00D1FF; }
    .data-card { background-color: #0D1117; padding: 20px; border-radius: 10px; border: 1px solid #30363D; margin-bottom: 15px; }
    .data-row { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #21262D; }
    .data-label { color: #8B949E; font-size: 13px; }
    .data-value { font-weight: 700; color: #F0F6FC; }
    .veredito { padding: 20px; border-radius: 8px; text-align: center; font-weight: 900; font-size: 24px; margin: 20px 0; border: 1px solid rgba(255,255,255,0.1); }
    div.stButton > button { width: 100% !important; background: #0070FF !important; color: white !important; font-weight: 800; border-radius: 4px; height: 3.5em; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE PERSISTÊNCIA ---
if not os.path.exists("dados"): os.makedirs("dados")

def load_data(name):
    path = f"dados/{name}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        if not df.empty and "Mês" in df.columns:
            df['dt_tmp'] = pd.to_datetime(df['Mês'], format='%b %y', errors='coerce')
            df = df.sort_values(by='dt_tmp', ascending=False).drop(columns=['dt_tmp'])
        return df
    return pd.DataFrame()

def get_month_options():
    months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    y = datetime.now().year % 100
    return [f"{m} {y}" for m in months[::-1]] + [f"{m} {y-1}" for m in months[::-1]]

# --- 4. MOTOR DCF (ROBUSTO) ---
def safe_dcf(ticker_info, growth_est):
    try:
        fcf = ticker_info.get('freeCashflow') or ticker_info.get('operatingCashflow', 0) * 0.8
        shares = ticker_info.get('sharesOutstanding')
        if not fcf or not shares or shares == 0: return 0
        
        r = 0.10 # Discount Rate (10%)
        g = min(growth_est, 0.15) # Cap de crescimento conservador
        tg = 0.02 # Terminal Growth (2%)
        
        # PV de 5 anos
        pv_cfs = sum([(fcf * (1 + g)**i) / (1 + r)**i for i in range(1, 6)])
        # Terminal Value
        tv = (fcf * (1 + g)**5 * (1 + tg)) / (r - tg)
        pv_tv = tv / (1 + r)**5
        
        return (pv_cfs + pv_tv) / shares
    except: return 0

# --- 5. LOGIN ---
if 'acesso' not in st.session_state: st.session_state.acesso = False
if not st.session_state.acesso:
    st.markdown('<div class="app-logo"><span class="logo-f">F</span><span class="logo-invest">|QUANT</span></div>', unsafe_allow_html=True)
    _, c2, _ = st.columns([1, 4, 1])
    with c2:
        pwd = st.text_input("ACCESS CODE", type="password")
        if st.button("AUTHENTICATE") or pwd == "1214":
            if pwd == "1214": st.session_state.acesso = True; st.rerun()
    st.stop()

# --- 6. INTERFACE ---
st.markdown('<div class="app-logo"><span class="logo-f">F</span><span class="logo-invest">|QUANT</span></div>', unsafe_allow_html=True)
menu = st.tabs(["🏛️ ASSETS", "💰 FLOW", "🔬 QUANT ALGO V7"])

# ABA ASSETS
with menu[0]:
    df_p = load_data("patrimonio")
    val = df_p["Total"].iloc[0] if not df_p.empty else 0
    st.markdown(f"<h1 style='text-align:center; color:#00FF85;'>{val:,.2f} €</h1>", unsafe_allow_html=True)
    with st.expander("LOG NEW DATA"):
        m = st.selectbox("Month", get_month_options(), key="p_m")
        c1, c2 = st.columns(2)
        v1 = c1.number_input("T212", 0.0); v2 = c2.number_input("IBKR", 0.0)
        v3 = c1.number_input("CRYPTO", 0.0); v4 = c2.number_input("OTHER", 0.0)
        if st.button("SAVE ASSETS"):
            new = pd.DataFrame([{"Mês": m, "T212": v1, "IBKR": v2, "CRY": v3, "PPR": v4, "Total": v1+v2+v3+v4}])
            pd.concat([df_p, new], ignore_index=True).to_csv("dados/patrimonio.csv", index=False); st.rerun()
    for i, r in df_p.iterrows():
        st.markdown(f'<div class="data-card"><b>{r["Mês"]}</b>: {r["Total"]:,.2f} €</div>', unsafe_allow_html=True)

# ABA FLOW
with menu[1]:
    df_f = load_data("poupanca")
    with st.expander("LOG MONTHLY FLOW"):
        mf = st.selectbox("Month", get_month_options(), key="f_m")
        e = st.number_input("Incomes", 0.0); s = st.number_input("Expenses", 0.0)
        if st.button("SAVE FLOW"):
            new = pd.DataFrame([{"Mês": mf, "Incomes": e, "Expenses": s}])
            pd.concat([df_f, new], ignore_index=True).to_csv("dados/poupanca.csv", index=False); st.rerun()
    for i, r in df_f.iterrows():
        st.markdown(f'<div class="data-card">{r["Mês"]} | Net: {r["Incomes"]-r["Expenses"]:,.2f} €</div>', unsafe_allow_html=True)

# ABA ANALYTICS (O CORAÇÃO)
with menu[2]:
    ticker_in = st.text_input("SCAN TICKER", "").upper()
    if ticker_in:
        try:
            with st.spinner("Executing Algorithm..."):
                stock = yf.Ticker(ticker_in)
                inf = stock.info
                
                # Coleta de dados com fallback (evita o erro que tiveste)
                price = inf.get('currentPrice', 0)
                rev_g = inf.get('revenueGrowth', 0)
                eps_g = inf.get('earningsGrowth', 0)
                margin = inf.get('profitMargins', 0)
                roic = (inf.get('returnOnAssets') or 0) * 2
                cfo = inf.get('operatingCashflow', 0)
                ni = inf.get('netIncomeToCommon', 1)
                debt_ebitda = inf.get('debtToEbitda', 0)
                
                st.markdown(f"### {inf.get('longName', ticker_in)}")
                
                # Grid de Métricas
                c1, c2 = st.columns(2)
                score = 0
                
                with c1:
                    st.write("📊 **Growth & Margins**")
                    m1 = [("Revenue > 7%", rev_g > 0.07, f"{rev_g*100:.1f}%"),
                          ("Net Income > 9%", eps_g > 0.09, f"{eps_g*100:.1f}%"),
                          ("Net Margin > 10%", margin > 0.10, f"{margin*100:.1f}%")]
                    for l, p, v in m1:
                        score += 1 if p else 0
                        st.markdown(f'<div class="data-row"><span class="data-label">{l}</span><span class="data-value">{v} {"✅" if p else "❌"}</span></div>', unsafe_allow_html=True)
                
                with col2:
                    st.write("💰 **Cash & Debt**")
                    cfo_ni = cfo/ni if ni != 0 else 0
                    m2 = [("ROIC > 15%", roic > 0.15, f"{roic*100:.1f}%"),
                          ("CFO/NI > 90%", cfo_ni > 0.90, f"{cfo_ni*100:.1f}%"),
                          ("Debt/EBITDA < 3", 0 < debt_ebitda < 3, f"{debt_ebitda:.2f}")]
                    for l, p, v in m2:
                        score += 1 if p else 0
                        st.markdown(f'<div class="data-row"><span class="data-label">{l}</span><span class="data-value">{v} {"✅" if p else "❌"}</span></div>', unsafe_allow_html=True)

                # Valuation DCF
                intrinsic = safe_dcf(inf, rev_g)
                upside = ((intrinsic / price) - 1) * 100 if price > 0 else 0
                
                # Veredito
                status = "APPROVED" if score == 6 and upside > 15 else "WAITLIST" if score >= 4 else "REJECTED"
                color = "#00FF85" if status == "APPROVED" else "#FFD700" if status == "WAITLIST" else "#FF5252"
                
                st.markdown(f'<div class="veredito" style="background:{color}; color:#05070A;">{status} ({score}/6)</div>', unsafe_allow_html=True)
                
                v1, v2, v3 = st.columns(3)
                v1.metric("Market Price", f"{price:.2f}")
                v2.metric("Intrinsic (DCF)", f"{intrinsic:.2f}")
                v3.metric("Safety Margin", f"{upside:.1f}%", delta=f"{upside:.1f}%")
                
                st.latex(r"V_0 = \sum_{t=1}^{5} \frac{FCF_0(1+g)^t}{(1+r)^t} + \frac{TV}{(1+r)^5}")

        except Exception as e:
            st.error(f"Erro na extração: {ticker_in} pode ter dados limitados no Yahoo Finance.")

st.markdown("<br><center style='color:#30363D; font-size:10px;'>QUANT TERMINAL V7 | EXCLUSIVE ACCESS</center>", unsafe_allow_html=True)
