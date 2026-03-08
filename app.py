import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FARIA INVEST", page_icon="🔵", layout="wide")

# --- STYLE TRADING 212 (UI/UX CUSTOM) ---
st.markdown("""
    <style>
    /* Fundo e cores base */
    .stApp {
        background-color: #090B0F;
        color: #FFFFFF;
    }
    
    /* Estilização dos Inputs */
    input {
        background-color: #1A1D23 !important;
        border: 1px solid #2C3039 !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    /* Botões estilo T212 */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #00A3FF;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div.stButton > button:hover {
        background-color: #0082CC;
        border: none;
    }

    /* Cards de Métricas */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #00FF85; /* Verde T212 */
    }
    
    /* Tabs e Menu */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #090B0F;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1A1D23;
        border-radius: 8px 8px 0px 0px;
        color: #9BA3AF;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2C3039 !important;
        color: #00A3FF !important;
    }

    /* Data Editor (Tabela Fixa) */
    .stDataEditor {
        background-color: #1A1D23;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SISTEMA DE DADOS ---
if not os.path.exists("dados"):
    os.makedirs("dados")

def load_csv(name, columns):
    path = f"dados/{name}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        for col in columns:
            if col not in df.columns: df[col] = 0
        return df[columns]
    df = pd.DataFrame(columns=columns)
    df.to_csv(path, index=False)
    return df

df_patrimonio = load_csv("patrimonio", ["Mês", "T212", "IBKR", "CRYPTO", "PPR", "Total"])
df_poupanca = load_csv("poupanca", ["Mês", "Salario", "Despesas", "Investimentos", "Outros"])

# --- LOGIN ---
if 'acesso' not in st.session_state:
    st.session_state.acesso = False

if not st.session_state.acesso:
    st.markdown("<h2 style='text-align:center; padding-top:50px;'>FARIA <span style='color:#00A3FF'>INVEST</span></h2>", unsafe_allow_html=True)
    with st.container():
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            codigo = st.text_input("PASSWORD", type="password")
            if st.button("LOG IN"):
                if codigo == "1214":
                    st.session_state.acesso = True
                    st.rerun()
                else:
                    st.error("Código Inválido")
    st.stop()

# --- HEADER APP ---
st.markdown(f"<h3 style='text-align:left; color:white;'>Olá, Faria 👋</h3>", unsafe_allow_html=True)

# --- MENU NAVIGATION ---
menu = st.tabs(["📊 PORTFÓLIO", "💵 POUPANÇA", "📈 ANALYTICS"])

# ---------------- ABA 1: PORTFÓLIO ----------------
with menu[0]:
    # Totais Rápidos
    total_global = df_patrimonio["Total"].iloc[-1] if not df_patrimonio.empty else 0
    st.metric("VALOR TOTAL", f"{total_global:,.2f} €")
    
    with st.expander("➕ NOVO REGISTO MENSAL"):
        c1, c2 = st.columns(2)
        mes_in = c1.text_input("Mês/Ano", value=datetime.now().strftime("%b %y"))
        v_t212 = c1.number_input("Trading 212 (€)", min_value=0.0)
        v_ibkr = c2.number_input("IBKR (€)", min_value=0.0)
        v_crypto = c2.number_input("Crypto (€)", min_value=0.0)
        v_ppr = st.number_input("PPR (€)", min_value=0.0)
        
        if st.button("CONFIRMAR DEPÓSITO"):
            total_m = v_t212 + v_ibkr + v_crypto + v_ppr
            new_data = pd.DataFrame([{"Mês": mes_in, "T212": v_t212, "IBKR": v_ibkr, "CRYPTO": v_crypto, "PPR": v_ppr, "Total": total_m}])
            df_patrimonio = pd.concat([df_patrimonio, new_data], ignore_index=True)
            df_patrimonio.to_csv("dados/patrimonio.csv", index=False)
            st.success("Património atualizado!")
            st.rerun()

    st.markdown("### 📜 HISTÓRICO DE VALORES")
    # Tabela fixa e editável estilo folha de cálculo
    edited_patrimonio = st.data_editor(
        df_patrimonio, 
        num_rows="dynamic", 
        use_container_width=True,
        key="editor_patrimonio"
    )
    if st.button("GUARDAR ALTERAÇÕES NO HISTÓRICO"):
        edited_patrimonio.to_csv("dados/patrimonio.csv", index=False)
        st.toast("Histórico atualizado com sucesso!")

# ---------------- ABA 2: POUPANÇA ----------------
with menu[1]:
    st.markdown("### 💰 GESTÃO DE CASHFLOW")
    
    c1, c2 = st.columns(2)
    sal = c1.number_input("Salário Líquido", min_value=0.0)
    desp = c2.number_input("Despesas Totais", min_value=0.0)
    inv = c1.number_input("Investimento", min_value=0.0)
    out = c2.number_input("Outros", min_value=0.0)
    
    poupanca_real = sal - desp - inv - out
    st.metric("DISPONÍVEL", f"{poupanca_real:,.2f} €", 
              delta=f"{(poupanca_real/sal*100):.1f}% Taxa" if sal > 0 else None)

    if st.button("REGISTAR FLUXO"):
        new_p = pd.DataFrame([{"Mês": datetime.now().strftime("%b %y"), "Salario": sal, "Despesas": desp, "Investimentos": inv, "Outros": out}])
        df_poupanca = pd.concat([df_poupanca, new_p], ignore_index=True)
        df_poupanca.to_csv("dados/poupanca.csv", index=False)
        st.rerun()

    st.markdown("### 📑 REGISTOS PASSADOS")
    edited_poupanca = st.data_editor(df_poupanca, num_rows="dynamic", use_container_width=True)
    if st.button("ATUALIZAR TABELA POUPANÇA"):
        edited_poupanca.to_csv("dados/poupanca.csv", index=False)

# ---------------- ABA 3: ANALYTICS (STOCKS) ----------------
with menu[2]:
    st.markdown("### 🔍 ANÁLISE FUNDAMENTAL")
    ticker = st.text_input("PESQUISAR ATIVO (TICKER)", placeholder="Ex: TSLA").upper()
    
    if ticker:
        try:
            stock = yf.Ticker(ticker)
            price = stock.info.get('currentPrice', 0)
            currency = stock.info.get('currency', 'USD')
            
            col1, col2 = st.columns(2)
            col1.metric(f"PREÇO {ticker}", f"{price} {currency}")
            
            # Layout de Info Rápida
            st.markdown(f"""
            **Empresa:** {stock.info.get('longName', 'N/A')}  
            **Setor:** {stock.info.get('sector', 'N/A')}  
            **P/E Ratio:** {stock.info.get('forwardPE', 'N/A')}
            """)
            
        except:
            st.error("Ativo não encontrado ou erro de conexão.")

# --- FOOTER ---
st.markdown("<br><hr><center style='color: #4A4E57;'>TRADING 212 STYLE | PERSONAL FINANCES</center>", unsafe_allow_html=True)
