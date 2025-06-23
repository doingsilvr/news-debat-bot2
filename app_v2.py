# ===== IMPORTS =====
import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import random
from datetime import datetime
import gspread

# ===== SETUP =====
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

# ===== STATE =====
st.set_page_config(page_title="DebateBot 2", page_icon="🟣", layout="wide")
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

# ===== CSS =====
st.markdown("""
<style>
/* 기본 구조 */
.stApp { background-color: #fdfbff; }
.main-container {
    background-color: #ffffff; border-radius: 20px;
    padding: 30px; max-width: 800px; margin: auto;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}
.header { display: flex; flex-direction: column; align-items: center; margin-bottom: 20px; }
.header img { width: 80px; height: 80px; margin-bottom: 10px; }
.header-title { font-size: 2rem; font-weight: bold; color: #6b4eff; }
.header-subtitle { font-size: 1rem; color: #666; margin-top: 5px; }

/* 메시지 */
.chat-container { padding: 20px 0; max-height: 400px; overflow-y: auto; }
.bot-message, .user-message { display: flex; margin-bottom: 16px; }
.bot-message .avatar, .user-message .avatar {
    width: 40px; height: 40px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; background-color: #6b4eff20;
}
.bot-message .message, .user-message .message {
    padding: 12px 16px; border-radius: 15px; max-width: 70%;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08); line-height: 1.5;
}
.bot-message .message { background-color: #f4f2ff; color: #333; }
.user-message { flex-direction: row-reverse; }
.user-message .avatar { background-color: #d1c4fd; margin-left: 10px; margin-right: 0; }
.user-message .message { background-color: #6b4eff; color: #fff; }

/* 토픽 */
.topic-card {
    text-align: center; background-color: #ede7ff; color: #4a3fc1;
    padding: 15px; border-radius: 10px; font-weight: 600; margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.markdown('<div class="main-container">', unsafe_allow_html=True)
with open("/mnt/data/챗봇로고.png", "rb") as image_file:
    encoded = base64.b64encode(image_file.read()).decode()

st.markdown(f"""
<div class="header">
    <img src="data:image/png;base64,{encoded}" alt="Chatbot Logo">
    <div class="header-title">DebateBot 2</div>
    <div class="header-subtitle">보라색 감성의 논쟁형 AI 챗봇</div>
</div>
""", unsafe_allow_html=True)

# ===== TOPIC =====
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

# ===== INTRO MESSAGE =====
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"안녕하세요! 저는 토론 메이트예요 🤖\n\n**{st.session_state.current_topic}**\n\n이 주제에 대해 어떻게 생각하시나요? 찬성 또는 반대 의견을 들려주세요!"
    })

# ===== CHAT LOG VIEW =====
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <div class="avatar">👤</div>
            <div class="message">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="bot-message">
            <div class="avatar">🤖</div>
            <div class="message">{content}</div>
        </div>
        """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ===== USER INPUT + RESPONSE =====
if user_input := st.chat_input("당신의 생각을 들려주세요..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.turn_count += 1

    # SYSTEM PROMPT
    system_prompt = f"""
당신은 논리적이고 도전적인 토론 파트너입니다. 주제는 \"{st.session_state.current_topic}\"입니다.
반드시 사용자 주장에 반박하고, 가상의 인물을 인용하며 3-4줄 이내로 반응해주세요.
마지막에는 질문으로 마무리하세요.
"""

    with st.spinner("🤖 생각 중..."):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                temperature=0.7
            )
            bot_msg = response.choices[0].message.content
        except Exception as e:
            bot_msg = "❌ 죄송해요. 응답을 생성하는 중 오류가 발생했어요."

    st.session_state.messages.append({"role": "assistant", "content": bot_msg})
    try:
        log_to_gsheet(user_input, bot_msg, st.session_state.turn_count, st.session_state.start_time)
    except:
        pass
    st.rerun()

