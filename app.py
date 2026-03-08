import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt

# --- Configuração página ---
st.set_page_config(page_title="FARIA PERSONAL APP", page_icon="💰", layout="wide")

# --- Pastas e CSVs ---
if not os.path.exists("dados"):
    os.makedirs("dados")

def load_csv(name, columns):
    path = f"dados/{name}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        return df
    df = pd.DataFrame(columns=columns)
    df.to_csv(path, index=False)
    return df

# CSVs
df_patrimonio = load_csv("patrimonio", ["Mês", "T212", "IBKR", "CRYPTO", "PPR", "Total"])
df_poupanca = load_csv("poupanca", ["Mês", "Salario", "Despesas", "Investimentos", "Outros"])
df_investimentos = load_csv("investimentos", ["Ticker", "Valor Intrinseco", "Score", "Data"])

# --- Login ---
if 'acesso' not in st.session_state:
    st.session_state.acesso = False

st.markdown("<h1 style='text-align:center; color:#FF6F61; font-family:sans-serif;'>FARIA PERSONAL APP</h1>", unsafe_allow_html=True)

if not st.session_state.acesso:
    codigo = st.text_input("", type="password", placeholder="Código de acesso")
    if st.button("ENTRAR"):
        if codigo == "1214":
            st.session_state.acesso = True
        else:
            st.error("Código incorreto!")

# --- Menu state ---
if 'menu' not in st.session_state:
    st.session_state.menu = None

def menu_card(name, key, color="#FF6F61"):
    clicked = st.button(name, key=f"btn_{key}")
    if clicked:
        st.session_state.menu = key

# --- Inicializar session_state para inputs ---
def init_numeric_state(key):
    if key not in st.session_state:
        st.session_state[key] = 0.0
    else:
        try:
            st.session_state[key] = float(st.session_state[key])
        except:
            st.session_state[key] = 0.0

def init_string_state(key):
    if key not in st.session_state:
        st.session_state[key] = ""

# Património inputs
for k in ["t212", "ibkr", "crypto", "ppr"]:
    init_numeric_state(k)
# Poupança inputs
for k in ["salario", "despesas", "investimentos", "outros"]:
    init_numeric_state(k)
init_string_state("mes")
init_string_state("ticker")

