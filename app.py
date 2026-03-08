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
        df = pd.read_csv(path)
        df = df.reindex(columns=columns)  # força colunas corretas
        return df
    df = pd.DataFrame(columns=columns)
    df.to_csv(path, index=False)
    return df

# CSVs
df_patrimonio = load_csv("patrimonio", ["Mês","T212","IBKR","CRYPTO","PPR","Total"])
df_poupanca = load_csv("poupanca", ["Mês","Salario","Despesas","Investimentos","Outros"])
df_investimentos = load_csv("investimentos", ["Ticker","Valor Intrinseco","Score","Data"])

# --- Login ---
if 'acesso' not in st.session_state:
    st.session_state.acesso = False

st.markdown("<h1 style='text-align:center; color:#FF6F61; font-family:sans-serif;'>FARIA PERSONAL APP</h1>", unsafe_allow_html=True)

if not st.session_state.acesso:
    codigo = st.text_input("", type="password", placeholder="CÓDIGO DE ACESSO")
    if st.button("ENTRAR"):
        if codigo == "1214":
            st.session_state.acesso = True
            st.experimental_rerun()
        else:
            st.error("CÓDIGO INCORRETO!")

# --- Inicializar session_state ---
def init_numeric(key):
    if key not in st.session_state:
        st.session_state[key] = 0.0
def init_string(key):
    if key not in st.session_state:
        st.session_state[key] = ""

for k in ["t212","ibkr","crypto","ppr","salario","despesas","investimentos","outros"]:
    init_numeric(k)
for k in ["mes","ticker"]:
    init_string(k)

# --- Modo Day/Night ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
mode_col1, mode_col2 = st.columns([1,3])
with mode_col1:
    if st.button("🌞 DAY MODE"):
        st.session_state.dark_mode = False
        st.experimental_rerun()
with mode_col2:
    if st.button("🌙 NIGHT MODE"):
        st.session_state.dark_mode = True
        st.experimental_rerun()
if st.session_state.dark_mode:
    st.markdown("<style>body{background-color:#0E1117;color:white;}</style>", unsafe_allow_html=True)
else:
    st.markdown("<style>body{background-color:white;color:black;}</style>", unsafe_allow_html=True)

# --- Menu estilo cards ---
def menu_card(name, key, color):
    st.markdown(f"""
        <div style='
            background-color:{color};
            color:white;
            font-weight:bold;
            font-family:sans-serif;
            font-size:22px;
            padding:25px;
            border-radius:15px;
            text-align:center;
            cursor:pointer;
            text-transform:uppercase;
            margin-bottom:10px;'
        >{name}</div>
    """, unsafe_allow_html=True)
    clicked = st.button(name, key=f"btn_{key}")
    if clicked:
        st.session_state.menu = key

if st.session_state.acesso:
    st.markdown("---")
    col_menu = st.columns([1,1,1])
    with col_menu[0]: menu_card("📊 Património","patrimonio","#1E90FF")
    with col_menu[1]: menu_card("💵 Poupança","poupanca","#32CD32")
    with col_menu[2]: menu_card("📈 Investimentos","investimentos","#FF6F61")

