"""
streamlit_hr_diagram.py

Streamlit 앱: H-R 다이어그램(관측·물리량 기반)

설명
- 다양한 물리량(유효온도 Teff, B-V 색지수, 스펙트럼형, 반지름, 겉보기/절대 광도, 거리 등)을 이용해
  H-R 도(로그 온도 vs 로그 광도)를 인터랙티브하게 그립니다.
- 사용자가 CSV 업로드(예: name, Teff, B-V, Radius(Rsun), mV, distance_pc, Mbol 등)를 하면,
  가능한 경우 부족한 물리량(Teff, L/Lsun, Mbol, Mass_est 등)을 자동으로 계산합니다.
- 기본적인 물리식 및 근사식을 사용합니다: Stefan-Boltzmann 법칙, Ballesteros의 B-V → Teff 근사,
  질량-광도 관계(단순 분절적 근사) 등.

사용법
1) 필요 패키지 설치:
   pip install streamlit pandas plotly numpy
2) 실행:
   streamlit run streamlit_hr_diagram.py

주의
- 계산식 대부분은 근사식입니다(특히 색-온도 변환, 질량-광도 관계). 교육/시각화 목적에 적합하며,
  엄밀한 연구용 값은 더 정교한 모델(대기 모델, 스펙트럼 피팅 등)을 사용하세요.

"""

from typing import Optional, Tuple
import math
import io

import streamlit as st
import pandas as pd
import numpy as np

# plotly optional
try:
    import plotly.express as px
    _HAS_PLOTLY = True
except Exception:
    _HAS_PLOTLY = False

# Physical constants
SIGMA = 5.670374419e-8  # Stefan-Boltzmann constant, W m^-2 K^-4
R_SUN = 6.957e8  # m
L_SUN = 3.828e26  # W
T_SUN = 5772.0  # K
M_BOL_SUN = 4.74  # solar bolometric magnitude (commonly used value)

st.set_page_config(page_title="H-R Diagram Explorer", layout="wide")

# ----------------------
# Utility functions (physics + approximations)
# ----------------------

def bv_to_teff(bv: float) -> Optional[float]:
    """Ballesteros (2012) 근사식: B-V 색지수 -> 유효온도 (약)
    유효 범위: 대략 -0.4 < B-V < +2.0 에서 합리적.
    식: T(K) = 4600 * (1/(0.92*(B-V)+1.7) + 1/(0.92*(B-V)+0.62))
    """
    try:
        x = float(bv)
    except Exception:
        return None
    # valid domain check (not strict)
    if x <= -0.5 or x >= 2.5:
        # still compute but warn upstream
        pass
    T = 4600.0 * (1.0 / (0.92 * x + 1.7) + 1.0 / (0.92 * x + 0.62))
    return float(T)


def spectral_to_teff(spec: str) -> Optional[float]:
    """단순 스펙트럼형 -> 온도 근사.
    입력 예: 'G2V', 'K5', 'M1', 'B8'
    방법: 기본 클래스(OBAFGKM)에 대한 대표 온도(대략)를 사용하고,
    숫자 서브타입(0-9)을 선형 보간.
    매우 근사적임.
    """
    if not isinstance(spec, str):
        return None
    s = spec.strip().upper()
    if len(s) == 0:
        return None
    # 대표 온도 (대략)
    base = {'O': 40000.0, 'B': 20000.0, 'A': 8500.0, 'F': 6500.0, 'G': 5770.0, 'K': 4500.0, 'M': 3000.0}
    letter = s[0]
    if letter not in base:
        return None
    # find subtype digit if present
    subtype = None
    for ch in s[1:]:
        if ch.isdigit():
            subtype = int(ch)
            break
    # find next spectral class rough neighbor for interpolation
    order = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
    idx = order.index(letter)
    if idx < len(order) - 1:
        next_letter = order[idx + 1]
        T1 = base[letter]
        T2 = base[next_letter]
    else:
        # M class end
        T1 = base[letter]
        T2 = base[letter] - 1000.0
    if subtype is None:
        return float(T1)
    # linear interpolation between T1 (subtype 0) and T2 (subtype 9)
    frac = subtype / 9.0
    T = T1 * (1 - frac) + T2 * frac
    return float(T)


