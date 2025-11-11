"""
streamlit_korea_geoparks.py

안내:
- Streamlit 앱으로 대한민국 국가지질공원 위치를 표시합니다.
- CSV 업로드(예: name,latitude,longitude,description)를 지원하며,
  위도/경도가 없으면 Nominatim으로 지오코딩을 수행합니다.
- 실행: streamlit run streamlit_korea_geoparks.py
"""

from functools import lru_cache
import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

st.set_page_config(page_title="국가지질공원 지도", layout="wide")

# ----------------------
# 기본 데이터 (예시)
# ----------------------
DEFAULT_GEOPARKS = [
    {"name": "제주도 국가지질공원", "description": "한라산, 용암동굴, 주상절리 등 화산 지형"},
    {"name": "울릉도·독도 국가지질공원", "description": "화산섬과 해안 절벽"},
    {"name": "부산 국가지질공원", "description": "해안 절리 및 퇴적층"},
    {"name": "강원 한탄·임진강(강원평화지역) 국가지질공원", "description": "현무암 주상절리 등 화산 활동 흔적"},
    {"name": "청송 국가지질공원", "description": "특이한 풍화지형과 주상절리"},
    {"name": "무등산권 국가지질공원", "description": "화강암 기암절벽과 지질학적 가치"},
]

# ----------------------
# 지오코더 설정 (모듈 레벨)
# ----------------------
_geolocator = Nominatim(user_agent="korea_geoparks_app")
_geocode_limited = RateLimiter(_geolocator.geocode, min_delay_seconds=1)

@lru_cache(maxsize=256)
def geocode_place(place_name: str):
    """주어진 장소명(문자열)을 지오코딩하여 (lat, lon)를 반환합니다. 실패 시 (None, None)."""
    if not place_name:
        return None, None
    try:
        query = f"{place_name}, South Korea"
        location = _geocode_limited(query)
        if location:
            return float(location.latitude), float(location.longitude)
    except Exception:
        # 네트워크/서비스 오류는 None 반환
        return None, None
    return None, None

# ----------------------
# CSV 로드/정리 함수
# ----------------------
def load_and_prepare_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)

    # 컬럼명 소문자 매핑 (유연성 확보)
    lower_map = {c.lower(): c for c in df.columns}
    name_col = lower_map.get('name') or lower_map.get('지역') or lower_map.get('지질공원명')
    lat_col = lower_map.get('latitude') or lower_map.get('lat') or lower_map.get('위도')
    lon_col = lower_map.get('longitude') or lower_map.get('lon') or lower_map.get('경도')
    desc_col = lower_map.get('description') or lower_map.get('설명')

    if not name_col:
        raise ValueError("CSV에 'name' 컬럼(또는 '지역', '지질공원명')이 필요합니다.")

    # 이름 컬럼은 반드시 'name'으로 변경
    df = df.rename(columns={name_col: 'name'})

    # 설명 컬럼 처리
    if desc_col:
        df = df.rename(columns={desc_col: 'description'})
    else:
        df['description'] = df.get('description', '')

    # 위도/경도 컬럼이 없으면 지오코딩으로 채운다
    if not (lat_col and lon_col):
        latitudes = []
        longitudes = []
        for place in df['name'].astype(str):
            lat, lon = geocode_place(place)
            latitudes.append(lat)
            longitudes.append(lon)
        df['latitude'] = latitudes
        df['longitude'] = longitudes
    else:
        df = df.rename(columns={lat_col: 'latitude', lon_col: 'longitude'})

    return df

# ----------------------
# 앱 UI
# ----------------------
st.sidebar.title("설정")
st.sidebar.markdown("CSV 업로드(예: name,latitude,longitude,description) 또는 내장 목록 사용")
uploaded_file = st.sidebar.file_uploader("지오파크 CSV 업로드", type=["csv"]) 
use_builtin = st.sidebar.checkbox("내장 국가지질공원 목록 사용(지오코딩 수행)", value=True)

st.sidebar.info("지오코딩은 Nominatim(오픈스트리트맵)을 사용합니다. 한 번에 많은 요청을 보내면 차단될 수 있으니 주의하세요.")

# 데이터 준비
try:
    if uploaded_file is not None:
        df = load_and_prepare_csv(uploaded_file)
    else:
        if use_builtin:
            df = pd.DataFrame(DEFAULT_GEOPARKS)
            # 내장 목록에 대해 지오코딩(필요 시)
            if 'latitude' not in df.columns or 'longitude' not in df.columns:
                lat_list = []
                lon_list = []
                for name in df['name'].astype(str):
                    lat, lon = geocode_place(name)
                    lat_list.append(lat)
                    lon_list.append(lon)
                df['latitude'] = lat_list
                df['longitude'] = lon_list
        else:
            st.info("왼쪽 사이드바에서 CSV를 업로드하거나 '내장 목록 사용'을 체크하세요.")
            st.stop()
except Exception as e:
    st.error(f"데이터 처리 중 오류: {e}")
    st.stop()

# 좌표 유효한 것만 필터
valid_mask = df['latitude'].notnull() & df['longitude'].notnull()
if not valid_mask.any():
    st.error("유효한 좌표가 없습니다. CSV에 위도/경도 컬럼을 추가하거나 내장 목록의 지오코딩 결과를 확인하세요.")
    st.stop()

map_df = df[valid_mask].copy()

# ----------------------
# 지도 표시
# ----------------------
st.title("🇰🇷 대한민국 국가지질공원 지도")
col1, col2 = st.columns((2, 1))

with col1:
    st.subheader("지도")
    midpoint = (map_df['latitude'].mean(), map_df['longitude'].mean())
    view_state = pdk.ViewState(latitude=midpoint[0], longitude=midpoint[1], zoom=6, pitch=30)

    scatter = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position='[longitude, latitude]',
        get_fill_color='[200, 30, 0, 160]',
        get_radius=5000,
        pickable=True,
        auto_highlight=True,
    )

    tooltip = {"html": "<b>{name}</b><br/>{description}", "style": {"backgroundColor": "steelblue", "color": "white"}}

    deck = pdk.Deck(layers=[scatter], initial_view_state=view_state, tooltip=tooltip)
    st.pydeck_chart(deck)

with col2:
    st.subheader("지오파크 목록")
    search = st.text_input("검색: 지오파크명 입력")
    if search:
        filtered = map_df[map_df['name'].str.contains(search, case=False, na=False)]
    else:
        filtered = map_df

    for _, row in filtered.iterrows():
        st.markdown(f"**{row['name']}**")
        st.write(row.get('description', ''))
        st.write(f"위도: {row['latitude']:.6f}  경도: {row['longitude']:.6f}")
        st.write('---')

# CSV 다운로드
@st.cache_data
def df_to_csv_bytes(df):
    return df.to_csv(index=False).encode('utf-8')

csv_bytes = df_to_csv_bytes(map_df)
st.download_button("현재 데이터 다운로드 (CSV)", data=csv_bytes, file_name="korea_geoparks.csv", mime='text/csv')

# 사이드바 도움말
st.sidebar.markdown("---")
st.sidebar.header("참고")
st.sidebar.markdown("1. 공식 데이터(data.go.kr)를 리포지토리에 추가하면 지오코딩 과정을 줄일 수 있습니다.\n2. Folium으로 교체하면 사진/HTML 팝업을 더 쉽게 넣을 수 있습니다.")

# 끝
