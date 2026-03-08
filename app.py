import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FARIA | TERMINAL", page_icon="⚖️", layout="wide")

# --- 2. STYLE PROFISSIONAL (ULTRA CONTRASTE & MOBILE) ---
st.markdown("""
    <style>
    .stApp { background-color: #12151C; color: #FFFFFF; }
    
    /* Logo */
    .app-logo { text-align: center; padding: 25px 0; }
    .logo-f { font-size: 34px; font-weight: 900; color: #FFFFFF; letter-spacing: 2px; }
    .logo-invest { font-size: 34px; font-weight: 200; color: #00D1FF; letter-spacing: 4px; }

    /* Cards */
    .history-card {
        background-color: #1C212D;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #454D5E;
        margin-bottom: 12px;
    }
    .card-header { display: flex; justify-content: space-between; align-items: center; }
    .card-date { color: #FFFFFF; font-weight: 800; font-size: 16px; }
    .card-total { color: #00FF85; font-size: 22px; font-weight: 900; }

    /* BOTOES - AZUL VIBRANTE E TEXTO BRANCO PURO */
    div.stButton > button {
        width: 100% !important;
        border-radius: 10px !important;
        background-color: #0070FF !important; 
        color: #FFFFFF !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        height: 4.2em !important;
        border: none !important;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(0,112,255,0.4);
    }
    
    .stButton > button[kind="secondary"] {
        background-color: transparent !important;
        border: 2px solid #FF5252 !important;
        color: #FF5252 !important;
        height: 2.8em !important;
    }

    /* Estilo para Selectbox e Inputs */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1C212D !important;
        border: 2px solid #4FC3F7 !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. GERAÇÃO DA LISTA DE MESES (PARA O DESPREGÁVEL) ---
def get_month_options():
    months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    year_now = datetime.now().year % 100
    year_prev = year_now - 1
    # Lista com meses do ano atual e anterior (Ex: "Mar 26", "Fev 26"...)
    options = [f"{m} {year_now}" for m in months[::-1]] + [f"{m} {year_prev}" for m in months[::-1]]
    return options

# --- 4. LÓGICA DE DADOS ---
if not os.path.exists("dados"): os.makedirs("dados")

def load_data(name):
    path = f"dados/{name}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        if not df.empty and "Mês" in df.columns:
            try:
                df['date_tmp'] = pd.to_datetime(df['Mês'], format='%b %y', errors='coerce')
                df = df.sort_values(by='date_tmp', ascending=False).drop(columns=['date_tmp'])
            except: pass
        return df
    return pd.DataFrame()

# --- 5. LOGIN ---
if 'acesso' not in st.session_state: st.session_state.acesso = False

if not st.session_state.acesso:
    st.markdown('<div class="app-logo"><span class="logo-f">F</span><span class="logo-invest">|INVEST</span></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 8, 1])
    with c2:
        pwd = st.text_input("PASSWORD", type="password", key="login_pwd")
        if st.button("ENTRAR") or (pwd == "1214"):
            if pwd == "1214":
                st.session_state.acesso = True
                st.rerun()
    st.stop()

# --- 6. INTERFACE ---
st.markdown('<div class="app-logo"><span class="logo-f">F</span><span class="logo-invest">|INVEST</span></div>', unsafe_allow_html=True)
df_patrimonio = load_data("patrimonio")
df_poupanca = load_data("poupanca")

menu = st.tabs(["📊 PORTFÓLIO", "💵 CASHFLOW", "📈 ANALYTICS"])

# ---------------- PORTFÓLIO ----------------
with menu[0]:
    val = df_patrimonio["Total"].iloc[0] if not df_patrimonio.empty else 0
    st.markdown(f"<h1 style='text-align:center; color:#00FF85; font-size:48px;'>{val:,.2f} €</h1>", unsafe_allow_html=True)

    with st.expander("➕ NOVO REGISTO"):
        # MENU DESPREGÁVEL PARA O MÊS
        mes_sel = st.selectbox("Escolha o Mês", options=get_month_options())
        
        c1, c2 = st.columns(2)
        v_t212 = c1.number_input("Trading 212 (€)", min_value=0.0)
        v_ibkr = c2.number_input("IBKR (€)", min_value=0.0)
        v_cry = c1.number_input("Crypto (€)", min_value=0.0)
        v_ppr = c2.number_input("PPR (€)", min_value=0.0)
        
        if st.button("GUARDAR PATRIMÓNIO"):
            total = v_t212 + v_ibkr + v_cry + v_ppr
            new = pd.DataFrame([{"Mês": mes_sel, "T212": v_t212, "IBKR": v_ibkr, "CRYPTO": v_cry, "PPR": v_ppr, "Total": total}])
            pd.concat([df_patrimonio, new], ignore_index=True).to_csv("dados/patrimonio.csv", index=False)
            st.rerun()

    for index, row in df_patrimonio.iterrows():
        st.markdown(f"""
        <div class="history-card">
            <div class="card-header">
                <span class="card-date">{row['Mês']}</span>
                <span class="card-total">{row['Total']:,.2f} €</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"ELIMINAR {row['Mês']}", key=f"del_{index}", kind="secondary"):
            df_patrimonio.drop(index).to_csv("dados/patrimonio.csv", index=False)
            st.rerun()