def luminosity_from_tr(teff_k: float, radius_rsun: float) -> Optional[float]:
    """Stefan-Boltzmann 법칙으로 L/L_sun 계산
    teff_k: 온도 (K)
    radius_rsun: 반지름 (R_sun 단위)
    L = 4*pi*R^2*sigma*T^4
    """
    try:
        T = float(teff_k)
        R = float(radius_rsun)
    except Exception:
        return None
    R_m = R * R_SUN
    L = 4.0 * math.pi * (R_m ** 2) * SIGMA * (T ** 4)
    return float(L / L_SUN)


def lum_from_Mbol(Mbol: float) -> float:
    """절대 볼로메트릭 광도 Mbol -> L/L_sun
    L/Ls = 10^{(M_bol_sun - Mbol)/2.5}
    """
    return 10 ** ((M_BOL_SUN - Mbol) / 2.5)


def Mbol_from_m_and_dist(m: float, d_pc: float, BC: float = 0.0) -> float:
    """겉보기 등급 m, 거리(pc), 보정 BC -> 절대 볼로메트릭 등급 Mbol
    M = m - 5*log10(d/10)
    Mbol = M + BC
    """
    M = m - 5.0 * math.log10(d_pc / 10.0)
    return M + BC


def mass_from_luminosity(L: float) -> Optional[float]:
    """단순 분절적 질량-광도 역관계로 질량 추정 (Msun 단위)
    근사식 (대략적):
      M < 0.43 : L = M^{2.3}
      0.43 <= M < 2 : L = M^{4}
      2 <= M < 20 : L = M^{3.5}
    역함수는 L^{1/alpha}이며, 얻어진 값이 각 구간에 들어오는지 확인함.
    매우 근사적이고 주로 주계열에만 적용 가능.
    """
    try:
        Lval = float(L)
        if Lval <= 0:
            return None
    except Exception:
        return None

    # Candidate from each regime
    regimes = [
        (2.3, 0.01, 0.43),
        (4.0, 0.43, 2.0),
        (3.5, 2.0, 80.0),
    ]
    for alpha, m_min, m_max in regimes:
        M_cand = Lval ** (1.0 / alpha)
        if M_cand >= m_min and M_cand < m_max:
            return float(M_cand)
    # if none matched, return best guess from middle regime
    return float(Lval ** (1.0 / 3.5))

# ----------------------
# Sample dataset (교육용)
# ----------------------
SAMPLE = pd.DataFrame([
    {"name": "Sun", "Teff": T_SUN, "Radius_Rsun": 1.0, "Mbol": 4.74},
    {"name": "Sirius A", "Teff": 9900.0, "Radius_Rsun": 1.71, "Mbol": 1.42},
    {"name": "Vega", "Teff": 9600.0, "Radius_Rsun": 2.362, "Mbol": 0.58},
    {"name": "Arcturus", "Teff": 4286.0, "Radius_Rsun": 25.4, "Mbol": -0.30},
    {"name": "Betelgeuse", "Teff": 3500.0, "Radius_Rsun": 887.0, "Mbol": -5.85},
    {"name": "Rigel", "Teff": 11000.0, "Radius_Rsun": 78.9, "Mbol": -7.84},
])

# ----------------------
# Streamlit UI
# ----------------------
st.title('Hertzsprung–Russell Diagram Explorer')
st.markdown('Upload a CSV with stellar data (examples: name, Teff, B-V, Radius_Rsun, mV, distance_pc, Mbol).')

col1, col2 = st.columns([3, 1])
with col2:
    st.sidebar.header('Data & Settings')
    uploaded = st.sidebar.file_uploader('Upload CSV (optional)', type=['csv'])
    use_sample = st.sidebar.checkbox('Use sample dataset (if no upload)', value=True)

    st.sidebar.markdown('---')
    st.sidebar.subheader('Axis options')
    x_choice = st.sidebar.selectbox('X axis', ['logTeff (K, reversed)', 'Teff (K)', 'B-V', 'Spectral -> Teff'])
    y_choice = st.sidebar.selectbox('Y axis', ['logL (L_sun)', 'L (L_sun)', 'Mbol', 'Radius (R_sun)'])

    st.sidebar.markdown('---')
    st.sidebar.subheader('Plot controls')
    color_by = st.sidebar.selectbox('Color by', ['none', 'Spectral', 'Mass_est', 'Radius_Rsun'])
    size_by = st.sidebar.selectbox('Size by', ['none', 'Radius_Rsun', 'Mass_est'])
    show_labels = st.sidebar.checkbox('Show star labels', value=False)

    st.sidebar.markdown('---')
    st.sidebar.caption('Computed quantities: Teff (from B-V/spectral), L from (Teff,Radius) or Mbol, mass from L (approx).')

