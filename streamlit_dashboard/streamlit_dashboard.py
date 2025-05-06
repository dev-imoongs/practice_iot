import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import os
import altair as alt
from streamlit_autorefresh import st_autorefresh  # 중요!
import docker

# 페이지 설정
st.set_page_config(
    page_title="실시간 가스 모니터링",
    page_icon="🔥",
    layout="wide"
)

# 자동 새로고침 (5초마다)
st_autorefresh(interval=1000, limit=None, key="refresh")

# 환경변수 또는 기본값
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# DB 연결
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def restart_container(container_name):
    client = docker.from_env()  # Docker 클라이언트 생성
    try:
        container = client.containers.get(container_name)  # 컨테이너 가져오기
        if container.status != 'running':  # 컨테이너가 정지된 경우
            print(f"{container_name}가 정지되었습니다. 재시작 중...")
            container.start()  # 컨테이너 재시작
            st.success(f"{container_name} 컨테이너가 성공적으로 재시작되었습니다.")
        else:
            st.info(f"{container_name} 컨테이너는 이미 실행 중입니다.")
    except docker.errors.NotFound:
        st.error(f"컨테이너 {container_name}을(를) 찾을 수 없습니다.")
    except docker.errors.APIError as e:
        st.error(f"Docker API 오류: {e}")

# 데이터 로드
def load_data(minutes=5):
    conn = get_connection()
    cursor = conn.cursor()
    time_threshold = datetime.now() - timedelta(minutes=minutes)
    cursor.execute("""
        SELECT measured_at, sensor_id, gas_type, value, is_normal
        FROM sensor_readings
        WHERE measured_at >= %s
        ORDER BY measured_at ASC
    """, (time_threshold,))
    rows = cursor.fetchall()
    cursor.close()
    return pd.DataFrame(rows, columns=["measured_at", "sensor_id", "gas_type", "value", "is_normal"])

# 본격 UI
st.title("🔥 실시간 가스 센서 모니터링")

minutes = st.slider("최근 몇 분 데이터를 볼까요?", 1, 60, 5)

# 데이터 로딩
df = load_data(minutes)

if df.empty:
    st.warning("데이터가 없습니다.")
    if st.button("🚀 시뮬레이터 실행"):
        with st.spinner('시뮬레이터 컨테이너를 실행하는 중입니다...'):
            try:
                restart_container('gas_sensor_simulator')
            except Exception as e:
                st.error(f"❌ 시뮬레이터 실행 실패: {e}")
else:
    sensor_types = df["gas_type"].unique().tolist()
    selected_type = st.selectbox("센서 타입", sensor_types)

    df_filtered = df[df["gas_type"] == selected_type]

    # Altair 차트
    chart = alt.Chart(df_filtered).mark_line().encode(
        x=alt.X('measured_at:T', title='측정시간', axis=alt.Axis(format='%H:%M:%S')),
        y=alt.Y('value:Q', title='가스농도'),
        tooltip=['measured_at:T', 'value:Q', 'sensor_id:N']
    ).properties(
        width=900,
        height=400
    )
    
    st.altair_chart(chart, use_container_width=True)

    # 통계
    st.subheader("📊 통계")
    col1, col2, col3 = st.columns(3)
    col1.metric("평균", round(df_filtered["value"].mean(), 2))
    col2.metric("최대", round(df_filtered["value"].max(), 2))
    col3.metric("최소", round(df_filtered["value"].min(), 2))

    # 세션 상태 초기화
    if "show_alerts" not in st.session_state:
        st.session_state.show_alerts = False

    # 상단 텍스트와 버튼을 같은 줄에 배치
    col1, col2, col3 = st.columns([5, 1, 1])
    col1.subheader("📋 전체 센서 데이터")

    # 토글 버튼 텍스트 설정
    toggle_label = "📋 전체 데이터 보기" if st.session_state.show_alerts else "🚨 이상 데이터만 보기"
    if col2.button(toggle_label):
        st.session_state.show_alerts = not st.session_state.show_alerts

    # 시뮬레이터 다시 실행 버튼
    if col3.button("🚀 시뮬레이터 다시 실행"):
        with st.spinner('시뮬레이터 컨테이너를 다시 실행하는 중입니다...'):
            try:
                restart_container('gas_sensor_simulator')
            except Exception as e:
                st.error(f"❌ 시뮬레이터 실행 실패: {e}")

    # 상태에 따라 해당 위치에 데이터 표시
    if st.session_state.show_alerts:
        alerts = df_filtered[df_filtered["is_normal"] == False]
        if alerts.empty:
            st.info("이상 데이터가 없습니다.")
        else:
            st.error(f"🚨 이상 감지 {len(alerts)}건")
            st.dataframe(alerts[["measured_at", "sensor_id", "gas_type", "value", "is_normal"]])
    else:
        st.dataframe(df_filtered[["measured_at", "sensor_id", "gas_type", "value", "is_normal"]])

