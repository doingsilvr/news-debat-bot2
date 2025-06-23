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

# ============================ 초기 상태 ============================
st.set_page_config(
    page_title="DebateBot 2", 
    page_icon="🟣", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
        background-color: #fdfbff;
    }
    .main-container {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 30px;
        max-width: 800px;
        margin: auto;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    }
    .header {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 20px;
    }
    .header img {
        width: 80px;
        height: 80px;
        margin-bottom: 10px;
    }
    .header-title {
        font-size: 2rem;
        font-weight: bold;
        color: #6b4eff;
    }
    .header-subtitle {
        font-size: 1rem;
        color: #666;
        margin-top: 5px;
    }
    .chat-container {
        padding: 20px 0;
        max-height: 400px;
        overflow-y: auto;
    }
    .bot-message, .user-message {
        display: flex;
        margin-bottom: 16px;
    }
    .bot-message .avatar, .user-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-right: 10px;
        background-color: #6b4eff20;
    }
    .bot-message .message, .user-message .message {
        padding: 12px 16px;
        border-radius: 15px;
        max-width: 70%;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        line-height: 1.5;
    }
    .bot-message .message {
        background-color: #f4f2ff;
        color: #333;
    }
    .user-message {
        flex-direction: row-reverse;
    }
    .user-message .avatar {
        background-color: #d1c4fd;
        margin-left: 10px;
        margin-right: 0;
    }
    .user-message .message {
        background-color: #6b4eff;
        color: #fff;
    }
    .topic-card {
        text-align: center;
        background-color: #ede7ff;
        color: #4a3fc1;
        padding: 15px;
        border-radius: 10px;
        font-weight: 600;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ============================ 메인 UI ============================
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <img src="data:image/png;base64,""" + st.image("/mnt/data/챗봇로고.png", output_format="PNG") + """" alt="Chatbot Logo">
    <div class="header-title">DebateBot 2</div>
    <div class="header-subtitle">보라색 감성의 논쟁형 AI 챗봇</div>
</div>
""", unsafe_allow_html=True)

# 이후 코드는 기존 메시지 표시/입력 처리/로깅 구조 그대로 유지하되, 클래스 네이밍만 반영하여 새로운 스타일을 입히면 됨

