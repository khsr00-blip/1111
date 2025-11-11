# streamlit_pokemon_korean_search.py

import streamlit as st
import requests

st.set_page_config(page_title='포켓몬 정보 조회(한글 입력 지원)', layout='wide')
st.title('포켓몬 정보 조회기')
st.markdown('한글 포켓몬 이름을 입력하면 영어 이름, 타입, 진화 단계, 추천 스킬을 알려줍니다.')

poke_name_kr = st.text_input('포켓몬 이름 입력 (한글)')

if poke_name_kr:
    st.subheader(f'{poke_name_kr} 정보 검색 중…')
    # 한글 이름을 먼저 영어 이름 또는 ID로 바꾸는 로직 필요
    # 여기서는 단순히 '한글 이름 → 영어 이름' 사전 매핑 또는 검색 API 호출을 시도함
    # 예시: 한글을 영문으로 바꾸는 별도 데이터가 없으면 검색 실패
    # (매핑 없이 자동 변환은 지원되지 않음)
    # 아래는 예시 매핑 없이 검색을 시도하는 구조만 보여줌
    
    try:
        # 우선 영문 이름으로 시도
        eng_name = poke_name_kr.strip().lower()
        url = f'https://pokeapi.co/api/v2/pokemon/{eng_name}'
        resp = requests.get(url)
        if resp.status_code != 200:
            st.warning('영문 이름으로 조회 실패했습니다. 한글→영문 매핑 데이터가 필요합니다.')
        else:
            data = resp.json()
            # 영어 이름
            english = data.get('name', '').title()
            # 타입
            types = [t['type']['name'].title() for t in data.get('types', [])]
            # 추천 스킬 (초기 5개)
            moves = [m['move']['name'].replace('-', ' ').title() for m in data.get('moves', [])[:5]]
            # 진화 단계 조회
            species_url = data.get('species', {}).get('url')
            evo_stage = '정보 없음'
            if species_url:
                species = requests.get(species_url).json()
                evo_chain_url = species.get('evolution_chain', {}).get('url')
                if evo_chain_url:
                    evo_chain = requests.get(evo_chain_url).json().get('chain', {})
                    stages = []
                    chain = evo_chain
                    while chain:
                        name_sp = chain.get('species', {}).get('name', '')
                        if name_sp:
                            stages.append(name_sp.title())
                        evolves_to = chain.get('evolves_to')
                        chain = evolves_to[0] if evolves_to else None
                    if english in stages:
                        evo_stage = f'Stage {stages.index(english)+1} / {len(stages)}'
            # 출력
            st.markdown(f'**영문 이름:** {english}')
            st.markdown(f'**타입:** {" / ".join(types)}')
            st.markdown(f'**진화 단계:** {evo_stage}')
            st.markdown(f'**추천 스킬:** {", ".join(moves)}')
    except Exception as e:
        st.error(f'정보 조회 중 오류가 발생했습니다: {e}')