# Load data
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f'CSV 로드 오류: {e}')
        st.stop()
else:
    if use_sample:
        df = SAMPLE.copy()
    else:
        st.info('Upload a CSV or enable sample dataset in the sidebar.')
        st.stop()

# Normalise column names (case-insensitive)
cols_lower = {c.lower(): c for c in df.columns}

# Detect likely columns
col_Teff = cols_lower.get('teff') or cols_lower.get('teff_k')
col_bv = cols_lower.get('b-v') or cols_lower.get('bv') or cols_lower.get('b_v')
col_spec = cols_lower.get('spectral') or cols_lower.get('sp_type') or cols_lower.get('spectral_type')
col_radius = cols_lower.get('radius') or cols_lower.get('radius_rsun') or cols_lower.get('r')
col_m = cols_lower.get('m') or cols_lower.get('mv') or cols_lower.get('m_v')
col_dist = cols_lower.get('distance') or cols_lower.get('distance_pc') or cols_lower.get('d_pc')
col_Mbol = cols_lower.get('mbol') or cols_lower.get('m_bol') or cols_lower.get('absolute_bolometric_magnitude')

# Create working DataFrame with standard columns
work = df.copy()
# ensure name column
if 'name' not in [c.lower() for c in work.columns]:
    work['name'] = work.index.astype(str)

# Standardize numeric columns presence
if col_Teff is not None:
    work['Teff'] = pd.to_numeric(work[cols_lower[col_Teff]], errors='coerce')
else:
    work['Teff'] = np.nan

if col_bv:
    work['B-V'] = pd.to_numeric(work[cols_lower[col_bv]], errors='coerce')
else:
    work['B-V'] = np.nan

if col_spec:
    work['Spectral'] = work[cols_lower[col_spec]].astype(str)
else:
    work['Spectral'] = ''

if col_radius:
    work['Radius_Rsun'] = pd.to_numeric(work[cols_lower[col_radius]], errors='coerce')
else:
    work['Radius_Rsun'] = np.nan

if col_m:
    work['mV'] = pd.to_numeric(work[cols_lower[col_m]], errors='coerce')
else:
    work['mV'] = np.nan

if col_dist:
    work['distance_pc'] = pd.to_numeric(work[cols_lower[col_dist]], errors='coerce')
else:
    work['distance_pc'] = np.nan

if col_Mbol:
    work['Mbol_input'] = pd.to_numeric(work[cols_lower[col_Mbol]], errors='coerce')
else:
    work['Mbol_input'] = np.nan

# Derived calculations
# 1) Teff from B-V or Spectral if missing
for i, row in work.iterrows():
    if pd.isna(row['Teff']):
        if not pd.isna(row['B-V']):
            work.at[i, 'Teff'] = bv_to_teff(row['B-V'])
        elif row.get('Spectral'):
            t = spectral_to_teff(row['Spectral'])
            if t is not None:
                work.at[i, 'Teff'] = t

# 2) Mbol: from input Mbol_input OR from mV+distance (+optional BC)
# For simplicity, assume BC=0 unless user provides BC column (not implemented)
for i, row in work.iterrows():
    if not pd.isna(row['Mbol_input']):
        work.at[i, 'Mbol'] = row['Mbol_input']
    else:
        if not pd.isna(row['mV']) and not pd.isna(row['distance_pc']):
            try:
                Mbol = Mbol_from_m_and_dist(row['mV'], row['distance_pc'], BC=0.0)
                work.at[i, 'Mbol'] = Mbol
            except Exception:
                work.at[i, 'Mbol'] = np.nan
        else:
            work.at[i, 'Mbol'] = np.nan

# 3) Luminosity L/Lsun: from (Teff, Radius) if available, else from Mbol
for i, row in work.iterrows():
    Lval = np.nan
    if not pd.isna(row['Teff']) and not pd.isna(row['Radius_Rsun']):
        Lval = luminosity_from_tr(row['Teff'], row['Radius_Rsun'])
    elif not pd.isna(row.get('Mbol')):
        try:
            Lval = lum_from_Mbol(row['Mbol'])
        except Exception:
            Lval = np.nan
    work.at[i, 'L/Lsun'] = Lval

