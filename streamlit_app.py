import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

st.set_page_config(page_title="FFA Trading Dashboard", layout="wide")
st.title("Baltic Index & Fuel Price Data Viewer")

EXPECTED_COLUMNS = [
    'Date','C2','C3','C5','C7','C17','C2TCE','C3TCE','C5TCE','C7TCE','C17TCE',
    'C8','C9','C10','C14','C16','C5TC','Singapore','Rotterdam','Zhoushan'
]

@st.cache_data(show_spinner=False)
def load_csv(file_bytes: bytes) -> pd.DataFrame:
    txt = file_bytes.decode('utf-8', errors='ignore')
    df_l = pd.read_csv(StringIO(txt))
    df_l.columns = [c.strip() for c in df_l.columns]
    date_col = next((c for c in df_l.columns if c.lower()=="date"), df_l.columns[0])
    df_l = df_l.rename(columns={date_col:'Date'})
    df_l['Date'] = pd.to_datetime(df_l['Date'], errors='coerce')
    df_l = df_l.dropna(subset=['Date'])
    keep = [c for c in EXPECTED_COLUMNS if c in df_l.columns]
    return df_l[['Date'] + [c for c in keep if c!='Date']].sort_values('Date')

up = st.file_uploader("Upload Baltic/Fuel CSV", type=['csv'])
if up is None:
    st.info("Upload a CSV to begin.")
    st.stop()

try:
    df = load_csv(up.getvalue())
except Exception as e:
    st.error(f"Failed to parse file: {e}")
    st.stop()

if df.empty:
    st.warning("Dataset empty after cleaning.")
    st.stop()

st.sidebar.header("Filters")
min_d, max_d = df['Date'].min(), df['Date'].max()
sel = st.sidebar.date_input("Date Range", value=(min_d.date(), max_d.date()), min_value=min_d.date(), max_value=max_d.date())
if isinstance(sel,(list,tuple)) and len(sel)==2:
    start_d,end_d = sel
else:
    start_d=end_d=min_d.date()
mask = (df['Date']>=pd.to_datetime(start_d)) & (df['Date']<=pd.to_datetime(end_d))
dfv = df[mask].copy()

index_cols = [c for c in ['C5TC','C2TCE','C3TCE','C5TCE','C7TCE','C17TCE'] if c in dfv.columns]
voyage_cols = [c for c in ['C2','C3','C5','C7','C17','C8','C9','C10','C14','C16'] if c in dfv.columns]
fuel_cols  = [c for c in ['Singapore','Rotterdam','Zhoushan'] if c in dfv.columns]

st.subheader("Four Chart Panel")
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

def _plot_lines(columns, title, ax):
    if not columns:
        ax.set_title(f"{title} (no data)")
        return
    for c in columns:
        sub = dfv[['Date', c]].dropna()
        if sub.empty: 
            continue
        ax.plot(sub['Date'], sub[c], label=c)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)

with row1_col1:
    fig_a, ax_a = plt.subplots(figsize=(8,3.2))
    _plot_lines(index_cols, "Index Group", ax_a)
    st.pyplot(fig_a, clear_figure=True)
with row1_col2:
    fig_b, ax_b = plt.subplots(figsize=(8,3.2))
    _plot_lines(voyage_cols, "Voyage Routes", ax_b)
    st.pyplot(fig_b, clear_figure=True)
with row2_col1:
    fig_c, ax_c = plt.subplots(figsize=(8,3.2))
    _plot_lines(fuel_cols, "Fuel Prices", ax_c)
    st.pyplot(fig_c, clear_figure=True)
with row2_col2:
    fig_d, ax_d = plt.subplots(figsize=(8,3.2))
    if 'Singapore' in fuel_cols and any(fc in fuel_cols for fc in ['Rotterdam','Zhoushan']):
        base = dfv[['Date','Singapore']].dropna().rename(columns={'Singapore':'Base'})
        spread_plotted = False
        for other in ['Rotterdam','Zhoushan']:
            if other in fuel_cols:
                other_df = dfv[['Date',other]].dropna().rename(columns={other:'Other'})
                merged = pd.merge(base, other_df, on='Date', how='inner')
                if merged.empty: 
                    continue
                merged['Spread'] = merged['Base'] - merged['Other']
                ax_d.plot(merged['Date'], merged['Spread'], label=f"Singapore - {other}")
                spread_plotted = True
        if spread_plotted:
            ax_d.axhline(0, color='black', linewidth=1)
            ax_d.set_title('Fuel Spreads')
            ax_d.grid(True, alpha=0.3)
            ax_d.legend(fontsize=7)
        else:
            ax_d.set_title('Fuel Spreads (insufficient data)')
    else:
        ax_d.set_title('Fuel Spreads (need Singapore + other)')
    st.pyplot(fig_d, clear_figure=True)

st.caption("Panel layout: Index Group | Voyage Routes on first row; Fuel Prices | Fuel Spreads on second row.")

st.subheader("Statistics")

def _stats(cols):
    rows=[]
    for c in cols:
        s=dfv[c].dropna(); rows.append({'Column':c,'Count':int(s.count()),'Min':float(s.min()) if not s.empty else np.nan,'Max':float(s.max()) if not s.empty else np.nan,'Mean':float(s.mean()) if not s.empty else np.nan})
    return pd.DataFrame(rows)

tab1,tab2,tab3 = st.tabs(["Indices","Voyage","Fuel"])
with tab1: st.dataframe(_stats(index_cols), use_container_width=True, hide_index=True)
with tab2: st.dataframe(_stats(voyage_cols), use_container_width=True, hide_index=True)
with tab3: st.dataframe(_stats(fuel_cols), use_container_width=True, hide_index=True)

st.download_button("Download Filtered CSV", dfv.to_csv(index=False).encode('utf-8'), file_name="baltic_filtered.csv", mime='text/csv')

st.caption("Core viewer: upload CSV, filter dates, view charts & stats.")
