import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="FARIA | THE ORACLE v5.5", page_icon="🎯", layout="wide")

# --- 2. CSS "THE ORACLE" (CLEAN & CRITICAL) ---
st.markdown("""
    <style>
    .stApp { background-color: #0A0C10; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .logo-container { text-align: center; padding: 20px; border-bottom: 2px solid #1E222D; margin-bottom: 30px; }
    .logo-f { font-size: 32px; font-weight: 900; color: #FFFFFF; }
    .logo-invest { font-size: 32px; font-weight: 200; color: #00D1FF; }
    
    .status-card {
        background: #11141B; padding: 25px; border-radius: 12px;
        border: 1px solid #30363D; margin-bottom: 20px;
    }
    
    .data-table { width: 100%; border-collapse: collapse; margin: 15px 0; }
    .data-table td { padding: 12px; border-bottom: 1px solid #1E222D; font-size: 15px; }
    .label { color: #8B949E; font-weight: 500; }
    .value { color: #FFFFFF; font-weight: 700; text-align: right; }
    
    .badge {
        padding: 12px; border-radius: 8px; text-align: center;
        font-weight: 900; font-size: 18px; letter-spacing: 1px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. MOTOR DCF (A LÓGICA DO INVESTIDOR CRÍTICO) ---
def calculate_intrinsic_value(fcf, growth_rate, discount_rate, terminal_growth, shares):
    if fcf <= 0 or shares <= 0: return 0
    # Projeção 5 anos
    projected_fcf = []
    current_fcf = fcf
    for i in range(5):
        current_fcf *= (1 + growth_rate)
        projected_fcf.append(current_fcf / ((1 + discount_rate) ** (i + 1)))
    
    # Terminal Value (Gordon Growth Model)
    tv = (current_fcf * (1 + terminal_growth)) / (discount_rate - terminal_growth)
    tv_discounted = tv / ((1 + discount_rate) ** 5)
    
    intrinsic_value = (sum(projected_fcf) + tv_discounted) / shares
    return intrinsic_value

# --- 4. LOGIN ---
if 'acesso' not in st.session_state: st.session_state.acesso = False
if not st.session_state.acesso:
    st.markdown('<div class="logo-container"><span class="logo-f">F</span><span class="logo-invest">|QUANT</span></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        pwd = st.text_input("ENTER QUANT KEY", type="password")
        if st.button("UNLOCK") or pwd == "1214":
            if pwd == "1214": st.session_state.acesso = True; st.rerun()
    st.stop()

# --- 5. INTERFACE ---
st.markdown('<div class="logo-container"><span class="logo-f">F</span><span class="logo-invest">|ORACLE</span></div>', unsafe_allow_html=True)
menu = st.tabs(["🏛️ PORTFÓLIO", "🔬 ANALYTICS 5.5"])

with menu[1]:
    ticker_input = st.text_input("INSERIR TICKER PARA ANÁLISE DCF", placeholder="Ex: NVDA, AAPL, MSFT").upper()
    
    if ticker_input:
        try:
            with st.spinner("A processar fluxos de caixa..."):
                ticker = yf.Ticker(ticker_input)
                inf = ticker.info
                
                # Dados Fundamentais
                current_price = inf.get('currentPrice', 0)
                shares = inf.get('sharesOutstanding', 1)
                fcf = inf.get('freeCashflow', 0)
                cfo = inf.get('operatingCashflow', 0)
                net_income = inf.get('netIncomeToCommon', 0)
                rev_growth = inf.get('revenueGrowth', 0)
                eps_growth = inf.get('earningsGrowth', 0)
                margin = inf.get('profitMargins', 0)
                roic = inf.get('returnOnAssets', 0) * 2
                debt_ebitda = inf.get('debtToEbitda', 0)

                # --- PARÂMETROS CRÍTICOS ---
                st.markdown(f"### {inf.get('longName', ticker_input)}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="status-card">
                        <table class="data-table">
                            <tr><td class="label">Receita (YoY)</td><td class="value">{rev_growth*100:.2f}%</td></tr>
                            <tr><td class="label">Lucro Líquido (YoY)</td><td class="value">{eps_growth*100:.2f}%</td></tr>
                            <tr><td class="label">Margem Líquida</td><td class="value">{margin*100:.2f}%</td></tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="status-card">
                        <table class="data-table">
                            <tr><td class="label">ROIC (Est.)</td><td class="value">{roic*100:.2f}%</td></tr>
                            <tr><td class="label">CFO / Lucro Líquido</td><td class="value">{(cfo/net_income*100 if net_income else 0):.1f}%</td></tr>
                            <tr><td class="label">Dívida / EBITDA</td><td class="value">{debt_ebitda:.2f}</td></tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)

                # --- CÁLCULO DCF REAL ---
                # Ajuste conservador de crescimento: usamos o menor entre rev_growth e 15% (para evitar euforia)
                g = min(rev_growth, 0.15) if rev_growth > 0 else 0.02
                r = 0.10 # Taxa de desconto padrão 10% (Exigência do investidor)
                tg = 0.025 # Crescimento perpétuo 2.5%
                
                v_intrinsico = calculate_intrinsic_value(fcf, g, r, tg, shares)
                upside = ((v_intrinsico / current_price) - 1) * 100 if current_price > 0 else 0

                # --- SCORE E AVALIAÇÃO ---
                score = 0
                if rev_growth > 0.07: score += 1
                if eps_growth > 0.09: score += 1
                if roic > 0.15: score += 1
                if margin > 0.10: score += 1
                if net_income and (cfo/net_income) > 0.90: score += 1
                if 0 < debt_ebitda < 3: score += 1

                st.markdown("---")
                st.markdown(f"<h4 style='text-align:center;'>SCORE FARIA BUFFET: {score}/6</h4>", unsafe_allow_html=True)
                
                if score >= 5 and upside > 15:
                    status, color = "APROVADA - COMPRA SEGURA", "#00FF85"
                elif score >= 4 and upside > 0:
                    status, color = "INCONCLUSIVO - AGUARDAR MARGEM", "#FFD700"
                else:
                    status, color = "REJEITADA - FORA DOS CRITÉRIOS", "#FF5252"

                st.markdown(f'<div class="badge" style="background:{color}; color:#000;">{status}</div>', unsafe_allow_html=True)

                # --- VALUATION FINAL ---
                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                c1.metric("Preço de Mercado", f"{current_price:.2f}")
                c2.metric("Valor Intrínseco (DCF)", f"{v_intrinsico:.2f}")
                c3.metric("Margem de Segurança", f"{upside:.1f}%", delta=f"{upside:.1f}%")

                st.latex(r"V = \sum_{t=1}^{5} \frac{FCF \times (1+g)^t}{(1+r)^t} + \frac{TV}{(1+r)^5}")
                st.caption(f"Nota: Cálculo baseado em FCF de {fcf/1e9:.2f}B e crescimento projetado de {g*100:.1f}%.")

        except Exception as e:
            st.error(f"Erro na análise técnica: {e}")

# Aba de Portfólio simplificada e clean
with menu[0]:
    st.info("Módulo de Gestão de Ativos Ativo. Insira os dados para atualizar o património.")
    # (Lógica de portfólio anterior aqui...)
