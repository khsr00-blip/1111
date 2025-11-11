# streamlit_pokemon_english.py

import streamlit as st
import requests

st.set_page_config(page_title='포켓몬 정보 조회(영문 입력)', layout='wide')
st.title('포켓몬 정보 조회기')
st.markdown('영어 포켓몬 이름을 입력하면 타입, 진화 단계, 추천 스킬을 보여줍니다.')

poke_name_eng = st.text_input('포켓몬 이름 입력 (영어)')

if poke_name_eng:
    poke_name_eng = poke_name_eng.strip().lower()
    st.subheader(f'{poke_name_eng.title()} 정보 조회 중…')
    try:
        # 포켓몬 기본 정보
        poke_url = f'https://pokeapi.co/api/v2/pokemon/{poke_name_eng}'
        poke_res = requests.get(poke_url)
        if poke_res.status_code != 200:
            st.warning('해당 포켓몬을 찾을 수 없습니다. 이름을 확인하세요.')
        else:
            poke_data = poke_res.json()
            # 영어 이름
            english_name = poke_data.get('name', '').title()
            # 타입
            types = [t['type']['name'].title() for t in poke_data.get('types', [])]
            # 추천 스킬 (앞 5개)
            moves = [m['move']['name'].replace('-', ' ').title() for m in poke_data.get('moves', [])[:5]]

            # 진화 단계 조회
            species_url = poke_data.get('species', {}).get('url')
            evo_stage = '정보 없음'
            if species_url:
                species_res = requests.get(species_url).json()
                evo_chain_url = species_res.get('evolution_chain', {}).get('url')
                if evo_chain_url:
                    evo_chain_res = requests.get(evo_chain_url).json()
                    chain = evo_chain_res.get('chain', {})
                    stages = []
                    while chain:
                        species_name = chain.get('species', {}).get('name', '')
                        if species_name:
                            stages.append(species_name.title())
                        evolves_to = chain.get('evolves_to')
                        chain = evolves_to[0] if evolves_to else None
                    if english_name in stages:
                        evo_stage = f'Stage {stages.index(english_name)+1} / {len(stages)}'

            # 출력
            st.markdown(f'**영문 이름:** {english_name}')
            st.markdown(f'**타입:** {" / ".join(types)}')
            st.markdown(f'**진화 단계:** {evo_stage}')
            st.markdown(f'**추천 스킬:** {", ".join(moves)}')

    except Exception as e:
        st.error(f'정보 조회 중 오류 발생: {e}')
