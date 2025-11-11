from functools import lru_cache
df['description'] = df['description']
else:
st.info("왼쪽 사이드바에서 CSV를 업로드하거나 '내장 목록 사용'을 체크하세요.")
st.stop()


# 필터: 유효한 좌표만
valid_mask = df['latitude'].notnull() & df['longitude'].notnull()
if not valid_mask.any():
st.error("좌표가 유효한 지오파크가 없습니다. CSV에 위도/경도 컬럼을 추가하거나 내장 목록에서 지오코딩이 성공했는지 확인하세요.")
st.stop()


map_df = df[valid_mask].copy()


# ----------------------
# 메인 레이아웃: 지도 + 리스트
# ----------------------
st.title("🇰🇷 대한민국 국가지질공원 지도")
col1, col2 = st.columns((2,1))


with col1:
st.subheader("지도")
# pydeck 시각화
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


r = pdk.Deck(layers=[scatter], initial_view_state=view_state, tooltip=tooltip)
st.pydeck_chart(r)


with col2:
st.subheader("지오파크 목록")
search = st.text_input("검색: 지오파크명 입력")
if search:
filtered = map_df[map_df['name'].str.contains(search, case=False, na=False)]
else:
filtered = map_df
for idx, row in filtered.iterrows():
st.markdown(f"**{row['name']}**")
st.write(row.get('description', ''))
st.write(f"위도: {row['latitude']:.6f} 경도: {row['longitude']:.6f}")
st.write('---')


# 다운로드: 현재 데이터 CSV로 저장
@st.cache_data
def df_to_csv_bytes(df):
return df.to_csv(index=False).encode('utf-8')


csv_bytes = df_to_csv_bytes(map_df)
st.download_button("현재 데이터 다운로드 (CSV)", data=csv_bytes, file_name="korea_geoparks.csv", mime='text/csv')


# 간단한 도움말
st.sidebar.markdown("---")
st.sidebar.header("참고/다음 단계")
st.sidebar.markdown("1. 더 많은 필드를 추가하려면 CSV(예: `image_url`, `visit_info`)에 넣어 업로드하세요.\n2. Folium 지도를 선호하면 pydeck 레이어를 folium으로 바꿀 수 있습니다.\n3. 공식 데이터(data.go.kr)의 CSV를 저장소에 포함시키면 지오코딩 과정을 생략할 수 있습니다.")


st.sidebar.markdown("---")
st.sidebar.write("데이터 출처(예): 데이터포털(data.go.kr), UNESCO, 국토지리정보원")


# 끝
