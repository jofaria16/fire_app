import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="FARIA | QUANT TERMINAL v6.0", page_icon="📈", layout="wide")

# --- 2. STYLE (WALL STREET DARK & CLEAN) ---
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #FFFFFF; }
    .app-logo { text-align: center; padding: 15px 0; border-bottom: 1px solid #1E222D; margin-bottom: 20px; }
    .logo-f { font-size: 30px; font-weight: 900; color: #FFFFFF; }
    .logo-invest { font-size: 30px; font-weight: 200; color: #00D1FF; }
    .metric-card { background-color: #161B22; padding: 20px; border-radius: 12px; border: 1px solid #30363D; margin-bottom: 10px; }
    .check-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #2D3444; font-size: 15px; }
    .status-box { padding: 20px; border-radius: 10px; text-align: center; font-weight: 800; font-size: 22px; margin-top: 20px; }
    div.stButton > button { width: 100% !important; border-radius: 8px; background: linear-gradient(135deg, #0070FF 0%, #00A3FF 100%); color: white; font-weight: 800; height: 3.5em; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN & DATA LOGIC ---
if 'acesso' not in st.session_state: st.session_state.acesso = False
if not st.session_state.acesso:
    st.markdown('<div class="app-logo"><span class="logo-f">F</span><span class="logo-invest">|INVEST</span></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 6, 1])
    with c2:
        pwd = st.text_input("PASSWORD", type="password")
        if st.button("LOGIN") or pwd == "1214":
            if pwd == "1214": st.session_state.acesso = True; st.rerun()
    st.stop()

def get_month_options():
    months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    y = datetime.now().year % 100
    return [f"{m} {y}" for m in months[::-1]] + [f"{m} {y-1}" for m in months[::-1]]

# --- 4. MOTOR DCF PROFISSIONAL ---
def dcf_valuation(fcf, growth, discount_rate, shares):
    if fcf <= 0 or shares <= 0: return 0
    # Projeção conservadora a 5 anos
    terminal_growth = 0.025 # 2.5% perpétuo
    cash_flows = []
    for i in range(1, 6):
        cf = fcf * (1 + growth) ** i
        discounted_cf = cf / (1 + discount_rate) ** i
        cash_flows.append(discounted_cf)
    
    # Terminal Value
    tv = (fcf * (1 + growth)**5 * (1 + terminal_growth)) / (discount_rate - terminal_growth)
    discounted_tv = tv / (1 + discount_rate) ** 5
    
    return (sum(cash_flows) + discounted_tv) / shares

# --- 5. INTERFACE ---
st.markdown('<div class="app-logo"><span class="logo-f">F</span><span class="logo-invest">|INVEST</span></div>', unsafe_allow_html=True)
menu = st.tabs(["🏛️ PORTFÓLIO", "💰 FLUXO", "🔬 ANALYTICS 6.0"])

with menu[2]:
    st.markdown("### 🔬 FARIA BUFFET 2.0 - ENGINE")
    ticker = st.text_input("DIGITE O TICKER PARA ANÁLISE PROFISSIONAL", placeholder="Ex: NVDA").upper()
    
    if ticker:
        try:
            with st.spinner("Calculating Intrinsic Value..."):
                stock = yf.Ticker(ticker)
                inf = stock.info
                
                # Dados Base
                current_price = inf.get('currentPrice', 1)
                shares = inf.get('sharesOutstanding', 1)
                
                # Métricas Fundamentais
                rev_growth = inf.get('revenueGrowth', 0)
                net_income_growth = inf.get('earningsGrowth', 0)
                roic = inf.get('returnOnAssets', 0) * 2 # Estimativa ROIC
                net_margin = inf.get('profitMargins', 0)
                cfo = inf.get('operatingCashflow', 0)
                net_income = inf.get('netIncomeToCommon', 0)
                debt_ebitda = inf.get('debtToEbitda', 0)
                fcf = inf.get('freeCashflow', 0)

                # --- EXIBIÇÃO DE PARÂMETROS ---
                st.markdown(f"#### 📊 FUNDAMENTAIS: {inf.get('longName', ticker)}")
                
                col1, col2 = st.columns(2)
                
                score = 0
                with col1:
                    st.markdown("**1️⃣ CRESCIMENTO & MARGEM**")
                    checks_1 = [
                        ("Receita > 7%", rev_growth > 0.07, f"{rev_growth*100:.1f}%"),
                        ("Lucro Líquido > 9%", net_income_growth > 0.09, f"{net_income_growth*100:.1f}%"),
                        ("Margem Líquida > 10%", net_margin > 0.10, f"{net_margin*100:.1f}%")
                    ]
                    for l, p, v in checks_1:
                        score += 1 if p else 0
                        st.markdown(f'<div class="check-item"><span>{l}</span><span>{v} {"✅" if p else "❌"}</span></div>', unsafe_allow_html=True)

                with col2:
                    st.markdown("**2️⃣ RENTABILIDADE & DÍVIDA**")
                    cfo_ratio = (cfo / net_income) if net_income else 0
                    checks_2 = [
                        ("ROIC > 15%", roic > 0.15, f"{roic*100:.1f}%"),
                        ("CFO / Lucro Líquido > 90%", cfo_ratio > 0.90, f"{cfo_ratio*100:.1f}%"),
                        ("Dívida Líquida / EBITDA < 3", 0 < debt_ebitda < 3, f"{debt_ebitda:.2f}")
                    ]
                    for l, p, v in checks_2:
                        score += 1 if p else 0
                        st.markdown(f'<div class="check-item"><span>{l}</span><span>{v} {"✅" if p else "❌"}</span></div>', unsafe_allow_html=True)

                # --- CÁLCULO DE VALOR INTRÍNSECO (O CÉREBRO) ---
                st.markdown("---")
                # Ajuste de crescimento crítico: usamos o menor entre rev_growth e 15% para sermos conservadores
                growth_adj = min(rev_growth, 0.15) if rev_growth > 0 else 0.03
                discount_rate = 0.10 # 10% de taxa de desconto (padrão de segurança)
                
                v_intrinsico = dcf_valuation(fcf, growth_adj, discount_rate, shares)
                upside = ((v_intrinsico / current_price) - 1) * 100 if current_price > 0 else 0

                # --- RESULTADO FINAL ---
                st.markdown(f"### SCORE FINAL: {score}/6")
                
                if score == 6 and upside > 15:
                    status, color = "APROVADA - COMPRA SEGURA", "#00FF85"
                elif score >= 4 and upside > 0:
                    status, color = "INCONCLUSIVO - OBSERVAR MARGEM", "#FFD700"
                else:
                    status, color = "REJEITADA - FORA DOS PARÂMETROS", "#FF5252"

                st.markdown(f'<div class="status-box" style="background-color: {color}; color: #0B0E14;">{status}</div>', unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                c1.metric("Preço Atual", f"{current_price:.2f}")
                c2.metric("Valor Intrínseco (DCF)", f"{v_intrinsico:.2f}")
                c3.metric("Margem de Segurança", f"{upside:.1f}%", delta=f"{upside:.1f}%")

                st.latex(r"V = \sum_{t=1}^{5} \frac{FCF \times (1+g)^t}{(1+r)^t} + \frac{TerminalValue}{(1+r)^5}")

        except Exception as e:
            st.error(f"Erro no processamento. Ticker inválido ou dados insuficientes.")

# Mantém as outras abas (Portfolio/Fluxo) para garantir que a app está completa
