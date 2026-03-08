import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf
import plotly.express as px

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FARIA | QUANT TERMINAL v5.0", page_icon="💎", layout="wide")

# --- 2. CSS FUTURISTA (DARK MODE SUPREMO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #05070A; color: #E0E0E0; font-family: 'JetBrains Mono', monospace; }
    
    /* Logo Neon */
    .logo-container { text-align: center; padding: 20px; border-bottom: 1px solid #1E222D; }
    .logo-f { font-size: 35px; font-weight: 900; color: #FFFFFF; text-shadow: 0 0 10px #00D1FF; }
    .logo-invest { font-size: 35px; font-weight: 200; color: #00D1FF; }

    /* Cards de Alta Performance */
    .quant-card {
        background: linear-gradient(145deg, #0D1117, #161B22);
        padding: 25px; border-radius: 15px;
        border: 1px solid #30363D;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    
    /* Status Badge */
    .status-badge {
        padding: 10px 20px; border-radius: 8px; font-weight: 900; font-size: 20px;
        text-align: center; text-transform: uppercase; letter-spacing: 2px;
    }
    
    /* Metrics Table */
    .metric-row {
        display: flex; justify-content: space-between; padding: 12px 0;
        border-bottom: 1px solid #21262D; font-size: 14px;
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #0070FF, #00D1FF) !important;
        color: white !important; font-weight: 800 !important;
        border-radius: 12px !important; height: 4em !important; border: none !important;
        transition: 0.4s all; text-transform: uppercase;
    }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 20px #00D1FF; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGICA DE DADOS ---
def get_month_options():
    months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    y = datetime.now().year % 100
    return [f"{m} {y}" for m in months[::-1]] + [f"{m} {y-1}" for m in months[::-1]]

if not os.path.exists("dados"): os.makedirs("dados")

def load_data(name):
    path = f"dados/{name}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        if not df.empty:
            df['dt'] = pd.to_datetime(df['Mês'], format='%b %y', errors='coerce')
            df = df.sort_values(by='dt', ascending=False).drop(columns=['dt'])
        return df
    return pd.DataFrame()

# --- 4. SISTEMA DE LOGIN ---
if 'acesso' not in st.session_state: st.session_state.acesso = False
if not st.session_state.acesso:
    st.markdown('<div class="logo-container"><span class="logo-f">F</span><span class="logo-invest">|QUANT</span></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        st.write("")
        pwd = st.text_input("ENCRYPTED ACCESS CODE", type="password")
        if st.button("AUTHENTICATE") or pwd == "1214":
            if pwd == "1214": st.session_state.acesso = True; st.rerun()
    st.stop()

# --- 5. INTERFACE PRINCIPAL ---
st.markdown('<div class="logo-container"><span class="logo-f">F</span><span class="logo-invest">|QUANT</span></div>', unsafe_allow_html=True)
menu = st.tabs(["🏛️ ASSETS", "💰 CASHFLOW", "🔬 ANALYTICS 5.0"])

# (Abas Assets e Cashflow seguem o padrão futurista de cards)
with menu[0]:
    df_p = load_data("patrimonio")
    val_total = df_p["Total"].iloc[0] if not df_p.empty else 0
    st.markdown(f"<h1 style='text-align:center; color:#00FF85;'>{val_total:,.2f} €</h1>", unsafe_allow_html=True)
    with st.expander("NEW DATA ENTRY"):
        m = st.selectbox("Month", get_month_options())
        v1 = st.number_input("T212", min_value=0.0); v2 = st.number_input("IBKR", min_value=0.0)
        if st.button("UPDATE PORTFOLIO"):
            new = pd.DataFrame([{"Mês": m, "T212": v1, "IBKR": v2, "Total": v1+v2}])
            pd.concat([df_p, new], ignore_index=True).to_csv("dados/patrimonio.csv", index=False); st.rerun()

# ---------------- ANALYTICS 5.0 (O CÉREBRO) ----------------
with menu[2]:
    ticker = st.text_input("QUANT SCANNER (Ticker)", placeholder="Ex: MSFT").upper()
    
    if ticker:
        try:
            with st.spinner("RUNNING FARIA BUFFET 2.0 ALGORITHMS..."):
                stock = yf.Ticker(ticker)
                inf = stock.info
                hist = stock.history(period="1y")
                
                # --- EXTRAÇÃO DE MÉTRICAS ---
                rev_g = inf.get('revenueGrowth', 0)
                eps_g = inf.get('earningsGrowth', 0)
                roic = inf.get('returnOnAssets', 0) * 2 # Proxy ROIC
                margin = inf.get('profitMargins', 0)
                cfo = inf.get('operatingCashflow', 0)
                ni = inf.get('netIncomeToCommon', 0)
                debt_ebitda = inf.get('debtToEbitda', 0)
                pe = inf.get('forwardPE', 0)
                eps = inf.get('trailingEps', 0)
                
                # --- CÁLCULO VALOR INTRÍNSECO (GRAHAM MODIFICADO) ---
                # V = EPS * (8.5 + 2g) * 4.4 / Y (Y = yield 10y bonds approx 4%)
                expected_g = eps_g * 100 if eps_g else 5
                intrinsic_val = (eps * (8.5 + 2 * expected_g) * 4.4) / 4.2 if eps > 0 else 0
                current_price = inf.get('currentPrice', 1)
                upside = ((intrinsic_val / current_price) - 1) * 100

                # --- HEADER ANALYTICS ---
                st.markdown(f"### {inf.get('longName', ticker)} | Score Terminal")
                
                # Gráfico Técnico
                fig = px.area(hist, y="Close", title=f"PRICE ACTION (1Y)")
                fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=40,b=0), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

                # --- GRID DE MÉTRICAS ---
                st.markdown('<div class="quant-card">', unsafe_allow_html=True)
                
                metrics = [
                    ("Receita > 7%", rev_g > 0.07, f"{rev_g*100:.1f}%"),
                    ("Lucro Líquido > 9%", eps_g > 0.09, f"{eps_g*100:.1f}%"),
                    ("ROIC > 15%", roic > 0.15, f"{roic*100:.1f}%"),
                    ("Margem Líquida > 10%", margin > 0.10, f"{margin*100:.1f}%"),
                    ("CFO/Lucro > 90%", (cfo/ni > 0.9 if ni else False), f"{(cfo/ni*100 if ni else 0):.1f}%"),
                    ("Dívida/EBITDA < 3", 0 < debt_ebitda < 3, f"{debt_ebitda:.2f}")
                ]
                
                score = 0
                for label, pass_crit, val_str in metrics:
                    icon = "✅" if pass_crit else "❌"
                    color = "#00FF85" if pass_crit else "#FF5252"
                    if pass_crit: score += 1
                    st.markdown(f"""
                        <div class="metric-row">
                            <span style="color:#B0BEC5;">{label}</span>
                            <span style="color:{color}; font-weight:bold;">{val_str} {icon}</span>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"<h2 style='text-align:center; margin-top:20px;'>SCORE: {score}/6</h2>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # --- AVALIAÇÃO FINAL ---
                if score == 6 and upside > 10:
                    status, b_color, t_color = "APROVADA (BUY)", "#00FF85", "#05070A"
                elif score >= 4:
                    status, b_color, t_color = "INCONCLUSIVO (WATCH)", "#FFD700", "#05070A"
                else:
                    status, b_color, t_color = "REJEITADA (AVOID)", "#FF5252", "#FFFFFF"
                
                st.markdown(f"""
                    <div class="status-badge" style="background-color:{b_color}; color:{t_color};">
                        {status}
                    </div>
                """, unsafe_allow_html=True)

                # --- VALUATION SECTION ---
                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                c1.metric("Preço Atual", f"{current_price:.2f} {inf.get('currency')}")
                c2.metric("Valor Intrínseco", f"{intrinsic_val:.2f} {inf.get('currency')}")
                c3.metric("Margem Segurança", f"{upside:.1f}%", delta=f"{upside:.1f}%")

                st.markdown("---")
                st.latex(r"V = \frac{EPS \times (8.5 + 2g) \times 4.4}{Y}")
                st.caption("Fórmula de Valuation baseada no Modelo de Graham ajustado ao Faria Buffet 2.0")

        except Exception as e:
            st.error(f"Erro no processamento do Ticker. Detalhes: {e}")

st.markdown("<br><center style='color:#30363D; font-size:10px;'>QUANT v5.0 | SUPREME EDITION | NO FINANCIAL ADVICE</center>", unsafe_allow_html=True)
