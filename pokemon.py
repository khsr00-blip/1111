"""
streamlit_pokemon_helper.py

Streamlit 앱: 포켓몬 정보 조회
- 입력한 포켓몬 이름에 대해 타입, 진화 단계, 추천 스킬 표시
- 기본 내장 데이터베이스 사용(예시 1세대 포켓몬)
- 깃허브 업로드용으로 코드 구조 단순, 실행 가능

사용법
1) pip install streamlit pandas
2) streamlit run streamlit_pokemon_helper.py
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title='Pokémon Helper', layout='wide')

st.title('Pokémon Helper')
st.markdown('포켓몬 이름을 입력하면 타입, 진화 단계, 추천 스킬을 알려줍니다.')

# ----------------------
# Sample Pokémon database
# ----------------------
data = [
    {'name': 'Bulbasaur', 'type1': 'Grass', 'type2': 'Poison', 'evolution': 'Stage 1', 'skills': ['Vine Whip', 'Razor Leaf']},
    {'name': 'Ivysaur', 'type1': 'Grass', 'type2': 'Poison', 'evolution': 'Stage 2', 'skills': ['Vine Whip', 'Solar Beam']},
    {'name': 'Venusaur', 'type1': 'Grass', 'type2': 'Poison', 'evolution': 'Stage 3', 'skills': ['Solar Beam', 'Sludge Bomb']},
    {'name': 'Charmander', 'type1': 'Fire', 'type2': None, 'evolution': 'Stage 1', 'skills': ['Flamethrower', 'Fire Spin']},
    {'name': 'Charmeleon', 'type1': 'Fire', 'type2': None, 'evolution': 'Stage 2', 'skills': ['Flamethrower', 'Fire Fang']},
    {'name': 'Charizard', 'type1': 'Fire', 'type2': 'Flying', 'evolution': 'Stage 3', 'skills': ['Flamethrower', 'Dragon Claw']},
    {'name': 'Squirtle', 'type1': 'Water', 'type2': None, 'evolution': 'Stage 1', 'skills': ['Water Gun', 'Bubble']},
    {'name': 'Wartortle', 'type1': 'Water', 'type2': None, 'evolution': 'Stage 2', 'skills': ['Water Gun', 'Aqua Tail']},
    {'name': 'Blastoise', 'type1': 'Water', 'type2': None, 'evolution': 'Stage 3', 'skills': ['Hydro Pump', 'Surf']},
]

pokemon_df = pd.DataFrame(data)

# ----------------------
# User input
# ----------------------
poke_name = st.text_input('포켓몬 이름 입력')

if poke_name:
    poke_name_clean = poke_name.strip().title()
    poke_info = pokemon_df[pokemon_df['name'] == poke_name_clean]

    if not poke_info.empty:
        st.subheader(f'{poke_name_clean} 정보')
        type1 = poke_info.iloc[0]['type1']
        type2 = poke_info.iloc[0]['type2']
        evolution = poke_info.iloc[0]['evolution']
        skills = poke_info.iloc[0]['skills']

        st.markdown(f'**타입:** {type1}' + (f' / {type2}' if type2 else ''))
        st.markdown(f'**진화 단계:** {evolution}')
        st.markdown(f'**추천 스킬:** {", ".join(skills)}')
    else:
        st.warning('해당 포켓몬을 찾을 수 없습니다. 이름을 확인하세요.')
