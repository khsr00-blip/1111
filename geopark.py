"""
streamlit_korea_geoparks.py

새로 만든 안정적인 Streamlit 앱 (단일 파일)
- 의존성 최소화: `geopy`를 사용하지 않도록 변경했습니다. 대신 Nominatim(오픈스트리트맵) HTTP API를 `requests`로 호출합니다(옵션).
- `requests`가 설치되어 있지 않으면 지오코딩 기능은 비활성화되고, 사용자는 좌표가 포함된 CSV 업로드를 권장합니다.
- pydeck이 없으면 Streamlit의 `st.map`으로 대체 표시합니다.
- Nominatim 호출은 캐시(`st.cache_data`)되고 호출 간 1초 대기하여 차단을 줄입니다.

사용법:
    pip install streamlit pandas requests pydeck
    streamlit run streamlit_korea_geoparks.py

파일에는 예제 CSV 다운로드 버튼 및 현재 데이터 다운로드 버튼이 포함되어 있습니다.
"""

from functools import lru_cache
import io
import json
import time
import os
from typing import Tuple, Optional

import streamlit as st
import pandas as pd

# Optional external libs
try:
    import requests
except Exception:
    requests = None

try:
    import pydeck as pdk
    _HAS_PYDECK = True
except Exception:
    _HAS_PYDECK = False

# ----------------------
# 기본 설정
# ----------------------
st.set_page_config(page_title="국가지질공원 지도", layout="wide")

# 내장(예제) 지질공원 목록 — 이름과 간단한 설명
# 좌표는 제공하지 않아도 되며, 설치된 경우 자동 지오코딩을 시도합니다.
BUILTIN_GEOPARKS = [
    {"name": "제주도 국가지질공원", "description": "한라산·용암동굴·주상절리 등 화산 지형의 보고"},
    {"name": "울릉도·독도 국가지질공원", "description": "화산섬과 해안 절벽, 희귀 지질유산"},
    {"name": "부산 국가지질공원", "description": "도시 해안의 절리와 퇴적층"},
    {"name": "강원 한탄·임진강 국가지질공원", "description": "주상절리와 화산활동 흔적"},
    {"name": "청송 국가지질공원", "description": "응회암·주상절리 등 독특한 풍화지형"},
    {"name": "무등산권 국가지질공원", "description": "기암괴석과 암석학적 가치"},
]

