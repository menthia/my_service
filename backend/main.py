import json
import random
import uuid
from datetime import timedelta, timezone
from datetime import datetime as dt
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Location API")

LOCATIONS = {
    "강남": {"lat": 37.4979, "lon": 127.0276},
    "여의도": {"lat": 37.5219, "lon": 126.9245},
    "마포": {"lat": 37.5663, "lon": 126.9014},
    "울산": {"lat": 35.5384, "lon": 129.3114},
    "광주": {"lat": 35.1595, "lon": 126.8526},
    "충청": {"lat": 36.6357, "lon": 127.4917},
    "강릉": {"lat": 37.7519, "lon": 128.8761},
    "제주": {"lat": 33.4996, "lon": 126.5312},
}

KST = timezone(timedelta(hours=9))

DATA_FILE = Path(__file__).parent / "data" / "records.jsonl"
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


class RecordCreate(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=20)
    region: str
    score: int = Field(..., ge=1, le=5)
    memo: str = Field(default="", max_length=100)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/locations")
def get_locations():
    return LOCATIONS


@app.get("/locations/{name}")
def get_location(name: str):
    if name not in LOCATIONS:
        raise HTTPException(status_code=404, detail="location not found")
    return LOCATIONS[name]


@app.post("/records", status_code=201)
def create_record(payload: RecordCreate):
    if payload.region not in LOCATIONS:
        raise HTTPException(status_code=400, detail="invalid region")

    center = LOCATIONS[payload.region]
    record = {
        "id": uuid.uuid4().hex[:8],
        "user_name": payload.user_name,
        "region": payload.region,
        "score": payload.score,
        "memo": payload.memo,
        "lat": center["lat"] + random.uniform(-0.01, 0.01),
        "lon": center["lon"] + random.uniform(-0.01, 0.01),
        "created_at": dt.now(KST).isoformat(),
    }

    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


@app.get("/records")
def get_records():
    records = []
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))

    records.sort(key=lambda r: r["created_at"], reverse=True)
    return {"count": len(records), "records": records}


@app.get("/records/user/{user_name}")
def get_records_by_user(user_name: str):
    records = []
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    record = json.loads(line)
                    if record["user_name"] == user_name:
                        records.append(record)

    records.sort(key=lambda r: r["created_at"], reverse=True)
    count = len(records)
    avg_score = round(sum(r["score"] for r in records) / count, 1) if count else 0

    return {
        "user_name": user_name,
        "count": count,
        "avg_score": avg_score,
        "records": records,
    }