# ---------------- Património ----------------
if st.session_state.get("menu") == "patrimonio":
    st.subheader("ADICIONAR VALORES DO PORTFÓLIO")
    cols = st.columns([1,1,1,1,1,1])
    with cols[0]: st.session_state.mes = st.text_input("MÊS", value=st.session_state.mes, key="mes_p")
    with cols[1]: st.session_state.t212 = st.number_input("T212 (€)", min_value=0.0, value=st.session_state.t212, step=1.0)
    with cols[2]: st.session_state.ibkr = st.number_input("IBKR (€)", min_value=0.0, value=st.session_state.ibkr, step=1.0)
    with cols[3]: st.session_state.crypto = st.number_input("CRYPTO (€)", min_value=0.0, value=st.session_state.crypto, step=1.0)
    with cols[4]: st.session_state.ppr = st.number_input("PPR (€)", min_value=0.0, value=st.session_state.ppr, step=1.0)
    total_mes = st.session_state.t212+st.session_state.ibkr+st.session_state.crypto+st.session_state.ppr
    with cols[5]: st.metric("TOTAL PORTFÓLIO",f"€{total_mes:.2f}")

    if st.button("ADICIONAR REGISTRO", key="add_patrimonio"):
        if st.session_state.mes:
            df_patrimonio = df_patrimonio.reindex(columns=["Mês","T212","IBKR","CRYPTO","PPR","Total"])
            new_row = pd.DataFrame([{
                "Mês": st.session_state.mes,
                "T212": st.session_state.t212,
                "IBKR": st.session_state.ibkr,
                "CRYPTO": st.session_state.crypto,
                "PPR": st.session_state.ppr,
                "Total": total_mes
            }])
            df_patrimonio = pd.concat([df_patrimonio,new_row],ignore_index=True)
            df_patrimonio.to_csv("dados/patrimonio.csv",index=False)
            st.success("REGISTRO ADICIONADO!")
            st.experimental_rerun()

    # Histórico editável e gráfico
    if not df_patrimonio.empty:
        st.subheader("HISTÓRICO PATRIMÓNIO")
        for i,row in df_patrimonio[::-1].iterrows():
            c1,c2,c3,c4,c5,c6,c7 = st.columns([2,1,1,1,1,1,1])
            with c1: novo_mes = st.text_input(f"MÊS {i}",value=row["Mês"],key=f"edit_mes_{i}")
            with c2: novo_t212 = st.number_input(f"T212 {i}",value=row["T212"],key=f"edit_t212_{i}")
            with c3: novo_ibkr = st.number_input(f"IBKR {i}",value=row["IBKR"],key=f"edit_ibkr_{i}")
            with c4: novo_crypto = st.number_input(f"CRYPTO {i}",value=row["CRYPTO"],key=f"edit_crypto_{i}")
            with c5: novo_ppr = st.number_input(f"PPR {i}",value=row["PPR"],key=f"edit_ppr_{i}")
            with c6: novo_total = st.number_input(f"TOTAL {i}",value=row["Total"],key=f"edit_total_{i}")
            with c7:
                if st.button(f"APAGAR {i}",key=f"del_{i}"):
                    df_patrimonio = df_patrimonio.drop(i).reset_index(drop=True)
                    df_patrimonio.to_csv("dados/patrimonio.csv",index=False)
                    st.experimental_rerun()
            df_patrimonio.at[i,"Mês"]=novo_mes
            df_patrimonio.at[i,"T212"]=novo_t212
            df_patrimonio.at[i,"IBKR"]=novo_ibkr
            df_patrimonio.at[i,"CRYPTO"]=novo_crypto
            df_patrimonio.at[i,"PPR"]=novo_ppr
            df_patrimonio.at[i,"Total"]=novo_total
        df_patrimonio.to_csv("dados/patrimonio.csv",index=False)
        st.line_chart(df_patrimonio.set_index("Mês")["Total"])

