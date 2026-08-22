import os
import random

import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="위치 랜덤 데이터 시각화", layout="wide")
st.title("위치 기반 랜덤 데이터 시각화")

try:
    locations = requests.get(f"{BACKEND_URL}/locations", timeout=5).json()
except requests.exceptions.RequestException as e:
    st.error(f"백엔드 연결 실패: {e}")
    st.stop()

with st.form("record_form"):
    record_name = st.text_input("이름")
    record_city = st.selectbox("지역", list(locations.keys()))
    record_rating = st.slider("만족도", 1, 5, 3)
    record_memo = st.text_input("한 줄 메모")
    submitted = st.form_submit_button("기록 저장")

if submitted:
    if not record_name:
        st.warning("이름을 입력해주세요")
    else:
        try:
            res = requests.post(
                f"{BACKEND_URL}/records",
                json={
                    "user_name": record_name,
                    "region": record_city,
                    "score": record_rating,
                    "memo": record_memo,
                },
                timeout=5,
            )
            if res.status_code == 201:
                st.success(f"저장 완료! (id: {res.json()['id']})")
            else:
                st.error(res.json().get("detail"))
        except requests.exceptions.RequestException:
            st.error("백엔드에 연결할 수 없습니다. 터미널 1에서 백엔드가 켜져 있는지 확인하세요.")

city = st.selectbox("지역 선택", list(locations.keys()))
n_points = st.slider("랜덤 포인트 개수", 10, 200, 50)

center = locations[city]

random.seed()
df = pd.DataFrame(
    {
        "lat": [center["lat"] + random.uniform(-0.02, 0.02) for _ in range(n_points)],
        "lon": [center["lon"] + random.uniform(-0.02, 0.02) for _ in range(n_points)],
        "value": [random.randint(1, 100) for _ in range(n_points)],
    }
)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"{city} 지도")
    st.map(df, latitude="lat", longitude="lon", size="value")

with col2:
    st.subheader("값 분포")
    st.bar_chart(df["value"])

st.subheader("원본 데이터")
st.dataframe(df)

st.subheader("전체 기록")
try:
    records_res = requests.get(f"{BACKEND_URL}/records", timeout=5).json()
except requests.exceptions.RequestException:
    st.error("백엔드에 연결할 수 없습니다. 터미널 1에서 백엔드가 켜져 있는지 확인하세요.")
else:
    if records_res["count"] == 0:
        st.info("아직 기록이 없습니다. 위에서 첫 기록을 남겨보세요.")
    else:
        st.dataframe(pd.DataFrame(records_res["records"]))
