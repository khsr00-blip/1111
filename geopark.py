"""
streamlit_korea_geoparks.py


수정사항 요약:
- 원본에서 발생한 `SyntaxError: invalid syntax`(파일 상단의 잘못된 `else:`) 문제를 제거했습니다.
- CSV 파싱을 더 견고하게 처리하고, 위도/경도가 없을 경우 안전하게 Nominatim으로 지오코딩합니다.
- geopy의 RateLimiter와 lru_cache를 사용해 지오코딩 중과부하를 줄였습니다.
- PyDeck 지도를 사용해 마커를 표시하고, CSV 다운로드 기능 포함.


실행: `streamlit run streamlit_korea_geoparks.py`
필요 패키지: streamlit, pandas, pydeck, geopy
설치: `pip install streamlit pandas pydeck geopy`
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
# 한국 내 위치임을 명시하면 정확도가 올라갈 수 있음
query = f"{place_name}, South Korea"
location = _geocode_limited(query)
if location:
return float(location.latitude), float(location.longitude)
except Exception:
# 네트워크나 서비스 에러 등은 None 반환
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

