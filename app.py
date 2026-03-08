import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FARIA PERSONAL APP", page_icon="💰", layout="wide")

# --- CSS PERSONALIZADO (MELHORIA MOBILE) ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #FF6F61;
        color: white;
        font-weight: bold;
    }
    .stMetric {
        background-color: #1E1E1E;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    </style>
""", unsafe_allow_html=True)

# --- GESTÃO DE DADOS ---
if not os.path.exists("dados"):
    os.makedirs("dados")

def load_csv(name, columns):
    path = f"dados/{name}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        # Garante que as colunas existem
        for col in columns:
            if col not in df.columns:
                df[col] = 0
        return df[columns]
    df = pd.DataFrame(columns=columns)
    df.to_csv(path, index=False)
    return df

# Inicializar DataFrames
df_patrimonio = load_csv("patrimonio", ["Mês", "T212", "IBKR", "CRYPTO", "PPR", "Total"])
df_poupanca = load_csv("poupanca", ["Mês", "Salario", "Despesas", "Investimentos", "Outros"])
df_investimentos = load_csv("investimentos", ["Ticker", "Valor Intrinseco", "Score", "Data"])

# --- LOGIN ---
if 'acesso' not in st.session_state:
    st.session_state.acesso = False

st.markdown("<h1 style='text-align:center; color:#FF6F61;'>FARIA PERSONAL APP</h1>", unsafe_allow_html=True)

if not st.session_state.acesso:
    col_login, _ = st.columns([2, 1])
    with col_login:
        codigo = st.text_input("PASSWORD", type="password", placeholder="Introduza o código")
        if st.button("ENTRAR"):
            if codigo == "1214":
                st.session_state.acesso = True
                st.rerun()
            else:
                st.error("CÓDIGO INCORRETO!")
    st.stop()

# --- MENU DE NAVEGAÇÃO (DESIGN LIMPO) ---
menu = st.selectbox("SELECIONE A ÁREA:", ["📊 Património", "💵 Poupança", "📈 Investimentos"])

# --- FUNÇÕES DE AUXÍLIO ---
def save_data(df, name):
    df.to_csv(f"dados/{name}.csv", index=False)

# ---------------- PATRIMÓNIO ----------------
if "Património" in menu:
    st.subheader("Registo de Portfólio")
    
    with st.expander("➕ Adicionar Novo Mês", expanded=True):
        c1, c2 = st.columns(2)
        mes_input = c1.text_input("Mês (Ex: Jan/24)", value=datetime.now().strftime("%b/%y"))
        t212 = c1.number_input("T212 (€)", min_value=0.0, step=100.0)
        ibkr = c2.number_input("IBKR (€)", min_value=0.0, step=100.0)
        crypto = c2.number_input("CRYPTO (€)", min_value=0.0, step=100.0)
        ppr = st.number_input("PPR (€)", min_value=0.0, step=50.0)
        
        total_m = t212 + ibkr + crypto + ppr
        st.metric("TOTAL CALCULADO", f"{total_m:,.2f}€")
        
        if st.button("GRAVAR REGISTO"):
            new_row = pd.DataFrame([{"Mês": mes_input, "T212": t212, "IBKR": ibkr, "CRYPTO": crypto, "PPR": ppr, "Total": total_m}])
            df_patrimonio = pd.concat([df_patrimonio, new_row], ignore_index=True)
            save_data(df_patrimonio, "patrimonio")
            st.success("Dados guardados!")
            st.rerun()

    if not df_patrimonio.empty:
        st.subheader("Evolução")
        st.line_chart(df_patrimonio.set_index("Mês")["Total"])
        
        with st.expander("🗒️ Histórico / Editar"):
            edited_df = st.data_editor(df_patrimonio, num_rows="dynamic")
            if st.button("Confirmar Alterações"):
                save_data(edited_df, "patrimonio")
                st.rerun()

# ---------------- POUPANÇA ----------------
elif "Poupança" in menu:
    st.subheader("Controlo de Cashflow")
    
    tab1, tab2 = st.tabs(["Novo Registo", "Histórico"])
    
    with tab1:
        mes_p = st.text_input("Mês", value=datetime.now().strftime("%b/%y"), key="p_mes")
        sal = st.number_input("Salário Líquido (€)", min_value=0.0)
        desp = st.number_input("Despesas Fixas (€)", min_value=0.0)
        inv = st.number_input("Investimento Mensal (€)", min_value=0.0)
        out = st.number_input("Outros Gastos (€)", min_value=0.0)
        
        sobra = sal - desp - inv - out
        taxa_poupanca = (sobra / sal * 100) if sal > 0 else 0
        
        st.metric("SOBRA", f"{sobra:,.2f}€", delta=f"{taxa_poupanca:.1f}% Taxa Poup.")
        
        if st.button("GUARDAR POUPANÇA"):
            new_p = pd.DataFrame([{"Mês": mes_p, "Salario": sal, "Despesas": desp, "Investimentos": inv, "Outros": out}])
            df_poupanca = pd.concat([df_poupanca, new_p], ignore_index=True)
            save_data(df_poupanca, "poupanca")
            st.rerun()

    with tab2:
        if not df_poupanca.empty:
            st.dataframe(df_poupanca)

# ---------------- INVESTIMENTOS ----------------
elif "Investimentos" in menu:
    st.subheader("Análise Fundamentalista")
    
    ticker = st.text_input("TICKER DA ACÇÃO (Ex: AAPL, TSLA)", "").upper()
    
    if ticker:
        try:
            with st.spinner(f"A analisar {ticker}..."):
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Dados Principais
                preco = info.get("currentPrice", info.get("regularMarketPrice", 0))
                eps = info.get("trailingEps", 0)
                # Cálculo simples de Valor Intrínseco (Graham simplificado)
                valor_int = eps * 15 if eps > 0 else 0
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Preço Atual", f"${preco:.2f}")
                c2.metric("Valor Intrínseco (Est.)", f"${valor_int:.2f}")
                c3.metric("Margem", f"{((valor_int/preco)-1)*100:.1f}%" if preco > 0 else "N/A")

                # Critérios de Saúde Financeira
                criterios = {
                    "Receita a Crescer (>7%)": info.get("revenueGrowth", 0) > 0.07,
                    "Margem de Lucro (>10%)": info.get("profitMargins", 0) > 0.10,
                    "Dívida Controlada (D/E < 2)": info.get("debtToEquity", 0) < 200,
                    "ROE Positivo (>15%)": info.get("returnOnEquity", 0) > 0.15
                }
                
                score = sum(1 for v in criterios.values() if v)
                st.write(f"**SCORE DE QUALIDADE: {score}/4**")
                
                for k, v in criterios.items():
                    st.write(f"{'✅' if v else '❌'} {k}")

        except Exception as e:
            st.error(f"Erro ao obter dados: {e}")

# --- RODAPÉ ---
st.markdown("---")
st.caption("Faria Personal App v2.0 - Foco em Mobile & Performance")
