import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FARIA | TERMINAL", page_icon="⚖️", layout="wide")

# --- 2. STYLE PROFISSIONAL (MOBILE OPTIMIZED & HIGH CONTRASTE) ---
st.markdown("""
    <style>
    /* Fundo Deep Navy */
    .stApp { 
        background-color: #12151C; 
        color: #FFFFFF; 
    }
    
    /* Logo Minimalista */
    .app-logo {
        text-align: center;
        padding: 20px 0;
    }
    .logo-f { font-size: 32px; font-weight: 900; color: #FFFFFF; }
    .logo-invest { font-size: 32px; font-weight: 300; color: #00D1FF; }

    /* Ajuste de Cards para Mobile */
    .history-card {
        background-color: #1C212D;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #3D4455;
        margin-bottom: 10px;
    }
    
    .card-header { display: flex; justify-content: space-between; align-items: center; }
    .card-date { color: #FFFFFF; font-weight: 700; font-size: 14px; }
    .card-total { color: #00FF85; font-size: 18px; font-weight: 800; }

    /* BOTOES - MOBILE FRIENDLY (MAIORES) */
    div.stButton > button {
        width: 100% !important;
        border-radius: 10px !important;
        background-color: #007BFF !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        height: 4em !important; /* Mais alto para facilitar o toque */
        border: none !important;
        margin-top: 10px;
    }
    
    /* Inputs visíveis no telemóvel */
    .stTextInput > div > div > input {
        background-color: #1C212D !important;
        color: white !important;
        border: 2px solid #4FC3F7 !important;
        height: 3.5em !important;
    }

    /* Tabs - Navegação Mobile */
    .stTabs [data-baseweb="tab"] { 
        padding-left: 10px; 
        padding-right: 10px;
        font-size: 14px;
        color: #B0BEC5;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE DADOS ---
if not os.path.exists("dados"):
    os.makedirs("dados")

def load_and_sort(name, columns):
    path = f"dados/{name}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        if not df.empty and "Mês" in df.columns:
            try:
                df['date_tmp'] = pd.to_datetime(df['Mês'], format='%b %y', errors='coerce')
                df = df.sort_values(by='date_tmp', ascending=False).drop(columns=['date_tmp'])
            except: pass
        return df
    return pd.DataFrame(columns=columns)

# --- 4. SISTEMA DE LOGIN (FIXED FOR MOBILE) ---
if 'acesso' not in st.session_state:
    st.session_state.acesso = False

def validar_login():
    if st.session_state.pass_input == "1214":
        st.session_state.acesso = True
    else:
        st.error("PASSWORD INCORRETA")

if not st.session_state.acesso:
    st.markdown('<div class="app-logo"><span class="logo-f">F</span><span class="logo-invest">|INVEST</span></div>', unsafe_allow_html=True)
    
    # Contentor centralizado para login
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.write("")
        # Adicionado on_change para permitir entrar apenas com o "Enter" do teclado mobile
        st.text_input("PASSWORD DE ACESSO", type="password", key="pass_input", on_change=validar_login)
        if st.button("ENTRAR NO TERMINAL"):
            validar_login()
            if st.session_state.acesso:
                st.rerun()
    st.stop()

# --- 5. CARREGAR DADOS APÓS LOGIN ---
df_patrimonio = load_and_sort("patrimonio", ["Mês", "T212", "IBKR", "CRYPTO", "PPR", "Total"])
df_poupanca = load_and_sort("poupanca", ["Mês", "Salario", "Despesas", "Investimentos", "Outros"])

# --- 6. INTERFACE PRINCIPAL ---
st.markdown('<div class="app-logo"><span class="logo-f">F</span><span class="logo-invest">|INVEST</span></div>', unsafe_allow_html=True)

menu = st.tabs(["📊 PORTFÓLIO", "💵 CASHFLOW", "📈 ANALYTICS"])

# ---------------- PORTFÓLIO ----------------
with menu[0]:
    total_val = df_patrimonio["Total"].iloc[0] if not df_patrimonio.empty else 0
    st.markdown(f"<h1 style='text-align:center; color:#00FF85; margin-bottom:0;'>{total_val:,.2f} €</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#B0BEC5; font-weight:600;'>PATRIMÓNIO LÍQUIDO</p>", unsafe_allow_html=True)

    with st.expander("➕ ADICIONAR REGISTO"):
        mes_in = st.text_input("Mês/Ano", value=datetime.now().strftime("%b %y"), key="add_mes")
        v_t212 = st.number_input("Trading 212 (€)", min_value=0.0, step=10.0)
        v_ibkr = st.number_input("IBKR (€)", min_value=0.0, step=10.0)
        v_crypto = st.number_input("Crypto (€)", min_value=0.0, step=10.0)
        v_ppr = st.number_input("PPR (€)", min_value=0.0, step=10.0)
        
        if st.button("GUARDAR DADOS"):
            total_m = v_t212 + v_ibkr + v_crypto + v_ppr
            new_row = pd.DataFrame([{"Mês": mes_in, "T212": v_t212, "IBKR": v_ibkr, "CRYPTO": v_crypto, "PPR": v_ppr, "Total": total_m}])
            pd.concat([df_patrimonio, new_row], ignore_index=True).to_csv("dados/patrimonio.csv", index=False)
            st.rerun()

    st.markdown("### HISTÓRICO")
    for index, row in df_patrimonio.iterrows():
        st.markdown(f"""
        <div class="history-card">
            <div class="card-header">
                <span class="card-date">{row['Mês']}</span>
                <span class="card-total">{row['Total']:,.2f} €</span>
            </div>
            <div style="font-size:12px; color:#CFD8DC; margin-top:5px;">
                T212: {row['T212']}€ | IBKR: {row['IBKR']}€ | CRY: {row['CRYPTO']}€ | PPR: {row['PPR']}€
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"ELIMINAR {row['Mês']}", key=f"del_{index}"):
            df_patrimonio.drop(index).to_csv("dados/patrimonio.csv", index=False)
            st.rerun()