# --- Menu ---
if st.session_state.acesso:
    st.markdown("---")
    col_menu = st.columns([1,1,1])
    with col_menu[0]:
        menu_card("📊 Património", "patrimonio", "#1E90FF")
    with col_menu[1]:
        menu_card("💵 Poupança", "poupanca", "#32CD32")
    with col_menu[2]:
        menu_card("📈 Investimentos", "investimentos", "#FF6F61")

    # ---------------- Património ----------------
    if st.session_state.menu == "patrimonio":
        st.subheader("Adicionar valores do seu portfolio")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.session_state.t212 = st.number_input("T212 (€)", min_value=0.0, value=st.session_state.t212, step=1.0, key="input_t212")
        with col2:
            st.session_state.ibkr = st.number_input("IBKR (€)", min_value=0.0, value=st.session_state.ibkr, step=1.0, key="input_ibkr")
        with col3:
            st.session_state.crypto = st.number_input("CRYPTO (€)", min_value=0.0, value=st.session_state.crypto, step=1.0, key="input_crypto")
        with col4:
            st.session_state.ppr = st.number_input("PPR (€)", min_value=0.0, value=st.session_state.ppr, step=1.0, key="input_ppr")
        
        total = st.session_state.t212 + st.session_state.ibkr + st.session_state.crypto + st.session_state.ppr
        st.metric("TOTAL PORTFOLIO", f"€{total:.2f}")

        # Adicionar ao histórico
        with st.expander("Adicionar registro histórico", expanded=True):
            mes_input = st.text_input("Mês", key="mes_patrimonio")
            if st.button("Adicionar Património", key="add_patrimonio"):
                if mes_input:
                    df_patrimonio.loc[len(df_patrimonio)] = [mes_input, st.session_state.t212, st.session_state.ibkr, st.session_state.crypto, st.session_state.ppr, total]
                    df_patrimonio.to_csv("dados/patrimonio.csv", index=False)
                    st.success("Registro adicionado!")
                    st.experimental_rerun()
        
        # Mostrar histórico
        if not df_patrimonio.empty:
            st.subheader("Histórico Património")
            st.dataframe(df_patrimonio)
            # Gráfico evolução
            df_patrimonio_plot = df_patrimonio.copy()
            df_patrimonio_plot["Total"] = df_patrimonio_plot["Total"].astype(float)
            plt.figure(figsize=(8,4))
            plt.plot(df_patrimonio_plot["Mês"], df_patrimonio_plot["Total"], marker="o")
            plt.title("Evolução do Património")
            plt.xlabel("Mês")
            plt.ylabel("Total (€)")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    # ---------------- Poupança ----------------
    if st.session_state.menu == "poupanca":
        st.subheader("Registos de Poupança")
        tab1, tab2 = st.tabs(["Adicionar", "Resumo Histórico"])
        
        # Aba 1: Adicionar
        with tab1:
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.session_state.mes = st.text_input("Mês", value=st.session_state.mes, key="input_mes")
            with col2:
                st.session_state.salario = st.number_input("Salário (€)", min_value=0.0, value=st.session_state.salario, step=1.0, key="input_salario")
            with col3:
                st.session_state.despesas = st.number_input("Despesas (€)", min_value=0.0, value=st.session_state.despesas, step=1.0, key="input_despesas")
            with col4:
                st.session_state.investimentos = st.number_input("Investimentos (€)", min_value=0.0, value=st.session_state.investimentos, step=1.0, key="input_investimentos")
            with col5:
                st.session_state.outros = st.number_input("Outros (€)", min_value=0.0, value=st.session_state.outros, step=1.0, key="input_outros")
            
            if st.button("Adicionar Registro", key="add_poupanca"):
                df_poupanca.loc[len(df_poupanca)] = [st.session_state.mes, st.session_state.salario, st.session_state.despesas, st.session_state.investimentos, st.session_state.outros]
                df_poupanca.to_csv("dados/poupanca.csv", index=False)
                st.success("Registro adicionado!")
                st.experimental_rerun()
        
        # Aba 2: Resumo histórico
        with tab2:
            if not df_poupanca.empty:
                st.dataframe(df_poupanca)
                df_poupanca_plot = df_poupanca.copy()
                df_poupanca_plot["Poupanca (%)"] = ((df_poupanca_plot["Salario"] - df_poupanca_plot["Despesas"] - df_poupanca_plot["Investimentos"] - df_poupanca_plot["Outros"])/df_poupanca_plot["Salario"]*100).astype(float)
                plt.figure(figsize=(8,4))
                plt.plot(df_poupanca_plot["Mês"], df_poupanca_plot["Poupanca (%)"], marker="o", color="green")
                plt.title("Evolução da Poupança (%)")
                plt.xlabel("Mês")
                plt.ylabel("Poupança (%)")
                plt.xticks(rotation=45)
                st.pyplot(plt)

    # ---------------- Investimentos ----------------
    if st.session_state.menu == "investimentos":
        st.subheader("Analisar Investimento")
        st.session_state.ticker = st.text_input("TICKER (ex: AAPL)", value=st.session_state.ticker, key="input_ticker").upper()
        if st.session_state.ticker:
            try:
                stock = yf.Ticker(st.session_state.ticker)
                info = stock.info
                preco_atual = info.get("regularMarketPrice", 0)
                eps = info.get("trailingEps", 0)
                valor_intrinseco = eps * 15 if eps else 0

                revenue_growth = info.get("revenueGrowth", 0)
                net_income = info.get("netIncomeToCommon", 0)
                roic = info.get("returnOnEquity", 0) * 100
                profit_margin = info.get("profitMargins", 0) * 100
                cfo = info.get("operatingCashflow", 0)
                debt_ratio = info.get("debtToEquity", 0)
                ebitda = info.get("ebitda", 1)

                criterios = {
                    "Crescimento Receita >7%": "✅" if revenue_growth > 0.07 else "❌",
                    "Crescimento Lucro >9%": "✅" if net_income > 0 else "❌",
                    "ROIC >15%": "✅" if roic > 15 else "❌",
                    "Margem Lucro >10%": "✅" if profit_margin > 10 else "❌",
                    "CFO/NI >90%": "✅" if net_income > 0 and cfo/net_income > 0.9 else "❌",
                    "Dívida/EBITDA <3": "✅" if ebitda > 0 and debt_ratio < 3 else "❌",
                    "Valor Intrínseco > Preço": "✅" if valor_intrinseco > preco_atual else "❌",
                    "Margem Segurança >=20%": "✅" if (valor_intrinseco - preco_atual)/valor_intrinseco*100 >= 20 else "❌"
                }

                score = sum(1 for v in criterios.values() if v == "✅")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Preço Atual", f"${preco_atual:.2f}")
                    st.metric("Valor Intrínseco", f"${valor_intrinseco:.2f}")
                with col2:
                    st.metric("Score Total", f"{score}/{len(criterios)}")

                for k, v in criterios.items():
                    color = "green" if v=="✅" else "red"
                    st.markdown(f"- {k}: <span style='color:{color}'>{v}</span>", unsafe_allow_html=True)

                df_investimentos.loc[len(df_investimentos)] = [st.session_state.ticker, valor_intrinseco, score, datetime.now()]
                df_investimentos.to_csv("dados/investimentos.csv", index=False)

            except Exception as e:
                st.error(f"Erro ao buscar dados: {e}")
