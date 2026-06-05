import streamlit as st
import google.generativeai as genai

# 1. 웹사이트 탭 제목과 기본 레이아웃 설정
st.set_page_config(page_title="AI 웰니스 가이드", page_icon="🧠", layout="centered")

# 2. 메인 타이틀 및 설명
st.title("🧠 AI 호르몬 & 웰니스 가이드 🏋️‍♂️")
st.caption("당신의 상태를 입력하면, 내분비학 및 스포츠 영양학 기반의 맞춤형 솔루션을 제공합니다.")

# 3. 깃허브 배포용 API 키 설정 (스트림릿 비밀 금고 활용)
# 🚨 주의: 이 부분은 st.secrets를 사용하므로 깃허브에 코드가 공개되어도 안전합니다.
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("API 키가 설정되지 않았습니다. Streamlit 대시보드 [Settings] -> [Secrets]에서 GEMINI_API_KEY를 설정해주세요.")
    st.stop()

# 4. AI 페르소나 및 출력 형식 강제 (프롬프트 엔지니어링)
system_instruction = """
당신은 내분비학, 스포츠 영양학, 그리고 신체 단련에 정통한 'AI 웰니스 가이드'입니다.
사용자가 현재의 심리적, 신체적 상태(피로도, 감정, 운동 여부 등)를 입력하면, 
다음을 분석하여 명확하고 구조화된 형태의 솔루션을 제시하세요.

1. 상태 분석 및 관련 호르몬: 사용자의 텍스트를 기반으로 추정되는 호르몬 불균형 상태 (예: 코르티솔 수치 증가, 도파민/세로토닌 저하 등)
2. 맞춤형 운동 처방: 신경계 피로 회복을 위한 저강도 유산소, 또는 테스토스테론 분비를 유도하는 고볼륨 점진적 과부하 훈련 등 현재 상태에 최적화된 구체적인 운동 프로토콜
3. 영양 및 식단 가이드: 부족한 호르몬 합성을 돕거나 피로 물질을 제거하기 위한 구체적인 식품과 영양소 추천
4. 주의사항: "본 가이드는 건강 관리를 위한 참고용이며, 의학적 진단을 대체하지 않습니다."라는 면책 조항 포함

전문적이고 신뢰감 있는 어조로 답변하되, 가독성 좋게 글머리 기호를 사용하여 출력하세요.
"""

# 5. 대화 세션 초기화 (새로고침해도 대화 기록 유지)
if "chat_session" not in st.session_state:
    # 최신 2.5 Flash 모델 적용
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_instruction
    )
    st.session_state.chat_session = model.start_chat(history=[])

# 6. 이전 대화 기록 화면에 출력하기
for message in st.session_state.chat_session.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 7. 채팅 입력창 (사용자 맞춤형 예시 텍스트 포함)
prompt = st.chat_input("예: 요즘 해야 할 일에 집중하지 못하고, 피로도가 높고 의욕이 떨어집니다.")

# 8. 사용자 입력 처리 및 AI 답변 스트리밍 출력
if prompt:
    # 사용자의 메시지를 우측(사용자) 말풍선에 출력
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # AI의 답변을 좌측(AI) 말풍선에 출력 (타자기 효과 적용)
    with st.chat_message("assistant"):
        with st.spinner("호르몬 상태와 솔루션을 분석 중입니다..."):
            try:
                # stream=True 옵션으로 텍스트를 조각내서 받아옴
                response = st.session_state.chat_session.send_message(prompt, stream=True)
                
                # 포장지(chunk)를 열어 알맹이(text)만 타자기처럼 출력
                st.write_stream(chunk.text for chunk in response)
            except Exception as e:
                # 에러 메시지에 429나 quota라는 단어가 포함되어 있다면
                if "429" in str(e) or "quota" in str(e).lower():
                    st.warning("⏳ 구글 API 무료 제한(1분당 최대 5회)을 초과했습니다. 약 1분만 기다렸다가 다시 질문해 주세요!")
                else:
                    st.error(f"오류가 발생했습니다: {e}")