# ---------------- CASHFLOW ----------------
with menu[1]:
    st.markdown("### GESTÃO MENSAL")
    with st.expander("📝 REGISTAR MÊS"):
        mes_p = st.text_input("Mês", value=datetime.now().strftime("%b %y"), key="p_mes_input")
        sal = st.number_input("Salário Líquido", min_value=0.0)
        desp = st.number_input("Despesas", min_value=0.0)
        inv = st.number_input("Aportes", min_value=0.0)
        if st.button("GRAVAR FLUXO"):
            new_p = pd.DataFrame([{"Mês": mes_p, "Salario": sal, "Despesas": desp, "Investimentos": inv, "Outros": 0}])
            pd.concat([df_poupanca, new_p], ignore_index=True).to_csv("dados/poupanca.csv", index=False)
            st.rerun()

    for index, row in df_poupanca.iterrows():
        sobra = row['Salario'] - row['Despesas'] - row['Investimentos']
        st.markdown(f"""
        <div class="history-card">
            <b>{row['Mês']}</b> | <span style="color:#00FF85;">Sobra: {sobra:,.2f} €</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"APAGAR {row['Mês']}", key=f"del_p_{index}"):
            df_poupanca.drop(index).to_csv("dados/poupanca.csv", index=False)
            st.rerun()

# ---------------- ANALYTICS ----------------
with menu[2]:
    st.markdown("### TERMINAL ANALÍTICO")
    ticker = st.text_input("TICKER", placeholder="Ex: AAPL").upper()

    if ticker:
        try:
            stock = yf.Ticker(ticker)
            inf = stock.info
            st.markdown(f"**{inf.get('longName', ticker)}**")
            st.metric("Preço", f"{inf.get('currentPrice', 0)} {inf.get('currency', 'USD')}")
            
            # Checklist de critérios
            criterios = [
                ("Crescimento > 7%", inf.get('revenueGrowth', 0) > 0.07),
                ("Margem > 10%", inf.get('profitMargins', 0) > 0.10),
                ("ROE > 15%", inf.get('returnOnEquity', 0) > 0.15),
                ("Dívida/Eq < 1.5", inf.get('debtToEquity', 1000) < 150)
            ]
            
            score = 0
            for label, passou in criterios:
                icone, cor = ("✅", "#00FF85") if passou else ("❌", "#FF5252")
                if passou: score += 1
                st.markdown(f"<div style='display:flex; justify-content:space-between; border-bottom:1px solid #2D3444; padding:8px 0;'><span>{label}</span><span style='color:{cor};'>{icone}</span></div>", unsafe_allow_html=True)
            
            st.markdown(f"#### SCORE: {score}/{len(criterios)}")
        except:
            st.error("Erro ao carregar dados.")

st.markdown("<br><hr><center style='color:#CFD8DC; font-size:10px;'>FARIA TERMINAL | v3.4 (MOBILE FIXED)</center>", unsafe_allow_html=True)