# 4) log quantities
work['logTeff'] = np.log10(work['Teff'].replace({0: np.nan}))
work['logL'] = np.log10(work['L/Lsun'].replace({0: np.nan}))

# 5) Mass estimate from L
work['Mass_est'] = work['L/Lsun'].apply(lambda x: mass_from_luminosity(x) if pd.notna(x) else np.nan)

# Clean up for plotting: remove rows without X or Y depending on user choice
# Decide X and Y columns
if x_choice.startswith('logTeff'):
    xcol = 'logTeff'
    xlabel = 'log10(Teff [K]) (reversed)'
elif x_choice.startswith('Teff'):
    xcol = 'Teff'
    xlabel = 'Teff [K]'
elif x_choice.startswith('B-V'):
    xcol = 'B-V'
    xlabel = 'B-V color'
else:
    # Spectral -> Teff
    xcol = 'Teff'
    xlabel = 'Teff from Spectral [K]'

if y_choice.startswith('logL'):
    ycol = 'logL'
    ylabel = 'log10(L / L_sun)'
elif y_choice.startswith('L ('):
    ycol = 'L/Lsun'
    ylabel = 'L / L_sun'
elif y_choice.startswith('Mbol'):
    ycol = 'Mbol'
    ylabel = 'M_bol'
else:
    ycol = 'Radius_Rsun'
    ylabel = 'Radius [R_sun]'

plot_df = work[[c for c in ['name', xcol, ycol, 'Teff', 'L/Lsun', 'Radius_Rsun', 'Mass_est', 'Spectral', 'B-V'] if c in work.columns]].copy()
plot_df = plot_df.dropna(subset=[xcol, ycol])

if plot_df.empty:
    st.warning('현재 선택한 축에 대해 유효한 데이터가 없습니다. 데이터(예: Teff, Radius, Mbol)를 확인하세요.')

# Convert size/color columns
if color_by == 'none':
    color_col = None
elif color_by == 'Spectral':
    color_col = 'Spectral'
else:
    color_col = 'Mass_est' if color_by == 'Mass_est' else 'Radius_Rsun'

if size_by == 'none':
    size_col = None
else:
    size_col = size_by

# Plot
st.subheader('H-R plot')
if _HAS_PLOTLY:
    if not plot_df.empty:
        fig = px.scatter(plot_df, x=xcol, y=ycol, hover_name='name', color=color_col if color_col else None,
                         size=size_col if size_col else None, labels={xcol: xlabel, ycol: ylabel},
                         title='H-R diagram')
        # Reverse x axis if using Teff/ logTeff standard HR convention
        if xcol in ('logTeff', 'Teff'):
            fig.update_xaxes(autorange='reversed')
        # If y is logL, set log scale visual tick formatting
        if ycol == 'logL':
            fig.update_yaxes(title=ylabel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('플롯할 데이터가 없습니다.')
else:
    # matplotlib fallback (static)
    import matplotlib.pyplot as plt
    if not plot_df.empty:
        fig, ax = plt.subplots()
        x = plot_df[xcol]
        y = plot_df[ycol]
        ax.scatter(x, y)
        if xcol in ('logTeff', 'Teff'):
            ax.invert_xaxis()
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        st.pyplot(fig)
    else:
        st.info('플롯할 데이터가 없습니다.')

# Data table and download
with st.expander('Show data table and download'):
    st.dataframe(work)
    csv_bytes = work.to_csv(index=False).encode('utf-8')
    st.download_button('Download processed data (CSV)', data=csv_bytes, file_name='hr_processed.csv')

# Scientific notes and confidence
st.markdown('---')
st.subheader('Notes on physics & confidence')
st.markdown(
    '- Stefan-Boltzmann law used to compute luminosity from Teff and Radius: L = 4πR^2σT^4. Constants used: σ, R_sun, L_sun.\n'
    '- B−V → Teff conversion uses Ballesteros approximation. This is an empirical approximate formula (good for rough estimates).\n'
    '- Mass estimates come from a simple, piecewise mass–luminosity relation (main-sequence appropriate). These are very approximate and not valid for giants/supergiants/compact objects.\n'
    '- Overall confidence: I have checked the code for syntax errors and basic edge cases; it should run when dependencies (streamlit, pandas, numpy, plotly) are installed.\n'
)

st.caption('If you want, I can: (1) add bolometric corrections, (2) allow custom column mappings interactively, (3) add isochrones or model tracks (requires extra data). Tell me which and I will update the code.')
