import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf

# --- 1. CONFIGURAÇÃO DA PÁGINA (UI/UX) ---
st.set_page_config(page_title="FARIA | QUANT TERMINAL v8.0", page_icon="📈", layout="wide")

# --- 2. CSS CUSTOMIZADO (CLEAN & DARK) ---
st.markdown("""
    <style>
    .stApp { background-color: #05070A; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .main-header { text-align: center; padding: 20px 0; border-bottom: 1px solid #1E222D; margin-bottom: 25px; }
    .logo-f { font-size: 32px; font-weight: 900; color: #FFFFFF; }
    .logo-q { font-size: 32px; font-weight: 200; color: #00D1FF; }
    
    /* Cards de Dados */
    .metric-card { background-color: #0D1117; padding: 18px; border-radius: 12px; border: 1px solid #1E222D; margin-bottom: 15px; }
    .metric-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #161B22; font-size: 14px; }
    
    /* Veredito Final */
    .status-bar { padding: 15px; border-radius: 8px; text-align: center; font-weight: 800; font-size: 20px; margin: 15px 0; }
    
    /* Input & Buttons */
    div.stButton > button { 
        width: 100% !important; background: linear-gradient(90deg, #0070FF, #00A3FF) !important; 
        color: white !important; font-weight: 800; border-radius: 6px; border: none; height: 3em;
    }
    input { background-color: #0D1117 !important; color: white !important; border: 1px solid #30363D !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE DADOS (DATABASE) ---
if not os.path.exists("dados"): os.makedirs("dados")

def save_db(df, name):
    df.to_csv(f"dados/{name}.csv", index=False)

def load_db(name):
    path = f"dados/{name}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        if not df.empty and "Mês" in df.columns:
            try:
                df['tmp_dt'] = pd.to_datetime(df['Mês'], format='%b %y', errors='coerce')
                df = df.sort_values('tmp_dt', ascending=False).drop(columns=['tmp_dt'])
            except: pass
        return df
    return pd.DataFrame()

def get_months():
    m_names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    curr_y = datetime.now().year % 100
    return [f"{m} {curr_y}" for m in m_names[::-1]] + [f"{m} {curr_y-1}" for m in m_names[::-1]]

# --- 4. MOTOR QUANTITATIVO (DCF ENGINE) ---
def calculate_intrinsic_value(ticker_obj, growth_rate):
    try:
        inf = ticker_obj.info
        # Fallback robusto para FCF (Essencial para GOOGL/Techs)
        fcf = inf.get('freeCashflow') or (inf.get('operatingCashflow', 0) - abs(inf.get('capitalExpenditure', 0)))
        shares = inf.get('sharesOutstanding', 0)
        
        if fcf <= 0 or shares <= 0: return 0
        
        # Parâmetros Conservadores
        discount_rate = 0.10
        terminal_growth = 0.02
        g = min(growth_rate, 0.15) if growth_rate > 0 else 0.04 # Cap no crescimento
        
        # DCF 5 Anos
        pv_cfs = sum([(fcf * (1 + g)**i) / (1 + discount_rate)**i for i in range(1, 6)])
        tv = (fcf * (1 + g)**5 * (1 + terminal_growth)) / (discount_rate - terminal_growth)
        pv_tv = tv / (1 + discount_rate)**5
        
        return (pv_cfs + pv_tv) / shares
    except: return 0

# --- 5. CONTROLO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown('<div class="main-header"><span class="logo-f">F</span><span class="logo-q">|QUANT</span></div>', unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])
    with col:
        if st.text_input("KEY", type="password") == "1214" or st.button("UNLOCK"):
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 6. INTERFACE PRINCIPAL ---
st.markdown('<div class="main-header"><span class="logo-f">F</span><span class="logo-q">|QUANT</span></div>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["🏛️ PATRIMÓNIO", "💰 FLUXO", "🔬 ANALYTICS V8"])

# ABA PATRIMÓNIO
with tab1:
    df_p = load_db("patrimonio")
    total_recente = df_p["Total"].iloc[0] if not df_p.empty else 0
    st.markdown(f"<h1 style='text-align:center; color:#00FF85;'>{total_recente:,.2f} €</h1>", unsafe_allow_html=True)
    
    with st.expander("ADICIONAR REGISTO"):
        m = st.selectbox("Mês", get_months(), key="m1")
        c1, c2 = st.columns(2)
        v1 = c1.number_input("Trading 212", 0.0)
        v2 = c2.number_input("IBKR", 0.0)
        v3 = c1.number_input("Crypto", 0.0)
        v4 = c2.number_input("Outros/PPR", 0.0)
        if st.button("GRAVAR PATRIMÓNIO"):
            new_row = pd.DataFrame([{"Mês": m, "T212": v1, "IBKR": v2, "CRY": v3, "PPR": v4, "Total": v1+v2+v3+v4}])
            save_db(pd.concat([df_p, new_row], ignore_index=True), "patrimonio")
            st.rerun()
            
    for i, r in df_p.iterrows():
        st.markdown(f'<div class="metric-card"><b>{r["Mês"]}</b> <span style="float:right; color:#00FF85;">{r["Total"]:,.2f} €</span></div>', unsafe_allow_html=True)
        if st.button(f"Apagar {r['Mês']}", key=f"delp_{i}"):
            save_db(df_p.drop(i), "patrimonio"); st.rerun()

# ABA FLUXO
with tab2:
    df_f = load_db("poupanca")
    with st.expander("REGISTAR ENTRADAS/SAÍDAS"):
        mf = st.selectbox("Mês", get_months(), key="m2")
        ent = st.number_input("Entradas (Salário...)", 0.0)
        sai = st.number_input("Saídas (Despesas...)", 0.0)
        if st.button("GRAVAR FLUXO"):
            new_f = pd.DataFrame([{"Mês": mf, "Entradas": ent, "Saidas": sai}])
            save_db(pd.concat([df_f, new_f], ignore_index=True), "poupanca")
            st.rerun()
            
    for i, r in df_f.iterrows():
        net = r['Entradas'] - r['Saidas']
        st.markdown(f'<div class="metric-card"><b>{r["Mês"]}</b> | Sobra: <span style="color:#00D1FF;">{net:,.2f} €</span></div>', unsafe_allow_html=True)
        if st.button(f"Apagar Fluxo {r['Mês']}", key=f"delf_{i}"):
            save_db(df_f.drop(i), "poupanca"); st.rerun()

# ABA ANALYTICS (A MELHOR VERSÃO)
with tab3:
    ticker_in = st.text_input("SCAN TICKER (Ex: AAPL, GOOGL, NVDA)", "").upper()
    if ticker_in:
        try:
            with st.spinner("Analyzing Financials..."):
                stock = yf.Ticker(ticker_in)
                inf = stock.info
                
                # Dados Base
                price = inf.get('currentPrice') or inf.get('previousClose', 1)
                rev_g = inf.get('revenueGrowth', 0)
                eps_g = inf.get('earningsGrowth', 0)
                margin = inf.get('profitMargins', 0)
                roic = (inf.get('returnOnEquity') or 0.15)
                cfo = inf.get('operatingCashflow', 0)
                ni = inf.get('netIncomeToCommon', 1)
                debt_ebitda = inf.get('debtToEbitda', 0)

                st.markdown(f"### {inf.get('longName', ticker_in)}")
                
                # Checklist FARIA BUFFET 2.0
                c1, c2 = st.columns(2)
                score = 0
                
                with c1:
                    st.write("📈 **Crescimento**")
                    checks1 = [("Receita > 7%", rev_g > 0.07, f"{rev_g*100:.1f}%"),
                               ("Lucro > 9%", eps_g > 0.09, f"{eps_g*100:.1f}%"),
                               ("Margem > 10%", margin > 0.10, f"{margin*100:.1f}%")]
                    for l, p, v in checks1:
                        score += 1 if p else 0
                        st.markdown(f'<div class="metric-row"><span>{l}</span><span>{v} {"✅" if p else "❌"}</span></div>', unsafe_allow_html=True)
                
                with c2:
                    st.write("💎 **Qualidade**")
                    cfo_ni = cfo/ni if ni != 0 else 0
                    checks2 = [("ROE/ROIC > 15%", roic > 0.15, f"{roic*100:.1f}%"),
                               ("CFO/Lucro > 90%", cfo_ni > 0.90, f"{cfo_ni*100:.1f}%"),
                               ("Dívida/EBITDA < 3", debt_ebitda < 3, f"{debt_ebitda:.2f}")]
                    for l, p, v in checks2:
                        score += 1 if p else 0
                        st.markdown(f'<div class="metric-row"><span>{l}</span><span>{v} {"✅" if p else "❌"}</span></div>', unsafe_allow_html=True)

                # DCF Valuation
                intrinsic = calculate_intrinsic_value(stock, rev_g)
                upside = ((intrinsic / price) - 1) * 100 if price > 0 else 0
                
                # Resultado
                res = "APPROVED" if score == 6 and upside > 15 else "WAITLIST" if score >= 4 else "REJECTED"
                color = "#00FF85" if res == "APPROVED" else "#FFD700" if res == "WAITLIST" else "#FF5252"
                
                st.markdown(f'<div class="status-bar" style="background:{color}; color:#05070A;">{res} ({score}/6)</div>', unsafe_allow_html=True)
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Preço Atual", f"{price:.2f}")
                m2.metric("Valor Intrínseco (DCF)", f"{intrinsic:.2f}")
                m3.metric("Margem", f"{upside:.1f}%", delta=f"{upside:.1f}%")
                
                st.latex(r"V_0 = \sum_{t=1}^{5} \frac{FCF_t}{(1.10)^t} + \frac{TV}{(1.10)^5}")

        except Exception as e:
            st.error(f"Ticker inválido ou dados insuficientes para {ticker_in}.")

st.markdown("<br><center style='color:#30363D; font-size:10px;'>FARIA QUANT TERMINAL v8.0 | PROFESSIONAL EDITION</center>", unsafe_allow_html=True)
