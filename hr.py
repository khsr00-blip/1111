"""
streamlit_hr_diagram_safe.py

안정화된 H-R 다이어그램 Streamlit 앱
- CSV 컬럼 이름이 다양해도 안전하게 처리
- KeyError 방지 및 컬럼 매핑을 사이드바에서 직접 선택 가능
- 의존성: streamlit, pandas, numpy, plotly(optional)
"""

import streamlit as st
import pandas as pd
import numpy as np
import math

try:
    import plotly.express as px
    _HAS_PLOTLY = True
except ImportError:
    _HAS_PLOTLY = False

st.set_page_config(page_title='H-R Diagram Explorer', layout='wide')

# ----------------------
# Sample data
# ----------------------
SAMPLE = pd.DataFrame([
    {'name': 'Sun', 'Teff': 5772, 'Radius_Rsun': 1.0, 'Mbol': 4.74},
    {'name': 'Sirius A', 'Teff': 9900, 'Radius_Rsun': 1.71, 'Mbol': 1.42},
    {'name': 'Vega', 'Teff': 9600, 'Radius_Rsun': 2.362, 'Mbol': 0.58},
    {'name': 'Arcturus', 'Teff': 4286, 'Radius_Rsun': 25.4, 'Mbol': -0.30},
    {'name': 'Betelgeuse', 'Teff': 3500, 'Radius_Rsun': 887, 'Mbol': -5.85},
    {'name': 'Rigel', 'Teff': 11000, 'Radius_Rsun': 78.9, 'Mbol': -7.84},
])

# ----------------------
# Sidebar: CSV upload and column mapping
# ----------------------
st.sidebar.header('Data Upload & Column Mapping')
uploaded = st.sidebar.file_uploader('Upload CSV (optional)', type=['csv'])
use_sample = st.sidebar.checkbox('Use sample dataset', value=True)

# Load data
if uploaded is not None:
    df = pd.read_csv(uploaded)
elif use_sample:
    df = SAMPLE.copy()
else:
    st.info('Upload a CSV or enable sample dataset.')
    st.stop()

# ----------------------
# Column mapping UI
# ----------------------
st.sidebar.subheader('Column Mapping')
cols = list(df.columns)
name_col = st.sidebar.selectbox('Name column', options=[None]+cols, index=cols.index('name') if 'name' in cols else 0)
teff_col = st.sidebar.selectbox('Teff column', options=[None]+cols)
bv_col = st.sidebar.selectbox('B-V column', options=[None]+cols)
spec_col = st.sidebar.selectbox('Spectral column', options=[None]+cols)
radius_col = st.sidebar.selectbox('Radius column', options=[None]+cols)
mv_col = st.sidebar.selectbox('mV column', options=[None]+cols)
dist_col = st.sidebar.selectbox('Distance column', options=[None]+cols)
mbol_col = st.sidebar.selectbox('Mbol column', options=[None]+cols)

# ----------------------
# Prepare working DataFrame
# ----------------------
work = pd.DataFrame()
if name_col:
    work['name'] = df[name_col].astype(str)
else:
    work['name'] = df.index.astype(str)

def safe_numeric(col):
    if col and col in df.columns:
        return pd.to_numeric(df[col], errors='coerce')
    else:
        return np.nan

work['Teff'] = safe_numeric(teff_col)
work['B-V'] = safe_numeric(bv_col)
work['Radius_Rsun'] = safe_numeric(radius_col)
work['mV'] = safe_numeric(mv_col)
work['distance_pc'] = safe_numeric(dist_col)
work['Mbol_input'] = safe_numeric(mbol_col)

# ----------------------
# Derived quantities
# ----------------------
SIGMA = 5.670374419e-8
R_SUN = 6.957e8
L_SUN = 3.828e26
M_BOL_SUN = 4.74

def luminosity_from_tr(teff, radius):
    try:
        L = 4 * math.pi * (radius*R_SUN)**2 * SIGMA * teff**4
        return L / L_SUN
    except:
        return np.nan

work['L/Lsun'] = [luminosity_from_tr(row['Teff'], row['Radius_Rsun']) if not pd.isna(row['Teff']) and not pd.isna(row['Radius_Rsun']) else np.nan for idx, row in work.iterrows()]
work['logL'] = np.log10(work['L/Lsun'].replace({0: np.nan}))
work['logTeff'] = np.log10(work['Teff'].replace({0: np.nan}))

# ----------------------
# Plot
# ----------------------
st.subheader('H-R Diagram')
plot_df = work.dropna(subset=['logTeff','logL'])
if plot_df.empty:
    st.warning('No valid data for plotting. Check your column mapping.')
else:
    if _HAS_PLOTLY:
        fig = px.scatter(plot_df, x='logTeff', y='logL', hover_name='name', title='H-R Diagram')
        fig.update_xaxes(autorange='reversed')
        st.plotly_chart(fig, use_container_width=True)
    else:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.scatter(plot_df['logTeff'], plot_df['logL'])
        ax.invert_xaxis()
        ax.set_xlabel('logTeff')
        ax.set_ylabel('logL')
        st.pyplot(fig)

# ----------------------
# Data download
# ----------------------
csv_bytes = work.to_csv(index=False).encode('utf-8')
st.download_button('Download processed data (CSV)', data=csv_bytes, file_name='hr_processed.csv')
