# 우리 지역 체크인

방문한 지역에 대한 만족도와 한 줄 메모를 남기고, 쌓인 기록을 지도·통계·표로 확인할 수 있는 위치 기반 방문 기록 서비스입니다. FastAPI 백엔드가 기록을 파일에 저장하고, Streamlit 프런트가 입력부터 조회·삭제·통계·다운로드까지 하나의 화면에서 처리합니다. 강남·여의도·마포·울산·광주·충청·강릉·제주 8개 지역을 대상으로 합니다.

## 기능

- **방문 기록 입력**: 이름·지역·만족도(1~5)·한 줄 메모를 입력해 기록을 저장
- **전체 기록 조회**: 저장된 모든 기록을 표로 확인 (최신순 정렬)
- **검색/필터**: 사이드바에서 지역, 최소 만족도, 메모 키워드로 기록 필터링
- **내 기록 조회**: 이름으로 본인이 남긴 기록만 조회, 기록 수·평균 만족도 확인
- **기록 삭제**: 잘못 남긴 기록을 id로 골라 삭제
- **통계 대시보드**: 총 기록 수, 참여자 수, 전체 평균 만족도, 지역별 평균 만족도 그래프
- **CSV 내보내기**: 검색 조건이 적용된 기록을 엑셀에서 바로 열리는 CSV로 다운로드
- **데모 지도**: 실습 시작 코드에 있던 랜덤 좌표 지도(저장된 기록과는 무관)

데이터는 `backend/data/records.jsonl` 파일에 JSONL 형식으로 저장됩니다.

## 프로젝트 구조

```
.
├── backend/            # FastAPI 서버 (API, 데이터 저장/조회)
│   ├── main.py
│   └── requirements.txt
├── frontend/           # Streamlit 화면
│   ├── app.py
│   └── requirements.txt
└── docker-compose.yml
```

## 로컬에서 실행하기

### 1. conda 환경 만들기

```bash
conda create -n checkin python=3.11 -y
conda activate checkin
```

### 2. 패키지 설치

백엔드와 프런트가 사용하는 패키지를 함께 설치합니다.

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 3. 백엔드 실행 (터미널 1)

```bash
cd backend
uvicorn main:app --reload
```

- API 문서: http://localhost:8000/docs

### 4. 프런트 실행 (터미널 2)

같은 conda 환경을 활성화한 새 터미널에서 실행합니다.

```bash
conda activate checkin
cd frontend
streamlit run app.py
```

- 화면 접속: http://localhost:8501

백엔드가 켜져 있어야 프런트에서 지역 목록·기록 저장/조회가 정상 동작합니다.

## Docker로 실행하기 (선택)

```bash
docker compose up --build
```

- 프런트: http://localhost:8501
- 백엔드: http://localhost:8000
