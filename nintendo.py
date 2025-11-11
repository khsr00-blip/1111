# streamlit_nintendo_pokemon_recommend.py

import streamlit as st
import random

st.set_page_config(page_title='🎮 닌텐도 & 포켓몬 게임 추천기 💖', layout='wide')
st.markdown("<h1 style='text-align:center; color:#FF5C5C;'>🎉 귀여운 닌텐도 & 포켓몬 게임 추천기 🎉</h1>", unsafe_allow_html=True)
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

answers = [q1, q2, q3, q4, q5]

# --------------------------
# 게임 후보 데이터 (닌텐도 + 포켓몬, 안정적 이미지 + 설명 확장)
# --------------------------
games = [
    {"name": "젤다의 전설: 브레스 오브 더 와일드",
     "description": "방대한 오픈월드에서 자유롭게 탐험하며 다양한 퍼즐과 전투를 즐길 수 있는 액션 어드벤처 게임입니다. 다양한 지형을 탐험하며 숨겨진 비밀과 신비한 유적들을 발견하고, 여러 가지 장비와 무기를 활용해 창의적인 방법으로 문제를 해결할 수 있습니다. 플레이어는 다양한 생태계와 날씨 시스템을 경험하며, 각기 다른 전략과 모험 방식으로 게임을 즐길 수 있습니다. 보스 전투와 다양한 퀘스트, 그리고 다양한 캐릭터와 스토리를 통해 몰입감 높은 경험을 제공합니다.",
     "tags": ["모험/스토리","혼자","어려움","리얼리틱","긴 시간 몰입"],
     "img":"https://raw.githubusercontent.com/joel-porras/nintendo-game-images/main/zelda.jpg"},
    
    {"name": "슈퍼 마리오 오디세이",
     "description": "다양한 왕국을 탐험하며 마리오의 모험을 즐길 수 있는 액션 게임입니다. 각 왕국마다 독특한 배경과 도전 과제가 있으며, 다양한 미니게임과 수집 요소가 존재합니다. 캐릭터의 새로운 기술과 동작을 배우며 퍼즐과 장애물을 극복할 수 있고, 숨겨진 비밀을 발견하는 재미가 가득합니다. 친구와 가족과 함께 또는 혼자서 플레이하며, 아기자기한 그래픽과 재미있는 연출을 경험할 수 있습니다. 탐험, 수집, 점프 액션 등 모든 면에서 즐거움이 가득합니다.",
     "tags": ["모험/스토리","혼자","적당함","귀엽고 아기자기","적당히 즐기고 싶다"],
     "img":"https://raw.githubusercontent.com/joel-porras/nintendo-game-images/main/mario_odyssey.jpg"},
    
    {"name": "마리오 카트 8 디럭스",
     "description": "친구나 가족과 함께 즐길 수 있는 경주 게임입니다. 다양한 트랙과 레이스 모드, 아이템 배틀 등 다양한 모드를 통해 경쟁과 재미를 동시에 제공합니다. 플레이어는 카트와 캐릭터를 선택하고, 전략적으로 아이템을 사용하며 레이스를 진행할 수 있습니다. 각 트랙에는 숨겨진 지름길과 장애물이 있어 매번 다른 경험을 제공합니다. 빠른 속도감과 귀여운 그래픽, 다채로운 캐릭터와 트랙으로 파티 분위기를 즐기기에 최적의 게임입니다.",
     "tags": ["액션","친구/가족과","쉬움","귀엽고 아기자기","짧게 즐기고 싶다"],
     "img":"https://raw.githubusercontent.com/joel-porras/nintendo-game-images/main/mario_kart.jpg"},
    
    {"name": "동물의 숲: 뉴 호라이즌스",
     "description": "섬에서 생활하며 마을을 꾸미고 친구들과 교류하는 시뮬레이션 게임입니다. 플레이어는 집을 꾸미고, 섬의 구조를 바꾸며, 낚시, 곤충 채집, 농사 등 다양한 활동을 즐길 수 있습니다. 계절과 날씨에 따라 변화하는 환경 속에서 NPC 캐릭터들과 상호작용하며 친밀도를 높일 수 있습니다. 다양한 이벤트와 커뮤니티 활동을 통해 즐거움을 극대화하며, 자신만의 섬을 창조하는 재미가 있습니다.",
     "tags": ["시뮬레이션","상관없음","쉬움","귀엽고 아기자기","적당히 즐기고 싶다"],
     "img":"https://raw.githubusercontent.com/joel-porras/nintendo-game-images/main/animal_crossing.jpg"},
    
    {"name": "스플래툰 3",
     "description": "팀 대전 슈팅 게임으로 색칠을 통해 승리하는 경쟁 액션 게임입니다. 플레이어는 다양한 무기와 전략을 활용하여 팀과 협력해 상대 팀을 물리치고 맵을 점령합니다. 캐릭터의 커스터마이징과 다양한 경기 모드가 존재하며, 빠른 게임 플레이와 화려한 색감이 특징입니다. 친구와 함께 즐기거나 온라인으로 경쟁할 수 있으며, 협동과 전략적 사고를 요구하는 게임입니다.",
     "tags": ["액션","친구/가족과","적당함","픽셀/레트로","적당히 즐기고 싶다"],
     "img":"https://raw.githubusercontent.com/joel-porras/nintendo-game-images/main/splatoon3.jpg"},

    # 포켓몬 게임 추가
    {"name": "포켓몬스터 스칼렛/바이올렛",
     "description": "광대한 오픈월드에서 다양한 포켓몬을 만나고 포획하며 배틀을 즐기는 RPG 게임입니다. 각 포켓몬마다 특성과 기술이 있으며, 전략적으로 팀을 구성하고, 다양한 미션과 도전을 통해 성장할 수 있습니다. 친구와 교환하거나 배틀을 즐길 수 있으며, 각지의 도시와 마을, 던전 탐험 등 방대한 콘텐츠를 제공합니다. 시즌 이벤트와 배틀 토너먼트, 신규 포켓몬 추가 등 끊임없이 재미를 제공하는 게임입니다.",
     "tags": ["모험/스토리","혼자","적당함","귀엽고 아기자기","긴 시간 몰입"],
     "img":"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png"},

    {"name": "포켓몬스터 소드/실드",
     "description": "가라르 지방을 탐험하며 다양한 포켓몬을 잡고 키우는 RPG 게임입니다. 배틀 시스템과 전략 요소가 풍부하며, 친구와 온라인 배틀과 교환을 즐길 수 있습니다. 트레이너 성장과 포켓몬 육성을 통해 다양한 미션과 챌린지에 도전할 수 있으며, 각 포켓몬의 기술과 타입을 고려한 전략적 플레이가 핵심입니다. 지역 특산 포켓몬과 다양한 이벤트가 제공되어 매번 새로운 재미를 느낄 수 있습니다.",
     "tags": ["모험/스토리","혼자","적당함","귀엽고 아기자기","적당히 즐기고 싶다"],
     "img":"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"},
]

# --------------------------
# 추천 로직 (분산 + 랜덤)
# --------------------------
def recommend_game(answers, games):
    scores = []
    for game in games:
        score = sum([ans in game["tags"] for ans in answers])
        score += random.random()  # 랜덤 가중치
        scores.append((score, game))
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[0][1]

# --------------------------
# 추천 버튼
# --------------------------
if st.button("🎯 추천 받기"):
    best_match = recommend_game(answers, games)
    st.markdown(f"<div style='background-color:#FFF0F5; border-radius:20px; padding:20px; box-shadow: 5px 5px 15px #FFC0CB;'>", unsafe_allow_html=True)
    cols = st.columns([1,2])
    with cols[0]:
        st.image(best_match['img'], width=180)
    with cols[1]:
        st.markdown(f"### 🏆 {best_match['name']} 🏆")
        st.markdown(f"💖 **추천 이유:** 설문 결과와 가장 잘 맞는 게임이에요! 🎉")
        st.markdown(f"🎮 **게임 설명:** {best_match['description']}")
    st.markdown("</div>", unsafe_allow_html=True)
