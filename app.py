import streamlit as st
import pandas as pd
import os
from datetime import datetime
import yfinance as yf
import numpy as np

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FARIA | QUANT TERMINAL",
    page_icon="📈",
    layout="wide"
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #080B10; color: #DDE3EF; }
.block-container { padding-top: 1.5rem; max-width: 1200px; }

.fq-header { text-align:center; padding:20px 0 14px; border-bottom:1px solid #151C28; margin-bottom:24px; }
.fq-logo-f { font-family:'Space Mono',monospace; font-size:26px; font-weight:700; color:#FFFFFF; }
.fq-logo-q { font-family:'Space Mono',monospace; font-size:26px; font-weight:400; color:#00BFFF; }
.fq-sub    { font-size:10px; color:#2E3A50; letter-spacing:5px; margin-top:4px; font-family:'Space Mono',monospace; }

.card { background:#0D1219; border:1px solid #151C28; border-radius:10px; padding:18px 20px; margin-bottom:12px; }
.card:hover { border-color:#1E2A3E; }

.mrow { display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #111720; font-size:13.5px; }
.mrow:last-child { border-bottom:none; }
.mrow .label { color:#8899BB; }
.mrow .val   { font-family:'Space Mono',monospace; font-size:13px; }
.green { color:#00E87A; } .red { color:#FF4D6A; } .gold { color:#FFD060; } .blue { color:#00BFFF; }

.sec-title { font-size:10px; letter-spacing:4px; text-transform:uppercase; color:#304060; font-family:'Space Mono',monospace; margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid #111720; }

.verdict { padding:16px 24px; border-radius:8px; text-align:center; font-weight:700; font-size:17px; font-family:'Space Mono',monospace; letter-spacing:3px; margin:18px 0; }

.badge { display:inline-block; background:#0D1219; border:1px solid #1E2A3E; padding:2px 10px; border-radius:20px; font-size:11px; color:#6070A0; margin-left:6px; }

.stTabs [data-baseweb="tab-list"] { background:transparent; border-radius:0; gap:0; border:none; border-bottom:1px solid #151C28; }
.stTabs [data-baseweb="tab"]      { color:#556080; font-size:13px; font-weight:500; padding:10px 20px; border-radius:0; letter-spacing:0.5px; }
.stTabs [aria-selected="true"]    { color:#FFFFFF !important; background:transparent !important; border-bottom:2px solid #00BFFF !important; }

div.stButton > button {
    width:100% !important;
    background:linear-gradient(90deg,#004ECC,#0088FF) !important;
    color:white !important; font-weight:700; border-radius:6px; border:none;
    height:2.8em; font-family:'Space Mono',monospace; letter-spacing:1px; font-size:13px;
}
div.stButton > button:hover { opacity:0.85 !important; }

/* Small icon buttons (edit/delete) */
[data-testid="column"] div.stButton > button[kind="secondary"],
[data-testid="column"] div.stButton > button {
    background:transparent !important;
    border:1px solid #1E2A3E !important;
    color:#556080 !important;
    font-size:14px !important;
    height:2.2em !important;
    border-radius:6px !important;
    letter-spacing:0 !important;
    font-family: inherit !important;
}
[data-testid="column"] div.stButton > button:hover {
    border-color:#304060 !important;
    color:#AABBDD !important;
    opacity:1 !important;
}

.stTextInput input { background:#0D1219 !important; color:#DDE3EF !important; border:1px solid #1E2A3E !important; border-radius:6px !important; font-size:15px !important; }
.stTextInput input:focus { border-color:#00BFFF !important; }
.stNumberInput input { background:#0D1219 !important; color:#DDE3EF !important; border:1px solid #1E2A3E !important; }
.stSelectbox > div > div { background:#0D1219 !important; border:1px solid #1E2A3E !important; color:#DDE3EF !important; }
.streamlit-expanderHeader { background:#0D1219 !important; border:1px solid #151C28 !important; border-radius:8px !important; }

::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-thumb { background:#1E2A3E; border-radius:4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
DATA_DIR = "dados"
os.makedirs(DATA_DIR, exist_ok=True)

def save_db(df, name):
    if "Mês" in df.columns and not df.empty:
        try:
            df = df.copy()
            df["_dt"] = pd.to_datetime(df["Mês"], format="%b %y", errors="coerce")
            df = df.sort_values("_dt", ascending=False).drop(columns=["_dt"])
        except Exception:
            pass
    df.to_csv(f"{DATA_DIR}/{name}.csv", index=False)

def load_db(name):
    path = f"{DATA_DIR}/{name}.csv"
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    if df.empty or "Mês" not in df.columns:
        return df
    try:
        df["_dt"] = pd.to_datetime(df["Mês"], format="%b %y", errors="coerce")
        # sort descending: most recent first (iloc[0] = latest month)
        df = df.sort_values("_dt", ascending=False).drop(columns=["_dt"])
    except Exception:
        pass
    return df.reset_index(drop=True)

def get_months():
    names = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    y = datetime.now().year % 100
    return [f"{m} {y}" for m in reversed(names)] + [f"{m} {y-1}" for m in reversed(names)]

DESPESA_CATS = ["Habitação","Alimentação","Transportes","Saúde","Lazer","Subscrições","Educação","Outros"]
CAT_COLORS   = {
    "Habitação":"#00BFFF","Alimentação":"#00E87A","Transportes":"#FFD060",
    "Saúde":"#FF9ECD","Lazer":"#FF8C42","Subscrições":"#A78BFA",
    "Educação":"#34D399","Outros":"#8899BB"
}

# ─────────────────────────────────────────────
# SAFE GETTER
# ─────────────────────────────────────────────
def sg(d, *keys, default=0):
    for k in keys:
        v = d.get(k)
        if v is not None and v != "" and not (isinstance(v, float) and np.isnan(v)):
            try:
                f = float(v)
                if f != 0:
                    return f
            except Exception:
                return v
    return default

# ─────────────────────────────────────────────
# TICKER FETCH  (root fix for yfinance ≥0.2)
# ─────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_info(symbol: str):
    try:
        t    = yf.Ticker(symbol)
        info = t.info or {}

        # fast_info is more reliable for price
        try:
            fi    = t.fast_info
            price = (
                getattr(fi, "last_price", None) or
                getattr(fi, "regular_market_price", None) or
                info.get("currentPrice") or
                info.get("regularMarketPrice") or
                info.get("previousClose")
            )
            if price:
                info["currentPrice"] = float(price)
        except Exception:
            pass

        # last resort: pull from history
        if not info.get("currentPrice"):
            hist = t.history(period="5d")
            if not hist.empty:
                info["currentPrice"] = float(hist["Close"].iloc[-1])

        price = info.get("currentPrice", 0)
        name  = info.get("longName") or info.get("shortName") or ""

        if price == 0 and not name:
            return None, f"Ticker **{symbol}** não encontrado ou sem dados disponíveis."
        if not name:
            info["longName"] = symbol

        return info, None

    except Exception as e:
        msg = str(e)
        if "404" in msg or "No data" in msg.lower():
            return None, f"Ticker **{symbol}** inválido."
        return None, f"Erro ao carregar {symbol}: {msg}"

# ─────────────────────────────────────────────
# INTRINSIC VALUE ENGINE (sector-adjusted)
# ─────────────────────────────────────────────
SECTOR_CFG = {
    "Technology":             {"method":"dcf",      "dr":0.10,"tg":0.03, "cap":0.25,"label":"DCF — Free Cash Flow"},
    "Communication Services": {"method":"dcf",      "dr":0.10,"tg":0.025,"cap":0.20,"label":"DCF — Free Cash Flow"},
    "Healthcare":             {"method":"dcf",      "dr":0.09,"tg":0.025,"cap":0.18,"label":"DCF — Free Cash Flow"},
    "Consumer Cyclical":      {"method":"ev_ebitda","multiple":14,              "label":"EV / EBITDA"},
    "Consumer Defensive":     {"method":"pe_rel",   "base_pe":22,               "label":"P/E Relativo"},
    "Financial Services":     {"method":"pb_roe",                               "label":"P/B + ROE (Graham)"},
    "Industrials":            {"method":"ev_ebitda","multiple":11,              "label":"EV / EBITDA"},
    "Basic Materials":        {"method":"ev_ebitda","multiple":8,               "label":"EV / EBITDA"},
    "Energy":                 {"method":"ev_ebitda","multiple":7,               "label":"EV / EBITDA"},
    "Utilities":              {"method":"ddm",                                  "label":"Gordon Growth (DDM)"},
    "Real Estate":            {"method":"ffo",                                  "label":"P / FFO (REIT)"},
}

def intrinsic_value(info, sector):
    cfg    = SECTOR_CFG.get(sector, {"method":"dcf","dr":0.10,"tg":0.025,"cap":0.15,"label":"DCF — Geral"})
    method = cfg["method"]
    shares = sg(info, "sharesOutstanding", default=1)
    result = {"iv":0, "label":cfg["label"], "rows":[]}
    R      = result["rows"]
    try:
        if method == "dcf":
            dr, tg, cap = cfg.get("dr",0.10), cfg.get("tg",0.025), cfg.get("cap",0.15)
            fcf = sg(info,"freeCashflow",default=0)
            if fcf <= 0:
                fcf = sg(info,"operatingCashflow",default=0) - abs(sg(info,"capitalExpenditures",default=0))
            if fcf <= 0:
                fcf = sg(info,"netIncomeToCommon",default=0)
            if fcf <= 0 or shares <= 0: return result
            g  = min(max((sg(info,"revenueGrowth",default=0.05) + sg(info,"earningsGrowth",default=0.05))/2, 0.03), cap)
            pv = sum([(fcf*(1+g)**i)/(1+dr)**i for i in range(1,6)])
            tv = (fcf*(1+g)**5*(1+tg))/(dr-tg)
            result["iv"] = max((pv + tv/(1+dr)**5)/shares, 0)
            R += [("FCF Base",f"${fcf/1e9:.2f}B"),("Taxa Crescimento",f"{g*100:.1f}%"),
                  ("Taxa Desconto",f"{dr*100:.0f}%"),("Terminal Growth",f"{tg*100:.1f}%")]

        elif method == "ev_ebitda":
            ebitda = sg(info,"ebitda",default=0)
            if ebitda <= 0 or shares <= 0: return result
            mult   = cfg.get("multiple",12)
            equity = ebitda*mult - sg(info,"totalDebt",default=0) + sg(info,"totalCash",default=0)
            result["iv"] = max(equity/shares, 0)
            R += [("EBITDA",f"${ebitda/1e9:.2f}B"),("Múltiplo Setor",f"{mult}x")]

        elif method == "pe_rel":
            eps = sg(info,"trailingEps","forwardEps",default=0)
            if eps <= 0: return result
            adj_pe = cfg.get("base_pe",20) * (1 + sg(info,"revenueGrowth",default=0.04))
            result["iv"] = max(eps*adj_pe, 0)
            R += [("EPS TTM",f"${eps:.2f}"),("P/E Ajustado",f"{adj_pe:.1f}x")]

        elif method == "pb_roe":
            roe  = sg(info,"returnOnEquity",default=0.10)
            bvps = sg(info,"bookValue",default=0)
            if bvps <= 0: return result
            fair = max(roe/0.10, 0.5)
            result["iv"] = max(bvps*fair, 0)
            R += [("Book Value/Share",f"${bvps:.2f}"),("ROE",f"{roe*100:.1f}%"),("P/B Justo",f"{fair:.2f}x")]

        elif method == "ddm":
            div = sg(info,"dividendRate",default=0)
            if div <= 0: return result
            result["iv"] = max((div*1.025)/(0.07-0.025), 0)
            R += [("Dividendo Anual",f"${div:.2f}"),("r=7%, g=2.5%","Gordon Growth")]

        elif method == "ffo":
            ni  = sg(info,"netIncomeToCommon",default=0)
            ffo = ni + sg(info,"totalAssets",default=0)*0.02
            if ffo <= 0 or shares <= 0: return result
            result["iv"] = max(ffo/shares*16, 0)
            R += [("FFO/Share",f"${ffo/shares:.2f}"),("P/FFO Justo","16x")]

    except Exception as e:
        R.append(("Erro", str(e)))
    return result

# ─────────────────────────────────────────────
# CHECKLIST + VERDICT ENGINE
# ─────────────────────────────────────────────
def run_checklist(info, iv, price):
    rev_g   = sg(info,"revenueGrowth",default=0)
    eps_g   = sg(info,"earningsGrowth",default=0)
    margin  = sg(info,"profitMargins",default=0)
    gross_m = sg(info,"grossMargins",default=0)
    roe     = sg(info,"returnOnEquity",default=0)
    roa     = sg(info,"returnOnAssets",default=0)
    cfo     = sg(info,"operatingCashflow",default=0)
    ni      = sg(info,"netIncomeToCommon",default=1)
    debt_eq = sg(info,"debtToEquity",default=0)
    cr      = sg(info,"currentRatio",default=0)
    pe      = sg(info,"trailingPE",default=0)
    peg     = sg(info,"pegRatio",default=0)
    beta    = sg(info,"beta",default=1)
    upside  = ((iv/price)-1)*100 if price > 0 and iv > 0 else 0
    cfo_ni  = cfo/ni if ni != 0 else 0

    checks = [
        ("Crescimento",   "Receita YoY > 7%",       rev_g > 0.07,       f"{rev_g*100:.1f}%"),
        ("Crescimento",   "Lucro YoY > 9%",          eps_g > 0.09,       f"{eps_g*100:.1f}%"),
        ("Rentabilidade", "Margem Líquida > 10%",    margin > 0.10,      f"{margin*100:.1f}%"),
        ("Rentabilidade", "Margem Bruta > 40%",      gross_m > 0.40,     f"{gross_m*100:.1f}%"),
        ("Rentabilidade", "ROE > 15%",               roe > 0.15,         f"{roe*100:.1f}%"),
        ("Rentabilidade", "ROA > 5%",                roa > 0.05,         f"{roa*100:.1f}%"),
        ("Qualidade",     "CFO / Net Income > 80%",  cfo_ni > 0.80,      f"{cfo_ni*100:.1f}%"),
        ("Qualidade",     "Dívida/Equity < 1.5",     0 < debt_eq < 150,  f"{debt_eq/100:.2f}x" if debt_eq>1 else f"{debt_eq:.2f}x"),
        ("Qualidade",     "Current Ratio > 1.2",     cr > 1.2,           f"{cr:.2f}x"),
        ("Valuation",     "P/E < 30",                0 < pe < 30,        f"{pe:.1f}x" if pe>0 else "N/A"),
        ("Valuation",     "PEG < 1.5",               0 < peg < 1.5,      f"{peg:.2f}" if peg>0 else "N/A"),
        ("Valuation",     "Upside DCF > 15%",        upside > 15,        f"{upside:+.1f}%" if iv>0 else "N/A"),
        ("Risco",         "Beta < 1.5",              beta < 1.5,         f"{beta:.2f}"),
    ]
    score = sum(1 for _,_,p,_ in checks if p)
    n     = len(checks)
    qs    = sum(1 for c,_,p,_ in checks if c in ("Rentabilidade","Qualidade") and p)
    vs    = sum(1 for c,_,p,_ in checks if c == "Valuation" and p)

    if score >= 10 and vs >= 2:
        return checks,score,n,"APROVADA","#00E87A","#00E87A18","#00E87A44","Empresa de alta qualidade com valuation atrativo. Candidata a investimento."
    elif score >= 7 and qs >= 3:
        return checks,score,n,"INDECISA","#FFD060","#FFD06018","#FFD06044","Boas fundações mas alguns critérios não satisfeitos. Monitorizar."
    else:
        return checks,score,n,"REJEITADA","#FF4D6A","#FF4D6A18","#FF4D6A44","Não cumpre os critérios mínimos de qualidade ou valuation. Evitar."

# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown('<div class="fq-header"><div><span class="fq-logo-f">F</span><span class="fq-logo-q">|QUANT</span></div><div class="fq-sub">TERMINAL · PERSONAL EDITION</div></div>', unsafe_allow_html=True)
    _, col, _ = st.columns([1,1.2,1])
    with col:
        st.markdown("<br>", unsafe_allow_html=True)
        key = st.text_input("ACCESS KEY", type="password", placeholder="••••••")
        if st.button("UNLOCK →"):
            if key == "1214":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Chave incorreta.")
    st.stop()

# ─────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="fq-header"><div><span class="fq-logo-f">F</span><span class="fq-logo-q">|QUANT</span></div><div class="fq-sub">TERMINAL · PERSONAL EDITION</div></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["PATRIMÓNIO", "FLUXO DE CAIXA", "OBJETIVOS", "ANÁLISE DE AÇÕES"])

# ══════════════════════════════════════════════════════════════════
# TAB 1 — PATRIMÓNIO
# ══════════════════════════════════════════════════════════════════
with tab1:
    df_p = load_db("patrimonio")

    # ── session state for inline edit ──────────────────────────────────
    if "edit_pat_idx" not in st.session_state:
        st.session_state.edit_pat_idx = None

    # ── Performance por Carteira ────────────────────────────────────────
    if len(df_p) >= 2:
        # df_p is sorted descending: iloc[0]=most recent, iloc[1]=previous
        tot    = float(df_p["Total"].iloc[0]) if not df_p.empty else 0
        latest = df_p.iloc[0]   # most recent month (e.g. Abril)
        prev_r = df_p.iloc[1]   # previous month    (e.g. Março)
        st.markdown('<div class="sec-title" style="padding-left:4px; margin-top:8px;">PERFORMANCE POR CARTEIRA</div>', unsafe_allow_html=True)
        perf_cols = st.columns(4)
        for idx, (cn, label, color) in enumerate([("T212","Trading 212","#00BFFF"),("IBKR","IBKR","#FFD060"),("CRY","Crypto","#FF8C42"),("PPR","PPR / Outros","#A78BFA")]):
            if cn in df_p.columns:
                cur = float(latest.get(cn, 0) or 0)   # e.g. Abril
                prv = float(prev_r.get(cn, 0) or 0)   # e.g. Março
                d   = cur - prv                         # +320 se subiu
                dp  = (d/prv*100) if prv > 0 else 0
                s   = "+" if d >= 0 else ""
                dc2 = "#00E87A" if d >= 0 else "#FF4D6A"
                pct = (cur/tot*100) if tot > 0 else 0
                with perf_cols[idx]:
                    st.markdown(f"""
                        <div class="card" style="text-align:center; border-top:3px solid {color}; padding:14px 12px;">
                            <div style="font-size:10px; color:#556080; letter-spacing:2px; margin-bottom:8px;">{label.upper()}</div>
                            <div style="font-size:1.25em; font-weight:700; font-family:'Space Mono',monospace; color:{color};">{cur:,.0f}€</div>
                            <div style="font-size:12px; color:{dc2}; margin-top:4px;">{s}{d:,.0f}€ ({s}{dp:.1f}%)</div>
                            <div style="font-size:11px; color:#304060; margin-top:4px;">{pct:.1f}% do total</div>
                        </div>
                    """, unsafe_allow_html=True)

    # ── Add Record ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Adicionar Registo"):
        m     = st.selectbox("Mês", get_months(), key="m_pat")
        c1,c2 = st.columns(2)
        v1 = c1.number_input("Trading 212 (€)", min_value=0.0, format="%.2f", key="v1")
        v2 = c2.number_input("IBKR (€)",         min_value=0.0, format="%.2f", key="v2")
        v3 = c1.number_input("Crypto (€)",        min_value=0.0, format="%.2f", key="v3")
        v4 = c2.number_input("Outros / PPR (€)",  min_value=0.0, format="%.2f", key="v4")
        if st.button("GRAVAR PATRIMÓNIO"):
            row = pd.DataFrame([{"Mês":m,"T212":v1,"IBKR":v2,"CRY":v3,"PPR":v4,"Total":v1+v2+v3+v4}])
            save_db(pd.concat([df_p, row], ignore_index=True), "patrimonio")
            st.cache_data.clear()
            st.success("Gravado.")
            st.rerun()

    # ── History with edit + delete ───────────────────────────────────────
    st.markdown('<div class="sec-title" style="padding-left:4px; margin-top:4px;">HISTÓRICO</div>', unsafe_allow_html=True)

    for i, r in df_p.iterrows():
        is_editing = st.session_state.edit_pat_idx == i

        if is_editing:
            # ── EDIT MODE ─────────────────────────────────────────────
            st.markdown(f"""
                <div style="background:#0D1219; border:1px solid #00BFFF44; border-radius:10px; padding:16px 20px; margin-bottom:4px;">
                    <div style="font-size:10px; color:#00BFFF; letter-spacing:3px; margin-bottom:12px; font-family:'Space Mono',monospace;">A EDITAR — {r["Mês"]}</div>
                </div>
            """, unsafe_allow_html=True)
            ec1, ec2 = st.columns(2)
            e1 = ec1.number_input("Trading 212 (€)", value=float(r.get("T212",0) or 0), format="%.2f", key=f"e1_{i}")
            e2 = ec2.number_input("IBKR (€)",         value=float(r.get("IBKR",0) or 0), format="%.2f", key=f"e2_{i}")
            e3 = ec1.number_input("Crypto (€)",        value=float(r.get("CRY",0)  or 0), format="%.2f", key=f"e3_{i}")
            e4 = ec2.number_input("Outros / PPR (€)",  value=float(r.get("PPR",0)  or 0), format="%.2f", key=f"e4_{i}")
            sb1, sb2 = st.columns(2)
            if sb1.button("Guardar", key=f"esave_{i}"):
                df_p.at[i,"T212"]  = e1
                df_p.at[i,"IBKR"]  = e2
                df_p.at[i,"CRY"]   = e3
                df_p.at[i,"PPR"]   = e4
                df_p.at[i,"Total"] = e1+e2+e3+e4
                save_db(df_p, "patrimonio")
                st.session_state.edit_pat_idx = None
                st.rerun()
            if sb2.button("Cancelar", key=f"ecancel_{i}"):
                st.session_state.edit_pat_idx = None
                st.rerun()
        else:
            # ── VIEW MODE ─────────────────────────────────────────────
            bk = f'T212: {float(r.get("T212",0) or 0):,.0f}€ · IBKR: {float(r.get("IBKR",0) or 0):,.0f}€ · Crypto: {float(r.get("CRY",0) or 0):,.0f}€ · PPR: {float(r.get("PPR",0) or 0):,.0f}€'
            c_card, c_edit, c_del = st.columns([10, 1, 1])
            with c_card:
                st.markdown(f"""
                    <div class="card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-family:'Space Mono',monospace; font-weight:700; color:#AABBDD;">{r["Mês"]}</span>
                            <span class="green" style="font-family:'Space Mono',monospace; font-size:1.1em; font-weight:700;">{float(r["Total"]):,.2f} €</span>
                        </div>
                        <div style="font-size:11px; color:#304060; margin-top:6px;">{bk}</div>
                    </div>
                """, unsafe_allow_html=True)
            with c_edit:
                st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                if st.button("✏️", key=f"edit_{i}", help="Editar"):
                    st.session_state.edit_pat_idx = i
                    st.rerun()
            with c_del:
                st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                if st.button("🗑", key=f"dp_{i}", help="Apagar"):
                    save_db(df_p.drop(i).reset_index(drop=True), "patrimonio")
                    st.rerun()

# ══════════════════════════════════════════════════════════════════
# TAB 2 — FLUXO DE CAIXA
# ══════════════════════════════════════════════════════════════════
with tab2:
    df_f    = load_db("poupanca")
    df_desp = load_db("despesas")

    # ── Summary ─────────────────────────────────────────────────────────
    if not df_f.empty and "Entradas" in df_f.columns:
        te = float(df_f["Entradas"].sum())
        ts = float(df_f["Saidas"].sum()) if "Saidas" in df_f.columns else 0
        tn = te - ts
        avg_monthly = tn / len(df_f) if len(df_f) > 0 else 0
        months_left = 12 - datetime.now().month
        proj_extra  = avg_monthly * months_left

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total Entradas",   f"{te:,.0f} €")
        c2.metric("Total Saídas",     f"{ts:,.0f} €")
        c3.metric("Total Poupado",    f"{tn:,.0f} €", delta=f"{tn/te*100:.1f}% taxa" if te>0 else "")
        c4.metric("Projeção Fim Ano", f"+{proj_extra:,.0f} €", delta=f"{months_left} meses restantes")

        # Taxa média de poupança
        if te > 0:
            taxa_m = tn/te*100
            bc     = "#00E87A" if taxa_m >= 20 else "#FFD060" if taxa_m >= 10 else "#FF4D6A"
            bw     = min(int(taxa_m), 100)
            tip    = "🟢 Excelente! Acima de 20%" if taxa_m >= 20 else "🟡 Razoável. Tenta chegar a 20%" if taxa_m >= 10 else "🔴 Abaixo do ideal. Objetivo: 10%+"
            st.markdown(f"""
                <div class="card" style="margin-top:16px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                        <span style="font-size:12px; color:#8899BB; letter-spacing:1px;">TAXA DE POUPANÇA MÉDIA</span>
                        <span style="font-family:'Space Mono',monospace; color:{bc}; font-weight:700;">{taxa_m:.1f}%</span>
                    </div>
                    <div style="background:#111720; border-radius:20px; height:8px;">
                        <div style="width:{bw}%; height:8px; border-radius:20px; background:{bc};"></div>
                    </div>
                    <div style="font-size:11px; color:#304060; margin-top:8px;">{tip}</div>
                </div>
            """, unsafe_allow_html=True)

    # ── Categoria Breakdown ──────────────────────────────────────────────
    if not df_desp.empty and "Categoria" in df_desp.columns:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-title" style="padding-left:4px;">DESPESAS POR CATEGORIA (ACUMULADO)</div>', unsafe_allow_html=True)
        cat_totals  = df_desp[df_desp["Categoria"] != "_total_"].groupby("Categoria")["Saidas"].sum().sort_values(ascending=False)
        total_saidas = cat_totals.sum()
        if total_saidas > 0:
            cat_cols = st.columns(min(len(cat_totals), 4))
            for idx, (cat, val) in enumerate(cat_totals.items()):
                color = CAT_COLORS.get(cat, "#8899BB")
                pct   = (val/total_saidas*100)
                with cat_cols[idx % 4]:
                    st.markdown(f"""
                        <div class="card" style="text-align:center; border-top:2px solid {color}; padding:12px 16px;">
                            <div style="font-size:10px; color:#556080; letter-spacing:2px;">{cat.upper()}</div>
                            <div style="font-size:1.1em; font-weight:700; font-family:'Space Mono',monospace; color:{color}; margin-top:6px;">{val:,.0f}€</div>
                            <div style="font-size:11px; color:#304060; margin-top:3px;">{pct:.1f}%</div>
                        </div>
                    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Add Record ──────────────────────────────────────────────────────
    with st.expander("Registar Mês"):
        mf  = st.selectbox("Mês", get_months(), key="m_flx")
        sal = st.number_input("Salário / Total Entradas (€)", min_value=0.0, format="%.2f", key="sal")

        st.markdown("<div style='font-size:12px; color:#556080; margin:14px 0 6px; letter-spacing:1px;'>DESPESAS POR CATEGORIA</div>", unsafe_allow_html=True)
        cat_vals = {}
        c1_d,c2_d = st.columns(2)
        for idx, cat in enumerate(DESPESA_CATS):
            col = c1_d if idx % 2 == 0 else c2_d
            cat_vals[cat] = col.number_input(f"{cat} (€)", min_value=0.0, format="%.2f", key=f"cat_{cat}")

        total_desp = sum(cat_vals.values())
        sobra      = sal - total_desp
        taxa_p     = (sobra/sal*100) if sal > 0 else 0
        tc         = "#00E87A" if sobra >= 0 else "#FF4D6A"

        st.markdown(f"""
            <div style="background:#0D1219; border-radius:8px; padding:14px 16px; margin-top:12px; border:1px solid #1E2A3E;">
                <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:6px;">
                    <span style="color:#8899BB;">Total Despesas</span>
                    <span style="font-family:'Space Mono',monospace; color:#FF4D6A;">{total_desp:,.2f} €</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:15px; font-weight:700;">
                    <span style="color:#AABBDD;">Poupança do Mês</span>
                    <span style="font-family:'Space Mono',monospace; color:{tc};">{sobra:,.2f} € ({taxa_p:.1f}%)</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("GRAVAR FLUXO"):
            # Save summary to poupanca.csv
            summary = pd.DataFrame([{"Mês":mf,"Entradas":sal,"Saidas":total_desp}])
            save_db(pd.concat([df_f, summary], ignore_index=True), "poupanca")
            # Save category breakdown to despesas.csv
            cat_rows = [{"Mês":mf,"Categoria":cat,"Saidas":val} for cat, val in cat_vals.items()]
            save_db(pd.concat([df_desp, pd.DataFrame(cat_rows)], ignore_index=True), "despesas")
            st.cache_data.clear()
            st.success("✅  Gravado.")
            st.rerun()

    # ── History ──────────────────────────────────────────────────────────
    for i, r in df_f.iterrows():
        net  = float(r["Entradas"]) - float(r["Saidas"])
        taxa = (net/float(r["Entradas"])*100) if float(r["Entradas"]) > 0 else 0
        nc   = "#00E87A" if net >= 0 else "#FF4D6A"

        # category detail for this month
        cat_detail = ""
        if not df_desp.empty and "Categoria" in df_desp.columns:
            mc = df_desp[(df_desp["Mês"]==r["Mês"]) & (df_desp["Categoria"] != "_total_")]
            if not mc.empty:
                parts = [f'{row["Categoria"]}: {float(row["Saidas"]):,.0f}€' for _, row in mc.iterrows() if float(row["Saidas"]) > 0]
                cat_detail = " · ".join(parts[:5])

        c_card, c_del = st.columns([11,1])
        with c_card:
            st.markdown(f"""
                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-family:'Space Mono',monospace; font-weight:700; color:#AABBDD;">{r["Mês"]}</span>
                        <span style="color:{nc}; font-family:'Space Mono',monospace; font-weight:700;">{net:,.2f} € poupados ({taxa:.1f}%)</span>
                    </div>
                    <div style="font-size:11px; color:#304060; margin-top:5px;">
                        Entradas: {float(r["Entradas"]):,.0f}€ · Saídas: {float(r["Saidas"]):,.0f}€
                    </div>
                    {'<div style="font-size:11px; color:#253040; margin-top:3px;">'+cat_detail+'</div>' if cat_detail else ''}
                </div>
            """, unsafe_allow_html=True)
        with c_del:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑", key=f"df_{i}"):
                save_db(df_f.drop(i).reset_index(drop=True), "poupanca")
                st.rerun()

# ══════════════════════════════════════════════════════════════════
# TAB 3 — OBJETIVOS
# ══════════════════════════════════════════════════════════════════
with tab3:
    df_obj  = load_db("objetivos")
    df_p2   = load_db("patrimonio")
    pat_now = float(df_p2["Total"].iloc[0]) if not df_p2.empty else 0
    df_fx   = load_db("poupanca")
    avg_sav = 0
    if not df_fx.empty and "Entradas" in df_fx.columns:
        avg_sav = float((df_fx["Entradas"] - df_fx["Saidas"]).mean())

    st.markdown(f"""
        <div style="text-align:center; padding:16px 0 24px;">
            <div style="font-size:11px; color:#304060; letter-spacing:4px; font-family:'Space Mono',monospace; margin-bottom:8px;">PATRIMÓNIO ATUAL</div>
            <div style="font-size:2em; font-weight:700; color:#00E87A; font-family:'Space Mono',monospace;">{pat_now:,.0f} €</div>
            {'<div style="font-size:12px; color:#556080; margin-top:6px;">Poupança média: '+f'{avg_sav:,.0f}€/mês</div>' if avg_sav > 0 else ''}
        </div>
    """, unsafe_allow_html=True)

    with st.expander("Definir Novo Objetivo"):
        o_nome = st.text_input("Nome do Objetivo", placeholder="ex: 100K Club, Casa, Reforma Antecipada...")
        oc1,oc2 = st.columns(2)
        o_meta = oc1.number_input("Meta (€)", min_value=0.0, format="%.0f")
        o_ano  = oc2.number_input("Ano Alvo", min_value=2024, max_value=2060, value=datetime.now().year+3, step=1)
        o_emoji = st.selectbox("Ícone", ["🎯","🏠","🚀","🏖️","💎","🏎️","📚","💰","🌍","🔥"])
        if st.button("CRIAR OBJETIVO"):
            if o_nome and o_meta > 0:
                row = pd.DataFrame([{"Nome":o_nome,"Meta":o_meta,"Ano":int(o_ano),"Emoji":o_emoji}])
                save_db(pd.concat([df_obj, row], ignore_index=True), "objetivos")
                st.success("✅  Objetivo criado!")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if not df_obj.empty:
        for i, obj in df_obj.iterrows():
            meta      = float(obj["Meta"])
            prog      = min(pat_now/meta*100, 100) if meta > 0 else 0
            restante  = max(meta - pat_now, 0)
            anos_left = int(obj["Ano"]) - datetime.now().year
            months_needed = int(restante/avg_sav) if avg_sav > 0 and restante > 0 else None
            on_track  = months_needed is not None and months_needed <= anos_left*12

            bc = "#00E87A" if prog >= 75 else "#FFD060" if prog >= 40 else "#00BFFF"
            if prog >= 100: bc = "#00E87A"

            if prog >= 100:
                track = "🎉 OBJETIVO ATINGIDO!"
            elif months_needed is not None:
                track = f"✅ No caminho certo — aprox. {months_needed} meses" if on_track else f"⚠️ Ao ritmo atual: {months_needed} meses (objetivo: {anos_left*12})"
            else:
                track = ""

            c_obj, c_del = st.columns([11,1])
            with c_obj:
                st.markdown(f"""
                    <div class="card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                            <div>
                                <span style="font-size:1.3em;">{obj["Emoji"]}</span>
                                <span style="font-size:1.05em; font-weight:700; color:#DDE3EF; margin-left:8px;">{obj["Nome"]}</span>
                                <span style="font-size:11px; color:#304060; margin-left:8px;">até {int(obj["Ano"])}</span>
                            </div>
                            <span style="font-family:'Space Mono',monospace; font-weight:700; color:{bc}; font-size:1.1em;">{prog:.1f}%</span>
                        </div>
                        <div style="background:#111720; border-radius:20px; height:10px; margin-bottom:10px;">
                            <div style="width:{prog:.1f}%; height:10px; border-radius:20px; background:{bc};"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:12px; color:#556080;">
                            <span>{pat_now:,.0f}€ atual</span>
                            <span style="color:#304060;">faltam {restante:,.0f}€</span>
                            <span>{meta:,.0f}€ meta</span>
                        </div>
                        {'<div style="font-size:12px; color:#556080; margin-top:8px;">'+track+'</div>' if track else ''}
                    </div>
                """, unsafe_allow_html=True)
            with c_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑", key=f"do_{i}"):
                    save_db(df_obj.drop(i).reset_index(drop=True), "objetivos")
                    st.rerun()
    else:
        st.markdown("""
            <div style="text-align:center; padding:50px 20px; color:#253040;">
                <div style="font-size:2.5em; margin-bottom:12px;">🎯</div>
                <div style="font-family:'Space Mono',monospace; font-size:13px; letter-spacing:2px;">SEM OBJETIVOS DEFINIDOS</div>
                <div style="font-size:12px; margin-top:8px; color:#1E2A3E;">Define uma meta financeira para acompanhar o progresso</div>
            </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# TAB 4 — ANÁLISE DE AÇÕES
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("<div style='margin-bottom:6px; font-size:12px; color:#304060; letter-spacing:2px;'>TICKER SYMBOL</div>", unsafe_allow_html=True)
    col_inp, col_btn = st.columns([5,1])
    with col_inp:
        ticker_input = st.text_input(
            label="ticker", label_visibility="collapsed",
            placeholder="ex: AAPL   GOOGL   NVDA   MSFT   EDP.LS",
            key="ticker_field"
        ).strip().upper()
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        do_scan = st.button("▶  SCAN", key="scan_btn")

    if "active_ticker" not in st.session_state:
        st.session_state.active_ticker = ""
    if do_scan and ticker_input:
        st.session_state.active_ticker = ticker_input

    ticker_to_use = st.session_state.active_ticker

    if ticker_to_use:
        with st.spinner(f"A carregar {ticker_to_use}..."):
            info, err = fetch_info(ticker_to_use)

        if err:
            st.error(f"❌  {err}")
            st.info("💡  Confirma o ticker em finance.yahoo.com — Ex: GOOGL, AAPL, EDP.LS")
        else:
            price    = sg(info,"currentPrice","regularMarketPrice","previousClose",default=0)
            sector   = info.get("sector","")   or "N/A"
            industry = info.get("industry","") or "N/A"
            name     = info.get("longName") or info.get("shortName","") or ticker_to_use
            currency = info.get("currency","USD")
            exch     = info.get("exchange","") or ""

            st.markdown(f"""
                <div style="margin:8px 0 18px;">
                    <div style="font-size:1.45em; font-weight:700;">
                        {name} <span class="badge">{sector}</span> <span class="badge">{industry[:35]}</span>
                    </div>
                    <div style="font-size:11px; color:#304060; margin-top:5px; font-family:'Space Mono',monospace;">
                        {ticker_to_use} · {exch} · {currency}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            iv_res  = intrinsic_value(info, sector)
            iv      = iv_res["iv"]
            upside  = ((iv/price)-1)*100 if price > 0 and iv > 0 else 0
            checks, score, n_checks, verdict, vcolor, vbg, vborder, vdesc = run_checklist(info, iv, price)

            st.markdown(f"""
                <div class="verdict" style="background:{vbg}; border:1px solid {vborder}; color:{vcolor};">
                    {verdict} · {score}/{n_checks}
                </div>
                <div style="background:#0D1219; border-radius:8px; border:1px solid #151C28; padding:12px 18px; margin-bottom:18px; font-size:13px; color:#8899BB;">
                    {vdesc}
                </div>
            """, unsafe_allow_html=True)

            m1,m2,m3,m4 = st.columns(4)
            m1.metric("Preço Atual",    f"{price:.2f} {currency}")
            m2.metric("Valor Intrínseco", f"{iv:.2f} {currency}" if iv>0 else "N/A",
                                           delta=f"{upside:+.1f}%" if iv>0 else None)
            m3.metric("Metodologia",    iv_res["label"])
            m4.metric("Score",          f"{score}/{n_checks}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Checklist by category
            categories = ["Crescimento","Rentabilidade","Qualidade","Valuation","Risco"]
            cols = st.columns(2)
            col_idx = 0
            for cat in categories:
                cat_checks = [(l,p,v) for c,l,p,v in checks if c==cat]
                if not cat_checks: continue
                cs = sum(1 for _,p,_ in cat_checks if p)
                ct = len(cat_checks)
                cc = "#00E87A" if cs==ct else "#FFD060" if cs>0 else "#FF4D6A"
                html = f'<div class="card"><div class="sec-title">{cat} <span style="color:{cc};">{cs}/{ct}</span></div>'
                for label,passed,val in cat_checks:
                    ic = "✅" if passed else "❌"
                    vc = "#00E87A" if passed else "#FF4D6A"
                    html += f'<div class="mrow"><span class="label">{label}</span><span class="val" style="color:{vc};">{val} {ic}</span></div>'
                html += '</div>'
                with cols[col_idx % 2]:
                    st.markdown(html, unsafe_allow_html=True)
                col_idx += 1

            # Valuation breakdown
            if iv_res["rows"]:
                st.markdown("<br>", unsafe_allow_html=True)
                html = f'<div class="card"><div class="sec-title">Valuation Breakdown — {iv_res["label"]}</div>'
                for k,v in iv_res["rows"]:
                    html += f'<div class="mrow"><span class="label">{k}</span><span class="val blue">{v}</span></div>'
                if iv > 0:
                    uc = "#00E87A" if upside>15 else "#FFD060" if upside>-10 else "#FF4D6A"
                    html += f'<div class="mrow" style="margin-top:4px;"><span style="color:#AABBDD; font-weight:600;">Upside / Downside</span><span class="val" style="color:{uc}; font-size:15px;">{upside:+.1f}%</span></div>'
                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)

            # All metrics
            with st.expander("Todas as Métricas"):
                def fmtB(v): return f"${float(v)/1e9:.2f}B" if v else "N/A"
                def fmtP(v): return f"{float(v)*100:.1f}%" if v else "N/A"
                def fmtX(v): return f"{float(v):.2f}x" if v else "N/A"
                def fmtV(v): return f"{float(v):.2f}" if v else "N/A"

                all_m = [
                    ("── PREÇO & MERCADO","",""),
                    ("Preço Atual",         fmtV(price),""),
                    ("Market Cap",          fmtB(info.get("marketCap",0)),""),
                    ("52W High",            fmtV(sg(info,"fiftyTwoWeekHigh",default=0)),""),
                    ("52W Low",             fmtV(sg(info,"fiftyTwoWeekLow",default=0)),""),
                    ("EPS TTM",             fmtV(sg(info,"trailingEps",default=0)),""),
                    ("EPS Forward",         fmtV(sg(info,"forwardEps",default=0)),""),
                    ("── VALUATION","",""),
                    ("P/E TTM",             fmtX(sg(info,"trailingPE",default=0)),""),
                    ("P/E Forward",         fmtX(sg(info,"forwardPE",default=0)),""),
                    ("PEG Ratio",           fmtV(sg(info,"pegRatio",default=0)),""),
                    ("P/S Ratio",           fmtX(sg(info,"priceToSalesTrailing12Months",default=0)),""),
                    ("P/B Ratio",           fmtX(sg(info,"priceToBook",default=0)),""),
                    ("EV/EBITDA",           fmtX(sg(info,"enterpriseToEbitda",default=0)),""),
                    ("EV/Revenue",          fmtX(sg(info,"enterpriseToRevenue",default=0)),""),
                    ("── CRESCIMENTO","",""),
                    ("Receita YoY",         fmtP(sg(info,"revenueGrowth",default=0)),""),
                    ("Lucro YoY",           fmtP(sg(info,"earningsGrowth",default=0)),""),
                    ("── RENTABILIDADE","",""),
                    ("Margem Bruta",        fmtP(sg(info,"grossMargins",default=0)),""),
                    ("Margem Líquida",      fmtP(sg(info,"profitMargins",default=0)),""),
                    ("ROE",                 fmtP(sg(info,"returnOnEquity",default=0)),""),
                    ("ROA",                 fmtP(sg(info,"returnOnAssets",default=0)),""),
                    ("── BALANÇO","",""),
                    ("Receita Total",       fmtB(info.get("totalRevenue",0)),""),
                    ("EBITDA",              fmtB(info.get("ebitda",0)),""),
                    ("Lucro Líquido",       fmtB(info.get("netIncomeToCommon",0)),""),
                    ("Free Cash Flow",      fmtB(info.get("freeCashflow",0)),""),
                    ("Caixa Total",         fmtB(info.get("totalCash",0)),""),
                    ("Dívida Total",        fmtB(info.get("totalDebt",0)),""),
                    ("Current Ratio",       fmtX(sg(info,"currentRatio",default=0)),""),
                    ("── RISCO & DIVIDENDO","",""),
                    ("Beta",                fmtV(sg(info,"beta",default=0)),""),
                    ("Dividend Yield",      fmtP(sg(info,"dividendYield",default=0)),""),
                    ("── ANALISTAS","",""),
                    ("Preço Alvo Médio",    fmtV(sg(info,"targetMeanPrice",default=0)),""),
                    ("Upside p/ Alvo",      f"{((sg(info,'targetMeanPrice',default=0)/price)-1)*100:+.1f}%" if price and sg(info,'targetMeanPrice',default=0) else "N/A",""),
                    ("Recomendação",        (info.get("recommendationKey","") or "N/A").upper(),""),
                ]
                c1,c2 = st.columns(2)
                for idx,(k,v,_) in enumerate(all_m):
                    if k.startswith("──"):
                        for col in [c1,c2]:
                            col.markdown(f'<div style="font-size:10px; letter-spacing:3px; color:#253040; margin:14px 0 4px; font-family:Space Mono,monospace;">{k}</div>', unsafe_allow_html=True)
                    else:
                        (c1 if idx%2==0 else c2).markdown(
                            f'<div class="mrow"><span class="label">{k}</span><span class="val">{v}</span></div>',
                            unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="text-align:center; padding:60px 20px; color:#253040;">
                <div style="font-size:2.5em; margin-bottom:16px;">🔬</div>
                <div style="font-family:'Space Mono',monospace; font-size:14px; letter-spacing:2px;">INSERE UM TICKER E CLICA SCAN</div>
                <div style="font-size:12px; margin-top:10px; color:#1E2A3E;">AAPL · GOOGL · NVDA · MSFT · AMZN · EDP.LS</div>
            </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
    <div style="text-align:center; margin-top:40px; padding:16px 0; border-top:1px solid #101520;
        font-size:10px; color:#1E2A3E; font-family:'Space Mono',monospace; letter-spacing:3px;">
        FARIA QUANT TERMINAL · FOR PERSONAL USE ONLY
    </div>
""", unsafe_allow_html=True)

