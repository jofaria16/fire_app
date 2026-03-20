import streamlit as st
import streamlit.components.v1 as components  # noqa: F401 — used for PIN keypad
import pandas as pd
import os
import io
import base64
import requests
from datetime import datetime
import yfinance as yf
import numpy as np

st.set_page_config(page_title="F|QUANT", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")

# ══════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700;14..32,800;14..32,900&display=swap');

/* ─── RESET ───────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
.stApp { background: #F0F2F5; color: #0F172A; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ─── HIDE STREAMLIT CHROME ───────────────────────────────────────── */
#MainMenu, footer, header,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stSidebarNav"],
.stDeployButton { display: none !important; }

/* ─── TOPBAR ──────────────────────────────────────────────────────── */
.topbar {
    position: sticky; top: 0; z-index: 200;
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(0,0,0,0.06);
    padding: 0 20px;
    height: 52px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.topbar-brand {
    font-size: 16px; font-weight: 800;
    color: #0F172A; letter-spacing: -0.6px;
}
.topbar-brand em { color: #2563EB; font-style: normal; }
.topbar-date { font-size: 12px; color: #94A3B8; font-weight: 500; }

/* ─── TABS ────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF !important;
    border-bottom: 1.5px solid #F1F5F9 !important;
    border-radius: 0 !important; gap: 0 !important;
    padding: 0 8px !important;
    box-shadow: 0 1px 0 #F1F5F9;
}
.stTabs [data-baseweb="tab"] {
    font-size: 13px !important; font-weight: 500 !important;
    color: #94A3B8 !important; padding: 13px 16px !important;
    border-radius: 0 !important; letter-spacing: 0 !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
    transition: color 0.15s ease !important;
}
.stTabs [aria-selected="true"] {
    color: #2563EB !important; font-weight: 700 !important;
    border-bottom: 2.5px solid #2563EB !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: #F0F2F5 !important;
    padding: 20px 16px 40px !important;
}

/* ─── CARDS ───────────────────────────────────────────────────────── */
.card {
    background: #FFFFFF;
    border-radius: 18px;
    border: 1px solid rgba(0,0,0,0.05);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03);
    overflow: hidden;
    margin-bottom: 12px;
    transition: box-shadow 0.2s ease, transform 0.15s ease;
}
.card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    transform: translateY(-1px);
}
.card-body { padding: 18px 20px; }
.card-body-sm { padding: 14px 16px; }

/* ─── HERO GRADIENT CARD ──────────────────────────────────────────── */
.hero {
    background: linear-gradient(140deg, #1E3A8A 0%, #2563EB 60%, #3B82F6 100%);
    border-radius: 20px;
    padding: 26px 22px 22px;
    margin-bottom: 14px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(37,99,235,0.28);
}
.hero::before {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.07);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute; bottom: -30px; left: -20px;
    width: 120px; height: 120px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.hero-eyebrow {
    font-size: 10px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    color: rgba(255,255,255,0.55);
    margin-bottom: 6px;
}
.hero-amount {
    font-size: 40px; font-weight: 800;
    color: #FFFFFF; letter-spacing: -2px;
    line-height: 1; margin-bottom: 12px;
}
.hero-amount sup { font-size: 0.4em; font-weight: 500; opacity: 0.55; letter-spacing: 0; vertical-align: super; }
.hero-delta {
    display: inline-flex; align-items: center; gap: 8px;
    font-size: 13px; color: rgba(255,255,255,0.8); font-weight: 500;
}
.hero-pill {
    background: rgba(255,255,255,0.18);
    border-radius: 100px; padding: 3px 10px;
    font-size: 12px; font-weight: 700; color: #FFF;
    letter-spacing: 0.2px;
}
.hero-pill.up   { background: rgba(52,211,153,0.25); color: #6EE7B7; }
.hero-pill.down { background: rgba(248,113,113,0.25); color: #FCA5A5; }

/* ─── SAVINGS HERO ────────────────────────────────────────────────── */
.savings-hero {
    background: linear-gradient(140deg, #064E3B 0%, #059669 100%);
    border-radius: 20px; padding: 24px 22px;
    margin-bottom: 14px;
    box-shadow: 0 8px 32px rgba(5,150,105,0.22);
    position: relative; overflow: hidden;
}
.savings-hero::before {
    content: ''; position: absolute;
    top: -50px; right: -50px;
    width: 160px; height: 160px;
    background: rgba(255,255,255,0.06); border-radius: 50%;
}
.savings-big {
    font-size: 48px; font-weight: 900;
    color: #fff; letter-spacing: -3px; line-height: 1;
}
.savings-label {
    font-size: 10px; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: rgba(255,255,255,0.5);
    margin-bottom: 4px;
}
.savings-sub { font-size: 13px; color: rgba(255,255,255,0.65); margin-top: 8px; }

/* ─── PLATFORM GRID ───────────────────────────────────────────────── */
.platform-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 10px; margin-bottom: 14px;
}
.platform-card {
    background: #FFFFFF; border-radius: 16px;
    padding: 16px; border: 1px solid rgba(0,0,0,0.05);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: all 0.18s ease;
}
.platform-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.09); transform: translateY(-1px); }
.pc-label { font-size: 10px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; color: #94A3B8; margin-bottom: 8px; }
.pc-value { font-size: 22px; font-weight: 800; letter-spacing: -0.8px; line-height: 1.1; }
.pc-delta { font-size: 12px; font-weight: 600; margin-top: 4px; }
.pc-bar   { height: 3px; background: #F1F5F9; border-radius: 2px; margin-top: 12px; overflow: hidden; }
.pc-fill  { height: 3px; border-radius: 2px; transition: width 0.6s cubic-bezier(.4,0,.2,1); }

/* ─── LIST ROW ────────────────────────────────────────────────────── */
.list-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 20px;
    background: #FFFFFF;
    border-radius: 14px; margin-bottom: 8px;
    border: 1px solid rgba(0,0,0,0.04);
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    transition: all 0.15s ease;
    cursor: default;
}
.list-row:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.07); transform: translateY(-1px); }
.lr-left  { flex: 1; min-width: 0; }
.lr-title { font-size: 14px; font-weight: 600; color: #0F172A; }
.lr-sub   { font-size: 11px; color: #94A3B8; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.lr-right { text-align: right; flex-shrink: 0; margin-left: 12px; }
.lr-value { font-size: 16px; font-weight: 700; }
.lr-pct   { font-size: 11px; font-weight: 600; color: #94A3B8; margin-top: 2px; }

/* ─── SECTION LABEL ───────────────────────────────────────────────── */
.section-label {
    font-size: 11px; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; color: #94A3B8;
    padding: 16px 4px 8px;
}

/* ─── METRIC TILES ────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.05) !important;
    border-radius: 16px !important;
    padding: 16px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
[data-testid="stMetricLabel"] p {
    font-size: 10px !important; font-weight: 700 !important;
    color: #94A3B8 !important; letter-spacing: 1.2px !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-size: 20px !important; font-weight: 800 !important;
    color: #0F172A !important; letter-spacing: -0.5px !important;
}
[data-testid="stMetricDelta"] { font-size: 12px !important; font-weight: 600 !important; }

/* ─── MROW (metrics table) ────────────────────────────────────────── */
.mrow {
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 0; border-bottom: 1px solid #F8FAFC; font-size: 13px;
}
.mrow:last-child { border-bottom: none; }
.mrow .lbl { color: #64748B; }
.mrow .val { font-weight: 600; color: #0F172A; font-size: 13px; }

/* ─── VERDICT ─────────────────────────────────────────────────────── */
.verdict-wrap {
    display: flex; align-items: center; gap: 12px;
    padding: 14px 18px; border-radius: 14px;
    margin: 14px 0;
}
.verdict-icon {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: 800; flex-shrink: 0;
}
.verdict-title { font-size: 16px; font-weight: 800; }
.verdict-desc  { font-size: 12px; margin-top: 2px; opacity: 0.7; }

/* ─── CHECK ROW (treino) ──────────────────────────────────────────── */
.check-row {
    display: flex; align-items: flex-start; gap: 14px;
    padding: 11px 0; border-bottom: 1px solid #F8FAFC;
    transition: opacity 0.2s ease;
}
.check-row:last-child { border-bottom: none; }
.check-row.done { opacity: 0.38; }
.cr-circle {
    width: 24px; height: 24px; flex-shrink: 0;
    border-radius: 50%; border: 2px solid #CBD5E1;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.18s ease; margin-top: 1px;
    background: transparent;
}
.cr-circle.done { background: #2563EB; border-color: #2563EB; }
.cr-check { color: white; font-size: 12px; font-weight: 800; }
.cr-name { font-size: 14px; font-weight: 600; color: #0F172A; line-height: 1.3; }
.cr-name.done { text-decoration: line-through; color: #94A3B8; }
.cr-series {
    display: inline-block; font-size: 11px; font-weight: 700;
    padding: 2px 8px; border-radius: 20px; margin-top: 4px;
    letter-spacing: 0.2px;
}
.cr-desc { font-size: 11px; color: #94A3B8; margin-top: 3px; }

/* ─── PROGRESS BAR ────────────────────────────────────────────────── */
.prog-track {
    height: 5px; background: #F1F5F9;
    border-radius: 100px; overflow: hidden; margin: 10px 0 4px;
}
.prog-fill {
    height: 5px; border-radius: 100px;
    transition: width 0.6s cubic-bezier(.4,0,.2,1);
}

/* ─── DAY CARD ────────────────────────────────────────────────────── */
.day-card {
    background: #FFFFFF; border-radius: 18px;
    border: 1px solid rgba(0,0,0,0.05);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    margin-bottom: 12px; overflow: hidden;
}
.day-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 18px 12px;
}
.day-title { font-size: 16px; font-weight: 800; color: #0F172A; }
.day-sub   { font-size: 12px; color: #94A3B8; margin-top: 2px; }
.day-badge {
    font-size: 12px; font-weight: 700; padding: 4px 12px;
    border-radius: 100px; letter-spacing: 0.2px;
}
.day-body { padding: 0 18px 16px; }
.warmup-strip {
    background: #F8FAFC; border-radius: 10px;
    padding: 10px 14px; margin-bottom: 12px;
    font-size: 11px; color: #64748B;
}
.warmup-strip strong { font-weight: 700; color: #475569; margin-right: 6px; }

/* ─── EDIT BANNER ─────────────────────────────────────────────────── */
.edit-bar {
    background: #EFF6FF; border: 1px solid #BFDBFE;
    border-radius: 12px; padding: 12px 16px; margin-bottom: 12px;
    font-size: 13px; font-weight: 600; color: #2563EB;
    display: flex; align-items: center; gap: 8px;
}

/* ─── INLINE TOTAL ────────────────────────────────────────────────── */
.total-preview {
    display: flex; justify-content: space-between; align-items: center;
    background: #F8FAFC; border-radius: 10px;
    padding: 12px 14px; margin: 8px 0;
    font-size: 13px; color: #64748B;
}
.total-preview strong { font-size: 16px; font-weight: 800; color: #0F172A; }

/* ─── CAT GRID ────────────────────────────────────────────────────── */
.cat-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 11px 0; border-bottom: 1px solid #F8FAFC;
}
.cat-row:last-child { border-bottom: none; }
.cat-dot {
    width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.cat-name { font-size: 13px; color: #374151; flex: 1; margin-left: 10px; }
.cat-val  { font-size: 13px; font-weight: 700; color: #0F172A; }
.cat-pct  { font-size: 11px; color: #94A3B8; margin-left: 8px; min-width: 38px; text-align: right; }

/* ─── STOCK HEADER ────────────────────────────────────────────────── */
.stock-header {
    display: flex; align-items: flex-start;
    justify-content: space-between; gap: 12px;
}
.stock-name    { font-size: 20px; font-weight: 800; color: #0F172A; letter-spacing: -0.5px; }
.stock-meta    { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; align-items: center; }
.stock-ticker  { font-size: 12px; color: #94A3B8; font-weight: 600; }
.stock-price   { font-size: 32px; font-weight: 900; color: #0F172A; letter-spacing: -1.5px; line-height: 1; }
.stock-change  { font-size: 13px; font-weight: 600; margin-top: 4px; }

/* ─── TAG / CHIP ──────────────────────────────────────────────────── */
.chip {
    display: inline-block; font-size: 11px; font-weight: 600;
    padding: 3px 10px; border-radius: 100px; letter-spacing: 0.2px;
}
.chip-blue   { background: #EFF6FF; color: #2563EB; }
.chip-grey   { background: #F1F5F9; color: #64748B; }
.chip-green  { background: #ECFDF5; color: #059669; }
.chip-yellow { background: #FFFBEB; color: #D97706; }
.chip-red    { background: #FEF2F2; color: #DC2626; }

/* ─── NOTE STRIP ──────────────────────────────────────────────────── */
.note-strip {
    background: #F0FDF4; border-left: 3px solid #10B981;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px; margin: 8px 0;
    font-size: 12px; color: #059669;
}

/* ─── BUTTONS ─────────────────────────────────────────────────────── */
div.stButton > button {
    width: 100% !important;
    background: #2563EB !important;
    color: #FFFFFF !important; font-weight: 700 !important;
    border-radius: 14px !important; border: none !important;
    height: 50px !important; font-size: 14px !important;
    letter-spacing: 0.1px !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.25) !important;
    transition: all 0.15s ease !important;
}
div.stButton > button:hover {
    background: #1D4ED8 !important;
    box-shadow: 0 6px 20px rgba(37,99,235,0.35) !important;
    transform: translateY(-1px) !important;
    opacity: 1 !important;
}
div.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 1px 4px rgba(37,99,235,0.2) !important;
}
/* icon buttons */
[data-testid="column"] div.stButton > button {
    background: #FFFFFF !important; border: 1px solid #E2E8F0 !important;
    color: #94A3B8 !important; height: 40px !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    font-size: 15px !important;
}
[data-testid="column"] div.stButton > button:hover {
    background: #F8FAFC !important; color: #475569 !important;
    border-color: #CBD5E1 !important;
    transform: none !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}
.btn-green div.stButton > button {
    background: #059669 !important;
    box-shadow: 0 2px 8px rgba(5,150,105,0.25) !important;
}
.btn-green div.stButton > button:hover {
    background: #047857 !important;
    box-shadow: 0 6px 20px rgba(5,150,105,0.3) !important;
}
.btn-ghost div.stButton > button {
    background: #F8FAFC !important; color: #64748B !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: none !important;
}
.btn-ghost div.stButton > button:hover {
    background: #F1F5F9 !important; transform: none !important;
    box-shadow: none !important;
}

/* ─── INPUTS ──────────────────────────────────────────────────────── */
.stTextInput input, .stNumberInput input {
    background: #FFFFFF !important; color: #0F172A !important;
    border: 1.5px solid #E2E8F0 !important; border-radius: 12px !important;
    font-size: 14px !important; font-weight: 500 !important;
    padding: 11px 14px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 4px rgba(37,99,235,0.10) !important;
}
.stSelectbox > div > div {
    background: #FFFFFF !important; border: 1.5px solid #E2E8F0 !important;
    border-radius: 12px !important; color: #0F172A !important;
}
label[data-testid="stWidgetLabel"] p {
    font-size: 11px !important; font-weight: 700 !important;
    color: #64748B !important; letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}

/* ─── EXPANDER ────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: #FFFFFF !important; border: 1px solid rgba(0,0,0,0.06) !important;
    border-radius: 14px !important; padding: 14px 18px !important;
    font-weight: 600 !important; font-size: 14px !important;
    color: #374151 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
.streamlit-expanderContent {
    background: #FAFAFA !important; border: 1px solid rgba(0,0,0,0.06) !important;
    border-top: none !important; border-radius: 0 0 14px 14px !important;
    padding: 18px !important;
}

/* ─── CHECKBOX hidden (we build our own) ─────────────────────────── */
.stCheckbox { display: none !important; }

/* ─── SCROLLBAR ───────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }

/* ─── ANIMATIONS ──────────────────────────────────────────────────── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse-dot {
    0%,100% { transform: scale(1); }
    50%      { transform: scale(1.18); }
}
@keyframes shake {
    0%,100% { transform: translateX(0); }
    15%  { transform: translateX(-7px); }
    30%  { transform: translateX(7px); }
    45%  { transform: translateX(-5px); }
    60%  { transform: translateX(5px); }
    75%  { transform: translateX(-3px); }
}
.fade-up { animation: fadeUp 0.32s cubic-bezier(.4,0,.2,1) forwards; }
.shake   { animation: shake 0.45s cubic-bezier(.4,0,.2,1); }

/* ─── EMPTY STATE ─────────────────────────────────────────────────── */
.empty-state {
    text-align: center; padding: 52px 20px;
    color: #94A3B8;
}
.empty-state .icon { font-size: 36px; margin-bottom: 12px; opacity: 0.5; }
.empty-state .title { font-size: 15px; font-weight: 700; color: #64748B; margin-bottom: 6px; }
.empty-state .sub   { font-size: 13px; }

/* ─── PIN SCREEN ──────────────────────────────────────────────────── */
.pin-screen {
    display: flex; flex-direction: column;
    align-items: center; padding: 64px 0 8px;
}
.pin-logo {
    font-size: 28px; font-weight: 900; color: #0F172A;
    letter-spacing: -1px; margin-bottom: 6px;
}
.pin-logo span { color: #2563EB; }
.pin-subtitle {
    font-size: 14px; color: #94A3B8; font-weight: 400;
    margin-bottom: 48px;
}
.pin-dots {
    display: flex; gap: 18px; margin-bottom: 40px;
    justify-content: center;
}
.pin-dot {
    width: 14px; height: 14px; border-radius: 50%;
    border: 2px solid #CBD5E1; background: transparent;
    transition: all 0.12s ease;
}
.pin-dot.filled { background: #0F172A; border-color: #0F172A; transform: scale(1.1); }
.pin-dot.error  { background: #EF4444; border-color: #EF4444; }
.pin-error-msg  {
    text-align: center; color: #EF4444;
    font-size: 13px; font-weight: 600; margin-top: 12px;
}

/* ─── PIN KEYPAD BUTTONS ──────────────────────────────────────────── */
/* Scoped override: only applies inside .pin-row wrappers */
.pin-row { display: flex; justify-content: center; gap: 0; margin-bottom: 4px; }
.pin-row [data-testid="column"] { flex: 0 0 100px !important; max-width: 100px !important; }
.pin-row div.stButton > button {
    width: 72px !important; height: 72px !important;
    border-radius: 50% !important;
    background: #F1F5F9 !important;
    color: #0F172A !important;
    font-size: 22px !important; font-weight: 500 !important;
    border: none !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.07) !important;
    padding: 0 !important; letter-spacing: 0 !important;
    margin: 0 auto !important;
    transition: background 0.1s, transform 0.1s !important;
}
.pin-row div.stButton > button:hover {
    background: #E2E8F0 !important;
    transform: scale(0.93) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    opacity: 1 !important;
}
.pin-row div.stButton > button:active {
    background: #CBD5E1 !important; transform: scale(0.88) !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# DATABASE LAYER — GitHub as persistent storage
# ══════════════════════════════════════════════════════════════════════
GITHUB_REPO  = st.secrets.get("GITHUB_REPO",  "jofaria16/fire_app")
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_BRANCH = "main"
DATA_DIR = "dados"

PT_MONTHS = {"Jan":1,"Fev":2,"Mar":3,"Abr":4,"Mai":5,"Jun":6,
             "Jul":7,"Ago":8,"Set":9,"Out":10,"Nov":11,"Dez":12}

def parse_mes(m):
    try:
        p = str(m).strip().split()
        return (int(p[1]) + 2000) * 100 + PT_MONTHS.get(p[0], 0)
    except:
        return 0

def _gh_headers():
    return {
        "Authorization": "token " + GITHUB_TOKEN,
        "Accept": "application/vnd.github.v3+json"
    }

def _gh_path(name):
    return f"{DATA_DIR}/{name}.csv"

@st.cache_data(ttl=30, show_spinner=False)
def load_db(name):
    """Load CSV from GitHub repo."""
    if not GITHUB_TOKEN:
        return pd.DataFrame()
    url  = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{_gh_path(name)}"
    resp = requests.get(url, headers=_gh_headers(), timeout=10)
    if resp.status_code != 200:
        return pd.DataFrame()
    content = base64.b64decode(resp.json()["content"]).decode("utf-8")
    df = pd.read_csv(io.StringIO(content))
    if df.empty or "Mês" not in df.columns:
        return df.reset_index(drop=True)
    try:
        df["_s"] = df["Mês"].apply(parse_mes)
        df = df.sort_values("_s", ascending=False).drop(columns=["_s"])
    except:
        pass
    return df.reset_index(drop=True)

def save_db(df, name):
    """Save CSV to GitHub repo (creates or updates file)."""
    if not GITHUB_TOKEN:
        return
    # Sort by month if applicable
    if "Mês" in df.columns and not df.empty:
        try:
            df = df.copy()
            df["_s"] = df["Mês"].apply(parse_mes)
            df = df.sort_values("_s", ascending=False).drop(columns=["_s"])
        except:
            pass
    csv_content = df.to_csv(index=False)
    encoded     = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    url         = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{_gh_path(name)}"

    # Get current SHA (needed to update existing file)
    sha = None
    resp = requests.get(url, headers=_gh_headers(), timeout=10)
    if resp.status_code == 200:
        sha = resp.json().get("sha")

    payload = {
        "message": f"update {name}",
        "content": encoded,
        "branch":  GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    requests.put(url, headers=_gh_headers(), json=payload, timeout=15)
    # Clear cache so next load_db reads fresh data
    load_db.clear()

def get_months():
    n = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    y = datetime.now().year % 100
    return [f"{m} {y}" for m in reversed(n)] + [f"{m} {y-1}" for m in reversed(n)]

DESPESA_CATS  = ["Habitação","Alimentação","Transportes","Saúde","Lazer","Subscrições","Educação","Outros"]
CAT_ICONS     = {"Habitação":"🏠","Alimentação":"🍽","Transportes":"🚗","Saúde":"💊","Lazer":"🎮","Subscrições":"📱","Educação":"📚","Outros":"📦"}
CAT_COLORS    = {"Habitação":"#2563EB","Alimentação":"#059669","Transportes":"#D97706","Saúde":"#EC4899","Lazer":"#7C3AED","Subscrições":"#0891B2","Educação":"#16A34A","Outros":"#6B7280"}

# ══════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════
_defaults = {
    "auth": False, "pin_input": "", "pin_error": False,
    "edit_pat": None, "edit_flx": None,
    "ticker": "", "treino_edit": False,
    "selected_week": datetime.now().isocalendar()[1],
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
                if f != 0: return f
            except:
                return v
    return default

@st.cache_data(ttl=300, show_spinner=False)
def fetch_info(symbol):
    try:
        t = yf.Ticker(symbol); info = t.info or {}
        try:
            fi = t.fast_info
            p  = getattr(fi,"last_price",None) or getattr(fi,"regular_market_price",None) or info.get("currentPrice") or info.get("previousClose")
            if p: info["currentPrice"] = float(p)
        except: pass
        if not info.get("currentPrice"):
            h = t.history(period="5d")
            if not h.empty: info["currentPrice"] = float(h["Close"].iloc[-1])
        if not info.get("currentPrice",0) and not (info.get("longName") or info.get("shortName")):
            return None, f"Ticker **{symbol}** não encontrado."
        if not (info.get("longName") or info.get("shortName")): info["longName"] = symbol
        return info, None
    except Exception as e:
        return None, f"Erro: {str(e)}"

SECTOR_CFG = {
    "Technology":             {"method":"dcf",      "dr":.10,"tg":.03, "cap":.25,"label":"DCF — Free Cash Flow"},
    "Communication Services": {"method":"dcf",      "dr":.10,"tg":.025,"cap":.20,"label":"DCF — Free Cash Flow"},
    "Healthcare":             {"method":"dcf",      "dr":.09,"tg":.025,"cap":.18,"label":"DCF — Free Cash Flow"},
    "Consumer Cyclical":      {"method":"ev_ebitda","multiple":14,              "label":"EV / EBITDA"},
    "Consumer Defensive":     {"method":"pe_rel",   "base_pe":22,               "label":"P/E Relativo"},
    "Financial Services":     {"method":"pb_roe",                               "label":"P/B + ROE"},
    "Industrials":            {"method":"ev_ebitda","multiple":11,              "label":"EV / EBITDA"},
    "Basic Materials":        {"method":"ev_ebitda","multiple":8,               "label":"EV / EBITDA"},
    "Energy":                 {"method":"ev_ebitda","multiple":7,               "label":"EV / EBITDA"},
    "Utilities":              {"method":"ddm",                                  "label":"Gordon Growth"},
    "Real Estate":            {"method":"ffo",                                  "label":"P / FFO"},
}

def intrinsic_value(info, sector):
    cfg = SECTOR_CFG.get(sector, {"method":"dcf","dr":.10,"tg":.025,"cap":.15,"label":"DCF"})
    m   = cfg["method"]; sh = sg(info,"sharesOutstanding",default=1)
    r   = {"iv":0,"label":cfg["label"],"rows":[]}; R = r["rows"]
    try:
        if m == "dcf":
            dr,tg,cap = cfg.get("dr",.10), cfg.get("tg",.025), cfg.get("cap",.15)
            fcf = sg(info,"freeCashflow",default=0)
            if fcf<=0: fcf = sg(info,"operatingCashflow",default=0)-abs(sg(info,"capitalExpenditures",default=0))
            if fcf<=0: fcf = sg(info,"netIncomeToCommon",default=0)
            if fcf<=0 or sh<=0: return r
            g  = min(max((sg(info,"revenueGrowth",default=.05)+sg(info,"earningsGrowth",default=.05))/2,.03),cap)
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
        ("Crescimento","Receita YoY > 7%",   rg>0.07,  f"{rg*100:.1f}%"),
        ("Crescimento","Lucro YoY > 9%",      eg>0.09,  f"{eg*100:.1f}%"),
        ("Margem",     "Margem Líq. > 10%",   mg>0.10,  f"{mg*100:.1f}%"),
        ("Margem",     "Margem Bruta > 40%",  gm>0.40,  f"{gm*100:.1f}%"),
        ("Retorno",    "ROE > 15%",            roe>0.15, f"{roe*100:.1f}%"),
        ("Retorno",    "ROA > 5%",             roa>0.05, f"{roa*100:.1f}%"),
        ("Qualidade",  "CFO/NetInc > 80%",    cn>0.80,  f"{cn*100:.1f}%"),
        ("Qualidade",  "Dívida/Eq. < 1.5",    0<de<150, f"{de/100:.2f}×" if de>1 else f"{de:.2f}×"),
        ("Qualidade",  "Current Ratio > 1.2", cr>1.2,   f"{cr:.2f}×"),
        ("Valuation",  "P/E < 30",            0<pe<30,  f"{pe:.1f}×" if pe>0 else "N/A"),
        ("Valuation",  "PEG < 1.5",           0<peg<1.5,f"{peg:.2f}" if peg>0 else "N/A"),
        ("Valuation",  "Upside > 15%",        up>15,    f"{up:+.1f}%" if iv>0 else "N/A"),
        ("Risco",      "Beta < 1.5",          beta<1.5, f"{beta:.2f}"),
    ]
    score=sum(1 for _,_,p,_ in checks if p); n=len(checks)
    qs=sum(1 for c,_,p,_ in checks if c in ("Margem","Retorno","Qualidade") and p)
    vs=sum(1 for c,_,p,_ in checks if c=="Valuation" and p)
    if score>=10 and vs>=2:   return checks,score,n,"APROVADA","#059669","#ECFDF5","#6EE7B7","✓","Empresa de alta qualidade com valuation atrativo."
    elif score>=7 and qs>=3:  return checks,score,n,"INDECISA","#D97706","#FFFBEB","#FCD34D","~","Boas fundações. Alguns critérios em falta."
    else:                     return checks,score,n,"REJEITADA","#DC2626","#FEF2F2","#FCA5A5","✕","Não cumpre os critérios mínimos."

# ══════════════════════════════════════════════════════════════════════
# TRAINING PLAN
# ══════════════════════════════════════════════════════════════════════
TREINO = {
    "Segunda": {
        "sub": "Base & Estabilidade", "cor": "#2563EB",
        "warmup": ["Círculos de anca","Rotação torácica","10 agachamentos lentos","10 scapular push-ups"],
        "ex": [
            ("Goblet Squat",                   "3 × 10-12",      "Progressão lenta · controlo e profundidade"),
            ("Romanian Deadlift",               "3 × 10",         "Kettlebell ou barra · alongamento posterior"),
            ("Passadas Atrás",                  "3 × 8 cada",     "Excelente para estabilidade da anca"),
            ("Prancha Frontal",                 "3 × 30-45s",     ""),
            ("Side Plank",                      "2 × cada lado",  ""),
        ],
        "nota": "Reforça anca e core — essencial para a tua estrutura."
    },
    "Quarta": {
        "sub": "Ombros & Estabilidade Superior", "cor": "#7C3AED",
        "warmup": ["Mobilidade ombro","Elástico — rotação externa"],
        "ex": [
            ("Overhead Press",     "3 × 10",       "Halter ou máquina · controlado"),
            ("Elevações Laterais", "3 × 12-15",    ""),
            ("Face Pulls",         "3 × 12-15",    "Fundamental para proteger o ombro"),
            ("Remo Unilateral",    "3 × 10 cada",  "Ótimo para estabilidade do tronco"),
            ("Hiperextensão",      "3 × 12",       ""),
        ],
        "nota": ""
    },
    "Sexta": {
        "sub": "Peito & Costas — Principal", "cor": "#059669",
        "warmup": [],
        "ex": [
            ("Chest Press",             "3 × 12/10/8",          "Progressão de carga"),
            ("Remo Máquina",            "3 × 12/10/8",          ""),
            ("Press Inclinado",         "3 × 10/8/6",           ""),
            ("Dorsal Máquina / Barras", "3 × 10-12",            ""),
            ("Finisher",                "Flexões ou 5-8 barras","Opcional"),
        ],
        "nota": "Podes usar a pirâmide progressiva aqui."
    },
}

# ══════════════════════════════════════════════════════════════════════
# PIN AUTH
# ══════════════════════════════════════════════════════════════════════
CORRECT_PIN = "1214"

# Separate buffer key — never tied to a widget, safe to write any time
if "pin_buf" not in st.session_state:
    st.session_state.pin_buf = ""

if not st.session_state.auth:
    buf = st.session_state.pin_buf
    err = st.session_state.pin_error
    n   = len(buf)

    # ── dots ──────────────────────────────────────────────────────────
    dot_parts = []
    for i in range(4):
        if err:
            bg = "#EF4444"; bd = "#EF4444"
        elif i < n:
            bg = "#0F172A"; bd = "#0F172A"
        else:
            bg = "transparent"; bd = "#CBD5E1"
        dot_parts.append(
            '<div style="width:13px;height:13px;border-radius:50%;'
            + 'background:' + bg + ';border:2px solid ' + bd + ';'
            + 'transition:all 0.12s ease;"></div>'
        )
    dots = "".join(dot_parts)
    err_msg_html = "PIN incorreto. Tenta novamente." if err else ""


    st.markdown(f"""
    <style>
      .stApp {{ background:#FFFFFF !important; }}
      header, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
      [data-testid="stStatusWidget"], #MainMenu {{ display:none !important; }}
      .block-container {{ padding:0 !important; max-width:100% !important; }}

      /* PIN header — centered above the buttons */
      .pin-header {{
        text-align:center;
        padding: 72px 0 48px;
      }}
      .pin-logo  {{ font-size:26px; font-weight:800; color:#0F172A; letter-spacing:-0.8px; margin-bottom:6px; }}
      .pin-logo span {{ color:#2563EB; }}
      .pin-sub   {{ font-size:14px; color:#94A3B8; margin-bottom:44px; }}
      .pin-dots  {{ display:flex; gap:18px; justify-content:center; }}
      .pin-err   {{ min-height:20px; font-size:13px; font-weight:600; color:#EF4444; text-align:center; margin-top:14px; }}

      /* Keypad button overrides — circular, centered */
      div[data-testid="stButton"] > button {{
        width:76px !important; height:76px !important;
        border-radius:50% !important;
        background:#F1F5F9 !important;
        color:#0F172A !important;
        font-size:24px !important; font-weight:300 !important;
        border:none !important;
        box-shadow:0 2px 8px rgba(0,0,0,0.08) !important;
        padding:0 !important;
        display:flex !important; align-items:center !important; justify-content:center !important;
        margin:0 auto !important;
        transition:transform 0.08s ease, background 0.08s ease !important;
      }}
      div[data-testid="stButton"] > button:hover {{
        background:#E2E8F0 !important; opacity:1 !important;
        transform:scale(0.95) !important;
        box-shadow:0 1px 4px rgba(0,0,0,0.07) !important;
      }}
      div[data-testid="stButton"] > button:active {{
        background:#CBD5E1 !important; transform:scale(0.90) !important;
      }}

      /* Force columns to stay horizontal and centered even on mobile */
      [data-testid="stHorizontalBlock"] {{
        display:flex !important; flex-direction:row !important;
        justify-content:center !important; gap:14px !important;
        flex-wrap:nowrap !important;
      }}
      [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
        flex:0 0 76px !important; min-width:76px !important; max-width:76px !important;
        width:76px !important; padding:0 !important;
      }}
    </style>

    <div class="pin-header">
      <div class="pin-logo">F<span>|</span>QUANT</div>
      <div class="pin-sub">Introduce o teu PIN para continuar</div>
      <div class="pin-dots">{dots}</div>
      <div class="pin-err">{err_msg_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── keypad rows — pure st.button, buffer in pin_buf ───────────────
    rows = [["1","2","3"], ["4","5","6"], ["7","8","9"], ["_","0","⌫"]]
    for row in rows:
        c1, c2, c3 = st.columns(3)
        for col, val in zip([c1, c2, c3], row):
            with col:
                if val == "_":
                    st.markdown("<div style='height:76px'></div>", unsafe_allow_html=True)
                elif st.button(val, key=f"pb_{val}"):
                    if val == "⌫":
                        st.session_state.pin_buf   = buf[:-1]
                        st.session_state.pin_error = False
                    else:
                        new = buf + val
                        st.session_state.pin_buf   = new
                        st.session_state.pin_error = False
                        if len(new) == 4:
                            if new == CORRECT_PIN:
                                st.session_state.auth    = True
                                st.session_state.pin_buf = ""
                            else:
                                st.session_state.pin_error = True
                                st.session_state.pin_buf   = ""
                    st.rerun()

    st.stop()


# ══════════════════════════════════════════════════════════════════════
# APP SHELL
# ══════════════════════════════════════════════════════════════════════
now = datetime.now()
day_names = {0:"Segunda",1:"Terça",2:"Quarta",3:"Quinta",4:"Sexta",5:"Sábado",6:"Domingo"}
today_name = day_names[now.weekday()]

st.markdown(
    '<div class="topbar">'
    + '<div class="topbar-brand">F<em>|</em>QUANT</div>'
    + '<div class="topbar-date">' + today_name + ', ' + now.strftime("%-d %b") + '</div>'
    + '</div>',
    unsafe_allow_html=True
)

tab1, tab2, tab3, tab4 = st.tabs(["Património", "Fluxo", "Treino", "Análise"])


# ══════════════════════════════════════════════════════════════════════
# ▌TAB 1 — PATRIMÓNIO
# ══════════════════════════════════════════════════════════════════════
with tab1:
    df_p = load_db("patrimonio")

    # ── Hero ──────────────────────────────────────────────────────────
    if not df_p.empty:
        tot   = float(df_p["Total"].iloc[0])
        prev  = float(df_p["Total"].iloc[1]) if len(df_p) > 1 else tot
        dlt   = tot - prev
        dpct  = (dlt / prev * 100) if prev > 0 else 0
        sign  = "+" if dlt >= 0 else ""
        arrow = "↑" if dlt >= 0 else "↓"
        pill_cls = "up" if dlt >= 0 else "down"

        st.markdown(
            '<div class="hero fade-up">'
            + '<div class="hero-eyebrow">Total Investido</div>'
            + '<div class="hero-amount">' + f"{tot:,.0f}" + '<sup>EUR</sup></div>'
            + '<div class="hero-delta">' + arrow
            + '<span class="hero-pill ' + pill_cls + '">' + sign + f"{dlt:,.0f}" + ' € &nbsp;·&nbsp; ' + sign + f"{dpct:.1f}" + '%</span>'
            + '<span style="font-size:11px; opacity:0.5;">vs mês anterior</span>'
            + '</div></div>',
            unsafe_allow_html=True
        )

        # ── Platform grid ─────────────────────────────────────────────
        st.markdown('<div class="section-label">Carteiras</div>', unsafe_allow_html=True)
        latest = df_p.iloc[0]
        prev_r = df_p.iloc[1] if len(df_p) > 1 else latest
        platforms = [("T212","Trading 212","#2563EB"), ("IBKR","IBKR","#059669"),
                     ("CRY","Crypto","#D97706"),       ("PPR","PPR","#7C3AED")]

        grid_html = '<div class="platform-grid">'
        for cn, label, color in platforms:
            cur = float(latest.get(cn, 0) or 0) if cn in df_p.columns else 0.0
            prv = float(prev_r.get(cn, 0) or 0) if cn in df_p.columns else 0.0
            d   = cur - prv
            dp  = (d / prv * 100) if prv > 0 else 0.0
            s   = "+" if d >= 0 else ""
            dc  = "#059669" if d >= 0 else "#DC2626"
            bw  = int(cur / tot * 100) if tot > 0 else 0
            grid_html += (
                '<div class="platform-card">'
                + '<div class="pc-label">' + label + '</div>'
                + '<div class="pc-value" style="color:' + color + ';">' + f'{cur:,.0f}' + '€</div>'
                + '<div class="pc-delta" style="color:' + dc + ';">' + s + f'{d:,.0f}' + '€ &nbsp;·&nbsp; ' + s + f'{dp:.1f}' + '%</div>'
                + '<div class="pc-bar"><div class="pc-fill" style="width:' + str(bw) + '%;background:' + color + ';"></div></div>'
                + '</div>'
            )
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)


    else:
        st.markdown("""
            <div class="empty-state">
                <div class="icon">◈</div>
                <div class="title">Sem dados de patrimônio</div>
                <div class="sub">Adiciona o teu primeiro registo abaixo</div>
            </div>
        """, unsafe_allow_html=True)

    # ── Add record ────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Novo Registo</div>', unsafe_allow_html=True)
    with st.expander("Adicionar mês"):
        m = st.selectbox("Mês", get_months(), key="m_pat")
        c1, c2 = st.columns(2)
        v1 = c1.number_input("Trading 212 (€)", min_value=0.0, format="%.2f", key="v1")
        v2 = c2.number_input("IBKR (€)",         min_value=0.0, format="%.2f", key="v2")
        v3 = c1.number_input("Crypto (€)",        min_value=0.0, format="%.2f", key="v3")
        v4 = c2.number_input("PPR / Outros (€)",  min_value=0.0, format="%.2f", key="v4")
        tot_inp = v1 + v2 + v3 + v4
        st.markdown(
            '<div class="total-preview"><span>Total do mês</span>'
            + '<strong>' + f"{tot_inp:,.2f}" + ' €</strong></div>',
            unsafe_allow_html=True
        )
        if st.button("Gravar Património", key="btn_pat"):
            row = pd.DataFrame([{"Mês":m,"T212":v1,"IBKR":v2,"CRY":v3,"PPR":v4,"Total":tot_inp}])
            save_db(pd.concat([df_p, row], ignore_index=True), "patrimonio")
            st.rerun()

    # ── History ───────────────────────────────────────────────────────
    if not df_p.empty:
        st.markdown('<div class="section-label">Histórico</div>', unsafe_allow_html=True)
        for i, r in df_p.iterrows():
            if st.session_state.edit_pat == i:
                st.markdown('<div class="edit-bar">✏ A editar registo</div>', unsafe_allow_html=True)
                ec1, ec2 = st.columns(2)
                e1 = ec1.number_input("Trading 212", value=float(r.get("T212",0) or 0), format="%.2f", key=f"ep1_{i}")
                e2 = ec2.number_input("IBKR",        value=float(r.get("IBKR",0) or 0), format="%.2f", key=f"ep2_{i}")
                e3 = ec1.number_input("Crypto",      value=float(r.get("CRY",0)  or 0), format="%.2f", key=f"ep3_{i}")
                e4 = ec2.number_input("PPR",         value=float(r.get("PPR",0)  or 0), format="%.2f", key=f"ep4_{i}")
                sb1, sb2 = st.columns(2)
                with sb1:
                    if st.button("✓ Guardar", key=f"eps_{i}", type="primary"):
                        df_p.at[i,"T212"]=e1; df_p.at[i,"IBKR"]=e2
                        df_p.at[i,"CRY"]=e3;  df_p.at[i,"PPR"]=e4
                        df_p.at[i,"Total"]=e1+e2+e3+e4
                        save_db(df_p, "patrimonio"); st.session_state.edit_pat = None; st.rerun()
                with sb2:
                    if st.button("Cancelar", key=f"epc_{i}"):
                        st.session_state.edit_pat = None; st.rerun()
            else:
                sub = f'T212 {float(r.get("T212",0) or 0):,.0f} · IBKR {float(r.get("IBKR",0) or 0):,.0f} · Crypto {float(r.get("CRY",0) or 0):,.0f} · PPR {float(r.get("PPR",0) or 0):,.0f}'
                cc, ce, cd = st.columns([10, 1, 1])
                with cc:
                    st.markdown(
                        '<div class="list-row">'
                        + '<div class="lr-left">'
                        + '<div class="lr-title">' + str(r["Mês"]) + '</div>'
                        + '<div class="lr-sub">' + sub + '</div>'
                        + '</div>'
                        + '<div class="lr-right">'
                        + '<div class="lr-value">' + f'{float(r["Total"]):,.0f}' + '€</div>'
                        + '</div>'
                        + '</div>',
                        unsafe_allow_html=True
                    )
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
    df_f    = load_db("poupanca")
    df_desp = load_db("despesas")

    # ── Savings hero ──────────────────────────────────────────────────
    if not df_f.empty and "Entradas" in df_f.columns:
        te    = float(df_f["Entradas"].sum())
        ts    = float(df_f["Saidas"].sum()) if "Saidas" in df_f.columns else 0
        tn    = te - ts
        taxa  = tn / te * 100 if te > 0 else 0
        avg   = tn / len(df_f)
        proj  = avg * (12 - now.month)
        tip   = "Excelente ritmo" if taxa >= 20 else "Razoável" if taxa >= 10 else "Abaixo do ideal"
        bw    = min(int(taxa), 100)
        tc    = "rgba(255,255,255,0.85)"

        st.markdown(
            '<div class="savings-hero fade-up">'
            + '<div class="savings-label">Taxa de Poupança Média</div>'
            + '<div class="savings-big">' + f"{taxa:.1f}" + '<span style="font-size:0.4em;opacity:0.6;font-weight:500;letter-spacing:0;">%</span></div>'
            + '<div class="savings-sub">' + tip + ' &nbsp;·&nbsp; ' + f"{tn:,.0f}" + '€ poupados no total</div>'
            + '<div style="background:rgba(255,255,255,0.15);border-radius:99px;height:4px;margin-top:16px;overflow:hidden;">'
            + '<div style="width:' + str(bw) + '%;height:4px;border-radius:99px;background:rgba(255,255,255,0.75);transition:width 0.6s ease;"></div>'
            + '</div></div>',
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas",  f"{te:,.0f}€")
        c2.metric("Saídas",    f"{ts:,.0f}€")
        c3.metric("Projeção",  f"{proj:,.0f}€", delta=f"{12-now.month} meses restantes")

        # Category breakdown
        if not df_desp.empty and "Categoria" in df_desp.columns:
            cat_t   = df_desp[df_desp["Categoria"] != "_total_"].groupby("Categoria")["Saidas"].sum().sort_values(ascending=False)
            total_s = cat_t.sum()
            if total_s > 0:
                st.markdown('<div class="section-label" style="margin-top:20px;">Distribuição de Despesas</div>', unsafe_allow_html=True)
                cat_html = '<div class="card"><div class="card-body">'
                for cat, val in cat_t.items():
                    color = CAT_COLORS.get(cat, "#6B7280")
                    icon  = CAT_ICONS.get(cat, "•")
                    pct   = val / total_s * 100
                    bw_c  = int(pct)
                    cat_html += (
                        '<div class="cat-row">'
                        + '<div class="cat-dot" style="background:' + color + ';"></div>'
                        + '<div class="cat-name">' + icon + ' ' + cat + '</div>'
                        + '<div style="display:flex;align-items:center;gap:12px;flex-shrink:0;">'
                        + '<div style="width:80px;height:4px;background:#F1F5F9;border-radius:2px;overflow:hidden;">'
                        + '<div style="width:' + str(bw_c) + '%;height:4px;background:' + color + ';border-radius:2px;"></div>'
                        + '</div>'
                        + '<div class="cat-val">' + f'{val:,.0f}' + '€</div>'
                        + '<div class="cat-pct">' + f'{pct:.0f}' + '%</div>'
                        + '</div>'
                        + '</div>'
                    )
                cat_html += '</div></div>'
                st.markdown(cat_html, unsafe_allow_html=True)

    else:
        st.markdown("""
            <div class="empty-state">
                <div class="icon">📊</div>
                <div class="title">Sem registos de fluxo</div>
                <div class="sub">Começa por adicionar o teu primeiro mês</div>
            </div>
        """, unsafe_allow_html=True)

    # ── Add record ────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Novo Registo</div>', unsafe_allow_html=True)
    with st.expander("Registar mês"):
        mf  = st.selectbox("Mês", get_months(), key="m_flx")
        sal = st.number_input("Salário / Entradas (€)", min_value=0.0, format="%.2f", key="sal")
        st.markdown('<div style="font-size:11px;font-weight:700;color:#94A3B8;letter-spacing:1.2px;text-transform:uppercase;margin:14px 0 8px;">Despesas por categoria</div>', unsafe_allow_html=True)
        cat_vals = {}
        c1d, c2d = st.columns(2)
        for idx, cat in enumerate(DESPESA_CATS):
            col = c1d if idx % 2 == 0 else c2d
            cat_vals[cat] = col.number_input(f"{CAT_ICONS.get(cat,'')} {cat}", min_value=0.0, format="%.2f", key=f"c_{cat}")
        total_d = sum(cat_vals.values())
        sobra   = sal - total_d
        taxa_p  = (sobra / sal * 100) if sal > 0 else 0
        tc2     = "#059669" if sobra >= 0 else "#DC2626"
        st.markdown(
            '<div class="total-preview" style="margin-top:12px;">'
            + '<span>Poupança do mês</span>'
            + '<strong style="color:' + tc2 + ';">' + f"{sobra:,.0f}" + '€ <span style="font-size:0.7em;font-weight:600;opacity:0.7;">(' + f"{taxa_p:.1f}" + '%)</span></strong>'
            + '</div>',
            unsafe_allow_html=True
        )
        if st.button("Gravar Fluxo", key="btn_flx"):
            summary  = pd.DataFrame([{"Mês":mf,"Entradas":sal,"Saidas":total_d}])
            cat_rows = [{"Mês":mf,"Categoria":cat,"Saidas":val} for cat, val in cat_vals.items()]
            save_db(pd.concat([df_f, summary], ignore_index=True), "poupanca")
            save_db(pd.concat([df_desp, pd.DataFrame(cat_rows)], ignore_index=True), "despesas")
            st.rerun()

    # ── History ───────────────────────────────────────────────────────
    if not df_f.empty:
        st.markdown('<div class="section-label">Histórico</div>', unsafe_allow_html=True)
        for i, r in df_f.iterrows():
            net  = float(r["Entradas"]) - float(r["Saidas"])
            taxa = (net / float(r["Entradas"]) * 100) if float(r["Entradas"]) > 0 else 0
            nc   = "#059669" if net >= 0 else "#DC2626"

            cat_detail = ""
            if not df_desp.empty and "Categoria" in df_desp.columns:
                mc = df_desp[(df_desp["Mês"] == r["Mês"]) & (df_desp["Categoria"] != "_total_")]
                if not mc.empty:
                    parts = [f'{row["Categoria"]}: {float(row["Saidas"]):,.0f}€' for _, row in mc.iterrows() if float(row["Saidas"]) > 0]
                    cat_detail = " · ".join(parts[:3])

            if st.session_state.edit_flx == i:
                st.markdown('<div class="edit-bar">✏ A editar registo</div>', unsafe_allow_html=True)
                fe1, fe2 = st.columns(2)
                ne = fe1.number_input("Entradas", value=float(r["Entradas"]), format="%.2f", key=f"fei_{i}")
                ns = fe2.number_input("Saídas",   value=float(r["Saidas"]),   format="%.2f", key=f"fes_{i}")
                fb1, fb2 = st.columns(2)
                with fb1:
                    if st.button("✓ Guardar", key=f"fsv_{i}", type="primary"):
                        df_f.at[i,"Entradas"] = ne; df_f.at[i,"Saidas"] = ns
                        save_db(df_f, "poupanca"); st.session_state.edit_flx = None; st.rerun()
                with fb2:
                    if st.button("Cancelar", key=f"fca_{i}"):
                        st.session_state.edit_flx = None; st.rerun()
            else:
                cc, ce, cd = st.columns([10, 1, 1])
                with cc:
                    cat_suffix = "&nbsp;·&nbsp; " + cat_detail if cat_detail else ""
                    st.markdown(
                        '<div class="list-row">'
                        + '<div class="lr-left">'
                        + '<div class="lr-title">' + str(r["Mês"]) + '</div>'
                        + '<div class="lr-sub">↑ ' + f'{float(r["Entradas"]):,.0f}' + '€ &nbsp;·&nbsp; ↓ ' + f'{float(r["Saidas"]):,.0f}' + '€' + cat_suffix + '</div>'
                        + '</div>'
                        + '<div class="lr-right">'
                        + '<div class="lr-value" style="color:' + nc + ';">' + f'{net:,.0f}' + '€</div>'
                        + '<div class="lr-pct">' + f'{taxa:.1f}' + '%</div>'
                        + '</div>'
                        + '</div>',
                        unsafe_allow_html=True
                    )
                with ce:
                    if st.button("✏️", key=f"fe_{i}"):
                        st.session_state.edit_flx = i; st.rerun()
                with cd:
                    if st.button("🗑", key=f"fd_{i}"):
                        save_db(df_f.drop(i).reset_index(drop=True), "poupanca"); st.rerun()


# ══════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════
# ▌TAB 3 — PLANO TREINO
# ══════════════════════════════════════════════════════════════════════
with tab3:
    treino_path = f"{DATA_DIR}/treino_custom.csv"
    custom_plan = {}
    if os.path.exists(treino_path):
        try:
            df_tc = pd.read_csv(treino_path)
            for dia in TREINO:
                rows_dia = df_tc[df_tc["dia"] == dia]
                if not rows_dia.empty:
                    custom_plan[dia] = [(r["nome"], r["series"], r["desc"]) for _, r in rows_dia.iterrows()]
        except: pass

    # ── Week selector ─────────────────────────────────────────────────
    current_iso = datetime.now().isocalendar()[1]
    current_year = datetime.now().year

    # Build list of last 10 weeks (most recent first)
    week_options = []
    for delta in range(10):
        wn = current_iso - delta
        yr = current_year
        if wn <= 0:
            wn += 52
            yr -= 1
        label = "Semana " + str(wn) + (" (atual)" if delta == 0 else "")
        week_options.append((label, wn))

    week_labels = [w[0] for w in week_options]
    week_nums   = [w[1] for w in week_options]

    # Find index of currently selected week
    sel_wn = st.session_state.selected_week
    sel_idx = week_nums.index(sel_wn) if sel_wn in week_nums else 0

    sel_label = st.selectbox(
        "Semana",
        options=week_labels,
        index=sel_idx,
        key="week_selector",
        label_visibility="collapsed",
    )
    chosen_wn  = week_nums[week_labels.index(sel_label)]
    chosen_key = "w" + str(chosen_wn)

    # Persist selection and init state for chosen week
    if st.session_state.selected_week != chosen_wn:
        st.session_state.selected_week = chosen_wn
        st.session_state.treino_edit   = False
        st.rerun()

    if chosen_key not in st.session_state:
        st.session_state[chosen_key] = {}

    # ── Weekly progress card ───────────────────────────────────────────
    total_ex   = sum(len(custom_plan.get(d, TREINO[d]["ex"])) for d in TREINO)
    total_done = sum(
        1 for d in TREINO
        for idx in range(len(custom_plan.get(d, TREINO[d]["ex"])))
        if st.session_state[chosen_key].get(d + "_" + str(idx), False)
    )
    wpct = int(total_done / total_ex * 100) if total_ex > 0 else 0
    wc   = "#059669" if wpct == 100 else "#2563EB" if wpct > 0 else "#CBD5E1"
    wlbl = "✓ Semana completa!" if wpct == 100 else str(total_done) + " de " + str(total_ex) + " exercícios"

    card_html = (
        '<div class="card" style="margin-bottom:14px;">'
        + '<div class="card-body">'
        + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">'
        + '<div>'
        + '<div style="font-size:16px;font-weight:800;color:#0F172A;">Semana ' + str(chosen_wn) + ('&nbsp;<span style="font-size:11px;font-weight:600;color:#2563EB;background:#EFF6FF;padding:2px 8px;border-radius:20px;">atual</span>' if chosen_wn == current_iso else '') + '</div>'
        + '<div style="font-size:12px;color:#94A3B8;margin-top:2px;">3× semana &nbsp;·&nbsp; Seg · Qua · Sex</div>'
        + '</div>'
        + '<div style="font-size:28px;font-weight:900;color:' + wc + ';letter-spacing:-1px;">' + str(wpct) + '<span style="font-size:0.5em;opacity:0.6;font-weight:500;">%</span></div>'
        + '</div>'
        + '<div class="prog-track">'
        + '<div class="prog-fill" style="width:' + str(wpct) + '%;background:' + wc + ';"></div>'
        + '</div>'
        + '<div style="font-size:11px;color:#94A3B8;margin-top:6px;">' + wlbl + '</div>'
        + '</div></div>'
    )

    ch, ce = st.columns([9, 1])
    with ch:
        st.markdown(card_html, unsafe_allow_html=True)
    with ce:
        st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
        if st.button("✏️", key="btn_treino_edit"):
            st.session_state.treino_edit = not st.session_state.treino_edit
            st.rerun()

    # ── Edit mode ─────────────────────────────────────────────────────
    if st.session_state.treino_edit:
        st.markdown('<div class="edit-bar">✏ Modo edição — altera nome, séries ou notas</div>', unsafe_allow_html=True)
        edited = {}
        for dia, dados in TREINO.items():
            exs = custom_plan.get(dia, dados["ex"])
            st.markdown(
                '<div style="font-size:13px;font-weight:800;color:' + dados["cor"] + ';margin:16px 0 8px;">'
                + dia + ' — ' + dados["sub"] + '</div>',
                unsafe_allow_html=True
            )
            edited[dia] = []
            for idx, (nome, series, desc) in enumerate(exs):
                c1, c2, c3 = st.columns([3, 2, 4])
                n = c1.text_input("", value=nome,   key="tn_" + dia + "_" + str(idx), placeholder="Nome")
                s = c2.text_input("", value=series, key="ts_" + dia + "_" + str(idx), placeholder="Séries")
                d = c3.text_input("", value=desc,   key="td_" + dia + "_" + str(idx), placeholder="Notas")
                edited[dia].append((n, s, d))
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        sc1, sc2 = st.columns(2)
        with sc1:
            if st.button("✓ Guardar Plano", key="save_treino", type="primary"):
                save_rows = [{"dia": dia, "nome": n, "series": s, "desc": d}
                             for dia, exs in edited.items() for n, s, d in exs]
                pd.DataFrame(save_rows).to_csv(treino_path, index=False)
                st.session_state.treino_edit = False
                st.rerun()
        with sc2:
            if st.button("Cancelar", key="cancel_treino"):
                st.session_state.treino_edit = False
                st.rerun()

    else:
        # ── Display mode ──────────────────────────────────────────────
        for dia, dados in TREINO.items():
            exs   = custom_plan.get(dia, dados["ex"])
            cor   = dados["cor"]
            done  = sum(1 for idx in range(len(exs)) if st.session_state[chosen_key].get(dia + "_" + str(idx), False))
            total = len(exs)
            pct   = int(done / total * 100) if total > 0 else 0
            bc    = "#059669" if pct == 100 else cor if pct > 0 else "#CBD5E1"

            badge_bg  = "#ECFDF5" if pct == 100 else cor + "22" if pct > 0 else "#F8FAFC"
            badge_txt = "#059669" if pct == 100 else cor         if pct > 0 else "#94A3B8"
            badge_lbl = "✓ Completo" if pct == 100 else str(done) + "/" + str(total)

            if dados["warmup"]:
                wu_joined   = " · ".join(dados["warmup"])
                warmup_html = '<div class="warmup-strip" style="margin:0 18px 8px;"><strong>Aquecimento &nbsp;</strong>' + wu_joined + '</div>'
            else:
                warmup_html = ""

            day_html = (
                '<div class="day-card" style="border-top:3px solid ' + cor + '; margin-bottom:4px;">'
                + '<div class="day-header">'
                + '<div>'
                + '<div class="day-title">' + dia + '</div>'
                + '<div class="day-sub">' + dados["sub"] + '</div>'
                + '</div>'
                + '<div class="day-badge" style="background:' + badge_bg + ';color:' + badge_txt + ';">' + badge_lbl + '</div>'
                + '</div>'
                + '<div style="padding:0 18px 8px;">'
                + '<div class="prog-track">'
                + '<div class="prog-fill" style="width:' + str(pct) + '%;background:' + bc + ';"></div>'
                + '</div></div>'
                + warmup_html
                + '</div>'
            )
            st.markdown(day_html, unsafe_allow_html=True)

            for idx, (nome, series, desc) in enumerate(exs):
                ck      = dia + "_" + str(idx)
                done_ex = st.session_state[chosen_key].get(ck, False)

                col_info, col_btn = st.columns([5, 1])
                with col_info:
                    opacity     = "0.35" if done_ex else "1"
                    name_style  = "text-decoration:line-through;color:#94A3B8;" if done_ex else "font-weight:600;color:#0F172A;"
                    badge_style = "background:#F1F5F9;color:#94A3B8;" if done_ex else "background:" + cor + "18;color:" + cor + ";"
                    desc_block  = '<div style="font-size:11px;color:#94A3B8;margin-top:2px;">' + desc + '</div>' if desc else ""
                    row_html = (
                        '<div style="padding:10px 0 10px 4px;opacity:' + opacity + ';transition:opacity 0.2s;">'
                        + '<div style="font-size:14px;' + name_style + '">' + nome + '</div>'
                        + '<span style="font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;' + badge_style + '">' + series + '</span>'
                        + desc_block
                        + '</div>'
                    )
                    st.markdown(row_html, unsafe_allow_html=True)

                with col_btn:
                    btn_label = "✓" if done_ex else "○"
                    if st.button(btn_label, key="ck_" + ck + "_" + chosen_key):
                        st.session_state[chosen_key][ck] = not done_ex
                        st.rerun()

            if dados["nota"]:
                st.markdown('<div class="note-strip" style="margin:4px 0 16px;">' + dados["nota"] + '</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("↺ Reiniciar Semana " + str(chosen_wn), key="reset_week"):
            st.session_state[chosen_key] = {}
            st.rerun()

# ▌TAB 4 — ANÁLISE DE AÇÕES
# ══════════════════════════════════════════════════════════════════════
with tab4:
    ci, cb = st.columns([5, 1])
    with ci:
        ticker_input = st.text_input(
            "", placeholder="Ticker — AAPL · NVDA · GOOGL · EDP.LS",
            label_visibility="collapsed", key="ticker_field"
        ).strip().upper()
    with cb:
        do_scan = st.button("Scan", key="btn_scan")

    if do_scan and ticker_input:
        st.session_state.ticker = ticker_input
    use_ticker = st.session_state.ticker

    if use_ticker:
        with st.spinner(f"A carregar {use_ticker}..."):
            info, err = fetch_info(use_ticker)

        if err:
            st.error(err)
        else:
            price    = sg(info,"currentPrice","regularMarketPrice","previousClose",default=0)
            sector   = info.get("sector","")   or "N/A"
            industry = info.get("industry","") or ""
            name     = info.get("longName") or info.get("shortName","") or use_ticker
            currency = info.get("currency","USD")
            prev_c   = sg(info,"previousClose","regularMarketPreviousClose",default=price)
            day_d    = price - prev_c
            day_p    = (day_d / prev_c * 100) if prev_c > 0 else 0
            ds       = "+" if day_d >= 0 else ""
            dc       = "#059669" if day_d >= 0 else "#DC2626"

            # Stock header card
            industry_chip = '<span class="chip chip-grey">' + industry[:24] + '</span>' if industry else ""
            st.markdown(
                '<div class="card fade-up"><div class="card-body"><div class="stock-header">'
                + '<div style="flex:1;min-width:0;">'
                + '<div class="stock-name">' + name + '</div>'
                + '<div class="stock-meta">'
                + '<span class="stock-ticker">' + use_ticker + '</span>'
                + '<span class="chip chip-blue">' + sector + '</span>'
                + industry_chip
                + '</div></div>'
                + '<div style="text-align:right;flex-shrink:0;">'
                + '<div class="stock-price">' + f"{price:.2f}" + '</div>'
                + '<div class="stock-change" style="color:' + dc + ';">' + ds + f"{day_d:.2f}" + ' &nbsp; ' + ds + f"{day_p:.2f}" + '%</div>'
                + '</div></div></div></div>',
                unsafe_allow_html=True
            )

            # Run engines
            iv_res = intrinsic_value(info, sector)
            iv     = iv_res["iv"]
            upside = ((iv / price) - 1) * 100 if price > 0 and iv > 0 else 0
            checks, score, n_ch, verdict, vc, vbg, vborder, vicon, vdesc = run_checklist(info, iv, price)

            # Verdict
            st.markdown(
                '<div class="verdict-wrap fade-up" style="background:' + vbg + ';border:1.5px solid ' + vborder + ';">'
                + '<div class="verdict-icon" style="background:' + vc + '20;color:' + vc + ';">' + vicon + '</div>'
                + '<div>'
                + '<div class="verdict-title" style="color:' + vc + ';">' + verdict + '</div>'
                + '<div class="verdict-desc" style="color:' + vc + ';">' + vdesc + '</div>'
                + '</div>'
                + '<div style="margin-left:auto;text-align:right;flex-shrink:0;">'
                + '<div style="font-size:22px;font-weight:900;color:' + vc + ';letter-spacing:-0.5px;">' + str(score) + '<span style="font-size:0.55em;opacity:0.5;">/' + str(n_ch) + '</span></div>'
                + '<div style="font-size:10px;color:' + vc + ';opacity:0.6;font-weight:600;letter-spacing:1px;">CRITÉRIOS</div>'
                + '</div></div>',
                unsafe_allow_html=True
            )

            # Key metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Preço",            f"{price:.2f} {currency}")
            m2.metric("Valor Intrínseco", f"{iv:.2f}" if iv > 0 else "N/A",
                      delta=f"{upside:+.1f}%" if iv > 0 else None)
            m3.metric("Modelo",           iv_res["label"])

            # Checklist by category
            st.markdown('<div class="section-label" style="margin-top:20px;">Análise Detalhada</div>', unsafe_allow_html=True)
            cats = ["Crescimento","Margem","Retorno","Qualidade","Valuation","Risco"]
            for cat in cats:
                cc_items = [(l, p, v) for c, l, p, v in checks if c == cat]
                if not cc_items: continue
                cs = sum(1 for _, p, _ in cc_items if p); ct = len(cc_items)
                cc_col = "#059669" if cs==ct else "#D97706" if cs>0 else "#DC2626"
                chip_cls = "chip chip-green" if cs == ct else "chip chip-yellow" if cs > 0 else "chip chip-red"
                html = f"""
                    <div class="card" style="margin-bottom:8px;">
                        <div class="card-body-sm">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                                <span style="font-size:11px;font-weight:700;color:#374151;letter-spacing:1px;">{cat.upper()}</span>
                                <span class="{chip_cls}">{cs}/{ct}</span>
                            </div>
                """
                for label, passed, val in cc_items:
                    ic  = "✓" if passed else "✕"
                    ibc = "#059669" if passed else "#DC2626"
                    ibg = "#ECFDF5" if passed else "#FEF2F2"
                    html += f'<div class="mrow"><span class="lbl">{label}</span><div style="display:flex;align-items:center;gap:8px;"><span class="val">{val}</span><div style="width:20px;height:20px;border-radius:50%;background:{ibg};display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;color:{ibc};">{ic}</div></div></div>'
                html += "</div></div>"
                st.markdown(html, unsafe_allow_html=True)

            # Valuation detail
            if iv_res["rows"]:
                html = f"""
                    <div class="card" style="margin-bottom:8px;">
                        <div class="card-body-sm">
                            <div style="font-size:11px;font-weight:700;color:#374151;letter-spacing:1px;margin-bottom:8px;">{iv_res["label"].upper()}</div>
                """
                for k, v in iv_res["rows"]:
                    html += f'<div class="mrow"><span class="lbl">{k}</span><span class="val" style="color:#2563EB;">{v}</span></div>'
                if iv > 0:
                    uc = "#059669" if upside > 15 else "#D97706" if upside > -10 else "#DC2626"
                    html += f'<div class="mrow" style="padding-top:12px;border-top:2px solid #F1F5F9;margin-top:4px;"><span style="font-weight:700;color:#0F172A;font-size:13px;">Upside / Downside</span><span style="font-size:18px;font-weight:900;color:{uc};letter-spacing:-0.5px;">{upside:+.1f}%</span></div>'
                html += "</div></div>"
                st.markdown(html, unsafe_allow_html=True)

            # All metrics expander
            with st.expander("Todas as métricas"):
                def fB(v): return f"${float(v)/1e9:.2f}B" if v and float(v)!=0 else "N/A"
                def fP(v): return f"{float(v)*100:.1f}%" if v and float(v)!=0 else "N/A"
                def fX(v): return f"{float(v):.2f}×" if v and float(v)!=0 else "N/A"
                def fF(v): return f"{float(v):.2f}" if v and float(v)!=0 else "N/A"
                rows_all = [
                    ("PREÇO","",""),
                    ("Preço Atual",    f"{price:.2f} {currency}",""),
                    ("52W Alto",       fF(sg(info,"fiftyTwoWeekHigh",default=0)),""),
                    ("52W Baixo",      fF(sg(info,"fiftyTwoWeekLow",default=0)),""),
                    ("EPS TTM",        fF(sg(info,"trailingEps",default=0)),""),
                    ("EPS Fwd",        fF(sg(info,"forwardEps",default=0)),""),
                    ("VALUATION","",""),
                    ("P/E TTM",        fX(sg(info,"trailingPE",default=0)),""),
                    ("P/E Fwd",        fX(sg(info,"forwardPE",default=0)),""),
                    ("PEG",            fF(sg(info,"pegRatio",default=0)),""),
                    ("P/S",            fX(sg(info,"priceToSalesTrailing12Months",default=0)),""),
                    ("P/B",            fX(sg(info,"priceToBook",default=0)),""),
                    ("EV/EBITDA",      fX(sg(info,"enterpriseToEbitda",default=0)),""),
                    ("CRESCIMENTO","",""),
                    ("Receita YoY",    fP(sg(info,"revenueGrowth",default=0)),""),
                    ("Lucro YoY",      fP(sg(info,"earningsGrowth",default=0)),""),
                    ("RENTABILIDADE","",""),
                    ("Margem Bruta",   fP(sg(info,"grossMargins",default=0)),""),
                    ("Margem Líquida", fP(sg(info,"profitMargins",default=0)),""),
                    ("ROE",            fP(sg(info,"returnOnEquity",default=0)),""),
                    ("ROA",            fP(sg(info,"returnOnAssets",default=0)),""),
                    ("BALANÇO","",""),
                    ("Receita",        fB(info.get("totalRevenue",0)),""),
                    ("EBITDA",         fB(info.get("ebitda",0)),""),
                    ("Lucro Líq.",     fB(info.get("netIncomeToCommon",0)),""),
                    ("Free Cash Flow", fB(info.get("freeCashflow",0)),""),
                    ("Caixa",          fB(info.get("totalCash",0)),""),
                    ("Dívida Total",   fB(info.get("totalDebt",0)),""),
                    ("Current Ratio",  fX(sg(info,"currentRatio",default=0)),""),
                    ("RISCO","",""),
                    ("Beta",           fF(sg(info,"beta",default=0)),""),
                    ("Yield",          fP(sg(info,"dividendYield",default=0)),""),
                    ("ANALISTAS","",""),
                    ("Preço Alvo",     fF(sg(info,"targetMeanPrice",default=0)),""),
                    ("Recomendação",   (info.get("recommendationKey","") or "N/A").upper(),""),
                ]
                cm1, cm2 = st.columns(2)
                for idx, (k, v, _) in enumerate(rows_all):
                    if not v:  # section header
                        for col in [cm1, cm2]:
                            col.markdown(f'<div style="font-size:10px;font-weight:700;letter-spacing:1.5px;color:#CBD5E1;margin:14px 0 6px;">{k}</div>', unsafe_allow_html=True)
                    else:
                        (cm1 if idx % 2 == 0 else cm2).markdown(
                            f'<div class="mrow"><span class="lbl">{k}</span><span class="val">{v}</span></div>',
                            unsafe_allow_html=True
                        )
    else:
        st.markdown("""
            <div class="empty-state fade-up">
                <div class="icon">◈</div>
                <div class="title">Análise Fundamentalista</div>
                <div class="sub">Insere um ticker e clica Scan</div>
                <div style="margin-top:16px;font-size:12px;color:#CBD5E1;letter-spacing:0.5px;">AAPL &nbsp;·&nbsp; GOOGL &nbsp;·&nbsp; NVDA &nbsp;·&nbsp; MSFT &nbsp;·&nbsp; EDP.LS</div>
            </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
    <div style="text-align:center;padding:28px 0 20px;font-size:11px;color:#CBD5E1;letter-spacing:0.5px;">
        F|QUANT &nbsp;·&nbsp; Personal Edition
    </div>
""", unsafe_allow_html=True)
