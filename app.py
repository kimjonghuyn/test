import time
import streamlit as st

# 페이지 세팅 (반응형 화면 및 타이틀 설정)
st.set_page_config(
    page_title="⏱️ 나만의 반응형 타이머",
    page_icon="⏱️",
    layout="centered"
)

# -------------------------------------------------------------------
# [커스텀 CSS] 카드 형태 중앙 배치, clamp() 반응형 폰트 및 모바일 최적화
# -------------------------------------------------------------------
st.markdown("""
    <style>
    /* 배경 및 기본 글꼴 설정 */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* 타이머 카드 용기 */
    .timer-card {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* clamp()를 이용해 화면 크기에 따라 반응형으로 조절되는 큰 시계 텍스트 */
    .timer-display {
        font-family: 'Courier New', Courier, monospace;
        font-size: clamp(3.5rem, 12vw, 6.5rem);
        font-weight: 800;
        color: #2563eb;
        letter-spacing: 2px;
        margin: 1rem 0;
    }
    
    /* 버튼 스타일 조정 */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# [세션 상태(st.session_state) 초기화]
# -------------------------------------------------------------------
# status 종류: 'stopped'(정지/초기상태), 'running'(진행중), 'paused'(일시정지), 'completed'(완료)
if "status" not in st.session_state:
    st.session_state.status = "stopped"

if "total_seconds" not in st.session_state:
    st.session_state.total_seconds = 0

if "remaining_seconds" not in st.session_state:
    st.session_state.remaining_seconds = 0

if "end_time" not in st.session_state:
    st.session_state.end_time = 0.0

if "input_min" not in st.session_state:
    st.session_state.input_min = 0

if "input_sec" not in st.session_state:
    st.session_state.input_sec = 0

# -------------------------------------------------------------------
# [타이머 상태 변경 처리 함수들]
# -------------------------------------------------------------------
def set_quick_time(minutes):
    """빠른 설정 버튼을 눌렀을 때 입력값을 바꾸는 함수"""
    if st.session_state.status in ["stopped", "completed"]:
        st.session_state.input_min = minutes
        st.session_state.input_sec = 0

def start_timer():
    """타이머 시작 함수"""
    total = (st.session_state.input_min * 60) + st.session_state.input_sec
    if total <= 0:
        st.error("⚠️ 0분 0초 이상의 시간을 설정해 주세요!")
        return
    
    st.session_state.total_seconds = total
    st.session_state.remaining_seconds = float(total)
    # time.monotonic()으로 정확한 목표 끝 시각을 계산
    st.session_state.end_time = time.monotonic() + float(total)
    st.session_state.status = "running"

def pause_timer():
    """타이머 일시정지 함수"""
    if st.session_state.status == "running":
        # 현재 남은 시간을 정확하게 보존
        now = time.monotonic()
        rem = max(0.0, st.session_state.end_time - now)
        st.session_state.remaining_seconds = rem
        st.session_state.status = "paused"

def resume_timer():
    """타이머 계속(재개) 함수"""
    if st.session_state.status == "paused":
        # 보존된 남은 시각으로 end_time 재설정
        st.session_state.end_time = time.monotonic() + st.session_state.remaining_seconds
        st.session_state.status = "running"

def reset_timer():
    """타이머 초기화 함수"""
    st.session_state.status = "stopped"
    st.session_state.remaining_seconds = 0
    st.session_state.total_seconds = 0

# -------------------------------------------------------------------
# [실시간 갱신 프래그먼트 (st.fragment & run_every)]
# -------------------------------------------------------------------
@st.fragment(run_every="1s")
def render_timer_ui():
    """1초마다 UI를 실시간 부분 갱신하는 프래그먼트"""
    
    # 실행 중일 때는 단조 시계(monotonic) 기준으로 남은 시간 실시간 계산
    if st.session_state.status == "running":
        now = time.monotonic()
        remaining = max(0.0, st.session_state.end_time - now)
        st.session_state.remaining_seconds = remaining
        
        # 타이머 종료 처리
        if remaining <= 0:
            st.session_state.status = "completed"
            st.rerun()

    # 표시용 분/초 계산
    curr_rem = int(round(st.session_state.remaining_seconds))
    display_min = curr_rem // 60
    display_sec = curr_rem % 60
    time_str = f"{display_min:02d}:{display_sec:02d}"

    # 카드 형태 UI 출력
    st.markdown("<div class='timer-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='timer-display'>{time_str}</div>", unsafe_allow_html=True)

    # 진행률 막대(Progress Bar) 계산
    if st.session_state.total_seconds > 0:
        progress_val = min(1.0, max(0.0, st.session_state.remaining_seconds / st.session_state.total_seconds))
    else:
        progress_val = 0.0
    st.progress(progress_val)
    st.markdown("</div>", unsafe_allow_html=True)

    # 완료 상태 처리
    if st.session_state.status == "completed":
        st.balloons()
        st.success("🎉 시간이 완료되었습니다! 수고하셨습니다!")

# -------------------------------------------------------------------
# [메인 화면 레이아웃]
# -------------------------------------------------------------------
st.title("⏱️ 나만의 반응형 타이머")

# 1. 빠른 설정 버튼 (1분, 3분, 5분, 10분)
st.caption("⚡ 빠른 시간 설정")
q_col1, q_col2, q_col3, q_col4 = st.columns(4)
is_disabled = st.session_state.status in ["running", "paused"]

with q_col1:
    st.button("1분", on_click=set_quick_time, args=(1,), disabled=is_disabled, use_container_width=True)
with q_col2:
    st.button("3분", on_click=set_quick_time, args=(3,), disabled=is_disabled, use_container_width=True)
with q_col3:
    st.button("5분", on_click=set_quick_time, args=(5,), disabled=is_disabled, use_container_width=True)
with q_col4:
    st.button("10분", on_click=set_quick_time, args=(10,), disabled=is_disabled, use_container_width=True)

st.markdown("---")

# 2. 직접 시간 입력 수치 (실행 중에는 변경 금지 disabled=is_disabled)
input_col1, input_col2 = st.columns(2)
with input_col1:
    st.number_input(
        "분 (Min)",
        min_value=0,
        max_value=180,
        key="input_min",
        disabled=is_disabled
    )
with input_col2:
    st.number_input(
        "초 (Sec)",
        min_value=0,
        max_value=59,
        key="input_sec",
        disabled=is_disabled
    )

# 3. 실시간 타이머 및 진행률 막대 렌더링
render_timer_ui()

# 4. 제어 버튼 (시작 / 일시정지 / 계속 / 초기화)
btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    if st.session_state.status in ["stopped", "completed"]:
        st.button("▶️ 시작", on_click=start_timer, type="primary", use_container_width=True)
    elif st.session_state.status == "running":
        st.button("⏸️ 일시정지", on_click=pause_timer, use_container_width=True)
    elif st.session_state.status == "paused":
        st.button("▶️ 계속", on_click=resume_timer, type="primary", use_container_width=True)

with btn_col2:
    st.button("🔄 초기화", on_click=reset_timer, use_container_width=True)

with btn_col3:
    # 상태 안내 표시
    status_kr = {
        "stopped": "대기 중",
        "running": "작동 중",
        "paused": "일시정지",
        "completed": "완료됨"
    }
    st.info(f"상태: {status_kr.get(st.session_state.status, '대기 중')}")