# ---------------- CASHFLOW ----------------
with menu[1]:
    with st.expander("📝 REGISTAR MÊS"):
        # MENU DESPREGÁVEL PARA O MÊS
        mes_p = st.selectbox("Mês do Fluxo", options=get_month_options(), key="sb_p")
        sal = st.number_input("Salário Líquido", min_value=0.0)
        desp = st.number_input("Despesas", min_value=0.0)
        inv = st.number_input("Investimento", min_value=0.0)
        if st.button("GRAVAR CASHFLOW"):
            new_p = pd.DataFrame([{"Mês": mes_p, "Salario": sal, "Despesas": desp, "Investimentos": inv, "Outros": 0}])
            pd.concat([df_poupanca, new_p], ignore_index=True).to_csv("dados/poupanca.csv", index=False)
            st.rerun()

    for index, row in df_poupanca.iterrows():
        sobra = row['Salario'] - row['Despesas'] - row['Investimentos']
        st.markdown(f'<div class="history-card"><b>{row["Mês"]}</b> | <span style="color:#00FF85;">{sobra:,.2f} €</span></div>', unsafe_allow_html=True)
        if st.button(f"REMOVER {row['Mês']}", key=f"del_p_{index}", kind="secondary"):
            df_poupanca.drop(index).to_csv("dados/poupanca.csv", index=False)
            st.rerun()

# ---------------- ANALYTICS ----------------
with menu[2]:
    ticker = st.text_input("TICKER", placeholder="Ex: NVDA").upper()
    if ticker:
        try:
            stock = yf.Ticker(ticker)
            inf = stock.info
            st.markdown(f"### {inf.get('longName', ticker)}")
            st.metric("Preço", f"{inf.get('currentPrice', 0)} {inf.get('currency', 'USD')}")
            # Checklist de critérios (Certo ou X)
            criterios = [
                ("Receita > 7%", inf.get('revenueGrowth', 0) > 0.07),
                ("Margem > 10%", inf.get('profitMargins', 0) > 0.10),
                ("ROE > 15%", inf.get('returnOnEquity', 0) > 0.15),
                ("Dívida/Eq < 1.5", inf.get('debtToEquity', 1000) < 150)
            ]
            for label, passou in criterios:
                st.markdown(f"<div style='display:flex; justify-content:space-between; border-bottom:1px solid #2D3444; padding:10px 0;'><span>{label}</span><span>{'✅' if passou else '❌'}</span></div>", unsafe_allow_html=True)
        except: st.error("Erro nos dados.")

st.markdown("<br><center style='color:#B0BEC5; font-size:10px; font-weight:700;'>FARIA TERMINAL | v3.6</center>", unsafe_allow_html=True)
