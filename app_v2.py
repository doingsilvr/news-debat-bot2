import streamlit as st
from openai import OpenAI
from PIL import Image
import random
from datetime import datetime
import gspread

# ============================ 시크릿 설정 ============================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ============================ 구글 시트 연동 ============================
def get_gsheet():
    credentials = st.secrets["GSHEET_CREDENTIALS"]
    gc = gspread.service_account_from_dict(credentials)
    sheet = gc.open_by_url(st.secrets["GSHEET_URL"]).worksheet("시트2")
    return sheet

def log_to_gsheet(user_input, gpt_response, turn, start_time):
    sheet = get_gsheet()
    duration_sec = int((datetime.now() - start_time).total_seconds())
    is_bounce = turn <= 1
    last_gpt_message = ""
    for m in reversed(st.session_state.messages):
        if m["role"] == "assistant":
            last_gpt_message = m["content"]
            break
    sheet.append_row([
        st.session_state.session_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        st.session_state.current_topic,
        turn,
        user_input,
        gpt_response,
        duration_sec,
        is_bounce,
        last_gpt_message
    ])

# ============================ 초기 상태 ============================
st.set_page_config(page_title="토론 메이트", page_icon="🗣️", layout="centered")

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()

# ============================ UI ============================
try:
    service_logo = Image.open("로고1.png")
    st.image(service_logo, width=100)
except:
    st.warning("로고1 이미지를 불러올 수 없습니다. '로고1.png' 파일을 확인해주세요.")

st.title("토론 메이트 - 오늘의 주제 한마디")
st.markdown("""<div style="text-align:center; margin-top:-10px; margin-bottom:30px; font-size:16px; color:#bbb;">흥미로운 사회 주제에 대해 함께 생각해보고 이야기 나눠보아요. 🧠</div>""", unsafe_allow_html=True)

topic_pool = [
    "재택근무, 계속 확대되어야 할까요?",
    "AI 면접 도입, 공정한 채용일까요?",
    "출산 장려 정책, 효과가 있을까요?",
    "기후 변화 대응, 개인의 책임도 클까요?",
    "학벌 중심 사회, 과연 공정한가요?",
]

def pick_new_topic():
    st.session_state.current_topic = random.choice(topic_pool)
    st.session_state.messages = []
    st.session_state.turn_count = 0
    st.session_state.start_time = datetime.now()

if not st.session_state.current_topic:
    pick_new_topic()

# 첫 인삿말
if not st.session_state.messages:
    intro = f"""안녕하세요, 저는 오늘의 주제를 함께 이야기 나누는 '토론 메이트'예요! 🤖  
🗣️ **오늘의 주제: {st.session_state.current_topic}**  
이 주제에 대해 어떻게 생각하시나요? 찬성/반대 또는 다른 관점에서 자유롭게 이야기해 주세요."""
    st.session_state.messages.append({"role": "assistant", "content": intro})

# 이전 메시지 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🧑"):
        st.markdown(msg["content"])

# 주제 바꾸기 버튼
if st.button("🔄 다른 주제 주세요"):
    pick_new_topic()
    st.rerun()

# ============================ 사용자 입력 처리 ============================
if user_input := st.chat_input("당신의 생각은 어떠신가요?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.turn_count += 1

    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    # 프롬프트 (전략 2-1: 인물 관점 + 반복 방지 조건 강화)
    system_prompt = f"""
    당신은 논리적이고 친근한 토론 파트너입니다. 주제는 "{st.session_state.current_topic}"입니다.

    다음 조건을 지키세요:
    - 반드시 하나의 주장을 제시하되, **특정 인물(가상 인물 또는 실제 인물)**의 관점에서 설명해 주세요.(예시 : “정의당 국회의원 A는 출산 장려 정책이 실효성이 없다고 말했어요.”, “회사원이자 엄마인 B 씨는 다르게 생각해요…”)
    - 사용자의 의견을 존중하되, 반드시 반대 시각도 함께 제시해 주세요.
    - 사용자의 이전 발언과 당신의 발언에서 **동일한 표현이나 논리를 반복하지 마세요**.
    - 필요하다면 구체적인 사례, 상황을 통해 질문을 유도하세요.
    - 응답은 5줄 이내로 요약해 주세요.
    - 끝에는 반드시 구체적인 질문으로 연결해 주세요.
    """

    with st.chat_message("assistant", avatar="🤖"):
        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                stream=True,
            )
            response = st.write_stream(stream)
        except Exception as e:
            response = f"❌ GPT 호출 중 오류가 발생했습니다: {str(e)}"
            st.error(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

    # 전략 1-2: turn=3일 때 주제 전환 안내 및 버튼 제공
    if st.session_state.turn_count == 3:
        st.markdown("👀 혹시 이 주제가 너무 어렵거나 지루하셨다면, 아래 버튼을 눌러 다른 주제로 바꿔보실 수 있어요!")
        if st.button("🔄 다른 주제 보기"):
            pick_new_topic()
            st.rerun()

    # 로그 저장
    log_to_gsheet(user_input, response, st.session_state.turn_count, st.session_state.start_time)
