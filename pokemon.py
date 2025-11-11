# streamlit_pokemon_cute_with_image.py

import streamlit as st
import requests

st.set_page_config(page_title='🌟 포켓몬 헬퍼 🌟', layout='wide')
st.markdown("<h1 style='text-align: center; color: #FF5C5C;'>🐾 포켓몬 헬퍼 🐾</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>영어 이름을 입력하면 타입, 진화 단계, 추천 스킬과 함께 이미지를 보여줘요! 💖</p>", unsafe_allow_html=True)
st.markdown("---")

poke_name_eng = st.text_input('포켓몬 이름 입력 (영어) 🔍')

if poke_name_eng:
    poke_name_eng = poke_name_eng.strip().lower()
    st.markdown(f"### 🔎 {poke_name_eng.title()} 정보 조회 중...")
    try:
        # 포켓몬 기본 정보
        poke_url = f'https://pokeapi.co/api/v2/pokemon/{poke_name_eng}'
        poke_res = requests.get(poke_url)
        if poke_res.status_code != 200:
            st.warning('❌ 해당 포켓몬을 찾을 수 없습니다. 이름을 확인해주세요!')
        else:
            poke_data = poke_res.json()
            # 영어 이름
            english_name = poke_data.get('name', '').title()
            # 타입
            types = [t['type']['name'].title() for t in poke_data.get('types', [])]
            # 추천 스킬 (앞 5개)
            moves = [m['move']['name'].replace('-', ' ').title() for m in poke_data.get('moves', [])[:5]]
            # 포켓몬 이미지
            image_url = poke_data.get('sprites', {}).get('front_default')

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

            # 귀여운 카드 스타일
            st.markdown(f"""
            <div style='background-color: #FFF0F5; border-radius: 15px; padding: 20px; margin: 10px; text-align:center; box-shadow: 3px 3px 10px #FFC0CB;'>
                <h2 style='color:#FF69B4;'>✨ {english_name} ✨</h2>
                {f"<img src='{image_url}' width='150' style='border-radius:10px;' />" if image_url else ""}
                <p style='font-size:18px;'>💠 타입: {' / '.join(types)}</p>
                <p style='font-size:18px;'>🔺 진화 단계: {evo_stage}</p>
                <p style='font-size:18px;'>⭐ 추천 스킬: {', '.join(moves)}</p>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f'⚠️ 정보 조회 중 오류 발생: {e}')
