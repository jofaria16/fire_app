# app.py
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

# --- Função para criar menu estilo botão ---
def menu_button(name, key, color="#FF6F61"):
    st.markdown(f"""
        <div style="
            background-color:{color};
            color:white;
            font-weight:bold;
            font-family:sans-serif;
            font-size:18px;
            padding:20px;
            border-radius:12px;
            text-align:center;
            cursor:pointer;
            margin-bottom:10px;
            text-transform:uppercase;">
            {name}
        </div>
    """, unsafe_allow_html=True)
    return st.button(name, key=key)

if st.session_state.acesso:
    # Menu principal
    st.markdown("---")
    if menu_button("📊 Património", "patrimonio", "#1E90FF"):
        menu_choice = "patrimonio"
    elif menu_button("💵 Poupança", "poupanca", "#32CD32"):
        menu_choice = "poupanca"
    elif menu_button("📈 Investimentos", "investimentos", "#FF6F61"):
        menu_choice = "investimentos"
    else:
        menu_choice = None

    # --- Património ---
    if menu_choice == "patrimonio":
        st.subheader("Adicionar os valores do seu portfolio")
        t212 = st.number_input("T212 (€)", min_value=0.0, key="t212")
        ibkr = st.number_input("IBKR (€)", min_value=0.0, key="ibkr")
        crypto = st.number_input("CRYPTO (€)", min_value=0.0, key="crypto")
        ppr = st.number_input("PPR (€)", min_value=0.0, key="ppr")

        total_portfolio = t212 + ibkr + crypto + ppr
        st.metric("TOTAL PORTFOLIO", f"€{total_portfolio:.2f}")

    # --- Poupança ---
    elif menu_choice == "poupanca":
        with st.expander("ADICIONAR REGISTO", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                mes = st.text_input("MÊS", key="mes")
            with col2:
                salario = st.number_input("SALÁRIO (€)", min_value=0.0, key="salario")
            with col3:
                despesas = st.number_input("DESPESAS (€)", min_value=0.0, key="despesas")
            with col4:
                investimentos = st.number_input("INVESTIMENTOS (€)", min_value=0.0, key="investimentos")
            if st.button("ADICIONAR", key="add_poupanca"):
                df_poupanca.loc[len(df_poupanca)] = [mes, salario, despesas, investimentos]
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

            df_poupanca["Poupanca (%)"] = (df_poupanca["Salario"] - df_poupanca["Despesas"] - df_poupanca["Investimentos"]) / df_poupanca["Salario"] * 100
            st.metric("Média Poupança", f"{df_poupanca['Poupanca (%)'].mean():.2f}%")

    # --- Investimentos ---
    elif menu_choice == "investimentos":
        ticker = st.text_input("TICKER (ex: AAPL)", key="ticker").upper()
        if ticker:
            try:
                stock = yf.Ticker(ticker)
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

                df_investimentos.loc[len(df_investimentos)] = [ticker, valor_intrinseco, score, datetime.now()]
                df_investimentos.to_csv("dados/investimentos.csv", index=False)

            except Exception as e:
                st.error(f"Erro ao buscar dados: {e}")
