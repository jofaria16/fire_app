import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf

# --- Configuração página ---
st.set_page_config(page_title="FARIA PERSONAL APP", page_icon="💰", layout="wide")

# --- Pastas e CSVs ---
if not os.path.exists("dados"):
    os.makedirs("dados")

def load_csv(name, columns):
    path = f"dados/{name}.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    df = pd.DataFrame(columns=columns)
    df.to_csv(path, index=False)
    return df

df_poupanca = load_csv("poupanca", ["Mês", "Salario", "Despesas", "Investimentos"])
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

# --- Função para criar menu estilo card clicável ---
def menu_card(name, key, color="#FF6F61"):
    if key not in st.session_state:
        st.session_state[key] = False
    clicked = st.button(name, key=f"btn_{key}")
    if clicked:
        # Toggle
        st.session_state[key] = not st.session_state[key]
    return st.session_state[key]

# Inicializar session_state para inputs se não existirem
inputs = ["t212", "ibkr", "crypto", "ppr", "mes", "salario", "despesas", "investimentos", "ticker"]
for inp in inputs:
    if inp not in st.session_state:
        st.session_state[inp] = 0 if "t212" in inp or "ibkr" in inp or "crypto" in inp or "ppr" in inp or "salario" in inp or "despesas" in inp or "investimentos" in inp else ""

# --- Menu principal ---
if st.session_state.acesso:
    st.markdown("---")

    show_patrimonio = menu_card("📊 Património", "patrimonio", "#1E90FF")
    show_poupanca = menu_card("💵 Poupança", "poupanca", "#32CD32")
    show_investimentos = menu_card("📈 Investimentos", "investimentos", "#FF6F61")

    # --- Património ---
    if show_patrimonio:
        st.subheader("Adicionar os valores do seu portfolio")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.session_state.t212 = st.number_input("T212 (€)", min_value=0.0, value=st.session_state.t212, key="input_t212")
        with col2:
            st.session_state.ibkr = st.number_input("IBKR (€)", min_value=0.0, value=st.session_state.ibkr, key="input_ibkr")
        with col3:
            st.session_state.crypto = st.number_input("CRYPTO (€)", min_value=0.0, value=st.session_state.crypto, key="input_crypto")
        with col4:
            st.session_state.ppr = st.number_input("PPR (€)", min_value=0.0, value=st.session_state.ppr, key="input_ppr")

        total_portfolio = st.session_state.t212 + st.session_state.ibkr + st.session_state.crypto + st.session_state.ppr
        st.metric("TOTAL PORTFOLIO", f"€{total_portfolio:.2f}")

    # --- Poupança ---
    if show_poupanca:
        st.subheader("Registos de Poupança")
        with st.expander("ADICIONAR REGISTO", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.session_state.mes = st.text_input("MÊS", value=st.session_state.mes, key="input_mes")
            with col2:
                st.session_state.salario = st.number_input("SALÁRIO (€)", min_value=0.0, value=st.session_state.salario, key="input_salario")
            with col3:
                st.session_state.despesas = st.number_input("DESPESAS (€)", min_value=0.0, value=st.session_state.despesas, key="input_despesas")
            with col4:
                st.session_state.investimentos = st.number_input("INVESTIMENTOS (€)", min_value=0.0, value=st.session_state.investimentos, key="input_investimentos")
            if st.button("ADICIONAR", key="add_poupanca"):
                df_poupanca.loc[len(df_poupanca)] = [st.session_state.mes, st.session_state.salario, st.session_state.despesas, st.session_state.investimentos]
                df_poupanca.to_csv("dados/poupanca.csv", index=False)
                st.success("Registo adicionado!")

        if not df_poupanca.empty:
            for i, row in df_poupanca.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2,2,2,2,1])
                with col1:
                    st.write(f"{row['Mês']}")
                with col2:
                    st.write(f"Salário: €{row['Salario']}")
                with col3:
                    st.write(f"Despesas: €{row['Despesas']}")
                with col4:
                    st.write(f"Investimentos: €{row['Investimentos']}")
                with col5:
                    if st.button(f"APAGAR {i}", key=f"del_{i}"):
                        df_poupanca = df_poupanca.drop(i).reset_index(drop=True)
                        df_poupanca.to_csv("dados/poupanca.csv", index=False)
                        st.experimental_rerun()

        df_poupanca["Poupanca (%)"] = (df_poupanca["Salario"] - df_poupanca["Despesas"] - df_poupanca["Investimentos"]) / df_poupanca["Salario"] * 100 if not df_poupanca.empty else 0
        if not df_poupanca.empty:
            st.metric("Média Poupança", f"{df_poupanca['Poupanca (%)'].mean():.2f}%")

    # --- Investimentos ---
    if show_investimentos:
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
