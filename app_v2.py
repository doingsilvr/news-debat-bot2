import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import random
from datetime import datetime
import gspread
from pathlib import Path

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
st.set_page_config(page_title="DebateBot 2", page_icon="🤖", layout="wide")
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

# ============================ CSS ============================
st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fa;
    }
    .main-container {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 0 12px rgba(0, 0, 0, 0.05);
    }
    .header-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1c2c5b;
        text-align: center;
        margin-bottom: 10px;
    }
    .header-subtitle {
        font-size: 1rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 20px;
    }
    .chat-container {
        max-height: 450px;
        overflow-y: auto;
        padding-bottom: 10px;
    }
    .bot-message, .user-message {
        display: flex;
        align-items: flex-start;
        margin: 10px 0;
    }
    .bot-message .avatar, .user-message .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background-color: #1c2c5b;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        color: white;
        flex-shrink: 0;
    }
    .bot-message .message, .user-message .message {
        padding: 12px 16px;
        border-radius: 12px;
        margin: 0 10px;
        max-width: 80%;
        line-height: 1.5;
    }
    .bot-message .message {
        background-color: #eef1f9;
        color: #1c2c5b;
    }
    .user-message {
        flex-direction: row-reverse;
    }
    .user-message .avatar {
        background-color: #6f42c1;
    }
    .user-message .message {
        background-color: #1c2c5b;
        color: white;
    }
    .topic-card {
        background-color: #1c2c5b;
        color: white;
        padding: 12px 18px;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ============================ MAIN UI ============================
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown('<div class="header-title">DebateBot 2</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">남색 감성의 모바일 토론 챗봇</div>', unsafe_allow_html=True)

# ============================ 주제 표시 ============================
topics = [
    "재택근무, 계속 확대되어야 할까요?",
    "AI 면접 도입, 공정한 채용일까요?",
    "출산 장려 정책, 효과가 있을까요?",
    "기후 변화 대응, 개인의 책임도 클까요?",
    "학벌 중심 사회, 과연 공정한가요?",
]
if not st.session_state.current_topic:
    st.session_state.current_topic = random.choice(topics)
    st.session_state.messages = []
    st.session_state.turn_count = 0
    st.session_state.start_time = datetime.now()

st.markdown(f"<div class='topic-card'>📝 오늘의 주제: {st.session_state.current_topic}</div>", unsafe_allow_html=True)

# ============================ 첫 인삿말 ============================
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"안녕하세요! 저는 토론 메이트예요 🤖\n\n**{st.session_state.current_topic}**\n\n이 주제에 대해 어떻게 생각하시나요? 찬성 또는 반대 의견을 들려주세요!"
    })

# ============================ 채팅 표시 ============================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

avatar_path = Path("/mnt/data/챗봇로고.png")
avatar_tag = "🤖"
if avatar_path.exists():
    with open(avatar_path, "rb") as f:
        avatar_encoded = base64.b64encode(f.read()).decode()
        avatar_tag = f'<img src="data:image/png;base64,{avatar_encoded}" width="36" height="36" style="border-radius:50%;">'

for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.markdown(f"""
        <div class="bot-message">
            <div class="avatar">{avatar_tag}</div>
            <div class="message">{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="user-message">
            <div class="avatar">👤</div>
            <div class="message">{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================ 사용자 입력 ============================
if user_input := st.chat_input("당신의 생각을 들려주세요..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.turn_count += 1

    system_prompt = f"""
당신은 논리적이고 도전적인 토론 파트너입니다. 주제는 \"{st.session_state.current_topic}\"입니다.
반드시 사용자 주장에 반박하고, 가상의 인물을 인용하며 3-4줄 이내로 반응해주세요.
마지막에는 질문으로 마무리하세요.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
            temperature=0.7
        )
        bot_response = response.choices[0].message.content
    except Exception as e:
        bot_response = "❌ 죄송해요. 응답 생성 중 오류가 발생했어요."

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    try:
        log_to_gsheet(user_input, bot_response, st.session_state.turn_count, st.session_state.start_time)
    except:
        pass
    st.rerun()
