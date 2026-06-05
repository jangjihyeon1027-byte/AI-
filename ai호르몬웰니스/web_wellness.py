import streamlit as st
import google.generativeai as genai

# 1. 웹사이트 제목과 설정
st.set_page_config(page_title="AI 웰니스 가이드", page_icon="🧠", layout="centered")
st.title("🧠 AI 호르몬 & 웰니스 가이드 🏋️‍♂️")
st.caption("당신의 상태를 입력하면, 내분비학 및 스포츠 영양학 기반의 맞춤형 솔루션을 제공합니다.")

# 2. API 키 설정
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

system_instruction = """
당신은 내분비학, 스포츠 영양학, 그리고 신체 단련에 정통한 'AI 웰니스 가이드'입니다.
사용자가 현재의 심리적, 신체적 상태(피로도, 감정, 운동 여부 등)를 입력하면, 
다음을 분석하여 명확하고 구조화된 형태의 솔루션을 제시하세요.

1. 상태 분석 및 관련 호르몬: 추정되는 호르몬 상태
2. 맞춤형 운동 처방: 현재 상태에 최적화된 구체적인 운동 프로토콜
3. 영양 및 식단 가이드: 구체적인 식품과 영양소 추천
4. 주의사항: "본 가이드는 건강 관리를 위한 참고용이며, 의학적 진단을 대체하지 않습니다."라는 면책 조항 포함
"""

# 3. 대화 기록을 저장할 '세션 상태' 초기화
# 웹사이트는 새로고침될 때마다 데이터가 날아가기 때문에, 대화 기록을 기억하도록 설정해야 해.
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_instruction
    )
    st.session_state.chat_session = model.start_chat(history=[])

# 4. 이전 대화 기록들을 화면에 그려주기
for message in st.session_state.chat_session.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 5. 사용자 입력창 및 AI 답변 출력 부분
prompt = st.chat_input("현재의 기분, 체력 상태, 고민을 자유롭게 적어주세요")

if prompt:
    # 사용자가 입력한 내용을 화면에 표시
    with st.chat_message("user"):
        st.markdown(prompt)
        
   # AI가 생각하는 동안 빙글빙글 도는 로딩 애니메이션 표시
    with st.chat_message("assistant"):
        with st.spinner("호르몬 상태와 솔루션을 분석 중입니다..."):
            try:
                # 1. 스트리밍 옵션을 켜서 메시지 보내기
                response = st.session_state.chat_session.send_message(prompt, stream=True)
                
                # 2. st.write_stream() 함수를 사용해 글자가 타자 치듯 나오게 만들기
                st.write_stream(response)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
