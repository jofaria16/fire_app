import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FARIA | TERMINAL", page_icon="⚖️", layout="wide")

# --- 2. STYLE PROFISSIONAL (FOCO EM ALTO CONTRASTE) ---
st.markdown("""
    <style>
    /* Fundo Azul Noite Profissional */
    .stApp { 
        background-color: #12151C; 
        color: #FFFFFF; 
    }
    
    /* Logo Minimalista - Contraste Total */
    .app-logo {
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        letter-spacing: 4px;
        padding: 30px 0;
    }
    .logo-f { font-size: 32px; font-weight: 900; color: #FFFFFF; }
    .logo-invest { font-size: 32px; font-weight: 300; color: #00D1FF; }

    /* Cards de Histórico (Contraste nas Letras) */
    .history-card {
        background-color: #1C212D;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #3D4455; /* Borda mais visível */
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .card-date { color: #E0E0E0; font-weight: 700; font-size: 16px; }
    .card-total { color: #00FF85; font-size: 22px; font-weight: 800; }
    .card-details { color: #CFD8DC; font-size: 14px; display: flex; gap: 15px; flex-wrap: wrap; }

    /* Checklist Analytics */
    .check-container { background-color: #1C212D; padding: 20px; border-radius: 12px; border: 1px solid #3D4455; }
    .check-item {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #2D3444;
        color: #FFFFFF;
        font-weight: 500;
    }

    /* BOTOES - CONTRASTE MÁXIMO */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #007BFF; /* Azul mais forte */
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        border: none;
        height: 3.8em;
        box-shadow: 0 2px 8px rgba(0,123,255,0.3);
    }
    
    /* Botão de Apagar (Vermelho Vibrante) */
    .stButton > button[kind="secondary"] {
        background-color: transparent !important;
        border: 2px solid #FF5252 !important;
        color: #FF5252 !important;
        height: 2.5em !important;
        margin-top: 10px;
        font-weight: 700 !important;
    }

    /* Inputs - Borda mais clara para visibilidade */
    input { 
        background-color: #1C212D !important; 
        border: 1px solid #4FC3F7 !important; 
        color: white !important; 
        border-radius: 8px !important; 
    }
    
    /* Tabs - Texto mais claro */
    .stTabs [data-baseweb="tab"] { color: #B0BEC5; font-weight: 700; }
    .stTabs [aria-selected="true"] { color: #00D1FF !important; }
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

df_patrimonio = load_and_sort("patrimonio", ["Mês", "T212", "IBKR", "CRYPTO", "PPR", "Total"])
df_poupanca = load_and_sort("poupanca", ["Mês", "Salario", "Despesas", "Investimentos", "Outros"])

# --- 4. SISTEMA DE LOGIN ---
if 'acesso' not in st.session_state:
    st.session_state.acesso = False

if not st.session_state.acesso:
    st.markdown('<div class="app-logo"><span class="logo-f">F</span><span class="logo-invest">|INVEST</span></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        codigo = st.text_input("PASSWORD", type="password")
        if st.button("AUTENTICAR"):
            if codigo == "1214":
                st.session_state.acesso = True
                st.rerun()
    st.stop()

# --- 5. HEADER ---
st.markdown('<div class="app-logo"><span class="logo-f">F</span><span class="logo-invest">|INVEST</span></div>', unsafe_allow_html=True)

menu = st.tabs(["📊 PORTFÓLIO", "💵 CASHFLOW", "📈 ANALYTICS"])

# ---------------- PORTFÓLIO ----------------
with menu[0]:
    total_val = df_patrimonio["Total"].iloc[0] if not df_patrimonio.empty else 0
    st.markdown(f"<h1 style='text-align:center; color:#00FF85; margin-bottom:0; font-size:45px;'>{total_val:,.2f} €</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#B0BEC5; margin-bottom:30px; font-weight:600;'>VALOR TOTAL LÍQUIDO</p>", unsafe_allow_html=True)

    with st.expander("➕ ADICIONAR REGISTO MENSAL"):
        c1, c2 = st.columns(2)
        mes_in = c1.text_input("Mês/Ano", value=datetime.now().strftime("%b %y"))
        v_t212 = c1.number_input("Trading 212 (€)", min_value=0.0)
        v_ibkr = c2.number_input("IBKR (€)", min_value=0.0)
        v_crypto = c1.number_input("Crypto (€)", min_value=0.0)
        v_ppr = c2.number_input("PPR (€)", min_value=0.0)
        
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
            <div class="card-details">
                <span><b style="color:#00D1FF">T212:</b> {row['T212']}€</span>
                <span><b style="color:#00D1FF">IBKR:</b> {row['IBKR']}€</span>
                <span><b style="color:#00D1FF">CRY:</b> {row['CRYPTO']}€</span>
                <span><b style="color:#00D1FF">PPR:</b> {row['PPR']}€</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"ELIMINAR {row['Mês']}", key=f"del_{index}", kind="secondary"):
            df_patrimonio.drop(index).to_csv("dados/patrimonio.csv", index=False)
            st.rerun()

# ---------------- CASHFLOW ----------------
with menu[1]:
    st.markdown("### GESTÃO MENSAL")
    with st.expander("📝 REGISTAR MOVIMENTOS"):
        mes_p = st.text_input("Mês", value=datetime.now().strftime("%b %y"), key="p_mes")
        sal = st.number_input("Salário Líquido", min_value=0.0)
        desp = st.number_input("Despesas Fixas", min_value=0.0)
        inv = st.number_input("Aporte Investimento", min_value=0.0)
        if st.button("GRAVAR FLUXO"):
            new_p = pd.DataFrame([{"Mês": mes_p, "Salario": sal, "Despesas": desp, "Investimentos": inv, "Outros": 0}])
            pd.concat([df_poupanca, new_p], ignore_index=True).to_csv("dados/poupanca.csv", index=False)
            st.rerun()

    for index, row in df_poupanca.iterrows():
        sobra = row['Salario'] - row['Despesas'] - row['Investimentos']
        st.markdown(f"""
        <div class="history-card">
            <div class="card-header">
                <span class="card-date">{row['Mês']}</span>
                <span style="color: {'#00FF85' if sobra >= 0 else '#FF5252'}; font-weight:900; font-size:18px;">
                    Livre: {sobra:,.2f} €
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"REMOVER {row['Mês']}", key=f"del_p_{index}", kind="secondary"):
            df_poupanca.drop(index).to_csv("dados/poupanca.csv", index=False)
            st.rerun()

