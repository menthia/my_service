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

with st.sidebar:
    st.subheader("검색 조건")
    filter_region = st.selectbox("지역", ["전체"] + list(locations.keys()))
    filter_min_score = st.slider("최소 만족도", 1, 5, 1)
    filter_keyword = st.text_input("메모 검색")

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

st.subheader("전체 현황")
try:
    stats = requests.get(f"{BACKEND_URL}/stats", timeout=5).json()
except requests.exceptions.RequestException:
    st.error("백엔드에 연결할 수 없습니다. 터미널 1에서 백엔드가 켜져 있는지 확인하세요.")
else:
    s_col1, s_col2, s_col3 = st.columns(3)
    s_col1.metric("총 기록 수", stats["total"])
    s_col2.metric("참여자 수", stats["user_count"])
    s_col3.metric("전체 평균 만족도", stats["overall_avg"])

    if stats["by_region"]:
        region_df = pd.DataFrame(stats["by_region"]).set_index("region")
        st.bar_chart(region_df["avg_score"])

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

st.subheader("내 기록 조회")
query_name = st.text_input("조회할 이름")
if st.button("내 기록 보기"):
    try:
        st.session_state["user_res"] = requests.get(
            f"{BACKEND_URL}/records/user/{query_name}", timeout=5
        ).json()
    except requests.exceptions.RequestException:
        st.error("백엔드에 연결할 수 없습니다. 터미널 1에서 백엔드가 켜져 있는지 확인하세요.")

if "user_res" in st.session_state:
    user_res = st.session_state["user_res"]
    if user_res["count"] == 0:
        st.info(f"'{user_res['user_name']}' 이름으로 남긴 기록이 없습니다.")
    else:
        m_col1, m_col2 = st.columns(2)
        m_col1.metric("내 기록 수", user_res["count"])
        m_col2.metric("평균 만족도", user_res["avg_score"])
        st.dataframe(pd.DataFrame(user_res["records"]))

        delete_options = {
            f"{r['id']} · {r['region']} · {r['score']} · {r['memo']}": r["id"]
            for r in user_res["records"]
        }
        selected_label = st.selectbox("삭제할 기록 선택", list(delete_options.keys()))
        if st.button("선택한 기록 삭제"):
            record_id = delete_options[selected_label]
            try:
                del_res = requests.delete(f"{BACKEND_URL}/records/{record_id}", timeout=5)
            except requests.exceptions.RequestException:
                st.error("백엔드에 연결할 수 없습니다. 터미널 1에서 백엔드가 켜져 있는지 확인하세요.")
            else:
                if del_res.status_code == 200:
                    st.success("삭제했습니다")
                    st.session_state["user_res"] = requests.get(
                        f"{BACKEND_URL}/records/user/{user_res['user_name']}", timeout=5
                    ).json()
                    st.rerun()
                else:
                    st.error(del_res.json().get("detail"))

st.subheader("전체 기록")
filter_params = {}
if filter_region != "전체":
    filter_params["region"] = filter_region
if filter_min_score != 1:
    filter_params["min_score"] = filter_min_score
if filter_keyword:
    filter_params["keyword"] = filter_keyword

try:
    records_res = requests.get(f"{BACKEND_URL}/records", params=filter_params, timeout=5).json()
except requests.exceptions.RequestException:
    st.error("백엔드에 연결할 수 없습니다. 터미널 1에서 백엔드가 켜져 있는지 확인하세요.")
else:
    with st.sidebar:
        st.caption(f"조건에 맞는 기록: {records_res['count']}건")

    if records_res["count"] == 0:
        st.warning("조건에 맞는 기록이 없습니다. 조건을 완화해보세요.")
    else:
        st.dataframe(pd.DataFrame(records_res["records"]))

        try:
            csv_res = requests.get(
                f"{BACKEND_URL}/records/export.csv", params=filter_params, timeout=5
            )
            st.download_button(
                "CSV로 내려받기",
                data=csv_res.content,
                file_name="records.csv",
                mime="text/csv",
            )
        except requests.exceptions.RequestException:
            st.error("백엔드에 연결할 수 없습니다. 터미널 1에서 백엔드가 켜져 있는지 확인하세요.")
