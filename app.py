import streamlit as st
import streamlit.components.v1 as components  # noqa: F401
import pandas as pd
import os
from datetime import datetime
import yfinance as yf
import numpy as np

st.set_page_config(page_title="F|QUANT", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")

# ══════════════════════════════════════════════════════════════════════
# DATABASE LAYER
# ══════════════════════════════════════════════════════════════════════
DATA_DIR = "dados"
os.makedirs(DATA_DIR, exist_ok=True)

PT_MONTHS = {"Jan":1,"Fev":2,"Mar":3,"Abr":4,"Mai":5,"Jun":6,
             "Jul":7,"Ago":8,"Set":9,"Out":10,"Nov":11,"Dez":12}

def parse_mes(m):
    try:
        p = str(m).strip().split()
        return (int(p[1]) + 2000) * 100 + PT_MONTHS.get(p[0], 0)
    except:
        return 0

def save_db(df, name):
    if "Mês" in df.columns and not df.empty:
        try:
            df = df.copy()
            df["_s"] = df["Mês"].apply(parse_mes)
            df = df.sort_values("_s", ascending=False).drop(columns=["_s"])
        except:
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
        df["_s"] = df["Mês"].apply(parse_mes)
        df = df.sort_values("_s", ascending=False).drop(columns=["_s"])
    except:
        pass
    return df.reset_index(drop=True)

def get_months():
    n = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    y = datetime.now().year % 100
    return [f"{m} {y}" for m in reversed(n)] + [f"{m} {y-1}" for m in reversed(n)]

DESPESA_CATS = ["Habitação","Alimentação","Transportes","Saúde","Lazer","Subscrições","Educação","Outros"]
CAT_ICONS = {"Habitação":"🏠","Alimentação":"🍽","Transportes":"🚗","Saúde":"💊","Lazer":"🎮","Subscrições":"📱","Educação":"📚","Outros":"📦"}
CAT_COLORS = {"Habitação":"#2563EB","Alimentação":"#059669","Transportes":"#D97706","Saúde":"#EC4899","Lazer":"#7C3AED","Subscrições":"#0891B2","Educação":"#16A34A","Outros":"#6B7280"}

# ══════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════
_defaults = {
    "auth": False,
    "pin_input": "",
    "pin_error": False,
    "edit_pat": None,
    "edit_flx": None,
    "ticker": "",
    "treino_edit": False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

week_key = f"w{datetime.now().isocalendar()[1]}"
if week_key not in st.session_state:
    st.session_state[week_key] = {}

# ══════════════════════════════════════════════════════════════════════
# FINANCE ENGINE
# ══════════════════════════════════════════════════════════════════════
def sg(d, *keys, default=0):
    for k in keys:
        v = d.get(k)
        if v is not None and v != "" and not (isinstance(v, float) and np.isnan(v)):
            try:
                f = float(v)
                if f != 0:
                    return f
            except:
                return v
    return default

@st.cache_data(ttl=300, show_spinner=False)
def fetch_info(symbol):
    try:
        t = yf.Ticker(symbol); info = t.info or {}
        try:
            fi = t.fast_info
            p = getattr(fi,"last_price",None) or getattr(fi,"regular_market_price",None) or info.get("currentPrice") or info.get("previousClose")
            if p: info["currentPrice"] = float(p)
        except: pass
        if not info.get("currentPrice"):
            h = t.history(period="5d")
            if not h.empty: info["currentPrice"] = float(h["Close"].iloc[-1])
        if not info.get("currentPrice",0) and not (info.get("longName") or info.get("shortName")):
            return None, f"Ticker **{symbol}** não encontrado."
        if not (info.get("longName") or info.get("shortName")):
            info["longName"] = symbol
        return info, None
    except Exception as e:
        return None, f"Erro: {str(e)}"

SECTOR_CFG = {
    "Technology":             {"method":"dcf",      "dr":.10,"tg":.03, "cap":.25,"label":"DCF — Free Cash Flow"},
    "Communication Services": {"method":"dcf",      "dr":.10,"tg":.025,"cap":.20,"label":"DCF — Free Cash Flow"},
    "Healthcare":             {"method":"dcf",      "dr":.09,"tg":.025,"cap":.18,"label":"DCF — Free Cash Flow"},
    "Consumer Cyclical":      {"method":"ev_ebitda","multiple":14, "label":"EV / EBITDA"},
    "Consumer Defensive":     {"method":"pe_rel",   "base_pe":22, "label":"P/E Relativo"},
    "Financial Services":     {"method":"pb_roe",   "label":"P/B + ROE"},
    "Industrials":            {"method":"ev_ebitda","multiple":11, "label":"EV / EBITDA"},
    "Basic Materials":        {"method":"ev_ebitda","multiple":8,  "label":"EV / EBITDA"},
    "Energy":                 {"method":"ev_ebitda","multiple":7,  "label":"EV / EBITDA"},
    "Utilities":              {"method":"ddm",      "label":"Gordon Growth"},
    "Real Estate":            {"method":"ffo",      "label":"P / FFO"},
}

def intrinsic_value(info, sector):
    cfg = SECTOR_CFG.get(sector, {"method":"dcf","dr":.10,"tg":.025,"cap":.15,"label":"DCF"})
    m = cfg["method"]; sh = sg(info,"sharesOutstanding",default=1)
    r = {"iv":0,"label":cfg["label"],"rows":[]}; R = r["rows"]
    try:
        if m == "dcf":
            dr,tg,cap = cfg.get("dr",.10), cfg.get("tg",.025), cfg.get("cap",.15)
            fcf = sg(info,"freeCashflow",default=0)
            if fcf<=0: fcf = sg(info,"operatingCashflow",default=0)-abs(sg(info,"capitalExpenditures",default=0))
            if fcf<=0: fcf = sg(info,"netIncomeToCommon",default=0)
            if fcf<=0 or sh<=0: return r
            g = min(max((sg(info,"revenueGrowth",default=.05)+sg(info,"earningsGrowth",default=.05))/2,.03),cap)
            pv = sum([(fcf*(1+g)**i)/(1+dr)**i for i in range(1,6)])
            tv = (fcf*(1+g)**5*(1+tg))/(dr-tg)
            r["iv"] = max((pv+tv/(1+dr)**5)/sh,0)
            R += [("FCF",f"${fcf/1e9:.2f}B"),("Crescimento",f"{g*100:.1f}%"),("Desconto",f"{dr*100:.0f}%"),("Terminal g",f"{tg*100:.1f}%")]
        elif m == "ev_ebitda":
            eb = sg(info,"ebitda",default=0)
            if eb<=0 or sh<=0: return r
            mult = cfg.get("multiple",12)
            r["iv"] = max((eb*mult-sg(info,"totalDebt",default=0)+sg(info,"totalCash",default=0))/sh,0)
            R += [("EBITDA",f"${eb/1e9:.2f}B"),("Múltiplo",f"{mult}×")]
        elif m == "pe_rel":
            eps = sg(info,"trailingEps","forwardEps",default=0)
            if eps<=0: return r
            pe = cfg.get("base_pe",20)*(1+sg(info,"revenueGrowth",default=.04))
            r["iv"] = max(eps*pe,0); R += [("EPS",f"${eps:.2f}"),("P/E adj",f"{pe:.1f}×")]
        elif m == "pb_roe":
            roe=sg(info,"returnOnEquity",default=.10); bv=sg(info,"bookValue",default=0)
            if bv<=0: return r
            r["iv"] = max(bv*max(roe/.10,.5),0); R += [("Book Value",f"${bv:.2f}"),("ROE",f"{roe*100:.1f}%")]
        elif m == "ddm":
            d=sg(info,"dividendRate",default=0)
            if d<=0: return r
            r["iv"] = max((d*1.025)/(0.07-0.025),0); R += [("Dividendo",f"${d:.2f}"),("Modelo","Gordon Growth")]
        elif m == "ffo":
            ni=sg(info,"netIncomeToCommon",default=0); ffo=ni+sg(info,"totalAssets",default=0)*.02
            if ffo<=0 or sh<=0: return r
            r["iv"] = max(ffo/sh*16,0); R += [("FFO/Share",f"${ffo/sh:.2f}"),("P/FFO","16×")]
    except Exception as e:
        R.append(("Erro",str(e)))
    return r

def run_checklist(info, iv, price):
    rg=sg(info,"revenueGrowth",default=0); eg=sg(info,"earningsGrowth",default=0)
    mg=sg(info,"profitMargins",default=0); gm=sg(info,"grossMargins",default=0)
    roe=sg(info,"returnOnEquity",default=0); roa=sg(info,"returnOnAssets",default=0)
    cfo=sg(info,"operatingCashflow",default=0); ni=sg(info,"netIncomeToCommon",default=1)
    de=sg(info,"debtToEquity",default=0); cr=sg(info,"currentRatio",default=0)
    pe=sg(info,"trailingPE",default=0); peg=sg(info,"pegRatio",default=0)
    beta=sg(info,"beta",default=1)
    up=((iv/price)-1)*100 if price>0 and iv>0 else 0
    cn=cfo/ni if ni!=0 else 0
    checks=[
        ("Crescimento","Receita YoY > 7%",    rg>0.07,  f"{rg*100:.1f}%"),
        ("Crescimento","Lucro YoY > 9%",      eg>0.09,  f"{eg*100:.1f}%"),
        ("Margem",     "Margem Líq. > 10%",   mg>0.10,  f"{mg*100:.1f}%"),
        ("Margem",     "Margem Bruta > 40%",  gm>0.40,  f"{gm*100:.1f}%"),
        ("Retorno",    "ROE > 15%",           roe>0.15, f"{roe*100:.1f}%"),
        ("Retorno",    "ROA > 5%",            roa>0.05, f"{roa*100:.1f}%"),
        ("Qualidade",  "CFO/NetInc > 80%",    cn>0.80,  f"{cn*100:.1f}%"),
        ("Qualidade",  "Dívida/Eq. < 1.5",    0<de<1.5 if de>0 else de==0, f"{de:.2f}×" if de>0 else "N/A"),
        ("Qualidade",  "Current Ratio > 1.2",  cr>1.2,  f"{cr:.2f}×"),
        ("Valuation",  "P/E < 30",            0<pe<30,  f"{pe:.1f}×" if pe>0 else "N/A"),
        ("Valuation",  "PEG < 1.5",           0<peg<1.5,f"{peg:.2f}" if peg>0 else "N/A"),
        ("Valuation",  "Upside > 15%",        up>15,    f"{up:+.1f}%" if iv>0 else "N/A"),
        ("Risco",      "Beta < 1.5",          beta<1.5, f"{beta:.2f}"),
    ]
    score=sum(1 for _,_,p,_ in checks if p); n=len(checks)
    qs=sum(1 for c,_,p,_ in checks if c in ("Margem","Retorno","Qualidade") and p)
    vs=sum(1 for c,_,p,_ in checks if c=="Valuation" and p)
    if score>=10 and vs>=2:
        return checks,score,n,"APROVADA","#059669","#ECFDF5","#6EE7B7","✓","Empresa de alta qualidade com valuation atrativo."
    elif score>=7 and qs>=3:
        return checks,score,n,"INDECISA","#D97706","#FFFBEB","#FCD34D","~","Boas fundações. Alguns critérios em falta."
    else:
        return checks,score,n,"REJEITADA","#DC2626","#FEF2F2","#FCA5A5","✕","Não cumpre os critérios mínimos."

# ══════════════════════════════════════════════════════════════════════
# TRAINING PLAN
# ══════════════════════════════════════════════════════════════════════
TREINO = {
    "Segunda": {
        "sub": "Base & Estabilidade", "cor": "#2563EB",
        "warmup": ["Círculos de anca","Rotação torácica","10 agachamentos lentos","10 scapular push-ups"],
        "ex": [
            ("Goblet Squat",       "3 × 10-12", "Progressão lenta · controlo e profundidade"),
            ("Romanian Deadlift",  "3 × 10",    "Kettlebell ou barra · alongamento posterior"),
            ("Passadas Atrás",     "3 × 8 cada","Excelente para estabilidade da anca"),
            ("Prancha Frontal",    "3 × 30-45s",""),
            ("Side Plank",         "2 × cada lado",""),
        ],
        "nota": "Reforça anca e core — essencial para a tua estrutura."
    },
    "Quarta": {
        "sub": "Ombros & Estabilidade Superior", "cor": "#7C3AED",
        "warmup": ["Mobilidade ombro","Elástico — rotação externa"],
        "ex": [
            ("Overhead Press",      "3 × 10",    "Halter ou máquina · controlado"),
            ("Elevações Laterais",  "3 × 12-15", ""),
            ("Face Pulls",          "3 × 12-15", "Fundamental para proteger o ombro"),
            ("Remo Unilateral",     "3 × 10 cada","Ótimo para estabilidade do tronco"),
            ("Hiperextensão",       "3 × 12",    ""),
        ],
        "nota": ""
    },
    "Sexta": {
        "sub": "Peito & Costas — Principal", "cor": "#059669",
        "warmup": [],
        "ex": [
            ("Chest Press",                "3 × 12/10/8", "Progressão de carga"),
            ("Remo Máquina",               "3 × 12/10/8", ""),
            ("Press Inclinado",            "3 × 10/8/6",  ""),
            ("Dorsal Máquina / Barras",    "3 × 10-12",   ""),
            ("Finisher",                   "Flexões ou 5-8 barras","Opcional"),
        ],
        "nota": "Podes usar a pirâmide progressiva aqui."
    },
}

# ══════════════════════════════════════════════════════════════════════
# PIN AUTH — Auto-submit + error feedback
# ══════════════════════════════════════════════════════════════════════
CORRECT_PIN = "1214"

qp = st.query_params
if not st.session_state.auth and "pin" in qp:
    submitted = qp["pin"]
    st.query_params.clear()
    if submitted == CORRECT_PIN:
        st.session_state.auth = True
        st.session_state.pin_input = ""
        st.session_state.pin_error = False
    else:
        st.session_state.pin_error = True
        st.session_state.pin_input = ""
    st.rerun()

if not st.session_state.auth:
    err = st.session_state.pin_error

    pin_html = f"""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                min-height:580px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
                background:#0a0a0a;color:#fff;user-select:none;">

      <div style="font-size:28px;font-weight:700;letter-spacing:2px;margin-bottom:8px;">F|QUANT</div>
      <div style="font-size:13px;color:#888;margin-bottom:32px;">Introduce o teu PIN para continuar</div>

      <div id="dots" style="display:flex;gap:16px;margin-bottom:10px;">
        <span class="dot"></span><span class="dot"></span><span class="dot"></span><span class="dot"></span>
      </div>

      <div id="error" style="color:#ef4444;font-size:13px;height:24px;margin-bottom:12px;
           opacity:{'1' if err else '0'};transition:opacity .3s;">
        PIN incorreto. Tenta novamente.
      </div>

      <div style="display:grid;grid-template-columns:repeat(3,80px);gap:12px;">
        <button onclick="addDigit('1')" class="key"><span style="font-size:24px;">1</span></button>
        <button onclick="addDigit('2')" class="key"><span style="font-size:24px;">2</span><br><span style="font-size:9px;color:#888;">ABC</span></button>
        <button onclick="addDigit('3')" class="key"><span style="font-size:24px;">3</span><br><span style="font-size:9px;color:#888;">DEF</span></button>
        <button onclick="addDigit('4')" class="key"><span style="font-size:24px;">4</span><br><span style="font-size:9px;color:#888;">GHI</span></button>
        <button onclick="addDigit('5')" class="key"><span style="font-size:24px;">5</span><br><span style="font-size:9px;color:#888;">JKL</span></button>
        <button onclick="addDigit('6')" class="key"><span style="font-size:24px;">6</span><br><span style="font-size:9px;color:#888;">MNO</span></button>
        <button onclick="addDigit('7')" class="key"><span style="font-size:24px;">7</span><br><span style="font-size:9px;color:#888;">PQRS</span></button>
        <button onclick="addDigit('8')" class="key"><span style="font-size:24px;">8</span><br><span style="font-size:9px;color:#888;">TUV</span></button>
        <button onclick="addDigit('9')" class="key"><span style="font-size:24px;">9</span><br><span style="font-size:9px;color:#888;">WXYZ</span></button>
        <div></div>
        <button onclick="addDigit('0')" class="key"><span style="font-size:24px;">0</span></button>
        <button onclick="delDigit()" class="key" style="font-size:20px;">⌫</button>
      </div>
    </div>

    <style>
      .dot {{
        width:14px;height:14px;border-radius:50%;
        border:2px solid #555;background:transparent;
        transition:background .15s,border-color .15s;
      }}
      .dot.filled {{ background:#fff;border-color:#fff; }}
      .dot.wrong {{ background:#ef4444;border-color:#ef4444; }}
      .key {{
        width:80px;height:80px;border-radius:50%;border:1px solid #333;
        background:#1a1a1a;color:#fff;font-weight:500;
        cursor:pointer;transition:background .15s;
        display:flex;flex-direction:column;align-items:center;justify-content:center;
        line-height:1.2;
      }}
      .key:active {{ background:#333; }}
    </style>

    <script>
      let pin = "";
      let submitting = false;
      const dots = document.querySelectorAll(".dot");
      const errEl = document.getElementById("error");

      function updateDots() {{
        dots.forEach((d, i) => {{
          d.classList.toggle("filled", i < pin.length);
          d.classList.remove("wrong");
        }});
      }}

      function addDigit(d) {{
        if (pin.length >= 4 || submitting) return;
        pin += d;
        errEl.style.opacity = "0";
        updateDots();
        if (pin.length === 4) {{
          submitting = true;
          setTimeout(() => {{
            window.location.href = window.location.pathname + "?pin=" + pin;
          }}, 250);
        }}
      }}

      function delDigit() {{
        if (submitting) return;
        pin = pin.slice(0, -1);
        updateDots();
      }}

      // Animação de erro nos dots
      if ({'true' if err else 'false'}) {{
        dots.forEach(d => d.classList.add("wrong"));
        setTimeout(() => dots.forEach(d => d.classList.remove("wrong")), 800);
      }}
    </script>
    """

    st.components.v1.html(pin_html, height=620, scrolling=False)
    st.stop()

# ══════════════════════════════════════════════════════════════════════
# APP SHELL
# ══════════════════════════════════════════════════════════════════════
now = datetime.now()
day_names = {0:"Segunda",1:"Terça",2:"Quarta",3:"Quinta",4:"Sexta",5:"Sábado",6:"Domingo"}
today_name = day_names[now.weekday()]

st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;padding:16px 0;border-bottom:1px solid #1a1a1a;margin-bottom:24px;">
  <div style="font-size:22px;font-weight:700;letter-spacing:2px;">F|QUANT</div>
  <div style="font-size:13px;color:#888;">{today_name}, {now.strftime("%-d %b")}</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Património", "Fluxo", "Treino", "Análise"])

# ══════════════════════════════════════════════════════════════════════
# ▌TAB 1 — PATRIMÓNIO
# ══════════════════════════════════════════════════════════════════════
with tab1:
    df_p = load_db("patrimonio")

    if not df_p.empty:
        tot = float(df_p["Total"].iloc[0])
        prev = float(df_p["Total"].iloc[1]) if len(df_p) > 1 else tot
        dlt = tot - prev
        dpct = (dlt / prev * 100) if prev > 0 else 0
        sign = "+" if dlt >= 0 else ""
        arrow = "↑" if dlt >= 0 else "↓"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0a0a0a,#1a1a2e);border-radius:16px;padding:32px;margin-bottom:24px;">
          <div style="font-size:13px;color:#888;">Total Investido</div>
          <div style="font-size:42px;font-weight:700;margin:8px 0;">{tot:,.0f}<span style="font-size:18px;color:#888;"> EUR</span></div>
          <div style="font-size:13px;color:{'#059669' if dlt>=0 else '#DC2626'};">
            {arrow} {sign}{dlt:,.0f} €  ·  {sign}{dpct:.1f}% vs mês anterior
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="font-size:16px;font-weight:600;margin-bottom:12px;">Carteiras</div>', unsafe_allow_html=True)
        latest = df_p.iloc[0]
        prev_r = df_p.iloc[1] if len(df_p) > 1 else latest
        platforms = [("T212","Trading 212","#2563EB"), ("IBKR","IBKR","#059669"), ("CRY","Crypto","#D97706"), ("PPR","PPR","#7C3AED")]

        cols = st.columns(len(platforms))
        for idx, (cn, label, color) in enumerate(platforms):
            if cn not in df_p.columns:
                continue
            cur = float(latest.get(cn, 0) or 0)
            prv = float(prev_r.get(cn, 0) or 0)
            d = cur - prv
            dp = (d / prv * 100) if prv > 0 else 0
            s = "+" if d >= 0 else ""
            dc = "#059669" if d >= 0 else "#DC2626"
            bw = int(cur / tot * 100) if tot > 0 else 0
            with cols[idx]:
                st.markdown(f"""
                <div style="background:#111;border-radius:12px;padding:16px;border-left:3px solid {color};">
                  <div style="font-size:12px;color:#888;">{label}</div>
                  <div style="font-size:20px;font-weight:700;margin:4px 0;">{cur:,.0f}€</div>
                  <div style="font-size:11px;color:{dc};">{s}{d:,.0f}€  ·  {s}{dp:.1f}%</div>
                  <div style="background:#222;border-radius:4px;height:4px;margin-top:8px;">
                    <div style="background:{color};height:4px;border-radius:4px;width:{bw}%;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 0;">
          <div style="font-size:48px;margin-bottom:16px;">◈</div>
          <div style="font-size:18px;font-weight:600;">Sem dados de patrimônio</div>
          <div style="font-size:13px;color:#888;">Adiciona o teu primeiro registo abaixo</div>
        </div>
        """, unsafe_allow_html=True)

    # Add record
    st.markdown('<div style="font-size:16px;font-weight:600;margin:24px 0 12px;">Novo Registo</div>', unsafe_allow_html=True)
    with st.expander("Adicionar mês"):
        m = st.selectbox("Mês", get_months(), key="m_pat")
        c1, c2 = st.columns(2)
        v1 = c1.number_input("Trading 212 (€)", min_value=0.0, format="%.2f", key="v1")
        v2 = c2.number_input("IBKR (€)", min_value=0.0, format="%.2f", key="v2")
        v3 = c1.number_input("Crypto (€)", min_value=0.0, format="%.2f", key="v3")
        v4 = c2.number_input("PPR / Outros (€)", min_value=0.0, format="%.2f", key="v4")
        tot_inp = v1 + v2 + v3 + v4
        st.markdown(f'<div style="text-align:right;font-size:14px;margin:8px 0;">Total do mês <strong>{tot_inp:,.2f} €</strong></div>', unsafe_allow_html=True)
        if st.button("Gravar Património", key="btn_pat"):
            row = pd.DataFrame([{"Mês":m,"T212":v1,"IBKR":v2,"CRY":v3,"PPR":v4,"Total":tot_inp}])
            save_db(pd.concat([df_p, row], ignore_index=True), "patrimonio")
            st.cache_data.clear(); st.rerun()

    # History
    if not df_p.empty:
        st.markdown('<div style="font-size:16px;font-weight:600;margin:24px 0 12px;">Histórico</div>', unsafe_allow_html=True)
        for i, r in df_p.iterrows():
            if st.session_state.edit_pat == i:
                st.markdown('<div style="font-size:14px;font-weight:600;margin-bottom:8px;">✏ A editar registo</div>', unsafe_allow_html=True)
                ec1, ec2 = st.columns(2)
                e1 = ec1.number_input("Trading 212", value=float(r.get("T212",0) or 0), format="%.2f", key=f"ep1_{i}")
                e2 = ec2.number_input("IBKR", value=float(r.get("IBKR",0) or 0), format="%.2f", key=f"ep2_{i}")
                e3 = ec1.number_input("Crypto", value=float(r.get("CRY",0) or 0), format="%.2f", key=f"ep3_{i}")
                e4 = ec2.number_input("PPR", value=float(r.get("PPR",0) or 0), format="%.2f", key=f"ep4_{i}")
                sb1, sb2 = st.columns(2)
                with sb1:
                    if st.button("Guardar", key=f"eps_{i}"):
                        df_p.at[i,"T212"]=e1; df_p.at[i,"IBKR"]=e2
                        df_p.at[i,"CRY"]=e3; df_p.at[i,"PPR"]=e4
                        df_p.at[i,"Total"]=e1+e2+e3+e4
                        save_db(df_p, "patrimonio"); st.session_state.edit_pat = None; st.rerun()
                with sb2:
                    if st.button("Cancelar", key=f"epc_{i}"):
                        st.session_state.edit_pat = None; st.rerun()
            else:
                sub = f'T212 {float(r.get("T212",0) or 0):,.0f} · IBKR {float(r.get("IBKR",0) or 0):,.0f} · Crypto {float(r.get("CRY",0) or 0):,.0f} · PPR {float(r.get("PPR",0) or 0):,.0f}'
                cc, ce, cd = st.columns([10, 1, 1])
                with cc:
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid #1a1a1a;">
                      <div>
                        <div style="font-weight:600;">{r["Mês"]}</div>
                        <div style="font-size:11px;color:#888;">{sub}</div>
                      </div>
                      <div style="font-weight:700;">{float(r["Total"]):,.0f}€</div>
                    </div>
                    """, unsafe_allow_html=True)
                with ce:
                    if st.button("✏️", key=f"pe_{i}"):
                        st.session_state.edit_pat = i; st.rerun()
                with cd:
                    if st.button("🗑", key=f"pd_{i}"):
                        save_db(df_p.drop(i).reset_index(drop=True), "patrimonio"); st.rerun()

# ══════════════════════════════════════════════════════════════════════
# ▌TAB 2 — FLUXO DE CAIXA
# ══════════════════════════════════════════════════════════════════════
with tab2:
    df_f = load_db("poupanca")
    df_desp = load_db("despesas")

    if not df_f.empty and "Entradas" in df_f.columns:
        te = float(df_f["Entradas"].sum())
        ts = float(df_f["Saidas"].sum()) if "Saidas" in df_f.columns else 0
        tn = te - ts
        taxa = tn / te * 100 if te > 0 else 0
        avg = tn / len(df_f)
        proj = avg * (12 - now.month)
        tip = "Excelente ritmo" if taxa >= 20 else "Razoável" if taxa >= 10 else "Abaixo do ideal"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0a0a0a,#1a1a2e);border-radius:16px;padding:32px;margin-bottom:24px;">
          <div style="font-size:13px;color:#888;">Taxa de Poupança Média</div>
          <div style="font-size:42px;font-weight:700;margin:8px 0;">{taxa:.1f}%</div>
          <div style="font-size:13px;color:#888;">{tip}  ·  {tn:,.0f}€ poupados no total</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", f"{te:,.0f}€")
        c2.metric("Saídas", f"{ts:,.0f}€")
        c3.metric("Projeção", f"{proj:,.0f}€", delta=f"{12-now.month} meses restantes")

        if not df_desp.empty and "Categoria" in df_desp.columns:
            cat_t = df_desp[df_desp["Categoria"] != "_total_"].groupby("Categoria")["Saidas"].sum().sort_values(ascending=False)
            total_s = cat_t.sum()
            if total_s > 0:
                st.markdown('<div style="font-size:16px;font-weight:600;margin:24px 0 12px;">Distribuição de Despesas</div>', unsafe_allow_html=True)
                for cat, val in cat_t.items():
                    color = CAT_COLORS.get(cat, "#6B7280")
                    icon = CAT_ICONS.get(cat, "•")
                    pct = val / total_s * 100
                    bw_c = int(pct)
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:12px;padding:8px 0;">
                      <span style="font-size:18px;">{icon}</span>
                      <div style="flex:1;">
                        <div style="display:flex;justify-content:space-between;font-size:13px;">
                          <span>{cat}</span><span>{val:,.0f}€ · {pct:.0f}%</span>
                        </div>
                        <div style="background:#222;border-radius:4px;height:4px;margin-top:4px;">
                          <div style="background:{color};height:4px;border-radius:4px;width:{bw_c}%;"></div>
                        </div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# ▌TAB 3 — TREINO
# ══════════════════════════════════════════════════════════════════════
with tab3:
    for dia, dados in TREINO.items():
        is_today = dia == today_name
        st.markdown(f"""
        <div style="background:#111;border-radius:12px;padding:20px;margin-bottom:16px;border-left:3px solid {dados['cor']};
                    {'box-shadow:0 0 0 1px ' + dados['cor'] + '40;' if is_today else ''}">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
              <span style="font-weight:700;font-size:16px;">{dia}</span>
              {'<span style="background:' + dados['cor'] + ';color:#fff;font-size:10px;padding:2px 8px;border-radius:99px;margin-left:8px;">HOJE</span>' if is_today else ''}
            </div>
            <span style="font-size:12px;color:#888;">{dados['sub']}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if is_today or st.session_state.treino_edit:
            if dados["warmup"]:
                st.markdown('<div style="font-size:12px;color:#888;margin:8px 0;">Aquecimento</div>', unsafe_allow_html=True)
                for w in dados["warmup"]:
                    st.markdown(f'<div style="font-size:13px;padding:2px 0;">• {w}</div>', unsafe_allow_html=True)

            for ex_name, sets, nota in dados["ex"]:
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #1a1a1a;">
                  <div>
                    <div style="font-weight:600;font-size:14px;">{ex_name}</div>
                    <div style="font-size:11px;color:#888;">{nota}</div>
                  </div>
                  <div style="font-size:13px;color:#ccc;">{sets}</div>
                </div>
                """, unsafe_allow_html=True)

            if dados["nota"]:
                st.markdown(f'<div style="font-size:12px;color:#888;margin-top:8px;font-style:italic;">💡 {dados["nota"]}</div>', unsafe_allow_html=True)

    if st.button("Ver todos os treinos" if not st.session_state.treino_edit else "Fechar"):
        st.session_state.treino_edit = not st.session_state.treino_edit
        st.rerun()

# ══════════════════════════════════════════════════════════════════════
# ▌TAB 4 — ANÁLISE
# ══════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div style="font-size:16px;font-weight:600;margin-bottom:12px;">Análise de Ações</div>', unsafe_allow_html=True)

    ticker = st.text_input("Ticker (ex: AAPL, MSFT, NVDA)", value=st.session_state.ticker, key="ticker_input")

    if ticker:
        st.session_state.ticker = ticker
        with st.spinner("A analisar..."):
            info, err = fetch_info(ticker.upper().strip())

        if err:
            st.error(err)
        elif info:
            name = info.get("longName") or info.get("shortName", ticker)
            price = sg(info, "currentPrice", default=0)
            sector = info.get("sector", "")

            st.markdown(f"""
            <div style="background:#111;border-radius:12px;padding:20px;margin:16px 0;">
              <div style="font-size:20px;font-weight:700;">{name}</div>
              <div style="font-size:13px;color:#888;">{sector} · {info.get('exchange','')}</div>
              <div style="font-size:32px;font-weight:700;margin-top:8px;">${price:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

            # Intrinsic value
            iv_data = intrinsic_value(info, sector)
            iv = iv_data["iv"]

            if iv > 0:
                upside = ((iv / price) - 1) * 100 if price > 0 else 0
                iv_color = "#059669" if upside > 0 else "#DC2626"

                st.markdown(f"""
                <div style="background:#111;border-radius:12px;padding:20px;margin:16px 0;">
                  <div style="font-size:13px;color:#888;">Valor Intrínseco ({iv_data['label']})</div>
                  <div style="font-size:28px;font-weight:700;color:{iv_color};margin:4px 0;">${iv:,.2f}</div>
                  <div style="font-size:13px;color:{iv_color};">{'+'if upside>0 else ''}{upside:.1f}% {'upside' if upside>0 else 'downside'}</div>
                </div>
                """, unsafe_allow_html=True)

                for label, val in iv_data["rows"]:
                    st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:13px;padding:4px 0;"><span style="color:#888;">{label}</span><span>{val}</span></div>', unsafe_allow_html=True)

            # Checklist
            checks, score, n, verdict, v_color, v_bg, v_border, v_icon, v_msg = run_checklist(info, iv, price)

            st.markdown(f"""
            <div style="background:{v_bg};border:1px solid {v_border};border-radius:12px;padding:16px;margin:16px 0;">
              <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:24px;color:{v_color};">{v_icon}</span>
                <span style="font-size:18px;font-weight:700;color:{v_color};">{verdict}</span>
                <span style="font-size:13px;color:#888;margin-left:auto;">{score}/{n}</span>
              </div>
              <div style="font-size:13px;color:#666;margin-top:4px;">{v_msg}</div>
            </div>
            """, unsafe_allow_html=True)

            for cat, label, passed, val in checks:
                icon = "✅" if passed else "❌"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #1a1a1a;font-size:13px;">
                  <span>{icon} {label}</span>
                  <span style="color:#888;">{val}</span>
                </div>
                """, unsafe_allow_html=True)
