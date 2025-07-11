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
    sheet = gc.open_by_url(st.secrets["GSHEET_URL"]).worksheet("debatebot2")
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

# ============================ UI 스타일 ============================
st.markdown("""
<style>
    .stApp {
        background-color: #e0e7ff;
    }
    .main-title {
        font-size: 28px;
        font-weight: 700;
        color: #1c2c5b;
        margin-top: 10px;
        text-align: center;
    }
    .subtitle {
        font-size: 16px;
        color: #6c757d;
        text-align: center;
        margin-top: -5px;
        margin-bottom: 25px;
    }
    .topic-box {
        background-color: #1c2c5b;
        color: white;
        padding: 14px 20px;
        border-radius: 12px;
        font-size: 17px;
        font-weight: 600;
        text-align: center;
        margin-bottom: 10px;
    }
    .stChatMessage.user {
        background-color: #3b82f6 !important;
        color: white !important;
        border-radius: 18px 18px 4px 18px;
        padding: 10px 14px;
        max-width: 80%;
    }
    .stChatMessage.assistant {
        background-color: white !important;
        color: black !important;
        border-radius: 18px 18px 18px 4px;
        padding: 10px 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        max-width: 80%;
    }
    .typing-indicator {
        display: flex;
        gap: 6px;
        padding-left: 10px;
        padding-bottom: 10px;
        margin-top: -10px;
    }
    .typing-dot {
        width: 8px;
        height: 8px;
        background: #a5b4fc;
        border-radius: 50%;
        animation: blink 1.4s infinite ease-in-out;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes blink {
        0%, 80%, 100% { opacity: 0; }
        40% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ============================ 상단 로고 및 안내 ============================
try:
    service_logo = Image.open("로고1.png")
    st.image(service_logo, width=80)
except:
    st.warning("로고1 이미지를 불러올 수 없습니다.")

st.markdown('<div class="main-title">토론 메이트 - 오늘의 주제 한마디</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">흥미로운 사회 주제에 대해 함께 생각해보고 이야기 나눠보아요. 🧠</div>', unsafe_allow_html=True)

# ============================ 주제 설정 ============================
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

st.markdown(f"<div class='topic-box'>📝 오늘의 주제: {st.session_state.current_topic}</div>", unsafe_allow_html=True)

# ============================ 첫 인삿말 ============================
if not st.session_state.messages:
    intro = f"""안녕하세요, 저는 오늘의 주제를 함께 이야기 나누는 '토론 메이트'예요! 🤖  
🗣️ **오늘의 주제: {st.session_state.current_topic}**  
이 주제에 대해 어떻게 생각하시나요? 찬성/반대 또는 다른 관점에서 자유롭게 이야기해 주세요."""
    st.session_state.messages.append({"role": "assistant", "content": intro})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🧑"):
        st.markdown(msg["content"])

# ============================ 사용자 입력 처리 ============================
if user_input := st.chat_input("메시지를 입력해주세요"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.turn_count += 1

    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    system_prompt = f"""
    당신은 논리적이고 도전적인 토론 파트너입니다. 주제는 "{st.session_state.current_topic}"입니다.

다음 조건을 반드시 지키세요:

1. 사용자의 주장에 **명확한 반론**을 제시하세요. 무조건 반대하거나, 다른 시각에서 비판하세요.
2. **절대 사용자 발언을 그대로 요약하거나 반복하지 마세요.** 공감만 하고 넘어가지 마세요.
3. 처음 반대를 할 때, **가상의 역할을 가진 인물**(예: 전업주부 A씨, 스타트업 대표 B씨, 대학생 C씨 등)의 반대 시각을 제시해주세요.
4. **답변은 3~4줄 이내**로 작성하고, 마지막에 반드시 선택형 질문 또는 반박 유도 질문을 던지세요.
"""

    with st.chat_message("assistant", avatar="🤖"):
        with st.empty():
            st.markdown("""
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            """, unsafe_allow_html=True)

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

    if st.session_state.turn_count == 3:
        st.markdown("👀 혹시 이 주제가 너무 어렵거나 지루하셨다면, 아래 버튼을 눌러 다른 주제로 바꿔보실 수 있어요!")

# ============================ 하단 주제 버튼 ============================
if st.button("🔄 다른 주제 주세요"):
    pick_new_topic()
    st.rerun()

log_to_gsheet(user_input, response, st.session_state.turn_count, st.session_state.start_time)
