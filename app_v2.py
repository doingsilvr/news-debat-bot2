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
    당신은 논리적이고 도전적인 토론 파트너입니다. 주제는 "{st.session_state.current_topic}"입니다.

다음 조건을 반드시 지키세요:

1. 사용자의 주장에 **명확한 반론**을 제시하세요. 무조건 반대하거나, 다른 시각에서 비판하세요.
2. **절대 사용자 발언을 그대로 요약하거나 반복하지 마세요.** 공감만 하고 넘어가지 마세요.
3. 필요한 경우, **가상의 역할을 가진 인물**(예: 전업주부 A씨, 스타트업 대표 B씨, 대학생 C씨 등)의 반대 시각을 제시해주세요.
   - 반드시 "~인 상황인 A씨는 ~라고 말했어요"와 같이 **주어가 먼저** 나오도록 작성하세요.
   - 인물의 **직업/사회적 위치/배경 맥락**도 함께 제공하세요.
4. 사용자의 주장과 **완전히 대비되는 논리 또는 정책 방향**을 제시하세요.  
   예: "재택근무는 효율적이다" → "기업 생산성 저하 문제를 초래한다"
5. **답변은 3-4줄 이내**로 작성하고, 마지막에 반드시 선택형 질문 또는 반박을 유도하는 질문을 던지세요.  
   예: "그렇다면 C씨처럼 오히려 불공정하다고 느끼는 사람들의 의견은 어떻게 생각하세요?"

절대로:
- 사용자 의견을 반복하지 마세요.
- 토론을 흐지부지 마무리하지 마세요.
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
