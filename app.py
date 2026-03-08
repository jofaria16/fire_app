import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf
import time

st.set_page_config(page_title="FARIA PERSONAL APP", page_icon="💰", layout="wide")

# ---------- PASTA DADOS ----------
if not os.path.exists("dados"):
    os.makedirs("dados")

def load_csv(name, columns):
    path = f"dados/{name}.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    df = pd.DataFrame(columns=columns)
    df.to_csv(path, index=False)
    return df


# ---------- CSVs ----------
df_patrimonio = load_csv(
    "patrimonio",
    ["Mês","T212","IBKR","CRYPTO","PPR","TOTAL"]
)

df_poupanca = load_csv(
    "poupanca",
    ["Mês","Salario","Despesas","Investimentos","Outros"]
)

df_investimentos = load_csv(
    "investimentos",
    ["Ticker","Valor Intrinseco","Score","Data"]
)


# ---------- LOGIN ----------
if 'acesso' not in st.session_state:
    st.session_state.acesso = False

st.markdown(
"<h1 style='text-align:center;color:#FF6F61;'>FARIA PERSONAL APP</h1>",
unsafe_allow_html=True
)

if not st.session_state.acesso:

    codigo = st.text_input(
        "",
        type="password",
        placeholder="CÓDIGO DE ACESSO"
    )

    if st.button("ENTRAR"):

        if codigo == "1214":
            st.session_state.acesso = True
            st.rerun()

        else:
            st.error("CÓDIGO INCORRETO")


# ---------- MENU ----------
def menu_button(label,key,color):

    if st.button(
        label,
        key=key,
        use_container_width=True
    ):
        st.session_state.menu = key


if st.session_state.acesso:

    st.markdown("---")

    col1,col2,col3 = st.columns(3)

    with col1:
        menu_button("📊 PATRIMÓNIO","patrimonio","#1E90FF")

    with col2:
        menu_button("💵 POUPANÇA","poupanca","#32CD32")

    with col3:
        menu_button("📈 INVESTIMENTOS","investimentos","#FF6F61")

# =====================================================
# PATRIMÓNIO
# =====================================================

    if st.session_state.get("menu") == "patrimonio":

        st.subheader("ADICIONAR PORTFÓLIO")

        col1,col2,col3,col4 = st.columns(4)

        with col1:
            t212 = st.number_input("T212 (€)",0.0)

        with col2:
            ibkr = st.number_input("IBKR (€)",0.0)

        with col3:
            crypto = st.number_input("CRYPTO (€)",0.0)

        with col4:
            ppr = st.number_input("PPR (€)",0.0)

        total = t212 + ibkr + crypto + ppr

        st.metric("TOTAL PORTFÓLIO",f"€{total:,.2f}")

        mes = st.text_input("MÊS (ex: 2025-03)")

        if st.button("GUARDAR REGISTO"):

            if mes:

                novo = {
                    "Mês":mes,
                    "T212":t212,
                    "IBKR":ibkr,
                    "CRYPTO":crypto,
                    "PPR":ppr,
                    "TOTAL":total
                }

                df_patrimonio.loc[len(df_patrimonio)] = novo

                df_patrimonio = df_patrimonio.sort_values(
                    by="Mês",
                    ascending=False
                )

                df_patrimonio.to_csv(
                    "dados/patrimonio.csv",
                    index=False
                )

                st.success("REGISTO GUARDADO")

                st.rerun()

        # ---------- HISTÓRICO ----------

        if not df_patrimonio.empty:

            st.subheader("HISTÓRICO")

            for i,row in df_patrimonio.iterrows():

                col1,col2,col3,col4,col5,col6,col7 = st.columns(7)

                with col1:
                    mes_edit = st.text_input("MÊS",row["Mês"],key=f"mes{i}")

                with col2:
                    t212_edit = st.number_input("T212",value=row["T212"],key=f"t{i}")

                with col3:
                    ibkr_edit = st.number_input("IBKR",value=row["IBKR"],key=f"i{i}")

                with col4:
                    crypto_edit = st.number_input("CRYPTO",value=row["CRYPTO"],key=f"c{i}")

                with col5:
                    ppr_edit = st.number_input("PPR",value=row["PPR"],key=f"p{i}")

                total_edit = t212_edit + ibkr_edit + crypto_edit + ppr_edit

                with col6:
                    st.write(f"TOTAL €{total_edit:,.0f}")

                with col7:

                    if st.button("APAGAR",key=f"d{i}"):

                        df_patrimonio = df_patrimonio.drop(i)

                        df_patrimonio.to_csv(
                            "dados/patrimonio.csv",
                            index=False
                        )

                        st.rerun()

                df_patrimonio.at[i,"Mês"] = mes_edit
                df_patrimonio.at[i,"T212"] = t212_edit
                df_patrimonio.at[i,"IBKR"] = ibkr_edit
                df_patrimonio.at[i,"CRYPTO"] = crypto_edit
                df_patrimonio.at[i,"PPR"] = ppr_edit
                df_patrimonio.at[i,"TOTAL"] = total_edit

            df_patrimonio.to_csv("dados/patrimonio.csv",index=False)

            st.line_chart(df_patrimonio.set_index("Mês")["TOTAL"])


