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
st.set_page_config(
    page_title="토론 메이트", 
    page_icon="🗣️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================ 커스텀 CSS ============================
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 메인 컨테이너 */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 30px;
        margin: 20px auto;
        max-width: 800px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
    }
    
    /* 헤더 스타일 */
    .app-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    
    .app-subtitle {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 20px;
    }
    
    /* 온라인 상태 표시 */
    .status-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin-bottom: 20px;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: #4CAF50;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* 주제 카드 */
    .topic-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }
    
    /* 메시지 컨테이너 */
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 20px 0;
        margin: 20px 0;
    }
    
    /* 봇 메시지 */
    .bot-message {
        display: flex;
        align-items: flex-start;
        margin-bottom: 20px;
        gap: 12px;
    }
    
    .bot-avatar {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
    }
    
    .bot-message-content {
        background: #f8f9ff;
        border: 1px solid #e1e5f2;
        border-radius: 18px 18px 18px 4px;
        padding: 15px 20px;
        max-width: 70%;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* 사용자 메시지 */
    .user-message {
        display: flex;
        align-items: flex-start;
        margin-bottom: 20px;
        gap: 12px;
        flex-direction: row-reverse;
    }
    
    .user-avatar {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #4CAF50, #45a049);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
    }
    
    .user-message-content {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 15px 20px;
        max-width: 70%;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* 채팅 입력창 */
    .stChatInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e1e5f2;
        padding: 15px 20px;
        font-size: 1rem;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
    }
    
    .stChatInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 로딩 애니메이션 */
    .typing-indicator {
        display: flex;
        gap: 4px;
        padding: 15px 20px;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: #667eea;
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main-container {
            margin: 10px;
            padding: 20px;
        }
        
        .bot-message-content,
        .user-message-content {
            max-width: 85%;
        }
        
        .app-title {
            font-size: 2rem;
        }
    }
    
    /* 스크롤바 커스터마이징 */
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
</style>
""", unsafe_allow_html=True)

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

# ============================ 메인 컨테이너 ============================
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ============================ 헤더 ============================
st.markdown("""
<div class="app-header">
    <h1 class="app-title">🗣️ 토론 메이트</h1>
    <p class="app-subtitle">흥미로운 사회 주제에 대해 함께 생각해보고 이야기 나눠보아요</p>
    <div class="status-indicator">
        <div class="status-dot"></div>
        <span style="color: #4CAF50; font-weight: 600;">Online Now</span>
    </div>
</div>
""", unsafe_allow_html=True)

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

# 주제 표시
st.markdown(f"""
<div class="topic-card">
    📝 오늘의 주제: {st.session_state.current_topic}
</div>
""", unsafe_allow_html=True)

# 첫 인삿말
if not st.session_state.messages:
    intro = f"""안녕하세요! 저는 토론 메이트예요 🤖

**{st.session_state.current_topic}**

이 주제에 대해 어떻게 생각하시나요? 찬성이든 반대든, 여러분의 솔직한 의견을 들려주세요!"""
    st.session_state.messages.append({"role": "assistant", "content": intro})

# ============================ 채팅 메시지 표시 ============================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.markdown(f"""
        <div class="bot-message">
            <div class="bot-avatar">🤖</div>
            <div class="bot-message-content">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="user-message">
            <div class="user-avatar">👤</div>
            <div class="user-message-content">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================ 컨트롤 버튼 ============================
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔄 다른 주제로 바꾸기"):
        pick_new_topic()
        st.rerun()

with col2:
    if st.session_state.turn_count > 0:
        st.markdown(f"<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 10px;'>💬 대화 턴: {st.session_state.turn_count}</div>", unsafe_allow_html=True)

# ============================ 사용자 입력 처리 ============================
if user_input := st.chat_input("당신의 생각을 들려주세요..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.turn_count += 1

    # 사용자 메시지 즉시 표시
    st.markdown(f"""
    <div class="user-message">
        <div class="user-avatar">👤</div>
        <div class="user-message-content">{user_input}</div>
    </div>
    """, unsafe_allow_html=True)

    # 타이핑 인디케이터 표시
    typing_placeholder = st.empty()
    typing_placeholder.markdown("""
    <div class="bot-message">
        <div class="bot-avatar">🤖</div>
        <div class="bot-message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 프롬프트 (기존과 동일)
    system_prompt = f"""
    당신은 논리적이고 도전적인 토론 파트너입니다. 주제는 "{st.session_state.current_topic}"입니다.

다음 조건을 반드시 지키세요:

1. 사용자의 주장에 **명확한 반론**을 제시하세요. 무조건 반대하거나, 다른 시각에서 비판하세요.
2. **절대 사용자 발언을 그대로 요약하거나 반복하지 마세요.** 공감만 하고 넘어가지 마세요.
3. 처음 반대를 할 때, **가상의 역할을 가진 인물**(예: 전업주부 A씨, 스타트업 대표 B씨, 대학생 C씨 등)의 반대 시각을 제시해주세요.
   - 반드시 "~인 상황인 A씨는 ~라고 말했어요"와 같이 **주어가 먼저** 나오도록 작성하세요.
   - 인물의 **직업/사회적 위치/배경 맥락**도 함께 제공하세요.
4. 사용자의 주장과 **완전히 대비되는 논리 또는 정책 방향**을 제시하세요.  
   예: "재택근무는 효율적이다" → "기업 생산성 저하 문제를 초래한다"
5. **반드시 답변은 3-4줄 이내**로 작성하고, 마지막에 반드시 선택형 질문 또는 반박을 유도하는 질문을 던지세요.  
   예: "그렇다면 C씨처럼 오히려 불공정하다고 느끼는 사람들의 의견은 어떻게 생각하세요?"

절대로:
- 사용자 의견을 반복하지 마세요.
- 토론을 흐지부지 마무리하지 마세요.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
            temperature=0.7
        )
        bot_response = response.choices[0].message.content
        
        # 타이핑 인디케이터 제거 및 실제 응답 표시
        typing_placeholder.empty()
        
    except Exception as e:
        bot_response = f"❌ 죄송해요, 일시적인 오류가 발생했습니다. 다시 시도해주세요."
        typing_placeholder.empty()

    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # 봇 응답 표시
    st.markdown(f"""
    <div class="bot-message">
        <div class="bot-avatar">🤖</div>
        <div class="bot-message-content">{bot_response}</div>
    </div>
    """, unsafe_allow_html=True)

    # turn=3일 때 주제 전환 안내
    if st.session_state.turn_count == 3:
        st.markdown("""
        <div style="text-align: center; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 10px; padding: 15px; margin: 20px 0; color: #856404;">
            💡 <strong>혹시 이 주제가 어렵거나 지루하셨나요?</strong><br>
            언제든 새로운 주제로 바꿔보실 수 있어요!
        </div>
        """, unsafe_allow_html=True)

    # 로그 저장
    try:
        log_to_gsheet(user_input, bot_response, st.session_state.turn_count, st.session_state.start_time)
    except:
        pass  # 로그 저장 실패해도 앱 동작에는 영향 없음

    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)  # main-container 종료