# ----------------------
# 유틸리티: Nominatim 지오코딩 (requests 사용)
# ----------------------
@st.cache_data
def _geocode_with_nominatim(query: str) -> Tuple[Optional[float], Optional[float]]:
    """Nominatim HTTP API로 지오코딩. 실패하면 (None, None).

    주의: 호출량이 많으면 차단될 수 있으니 앱에서 최소한의 호출만 하세요.
    """
    if requests is None:
        return None, None

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{query}, South Korea",
        "format": "json",
        "limit": 1,
        "addressdetails": 0,
    }
    headers = {"User-Agent": "KoreaGeoparksApp/1.0 (+contact@example.com)"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None, None
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon
    except Exception:
        return None, None

# ----------------------
# CSV 로드 및 데이터 준비
# ----------------------
def load_user_csv(uploaded) -> pd.DataFrame:
    df = pd.read_csv(uploaded)
    # 유연한 컬럼명 매핑
    colmap = {c.lower(): c for c in df.columns}
    name_col = colmap.get('name') or colmap.get('지역') or colmap.get('지질공원명')
    lat_col = colmap.get('latitude') or colmap.get('lat') or colmap.get('위도')
    lon_col = colmap.get('longitude') or colmap.get('lon') or colmap.get('경도')
    desc_col = colmap.get('description') or colmap.get('설명')

    if not name_col:
        raise ValueError("CSV에 'name' 컬럼(또는 '지역'/'지질공원명')이 필요합니다.")

    df = df.rename(columns={name_col: 'name'})
    if desc_col:
        df = df.rename(columns={desc_col: 'description'})
    else:
        df['description'] = df.get('description', '')

    if lat_col and lon_col:
        df = df.rename(columns={lat_col: 'latitude', lon_col: 'longitude'})
    # else: 위도/경도 컬럼 없으면 나중에 지오코딩 시도

    return df


def build_dataframe(uploaded_file) -> pd.DataFrame:
    """업로드된 CSV가 있으면 로드, 없으면 내장 목록을 DataFrame으로 반환.
    좌표가 없으면 requests가 설치된 경우 Nominatim을 통해 지오코딩합니다.
    """
    if uploaded_file is not None:
        df = load_user_csv(uploaded_file)
    else:
        df = pd.DataFrame(BUILTIN_GEOPARKS)

    # 모든 행에 latitude, longitude 컬럼이 있는지 확인
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        # 지오코딩 가능 여부 확인
        if requests is None:
            # 지오코딩 불가 — 좌표가 없는 항목은 NaN으로 남겨둠
            st.warning("지오코딩을 위해 `requests` 패키지가 필요합니다. 설치하려면 `pip install requests`를 실행하세요.\n또는 좌표(위도/경도)를 포함한 CSV를 업로드하세요.")
            df['latitude'] = df.get('latitude', pd.NA)
            df['longitude'] = df.get('longitude', pd.NA)
        else:
            lats = []
            lons = []
            with st.spinner("지오코딩 중입니다 — 한 번에 많은 요청을 보내면 차단될 수 있으니 기다려주세요..."):
                for name in df['name'].astype(str):
                    lat, lon = _geocode_with_nominatim(name)
                    lats.append(lat)
                    lons.append(lon)
                    # Nominatim 사용 규칙에 맞춰 지연
                    time.sleep(1)
            df['latitude'] = lats
            df['longitude'] = lons

    # 위도/경도 타입 정리
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    return df

# ----------------------
# Streamlit UI
# ----------------------
st.sidebar.title("설정")
st.sidebar.markdown("CSV(예: name,latitude,longitude,description) 업로드 또는 내장 목록 사용")
uploaded_file = st.sidebar.file_uploader("지오파크 CSV 업로드", type=['csv'])
use_builtin = st.sidebar.checkbox('내장 목록 사용(CSV 업로드가 없을 때)', value=True)

st.sidebar.markdown('---')
st.sidebar.info('Nominatim 지오코딩은 공개 API입니다. 대량 호출 시 차단될 수 있으니 주의하세요.')

if uploaded_file is None and not use_builtin:
    st.info('왼쪽에서 CSV 업로드 또는 "내장 목록 사용"을 체크하세요.')
    st.stop()

# 데이터 준비
try:
    df = build_dataframe(uploaded_file if uploaded_file is not None else None)
except Exception as e:
    st.error(f"데이터 로드/처리 오류: {e}")
    st.stop()

# 유효한 좌표만 필터
valid = df['latitude'].notna() & df['longitude'].notna()
if not valid.any():
    st.warning('유효한 좌표가 없습니다. CSV에 위도/경도 컬럼을 추가하거나 requests를 설치해 지오코딩을 허용하세요.')

map_df = df[valid].copy()

# 레이아웃
st.title('🇰🇷 대한민국 국가지질공원 지도')
col_map, col_list = st.columns((2, 1))

with col_map:
    st.subheader('지도')

    if map_df.empty:
        st.info('표시할 좌표가 없습니다.')
    else:
        # pydeck 사용 가능하면 세밀한 뷰, 아니면 st.map
        if _HAS_PYDECK:
            midpoint = (map_df['latitude'].mean(), map_df['longitude'].mean())
            view_state = pdk.ViewState(latitude=midpoint[0], longitude=midpoint[1], zoom=6, pitch=30)
            layer = pdk.Layer(
                'ScatterplotLayer',
                data=map_df,
                get_position='[longitude, latitude]',
                get_fill_color='[255, 99, 71, 160]',
                get_radius=5000,
                pickable=True,
                auto_highlight=True,
            )
            tooltip = {"html": "<b>{name}</b><br/>{description}", "style": {"backgroundColor": "#111", "color": "#fff"}}
            deck = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
            st.pydeck_chart(deck)
        else:
            # 간단한 지도
            st.map(map_df[['latitude', 'longitude']].rename(columns={'latitude':'lat','longitude':'lon'}))

with col_list:
    st.subheader('지오파크 목록')
    q = st.text_input('검색: 지오파크명')
    if q:
        shown = df[df['name'].str.contains(q, case=False, na=False)]
    else:
        shown = df

    if shown.empty:
        st.info('검색 결과가 없습니다.')
    else:
        for _, r in shown.iterrows():
            st.markdown(f"**{r['name']}**")
            if r.get('description'):
                st.write(r['description'])
            lat = r.get('latitude')
            lon = r.get('longitude')
            if pd.notna(lat) and pd.notna(lon):
                st.write(f"위도: {lat:.6f}  경도: {lon:.6f}")
            else:
                st.write('위치 정보(좌표) 없음')
            st.write('---')

# CSV 다운로드: 현재 데이터
@st.cache_data
def df_to_csv_bytes(df_local: pd.DataFrame) -> bytes:
    return df_local.to_csv(index=False).encode('utf-8')

if not df.empty:
    csv_bytes = df_to_csv_bytes(df)
    st.download_button('현재 데이터 다운로드 (CSV)', data=csv_bytes, file_name='korea_geoparks.csv', mime='text/csv')

# 예제 CSV 만들기
if st.sidebar.button('예제 CSV 생성'):
    sample = pd.DataFrame(BUILTIN_GEOPARKS)
    st.sidebar.download_button('예제 CSV 다운로드', data=sample.to_csv(index=False).encode('utf-8'), file_name='geoparks_sample.csv', mime='text/csv')

# 도움말 / 설치 안내
st.sidebar.markdown('---')
st.sidebar.header('실행/설치 안내')
st.sidebar.code('pip install streamlit pandas requests pydeck')
st.sidebar.write('requests가 없으면 앱이 지오코딩을 수행하지 못합니다. 오류가 나면 설치 후 다시 실행하세요.')

# 끝