# ---------------- ANALYTICS ----------------
with menu[2]:
    st.markdown("### TERMINAL ANALÍTICO")
    ticker = st.text_input("TICKER ATIVO", placeholder="Ex: NVDA").upper()

    if ticker:
        try:
            with st.spinner("A processar..."):
                stock = yf.Ticker(ticker)
                inf = stock.info
                st.markdown(f"<h2 style='color:white;'>{inf.get('longName', ticker)}</h2>", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                c1.metric("Preço", f"{inf.get('currentPrice', 0)} {inf.get('currency', 'USD')}")
                c2.metric("P/E Ratio", f"{inf.get('forwardPE', 'N/A')}")

                st.markdown('<div class="check-container">', unsafe_allow_html=True)
                criterios = [
                    ("Crescimento Receita > 7%", inf.get('revenueGrowth', 0) > 0.07),
                    ("Margem de Lucro > 10%", inf.get('profitMargins', 0) > 0.10),
                    ("ROE / ROIC > 15%", inf.get('returnOnEquity', 0) > 0.15),
                    ("Dívida/Equity < 1.5", inf.get('debtToEquity', 1000) < 150),
                    ("P/E Ratio Saudável (< 30)", 0 < inf.get('forwardPE', 100) < 30)
                ]

                score = 0
                for label, passou in criterios:
                    icone, cor = ("✅", "#00FF85") if passou else ("❌", "#FF5252")
                    if passou: score += 1
                    st.markdown(f'<div class="check-item"><span>{label}</span><span style="color:{cor}; font-weight:900;">{icone}</span></div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align:center; color:white;'>SCORE FINAL: {score}/5</h3>", unsafe_allow_html=True)
        except:
            st.error("Erro nos dados.")

# --- FOOTER ---
st.markdown("<br><hr><center style='color: #CFD8DC; font-size:11px; font-weight:600;'>FARIA PRIVATE TERMINAL | v3.3</center>", unsafe_allow_html=True)
