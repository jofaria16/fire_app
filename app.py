# app.py
import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime

# --- Configuração página ---
st.set_page_config(
    page_title="🔥 FIRE App Mobile",
    page_icon="💰",
    layout="centered",  # mobile-friendly
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

# --- Título ---
st.title("💰 FIRE App Mobile")
st.markdown("App limpa e interativa para telemóvel: Património, Poupança, Valor Intrínseco e Buffett 2.0")

# --- Menu ---
menu = st.radio("Escolhe a função:", ["📊 Património", "💵 Poupança", "💹 Valor Intrínseco", "📈 Faria Buffett 2.0"])

# --- Património ---
if menu == "📊 Património":
    st.header("📊 Total Património")
    for i, row in df_patrimonio.iterrows():
        valor = st.number_input(f"{row['Conta']}", value=float(row['Valor']), key=i)
        df_patrimonio.at[i, "Valor"] = valor
    df_patrimonio.to_csv("dados/patrimonio.csv", index=False)
    if not df_patrimonio.empty:
        st.markdown("**Distribuição do Património**")
        st.table(df_patrimonio)

# --- Poupança ---
elif menu == "💵 Poupança":
    st.header("💵 Taxa de Poupança")
    mes = st.text_input("Mês", key="mes")
    salario = st.number_input("Salário", min_value=0.0, key="salario")
    despesas = st.number_input("Despesas", min_value=0.0, key="despesas")
    investimentos = st.number_input("Investimentos", min_value=0.0, key="investimentos")
    if st.button("Adicionar Registo"):
        df_poupanca.loc[len(df_poupanca)] = [mes, salario, despesas, investimentos]
        df_poupanca.to_csv("dados/poupanca.csv", index=False)
        st.success("Registo adicionado!")
    if not df_poupanca.empty:
        df_poupanca["Poupanca (%)"] = (df_poupanca["Salario"] - df_poupanca["Despesas"] - df_poupanca["Investimentos"]) / df_poupanca["Salario"] * 100
        st.table(df_poupanca)
        st.metric("Média Poupança", f"{df_poupanca['Poupanca (%)'].mean():.2f}%")

# --- Valor Intrínseco ---
elif menu == "💹 Valor Intrínseco":
    st.header("💹 Valor Intrínseco (Modelo Buffett)")
    ticker = st.text_input("Ticker da ação (ex: AAPL)").upper()
    if ticker:
        try:
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url).json()
            eps = float(response.get("EPS", 0))
            PE_MEDIO = 15
            valor_intrinseco = eps * PE_MEDIO

            # Preço atual
            url_price = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
            quote = requests.get(url_price).json().get("Global Quote", {})
            preco_atual = float(quote.get("05. price", 0))

            if preco_atual == 0 or eps == 0:
                st.error("Não foi possível calcular o valor intrínseco com os dados disponíveis.")
            else:
                margem = (valor_intrinseco - preco_atual)/valor_intrinseco*100
                st.metric("Preço Atual", f"${preco_atual:.2f}")
                st.metric("Valor Intrínseco", f"${valor_intrinseco:.2f}", f"{margem:.2f}%")
                if margem >= 20:
                    st.success("Boa margem de segurança ✅")
                elif margem >= 0:
                    st.warning("Margem moderada ⚠️")
                else:
                    st.error("Preço acima do valor intrínseco ❌")
        except Exception as e:
            st.error(f"Erro ao buscar dados: {e}")

# --- Faria Buffett 2.0 ---
elif menu == "📈 Faria Buffett 2.0":
    st.header("📈 Faria Buffett 2.0")
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

            # Critérios Faria Buffett 2.0
            revenue_growth = float(response.get("RevenueTTM", 0))  # simplificação
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
            st.metric("Preço Atual", f"${preco_atual:.2f}")
            st.metric("Valor Intrínseco", f"${valor_intrinseco:.2f}")
            st.subheader("Critérios Buffett")
            for k, v in criterios.items():
                color = "green" if v=="✅" else "red"
                st.markdown(f"- {k}: <span style='color:{color}'>{v}</span>", unsafe_allow_html=True)
            st.markdown(f"### Score Total: {score}/{len(criterios)}")
            df_buffett.loc[len(df_buffett)] = [ticker, score, datetime.now()]
            df_buffett.to_csv("dados/buffett.csv", index=False)

        except Exception as e:
            st.error(f"Erro ao buscar dados: {e}")