# =====================================================
# POUPANÇA
# =====================================================

    if st.session_state.get("menu") == "poupanca":

        st.subheader("REGISTO POUPANÇA")

        col1,col2,col3,col4,col5 = st.columns(5)

        with col1:
            mes = st.text_input("MÊS")

        with col2:
            salario = st.number_input("SALÁRIO",0.0)

        with col3:
            despesas = st.number_input("DESPESAS",0.0)

        with col4:
            investimentos = st.number_input("INVESTIMENTOS",0.0)

        with col5:
            outros = st.number_input("OUTROS",0.0)

        if st.button("GUARDAR"):

            df_poupanca.loc[len(df_poupanca)] = [
                mes,
                salario,
                despesas,
                investimentos,
                outros
            ]

            df_poupanca.to_csv(
                "dados/poupanca.csv",
                index=False
            )

            st.success("GUARDADO")

            st.rerun()

        if not df_poupanca.empty:

            st.dataframe(df_poupanca)

            df_plot = df_poupanca.copy()

            df_plot["Poupança %"] = (
                (df_plot["Salario"]
                - df_plot["Despesas"]
                - df_plot["Investimentos"]
                - df_plot["Outros"])
                / df_plot["Salario"]*100
            )

            st.line_chart(
                df_plot.set_index("Mês")["Poupança %"]
            )


# =====================================================
# INVESTIMENTOS
# =====================================================

    if st.session_state.get("menu") == "investimentos":

        st.subheader("ANALISAR EMPRESA")

        ticker = st.text_input(
            "TICKER (ex: AAPL)"
        ).upper()

        if ticker:

            try:

                time.sleep(2)

                @st.cache_data
                def get_stock(t):

                    stock = yf.Ticker(t)

                    return stock.info

                info = get_stock(ticker)

                preco = info.get(
                    "regularMarketPrice",0
                )

                eps = info.get(
                    "trailingEps",0
                )

                valor_intrinseco = eps * 15 if eps else 0

                revenue_growth = info.get("revenueGrowth",0)
                net_income = info.get("netIncomeToCommon",0)
                roic = info.get("returnOnEquity",0)*100
                profit_margin = info.get("profitMargins",0)*100
                cfo = info.get("operatingCashflow",0)
                debt_ratio = info.get("debtToEquity",0)
                ebitda = info.get("ebitda",1)

                criterios = {
                "Crescimento Receita >7%": revenue_growth>0.07,
                "Lucro positivo": net_income>0,
                "ROIC >15%": roic>15,
                "Margem >10%": profit_margin>10,
                "CFO/NI >90%": net_income>0 and cfo/net_income>0.9,
                "Divida baixa": ebitda>0 and debt_ratio<3,
                "Intrinseco > preço": valor_intrinseco>preco
                }

                score = sum(criterios.values())

                col1,col2 = st.columns(2)

                with col1:
                    st.metric("PREÇO",f"${preco:.2f}")
                    st.metric("VALOR INTRÍNSECO",f"${valor_intrinseco:.2f}")

                with col2:
                    st.metric("SCORE",f"{score}/7")

                for k,v in criterios.items():

                    cor = "green" if v else "red"

                    st.markdown(
                    f"{k} : <span style='color:{cor}'>{v}</span>",
                    unsafe_allow_html=True
                    )

                df_investimentos.loc[len(df_investimentos)] = [
                    ticker,
                    valor_intrinseco,
                    score,
                    datetime.now()
                ]

                df_investimentos.to_csv(
                    "dados/investimentos.csv",
                    index=False
                )

            except Exception as e:

                st.error(f"Erro ao buscar dados: {e}")
