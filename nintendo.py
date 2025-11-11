# streamlit_nintendo_cute_images.py

import streamlit as st

st.set_page_config(page_title='🎮 닌텐도 게임 추천기 💖', layout='wide')
st.markdown("<h1 style='text-align:center; color:#FF5C5C;'>🎉 귀여운 닌텐도 게임 추천기 🎉</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>5문항 설문으로 당신에게 맞는 게임을 추천해드려요! 🐱‍👤</p>", unsafe_allow_html=True)
st.markdown("---")

# --------------------------
# 설문 조사
# --------------------------
q1 = st.radio("1️⃣ 게임을 즐길 때 선호하는 스타일은?", 
              ('모험/스토리', '액션', '퍼즐/전략', '시뮬레이션', '캐주얼'))
q2 = st.radio("2️⃣ 혼자 플레이 vs 친구/가족과?", 
              ('혼자', '친구/가족과', '상관없음'))
q3 = st.radio("3️⃣ 게임 난이도 선호?", 
              ('쉬움', '적당함', '어려움'))
q4 = st.radio("4️⃣ 그래픽 스타일 선호?", 
              ('귀엽고 아기자기', '리얼리틱', '픽셀/레트로', '상관없음'))
q5 = st.radio("5️⃣ 플레이 시간?", 
              ('짧게 즐기고 싶다', '적당히 즐기고 싶다', '긴 시간 몰입'))

# --------------------------
# 게임 후보 데이터 (이미지 포함, 안정적 URL)
# --------------------------
games = [
    {"name": "젤다의 전설: 브레스 오브 더 와일드",
     "description": "방대한 오픈월드에서 자유롭게 모험하며 퍼즐과 전투를 즐길 수 있는 액션 어드벤처 게임.",
     "tags": ["모험/스토리","혼자","어려움","리얼리틱","긴 시간 몰입"],
     "img":"https://raw.githubusercontent.com/robinbai/nintendo-game-images/main/zelda.jpg"},
    
    {"name": "슈퍼 마리오 오디세이",
     "description": "다양한 왕국을 탐험하며 마리오의 모험을 즐길 수 있는 액션 게임.",
     "tags": ["모험/스토리","혼자","적당함","귀엽고 아기자기","적당히 즐기고 싶다"],
     "img":"https://raw.githubusercontent.com/robinbai/nintendo-game-images/main/mario_odyssey.jpg"},
    
    {"name": "마리오 카트 8 디럭스",
     "description": "친구나 가족과 함께 즐기는 경주 게임.",
     "tags": ["액션","친구/가족과","쉬움","귀엽고 아기자기","짧게 즐기고 싶다"],
     "img":"https://raw.githubusercontent.com/robinbai/nintendo-game-images/main/mario_kart.jpg"},
    
    {"name": "동물의 숲: 뉴 호라이즌스",
     "description": "섬에서 생활하며 마을을 꾸미고 친구들과 교류하는 시뮬레이션 게임.",
     "tags": ["시뮬레이션","상관없음","쉬움","귀엽고 아기자기","적당히 즐기고 싶다"],
     "img":"https://raw.githubusercontent.com/robinbai/nintendo-game-images/main/animal_crossing.jpg"},
    
    {"name": "스플래툰 3",
     "description": "팀 대전 슈팅 게임으로 색칠을 통해 승리하는 경쟁 액션 게임.",
     "tags": ["액션","친구/가족과","적당함","픽셀/레트로","적당히 즐기고 싶다"],
     "img":"https://raw.githubusercontent.com/robinbai/nintendo-game-images/main/splatoon3.jpg"},
    
    {"name": "마리오 파티 슈퍼스타즈",
     "description": "미니게임으로 친구나 가족과 즐기는 파티 게임.",
     "tags": ["캐주얼","친구/가족과","쉬움","귀엽고 아기자기","짧게 즐기고 싶다"],
     "img":"https://raw.githubusercontent.com/robinbai/nintendo-game-images/main/mario_party.jpg"},
    
    {"name": "포켓몬스터 스칼렛/바이올렛",
     "description": "포켓몬을 잡고 키우며 모험하는 RPG 게임.",
     "tags": ["모험/스토리","혼자","적당함","귀엽고 아기자기","긴 시간 몰입"],
     "img":"https://raw.githubusercontent.com/robinbai/nintendo-game-images/main/pokemon_sv.jpg"},
    
    {"name": "피트니스 복싱 2",
     "description": "운동과 리듬 게임을 결합한 캐주얼 게임.",
     "tags": ["캐주얼","혼자","쉬움","상관없음","짧게 즐기고 싶다"],
     "img":"https://raw.githubusercontent.com/robinbai/nintendo-game-images/main/fitness_boxing.jpg"},
    
    {"name": "링 피트 어드벤처",
     "description": "운동과 RPG를 결합한 게임으로 신체 활동과 모험을 함께 즐김.",
     "tags": ["시뮬레이션","혼자","적당함","귀엽고 아기자기","적당히 즐기고 싶다"],
     "img":"https://raw.githubusercontent.com/robinbai/nintendo-game-images/main/ring_fit.jpg"},
    
    {"name": "루이지 맨션 3",
     "description": "유령을 잡으며 미션을 해결하는 퍼즐 액션 게임.",
     "tags": ["퍼즐/전략","혼자","적당함","귀엽고 아기자기","적당히 즐기고 싶다"],
     "img":"https://raw.githubusercontent.com/robinbai/nintendo-game-images/main/luigi_mansion.jpg"},
]

# --------------------------
# 추천 로직
# --------------------------
if st.button("🎯 추천 받기"):
    answers = [q1,q2,q3,q4,q5]
    best_match = None
    best_score = -1
    
    for game in games:
        score = sum([ans in game["tags"] for ans in answers])
        if score > best_score:
            best_score = score
            best_match = game
    
    if best_match:
        st.markdown(f"<div style='background-color:#FFF0F5; border-radius:20px; padding:20px; box-shadow: 5px 5px 15px #FFC0CB;'>", unsafe_allow_html=True)
        cols = st.columns([1,2])
        with cols[0]:
            st.image(best_match['img'], width=180)
        with cols[1]:
            st.markdown(f"### 🏆 {best_match['name']} 🏆")
            st.markdown(f"💖 **추천 이유:** 설문 결과와 가장 많은 선택지가 일치했어요!")
            st.markdown(f"🎮 **게임 설명:** {best_match['description']}")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("추천할 게임을 찾을 수 없어요 😢")