# ---------------- Poupança ----------------
if st.session_state.get("menu")=="poupanca":
    st.subheader("REGISTOS DE POUPANÇA")
    tab1, tab2 = st.tabs(["ADICIONAR","HISTÓRICO"])
    with tab1:
        cols = st.columns([1,1,1,1,1])
        with cols[0]: st.session_state.mes = st.text_input("MÊS", value=st.session_state.mes,key="input_mes")
        with cols[1]: st.session_state.salario = st.number_input("SALÁRIO (€)",min_value=0.0,value=st.session_state.salario)
        with cols[2]: st.session_state.despesas = st.number_input("DESPESAS (€)",min_value=0.0,value=st.session_state.despesas)
        with cols[3]: st.session_state.investimentos = st.number_input("INVESTIMENTOS (€)",min_value=0.0,value=st.session_state.investimentos)
        with cols[4]: st.session_state.outros = st.number_input("OUTROS (€)",min_value=0.0,value=st.session_state.outros)
        if st.button("ADICIONAR REGISTRO",key="add_poupanca"):
            df_poupanca = df_poupanca.reindex(columns=["Mês","Salario","Despesas","Investimentos","Outros"])
            new_row = pd.DataFrame([{
                "Mês":st.session_state.mes,
                "Salario":st.session_state.salario,
                "Despesas":st.session_state.despesas,
                "Investimentos":st.session_state.investimentos,
                "Outros":st.session_state.outros
            }])
            df_poupanca = pd.concat([df_poupanca,new_row],ignore_index=True)
            df_poupanca.to_csv("dados/poupanca.csv",index=False)
            st.success("REGISTRO ADICIONADO!")
            st.experimental_rerun()
    with tab2:
        if not df_poupanca.empty:
            st.dataframe(df_poupanca)
            df_poupanca_plot = df_poupanca.copy()
            df_poupanca_plot['Poupanca (%)'] = ((df_poupanca_plot['Salario']-df_poupanca_plot['Despesas']-df_poupanca_plot['Investimentos']-df_poupanca_plot['Outros'])/df_poupanca_plot['Salario']*100).astype(float)
            st.line_chart(df_poupanca_plot.set_index("Mês")["Poupanca (%)"])

# ---------------- Investimentos ----------------
if st.session_state.get("menu")=="investimentos":
    st.subheader("ANALISAR INVESTIMENTO")
    st.session_state.ticker = st.text_input("TICKER (ex: AAPL)", value=st.session_state.ticker).upper()
    if st.session_state.ticker:
        try:
            stock = yf.Ticker(st.session_state.ticker)
            info = stock.info
            preco_atual = info.get("regularMarketPrice",0)
            eps = info.get("trailingEps",0)
            valor_intrinseco = eps*15 if eps else 0
            revenue_growth = info.get("revenueGrowth",0)
            net_income = info.get("netIncomeToCommon",0)
            roic = info.get("returnOnEquity",0)*100
            profit_margin = info.get("profitMargins",0)*100
            cfo = info.get("operatingCashflow",0)
            debt_ratio = info.get("debtToEquity",0)
            ebitda = info.get("ebitda",1)
            criterios = {
                "Crescimento Receita >7%":"✅" if revenue_growth>0.07 else "❌",
                "Crescimento Lucro >9%":"✅" if net_income>0 else "❌",
                "ROIC >15%":"✅" if roic>15 else "❌",
                "Margem Lucro >10%":"✅" if profit_margin>10 else "❌",
                "CFO/NI >90%":"✅" if net_income>0 and cfo/net_income>0.9 else "❌",
                "Dívida/EBITDA <3":"✅" if ebitda>0 and debt_ratio<3 else "❌",
                "Valor Intrínseco > Preço":"✅" if valor_intrinseco>preco_atual else "❌",
                "Margem Segurança >=20%":"✅" if (valor_intrinseco-preco_atual)/valor_intrinseco*100>=20 else "❌"
            }
            score=sum(1 for v in criterios.values() if v=="✅")
            col1,col2=st.columns(2)
            with col1:
                st.metric("PREÇO ATUAL",f"${preco_atual:.2f}")
                st.metric("VALOR INTRÍNSECO",f"${valor_intrinseco:.2f}")
            with col2:
                st.metric("SCORE TOTAL",f"{score}/{len(criterios)}")
            for k,v in criterios.items():
                color="green" if v=="✅" else "red"
                st.markdown(f"- {k}: <span style='color:{color}'>{v}</span>",unsafe_allow_html=True)
            df_investimentos.loc[len(df_investimentos)] = [st.session_state.ticker,valor_intrinseco,score,datetime.now()]
            df_investimentos.to_csv("dados/investimentos.csv",index=False)
        except Exception as e:
            st.error(f"Erro ao buscar dados: {e}")
