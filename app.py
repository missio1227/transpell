import streamlit as st
import requests
from hanspell import spell_checker
import html

# 페이지 설정
st.set_page_config(
    page_title="맞춤법 교정 & 번역 도구",
    page_icon="📝",
    layout="wide"
)

# 제목
st.title("📝 맞춤법 교정 & 번역 도구")
st.markdown("---")

# DeepL API 설정
DEEPL_API_KEY = "c8202d95-2679-4bb2-a58f-baad9330e216:fx"
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"


# 맞춤법 교정 함수
def correct_spelling_with_hanspell(text):
    try:
        if not text.strip():
            st.warning("교정할 텍스트가 없습니다.")
            return text, []

        # 줄바꿈 보존을 위해 줄 단위로 처리
        lines = text.splitlines()
        corrected_lines = []

        for line in lines:
            if line.strip():  # 비어 있지 않은 줄만 검사
                result = spell_checker.check(line)
                corrected_lines.append(result.checked)
            else:
                corrected_lines.append("")  # 빈 줄은 그대로 유지

        corrected_text = "\n".join(corrected_lines)
        return corrected_text, []

    except Exception as e:
        st.error(f"맞춤법 교정 중 오류 발생: {str(e)}")
        st.error(f"오류 타입: {type(e).__name__}")
        return text, []


# 번역 함수 (한글 ↔ 영어 자동 감지)
def translate_text(text):
    try:
        if not text.strip():
            st.warning("번역할 텍스트가 없습니다.")
            return None

        # 언어 자동 감지
        if any('\uac00' <= char <= '\ud7a3' for char in text):
            source_lang = "KO"
            target_lang = "EN"
        elif any('a' <= char.lower() <= 'z' for char in text):
            source_lang = "EN"
            target_lang = "KO"
        else:
            st.warning("지원되지 않는 언어입니다. 한국어 또는 영어만 입력해주세요.")
            return None

        headers = {
            "Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "preserve_formatting": 1  # 줄바꿈, 공백 유지
        }

        response = requests.post(DEEPL_API_URL, headers=headers, data=data)

        if response.status_code == 200:
            result = response.json()
            translated_text = result["translations"][0]["text"]
            return translated_text
        else:
            st.error(f"번역 API 오류: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        st.error(f"번역 중 오류가 발생했습니다: {str(e)}")
        return None


# 입력 및 결과 UI
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 텍스트 입력")
    input_text = st.text_area("텍스트 입력:", height=200)

    col1_1, col1_2 = st.columns(2)

    with col1_1:
        if st.button("🔍 맞춤법 확인", type="primary", use_container_width=True):
            if input_text.strip():
                with st.spinner("맞춤법을 확인하고 있습니다..."):
                    corrected_text, _ = correct_spelling_with_hanspell(input_text)
                    if corrected_text:
                        st.session_state.corrected_text = corrected_text
                        st.success("맞춤법 교정 완료!")

    with col1_2:
        if st.button("🌐 번역", type="secondary", use_container_width=True):
            text_to_translate = st.session_state.get('corrected_text', input_text)
            if text_to_translate.strip():
                with st.spinner("번역 중입니다..."):
                    translated_text = translate_text(text_to_translate)
                    if translated_text:
                        st.session_state.translated_text = translated_text
                        st.success("번역 완료!")

with col2:
    st.subheader("📋 결과")

    if 'corrected_text' in st.session_state:
        st.markdown("**✅ 맞춤법 교정 결과:**")
        st.code(st.session_state.corrected_text, language="text")

    if 'translated_text' in st.session_state:
        st.markdown("**🌐 번역 결과:**")
        st.code(st.session_state.translated_text, language="text")

# 하단 정보
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Made with Streamlit, py-hanspell, and DeepL API</p>
</div>
""", unsafe_allow_html=True)