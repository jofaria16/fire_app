import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FARIA | QUANT TERMINAL v6.1", page_icon="📈", layout="wide")

# --- 2. STYLE (WALL STREET DARK & CLEAN) ---
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #FFFFFF; }
    .app-logo { text-align: center; padding: 15px 0; border-bottom: 1px solid #1E222D; margin-bottom: 20px; }
    .logo-f { font-size: 30px; font-weight: 900; color: #FFFFFF; }
    .logo-invest { font-size: 30px; font-weight: 200; color: #00D1FF; }
    .metric-card { background-color: #161B22; padding: 20px; border-radius: 12px; border: 1px solid #30363D; margin-bottom: 10px; }
    .check-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #2D3444; font-size: 15px; }
    .status-box { padding: 20px; border-radius: 10px; text-align: center; font-weight: 800; font-size: 22px; margin-top: 20px; }
    div.stButton > button { width: 100% !important; border-radius: 8px; background: linear-gradient(135deg, #0070FF 0%, #00A3FF 100%); color: white; font-weight: 800; height: 3.5em; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE DADOS (PERSISTÊNCIA) ---
if not os.path.exists("dados"): os.makedirs("dados")

def load_data(name):
    path = f"dados/{name}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        if not df.empty and "Mês" in df.columns:
            try:
                df['dt_tmp'] = pd.to_datetime(df['Mês'], format='%b %y', errors='coerce')
                df = df.sort_values(by='dt_tmp', ascending=False).drop(columns=['dt_tmp'])
            except: pass
        return df
    return pd.DataFrame()

def get_month_options():
    months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    y = datetime.now().year % 100
    return [f"{m} {y}" for m in months[::-1]] + [f"{m} {y-1}" for m in months[::-1]]

# --- 4. MOTOR DCF PROFISSIONAL ---
def dcf_valuation(fcf, growth, discount_rate, shares):
    if fcf <= 0 or shares <= 0: return 0
    terminal_growth = 0.025
    cash_flows = []
    for i in range(1, 6):
        cf = fcf * (1 + growth) ** i
        discounted_cf = cf / (1 + discount_rate) ** i
        cash_flows.append(discounted_cf)
    tv = (fcf * (1 + growth)**5 * (1 + terminal_growth)) / (discount_rate - terminal_growth)
    discounted_tv = tv / (1 + discount_rate) ** 5
    return (sum(cash_flows) + discounted_tv) / shares

# --- 5. LOGIN ---
if 'acesso' not in st.session_state: st.session_state.acesso = False
if not st.session_state.acesso:
    st.markdown('<div class="app-logo"><span class="logo-f">F</span><span class="logo-invest">|INVEST</span></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 6, 1])
    with c2:
        pwd = st.text_input("PASSWORD", type="password")
        if st.button("LOGIN") or pwd == "1214":
            if pwd == "1214": st.session_state.acesso = True; st.rerun()
    st.stop()

# --- 6. INTERFACE PRINCIPAL ---
st.markdown('<div class="app-logo"><span class="logo-f">F</span><span class="logo-invest">|INVEST</span></div>', unsafe_allow_html=True)
menu = st.tabs(["🏛️ PORTFÓLIO", "💰 FLUXO", "🔬 ANALYTICS 6.1"])

# --- ABA 1: PORTFÓLIO ---
with menu[0]:
    df_pat = load_data("patrimonio")
    total_recente = df_pat["Total"].iloc[0] if not df_pat.empty else 0
    st.markdown(f"<h1 style='text-align:center; color:#00FF85;'>{total_recente:,.2f} €</h1>", unsafe_allow_html=True)
    
    with st.expander("➕ REGISTAR VALORES"):
        m_sel = st.selectbox("Mês de Referência", get_month_options(), key="p_month")
        c1, c2 = st.columns(2)
        v1 = c1.number_input("Trading 212 (€)", min_value=0.0)
        v2 = c2.number_input("IBKR (€)", min_value=0.0)
        v3 = c1.number_input("Crypto (€)", min_value=0.0)
        v4 = c2.number_input("PPR / Outros (€)", min_value=0.0)
        if st.button("GUARDAR PATRIMÓNIO"):
            total = v1 + v2 + v3 + v4
            new_row = pd.DataFrame([{"Mês": m_sel, "T212": v1, "IBKR": v2, "CRY": v3, "PPR": v4, "Total": total}])
            pd.concat([df_pat, new_row], ignore_index=True).to_csv("dados/patrimonio.csv", index=False)
            st.rerun()

    for idx, row in df_pat.iterrows():
        st.markdown(f"""
        <div class="metric-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:800; font-size:18px;">{row['Mês']}</span>
                <span style="color:#00FF85; font-weight:900; font-size:20px;">{row['Total']:,.2f} €</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Eliminar {row['Mês']}", key=f"del_pat_{idx}"):
            df_pat.drop(idx).to_csv("dados/patrimonio.csv", index=False)
            st.rerun()

# --- ABA 2: FLUXO ---
with menu[1]:
    df_flu = load_data("poupanca")
    with st.expander("📝 REGISTAR CASHFLOW"):
        m_flu = st.selectbox("Mês do Fluxo", get_month_options(), key="f_month")
        s = st.number_input("Entradas (Salário/Outros)", min_value=0.0)
        d = st.number_input("Saídas (Despesas)", min_value=0.0)
        if st.button("GUARDAR FLUXO"):
            new_f = pd.DataFrame([{"Mês": m_flu, "Entradas": s, "Saidas": d}])
            pd.concat([df_flu, new_f], ignore_index=True).to_csv("dados/poupanca.csv", index=False)
            st.rerun()
    
    for idx, row in df_flu.iterrows():
        sobra = row['Entradas'] - row['Saidas']
        st.markdown(f"""
        <div class="metric-card">
            <b>{row['Mês']}</b> | Entradas: {row['Entradas']:.2f}€ | Saídas: {row['Saidas']:.2f}€ | 
            <span style="color:#00D1FF;">Sobra: {sobra:.2f}€</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Remover Fluxo {row['Mês']}", key=f"del_flu_{idx}"):
            df_flu.drop(idx).to_csv("dados/poupanca.csv", index=False)
            st.rerun()

# --- ABA 3: ANALYTICS ---
with menu[2]:
    st.markdown("### 🔬 FARIA BUFFET 2.0 - ENGINE")
    ticker_in = st.text_input("TICKER", placeholder="Ex: AAPL").upper()
    if ticker_in:
        try:
            with st.spinner("Analisando..."):
                stock = yf.Ticker(ticker_in)
                inf = stock.info
                # Métricas
                current_p = inf.get('currentPrice', 1)
                shares = inf.get('sharesOutstanding', 1)
                rev_g = inf.get('revenueGrowth', 0)
                eps_g = inf.get('earningsGrowth', 0)
                roic = inf.get('returnOnAssets', 0) * 2
                margin = inf.get('profitMargins', 0)
                cfo = inf.get('operatingCashflow', 0)
                ni = inf.get('netIncomeToCommon', 0)
                debt_ebitda = inf.get('debtToEbitda', 0)
                fcf = inf.get('freeCashflow', 0)

                st.markdown(f"#### {inf.get('longName', ticker_in)}")
                col1, col2 = st.columns(2)
                score = 0
                with col1:
                    st.markdown("**1️⃣ CRESCIMENTO & MARGEM**")
                    c1 = [("Receita > 7%", rev_g > 0.07, f"{rev_g*100:.1f}%"),
                          ("Lucro Líquido > 9%", eps_g > 0.09, f"{eps_g*100:.1f}%"),
                          ("Margem Líquida > 10%", margin > 0.10, f"{margin*100:.1f}%")]
                    for l, p, v in c1:
                        score += 1 if p else 0
                        st.markdown(f'<div class="check-item"><span>{l}</span><span>{v} {"✅" if p else "❌"}</span></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown("**2️⃣ RENTABILIDADE & DÍVIDA**")
                    cf_r = (cfo/ni) if ni else 0
                    c2 = [("ROIC > 15%", roic > 0.15, f"{roic*100:.1f}%"),
                          ("CFO / Lucro > 90%", cf_r > 0.90, f"{cf_r*100:.1f}%"),
                          ("Dívida/EBITDA < 3", 0 < debt_ebitda < 3, f"{debt_ebitda:.2f}")]
                    for l, p, v in c2:
                        score += 1 if p else 0
                        st.markdown(f'<div class="check-item"><span>{l}</span><span>{v} {"✅" if p else "❌"}</span></div>', unsafe_allow_html=True)

                growth_adj = min(rev_g, 0.15) if rev_g > 0 else 0.03
                v_intrinsico = dcf_valuation(fcf, growth_adj, 0.10, shares)
                upside = ((v_intrinsico / current_p) - 1) * 100 if current_p > 0 else 0

                st.markdown(f"### SCORE: {score}/6")
                status = "APROVADA" if score == 6 and upside > 15 else "INCONCLUSIVA" if score >= 4 else "REJEITADA"
                color = "#00FF85" if status == "APROVADA" else "#FFD700" if status == "INCONCLUSIVA" else "#FF5252"
                st.markdown(f'<div class="status-box" style="background:{color}; color:#0B0E14;">{status}</div>', unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                c1.metric("Mercado", f"{current_p:.2f}")
                c2.metric("Intrínseco (DCF)", f"{v_intrinsico:.2f}")
                c3.metric("Margem", f"{upside:.1f}%", delta=f"{upside:.1f}%")
        except: st.error("Erro nos dados.")
