import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FARIA | TERMINAL", page_icon="⚖️", layout="wide")

# --- 2. STYLE PROFISSIONAL (DEEP NAVY & MODERN CARDS) ---
st.markdown("""
    <style>
    /* Fundo Azul Noite Profissional */
    .stApp { 
        background-color: #12151C; 
        color: #E0E0E0; 
    }
    
    /* Logo Minimalista */
    .app-logo {
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        letter-spacing: 4px;
        padding: 30px 0;
    }
    .logo-f { font-size: 32px; font-weight: 900; color: #FFFFFF; }
    .logo-invest { font-size: 32px; font-weight: 200; color: #00A3FF; }

    /* Cards de Histórico FIXOS (Não Excel) */
    .history-card {
        background-color: #1C212D;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2D3444;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Layout de Texto nos Cards */
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .card-date { color: #9BA3AF; font-weight: 600; font-size: 16px; }
    .card-total { color: #00FF85; font-size: 20px; font-weight: 800; }
    .card-details { color: #9BA3AF; font-size: 13px; display: flex; gap: 15px; flex-wrap: wrap; }

    /* Checklist Analytics */
    .check-container { background-color: #1C212D; padding: 20px; border-radius: 12px; border: 1px solid #2D3444; }
    .check-item {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #2D3444;
    }

    /* Inputs e Botões */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #00A3FF;
        color: white;
        font-weight: bold;
        border: none;
        height: 3.5em;
    }
    
    /* Botão de Apagar (Vermelho e Discreto) */
    .stButton > button[kind="secondary"] {
        background-color: transparent !important;
        border: 1px solid #FF4B4B !important;
        color: #FF4B4B !important;
        height: 2.2em !important;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE DADOS & ORDENAÇÃO ---
if not os.path.exists("dados"):
    os.makedirs("dados")

def load_and_sort(name, columns):
    path = f"dados/{name}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        if not df.empty and "Mês" in df.columns:
            try:
                # Ordena por data (mais recente primeiro)
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
        codigo = st.text_input("PASSWORD DE ACESSO", type="password")
        if st.button("AUTENTICAR"):
            if codigo == "1214":
                st.session_state.acesso = True
                st.rerun()
    st.stop()

# --- 5. HEADER FIXO ---
st.markdown('<div class="app-logo"><span class="logo-f">F</span><span class="logo-invest">|INVEST</span></div>', unsafe_allow_html=True)

menu = st.tabs(["📊 PORTFÓLIO", "💵 CASHFLOW", "📈 ANALYTICS"])

# ---------------- PORTFÓLIO ----------------
with menu[0]:
    total_val = df_patrimonio["Total"].iloc[0] if not df_patrimonio.empty else 0
    st.markdown(f"<h1 style='text-align:center; color:#00FF85; margin-bottom:0;'>{total_val:,.2f} €</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#9BA3AF; margin-bottom:30px;'>VALOR ATUAL DO PATRIMÓNIO</p>", unsafe_allow_html=True)

    with st.expander("➕ ADICIONAR REGISTO"):
        c1, c2 = st.columns(2)
        mes_in = c1.text_input("Mês/Ano (Ex: Mar 24)", value=datetime.now().strftime("%b %y"))
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
        # CARD FIXO (NÃO EDITÁVEL)
        st.markdown(f"""
        <div class="history-card">
            <div class="card-header">
                <span class="card-date">{row['Mês']}</span>
                <span class="card-total">{row['Total']:,.2f} €</span>
            </div>
            <div class="card-details">
                <span><b>T212:</b> {row['T212']}€</span>
                <span><b>IBKR:</b> {row['IBKR']}€</span>
                <span><b>CRY:</b> {row['CRYPTO']}€</span>
                <span><b>PPR:</b> {row['PPR']}€</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # BOTÃO ÚNICO NO FIM PARA APAGAR
        if st.button(f"Apagar Registro {row['Mês']}", key=f"del_{index}", kind="secondary"):
            df_patrimonio.drop(index).to_csv("dados/patrimonio.csv", index=False)
            st.rerun()

# ---------------- CASHFLOW ----------------
with menu[1]:
    st.markdown("### GESTÃO MENSAL")
    with st.expander("📝 REGISTAR MOVIMENTOS"):
        mes_p = st.text_input("Mês", value=datetime.now().strftime("%b %y"), key="p_mes")
        sal = st.number_input("Salário Líquido", min_value=0.0)
        desp = st.number_input("Despesas", min_value=0.0)
        inv = st.number_input("Aportes", min_value=0.0)
        if st.button("GRAVAR MÊS"):
            new_p = pd.DataFrame([{"Mês": mes_p, "Salario": sal, "Despesas": desp, "Investimentos": inv, "Outros": 0}])
            pd.concat([df_poupanca, new_p], ignore_index=True).to_csv("dados/poupanca.csv", index=False)
            st.rerun()

    for index, row in df_poupanca.iterrows():
        sobra = row['Salario'] - row['Despesas'] - row['Investimentos']
        st.markdown(f"""
        <div class="history-card">
            <div class="card-header">
                <span class="card-date">{row['Mês']}</span>
                <span style="color: {'#00FF85' if sobra >= 0 else '#FF4B4B'}; font-weight:bold;">
                    Livre: {sobra:,.2f} €
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Apagar {row['Mês']}", key=f"del_p_{index}", kind="secondary"):
            df_poupanca.drop(index).to_csv("dados/poupanca.csv", index=False)
            st.rerun()

# ---------------- ANALYTICS (CHECKLIST) ----------------
with menu[2]:
    st.markdown("### TERMINAL ANALÍTICO")
    ticker = st.text_input("BUSCAR ATIVO (Ex: TSLA)", placeholder="Digite o ticker...").upper()

    if ticker:
        try:
            with st.spinner("Aceder a dados de mercado..."):
                stock = yf.Ticker(ticker)
                inf = stock.info
                
                st.markdown(f"#### {inf.get('longName', ticker)}")
                c1, c2 = st.columns(2)
                c1.metric("Preço", f"{inf.get('currentPrice', 0)} {inf.get('currency', 'USD')}")
                c2.metric("P/E Ratio", f"{inf.get('forwardPE', 'N/A')}")

                st.markdown("<br>", unsafe_allow_html=True)
                
                # --- MODELO DE CHECKLIST COM ÍCONES ---
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
                    icone = "✅" if passou else "❌"
                    cor = "#00FF85" if passou else "#FF4B4B"
                    if passou: score += 1
                    st.markdown(f"""
                    <div class="check-item">
                        <span style="color:#E0E0E0;">{label}</span>
                        <span style="color:{cor}; font-weight:bold;">{icone}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align:center;'>SCORE: {score}/5</h3>", unsafe_allow_html=True)

        except:
            st.error("Erro ao carregar dados. Verifica o ticker.")

# --- FOOTER ---
st.markdown("<br><hr><center style='color: #4A4E57; font-size:11px;'>FARIA PRIVATE TERMINAL | ASSET MANAGEMENT</center>", unsafe_allow_html=True)
