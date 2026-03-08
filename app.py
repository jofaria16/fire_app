import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FARIA INVEST | ASSET MANAGEMENT", page_icon="⚖️", layout="wide")

# --- STYLE REFINADO (PROFISSIONAL & DEEP NAVY) ---
st.markdown("""
    <style>
    /* Fundo ligeiramente mais claro (Deep Navy) */
    .stApp { 
        background-color: #12151C; 
        color: #E0E0E0; 
    }
    
    /* Logo Minimalista Profissional */
    .app-logo {
        text-align: center;
        font-family: 'serif';
        letter-spacing: 2px;
        padding: 20px 0;
    }
    .logo-main { font-size: 28px; font-weight: 800; color: #FFFFFF; }
    .logo-sub { font-size: 28px; font-weight: 300; color: #00A3FF; }

    /* Cards de Histórico */
    .history-card {
        background-color: #1C212D;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #2D3444;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    /* Checklist Analytics */
    .check-item {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #2D3444;
        font-size: 14px;
    }

    /* Tabs Customizadas */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        color: #9BA3AF;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #00A3FF !important;
        border-bottom-color: #00A3FF !important;
    }

    /* Inputs e Botões */
    input { background-color: #1C212D !important; border: 1px solid #2D3444 !important; color: white !important; border-radius: 5px !important; }
    
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        background-color: #00A3FF;
        color: white;
        font-weight: bold;
        border: none;
        height: 3em;
        transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #0082CC; }
    
    /* Botão de Remover Pequeno */
    .stButton > button[kind="secondary"] {
        background-color: transparent;
        border: 1px solid #FF4B4B;
        color: #FF4B4B;
        height: 2em;
        font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- GESTÃO DE DADOS ---
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

df_patrimonio = load_and_sort("patrimonio", ["Mês", "T212", "IBKR", "CRYPTO", "PPR", "Total"])
df_poupanca = load_and_sort("poupanca", ["Mês", "Salario", "Despesas", "Investimentos", "Outros"])

# --- LOGIN ---
if 'acesso' not in st.session_state:
    st.session_state.acesso = False

if not st.session_state.acesso:
    st.markdown('<div class="app-logo"><span class="logo-main">F</span><span class="logo-sub">|INVEST</span></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        codigo = st.text_input("AUTENTICAÇÃO", type="password")
        if st.button("ACEDER AO TERMINAL"):
            if codigo == "1214":
                st.session_state.acesso = True
                st.rerun()
    st.stop()

# --- APP HEADER (LOGO) ---
st.markdown('<div class="app-logo"><span class="logo-main">F</span><span class="logo-sub">|INVEST</span></div>', unsafe_allow_html=True)

menu = st.tabs(["📊 PORTFÓLIO", "💵 CASHFLOW", "📈 ANALYTICS"])

# ---------------- PORTFÓLIO ----------------
with menu[0]:
    total_atual = df_patrimonio["Total"].iloc[0] if not df_patrimonio.empty else 0
    st.markdown(f"<h1 style='text-align:center; color:#00FF85;'>{total_atual:,.2f} €</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#9BA3AF; margin-top:-20px;'>PATRIMÓNIO LÍQUIDO TOTAL</p>", unsafe_allow_html=True)

    with st.expander("📝 NOVO REGISTO MENSAL"):
        c1, c2 = st.columns(2)
        mes_in = c1.text_input("Mês/Ano", value=datetime.now().strftime("%b %y"))
        v_t212 = c1.number_input("Trading 212 (€)", min_value=0.0)
        v_ibkr = c2.number_input("IBKR (€)", min_value=0.0)
        v_crypto = c1.number_input("Crypto (€)", min_value=0.0)
        v_ppr = c2.number_input("PPR (€)", min_value=0.0)
        
        if st.button("SUBMETER DADOS"):
            total_m = v_t212 + v_ibkr + v_crypto + v_ppr
            new_row = pd.DataFrame([{"Mês": mes_in, "T212": v_t212, "IBKR": v_ibkr, "CRYPTO": v_crypto, "PPR": v_ppr, "Total": total_m}])
            pd.concat([df_patrimonio, new_row], ignore_index=True).to_csv("dados/patrimonio.csv", index=False)
            st.rerun()

    st.markdown("### 📜 HISTÓRICO DE ATIVOS")
    for index, row in df_patrimonio.iterrows():
        st.markdown(f"""
        <div class="history-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #FFFFFF; font-weight: 600;">{row['Mês']}</span>
                <span style="color: #00FF85; font-size: 18px; font-weight: bold;">{row['Total']:,.2f} €</span>
            </div>
            <div style="font-size: 12px; color: #9BA3AF; margin-top: 8px; display: flex; gap: 10px;">
                <span>T212: {row['T212']}€</span> | <span>IBKR: {row['IBKR']}€</span> | <span>CRY: {row['CRYPTO']}€</span> | <span>PPR: {row['PPR']}€</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Eliminar Registro", key=f"del_{index}", kind="secondary"):
            df_patrimonio.drop(index).to_csv("dados/patrimonio.csv", index=False)
            st.rerun()

# ---------------- CASHFLOW ----------------
with menu[1]:
    st.markdown("### 🏦 GESTÃO DE FLUXO")
    with st.expander("📝 ADICIONAR ENTRADAS/SAÍDAS"):
        mes_p = st.text_input("Mês", value=datetime.now().strftime("%b %y"), key="p_mes")
        sal = st.number_input("Rendimento Líquido", min_value=0.0)
        desp = st.number_input("Custos Fixos/Variáveis", min_value=0.0)
        inv = st.number_input("Aporte em Investimento", min_value=0.0)
        if st.button("GRAVAR FLUXO"):
            new_p = pd.DataFrame([{"Mês": mes_p, "Salario": sal, "Despesas": desp, "Investimentos": inv, "Outros": 0}])
            pd.concat([df_poupanca, new_p], ignore_index=True).to_csv("dados/poupanca.csv", index=False)
            st.rerun()

    for index, row in df_poupanca.iterrows():
        sobra = row['Salario'] - row['Despesas'] - row['Investimentos']
        st.markdown(f"""
        <div class="history-card">
            <div style="display:flex; justify-content:space-between;">
                <b>{row['Mês']}</b>
                <span style="color: {'#00FF85' if sobra >= 0 else '#FF4B4B'};">Sobra: {sobra:,.2f} €</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Eliminar", key=f"del_p_{index}", kind="secondary"):
            df_poupanca.drop(index).to_csv("dados/poupanca.csv", index=False)
            st.rerun()

# ---------------- ANALYTICS ----------------
with menu[2]:
    st.markdown("### 🔍 TERMINAL DE ANÁLISE")
    ticker = st.text_input("INTRODUZA O TICKER (Ex: NVDA)", "").upper()

    if ticker:
        try:
            with st.spinner("A processar dados fundamentais..."):
                stock = yf.Ticker(ticker)
                info = stock.info
                
                st.markdown(f"#### {info.get('longName', ticker)}")
                c1, c2, c3 = st.columns(3)
                c1.metric("Cotação", f"{info.get('currentPrice', 0)} {info.get('currency', 'USD')}")
                c2.metric("P/E Ratio", f"{info.get('forwardPE', 'N/A')}")
                c3.metric("Div. Yield", f"{info.get('dividendYield', 0)*100:.2f}%")

                st.markdown("---")
                st.markdown("#### CHECKLIST DE CRITÉRIOS")
                
                criterios = [
                    ("Crescimento Receita (>7%)", info.get('revenueGrowth', 0) > 0.07),
                    ("Margem de Lucro (>10%)", info.get('profitMargins', 0) > 0.10),
                    ("ROIC / ROE (>15%)", info.get('returnOnEquity', 0) > 0.15),
                    ("Dívida/Equity (<1.5)", info.get('debtToEquity', 1000) < 150),
                    ("Price/Earnings (<30)", 0 < info.get('forwardPE', 100) < 30)
                ]

                score = 0
                for nome_crit, passou in criterios:
                    icone = "✅" if passou else "❌"
                    cor = "#00FF85" if passou else "#FF4B4B"
                    if passou: score += 1
                    st.markdown(f'<div class="check-item"><span>{nome_crit}</span><span style="color:{cor};">{icone}</span></div>', unsafe_allow_html=True)
                
                st.markdown(f"<h3 style='text-align:center;'>SCORE: {score}/5</h3>", unsafe_allow_html=True)

        except:
            st.error("Erro na ligação ao terminal de dados.")

st.markdown("<br><hr><center style='color: #4A4E57; font-size:10px;'>PRIVATE ASSET TERMINAL | v3.2</center>", unsafe_allow_html=True)
