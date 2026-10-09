from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx, os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Разрешаем запросы с твоего сайта (можно поставить "*", но лучше указать домен)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # если знаешь домен, лучше указать его, например ["https://tvoi-sait.ru"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

YANDEX_API_KEY = os.environ["YANDEX_API_KEY"]
YANDEX_BASE = "https://api.rasp.yandex-net.ru/v3.0"

@app.get("/api/trains")
async def get_trains(station: str = Query(..., description="Код станции")):
    today = __import__("datetime").date.today().isoformat()
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{YANDEX_BASE}/schedule/", params={
            "apikey": YANDEX_API_KEY,
            "station": station,
            "transport_types": "train",
            "event": "arrival",
            "date": today,
            "lang": "ru_RU",
            "format": "json",
        })
        data = resp.json()

    trains = []
    for item in data.get("schedule", []):
        trains.append({
            "number": item["thread"]["number"],
            "title": item["thread"]["title"],
            "arrival": item.get("arrival", ""),
            "platform": item.get("platform", ""),
            "carrier": item["thread"].get("carrier", {}).get("title", ""),
        })
    trains.sort(key=lambda t: t["arrival"])
    return {"station": data.get("station", {}).get("title", station), "trains": trains}

@app.get("/", response_class=str)
def root():
    return "API работает"
