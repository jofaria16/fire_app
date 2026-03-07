# app.py
import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime

# --- Configuração da página ---
st.set_page_config(
    page_title="🔥 FIRE App Mobile",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- API Key Alpha Vantage ---
ALPHA_VANTAGE_API_KEY = "TUA_API_KEY"  # <--- Coloca aqui a tua API Key

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

df_patrimonio = load_csv("patrimonio", ["Conta", "Valor"])
df_poupanca = load_csv("poupanca", ["Mês", "Salario", "Despesas", "Investimentos"])
df_buffett = load_csv("buffett", ["Ticker", "Score", "Data"])

# --- Login com senha ---
if 'acesso_permitido' not in st.session_state:
    st.session_state.acesso_permitido = False

if not st.session_state.acesso_permitido:
    st.markdown("<h1 style='text-align:center; color:#FF6F61;'>🔒 FIRE App Mobile</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Insere o código de acesso</p>", unsafe_allow_html=True)
    codigo = st.text_input("", type="password", placeholder="Código de acesso", key="senha")
    if st.button("Entrar", key="login_button"):
        if codigo == "1214":
            st.session_state.acesso_permitido = True
            st.experimental_rerun()
        else:
            st.error("Código incorreto! Tenta novamente.")
else:
    # --- Título e apresentação ---
    st.markdown("<h1 style='text-align:center; color:#FF6F61;'>🔥 FIRE App Mobile</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555;'>Organiza o teu património, poupança e investimentos de forma fácil</p>", unsafe_allow_html=True)

    # --- Menu moderno ---
    menu = st.radio(
        "",
        ["📊 Património", "💵 Poupança", "📈 Investimentos"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # --- Património ---
    if menu == "📊 Património":
        st.header("📊 Património Total")
        st.markdown("---")
        for i, row in df_patrimonio.iterrows():
            col1, col2 = st.columns([3,1])
            with col1:
                st.markdown(f"**{row['Conta']}**")
            with col2:
                valor = st.number_input("", value=float(row['Valor']), key=f"pat_{i}", format="%.2f")
                df_patrimonio.at[i, "Valor"] = valor
        df_patrimonio.to_csv("dados/patrimonio.csv", index=False)
        if not df_patrimonio.empty:
            st.markdown("**Distribuição do Património**")
            st.table(df_patrimonio)

    # --- Poupança ---
    elif menu == "💵 Poupança":
        st.header("💵 Poupança Mensal")
        st.markdown("---")
        with st.expander("Adicionar Registo", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                mes = st.text_input("Mês", key="mes")
            with col2:
                salario = st.number_input("Salário (€)", min_value=0.0, key="salario")
            with col3:
                despesas = st.number_input("Despesas (€)", min_value=0.0, key="despesas")
            with col4:
                investimentos = st.number_input("Investimentos (€)", min_value=0.0, key="investimentos")
            if st.button("Adicionar", key="add_poupanca"):
                df_poupanca.loc[len(df_poupanca)] = [mes, salario, despesas, investimentos]
                df_poupanca.to_csv("dados/poupanca.csv", index=False)
                st.success("Registo adicionado!")

        if not df_poupanca.empty:
            st.subheader("📊 Histórico Poupança")
            for i, row in df_poupanca.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2,2,2,2,1])
                with col1:
                    st.write(f"**{row['Mês']}**")
                with col2:
                    st.write(f"Salário: €{row['Salario']}")
                with col3:
                    st.write(f"Despesas: €{row['Despesas']}")
                with col4:
                    st.write(f"Investimentos: €{row['Investimentos']}")
                with col5:
                    if st.button(f"Apagar {i}", key=f"del_{i}"):
                        df_poupanca = df_poupanca.drop(i).reset_index(drop=True)
                        df_poupanca.to_csv("dados/poupanca.csv", index=False)
                        st.experimental_rerun()

            df_poupanca["Poupanca (%)"] = (df_poupanca["Salario"] - df_poupanca["Despesas"] - df_poupanca["Investimentos"]) / df_poupanca["Salario"] * 100
            st.metric("Média Poupança", f"{df_poupanca['Poupanca (%)'].mean():.2f}%")

    # --- Investimentos (antigo Faria Buffett 2.0) ---
    elif menu == "📈 Investimentos":
        st.header("📈 Investimentos")
        st.markdown("---")
        ticker = st.text_input("Ticker da ação (ex: AAPL)", key="buffett_ticker").upper()
        if ticker:
            try:
                url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
                response = requests.get(url).json()

                eps = float(response.get("EPS", 0))
                PE_MEDIO = 15
                valor_intrinseco = eps * PE_MEDIO
                url_price = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
                quote = requests.get(url_price).json().get("Global Quote", {})
                preco_atual = float(quote.get("05. price", 0))

                # Critérios investimento
                revenue_growth = float(response.get("RevenueTTM", 0))
                net_income = float(response.get("NetIncomeTTM", 0))
                roic = float(response.get("ReturnOnEquityTTM", 0)) * 100
                profit_margin = float(response.get("ProfitMargin", 0)) * 100
                cfo = float(response.get("OperatingCashFlowTTM", 0))
                debt_ratio = float(response.get("DebtToEquity", 0))
                ebitda = float(response.get("EBITDA", 1))

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

                st.subheader("Critérios")
                for k, v in criterios.items():
                    color = "green" if v=="✅" else "red"
                    st.markdown(f"- {k}: <span style='color:{color}'>{v}</span>", unsafe_allow_html=True)

                df_buffett.loc[len(df_buffett)] = [ticker, score, datetime.now()]
                df_buffett.to_csv("dados/buffett.csv", index=False)

            except Exception as e:
                st.error(f"Erro ao buscar dados: {e}")
