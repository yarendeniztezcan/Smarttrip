from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import TripRequest, TripResponse
from .services import generate_trip_plan

app = FastAPI(
    title="SmartTrip API",
    description="Konsept tabanlı otomatik tatil planlayıcı API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "SmartTrip API calisiyor",
        "docs": "/docs",
        "health": "/health",
        "plan_trip": "POST /plan-trip",
        "frontend": "http://localhost/"
    }

@app.get("/health")
def health():
    return {"status": "ok", "service": "smarttrip-api", "version": "1.0.0"}

@app.post("/plan-trip", response_model=TripResponse)
def plan_trip(request: TripRequest):
    try:
        req_dict = request.model_dump()
        result = generate_trip_plan(req_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sehirler")
def sehirler():
    from .config import CITY_COSTS
    return {
        "sehirler": [
            {
                "sehir": k,
                "yemek_ortalama": v["meal_avg"],
                "toplu_tasima_gunluk": v["transport_daily"],
                "taxi_km": v["taxi_per_km"]
            }
            for k, v in CITY_COSTS.items() if k != "default"
        ]
    }

@app.get("/konseptler")
def konseptler():
    return {
        "tarihi": "Muzeler, anitlar, tarihi yapilar",
        "doğa": "Parklar, hayvanat bahceleri, dogal alanlar",
        "sanat": "Sanat galerileri, muzeler, tiyatrolar",
        "yemek": "Restoranlar, kafeler, yerel lezzetler",
        "mix": "Tum kategorilerden karisik"
    }
