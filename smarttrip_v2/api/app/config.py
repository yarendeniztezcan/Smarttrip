import os

# API Keys
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")

# Database & Cache
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/smarttrip")

# Şehir bazlı maliyetler (USD)
CITY_COSTS = {
    "default": {"meal_avg": 15, "transport_daily": 8, "taxi_per_km": 2.0},
    "istanbul": {"meal_avg": 10, "transport_daily": 3, "taxi_per_km": 0.8},
    "stockholm": {"meal_avg": 30, "transport_daily": 18, "taxi_per_km": 3.5},
    "paris": {"meal_avg": 25, "transport_daily": 15, "taxi_per_km": 2.8},
    "london": {"meal_avg": 28, "transport_daily": 20, "taxi_per_km": 4.0},
    "new york": {"meal_avg": 30, "transport_daily": 15, "taxi_per_km": 3.2},
    "tokyo": {"meal_avg": 22, "transport_daily": 10, "taxi_per_km": 4.0},
    "bangkok": {"meal_avg": 8, "transport_daily": 4, "taxi_per_km": 0.6},
    "rome": {"meal_avg": 20, "transport_daily": 10, "taxi_per_km": 2.0},
    "barcelona": {"meal_avg": 18, "transport_daily": 8, "taxi_per_km": 1.8},
    "berlin": {"meal_avg": 18, "transport_daily": 12, "taxi_per_km": 2.2},
    "dubai": {"meal_avg": 25, "transport_daily": 10, "taxi_per_km": 1.5},
    "singapore": {"meal_avg": 20, "transport_daily": 10, "taxi_per_km": 2.0},
    "sydney": {"meal_avg": 26, "transport_daily": 18, "taxi_per_km": 3.0},
    "amsterdam": {"meal_avg": 22, "transport_daily": 12, "taxi_per_km": 3.0},
    "vienna": {"meal_avg": 20, "transport_daily": 10, "taxi_per_km": 2.5},
    "prague": {"meal_avg": 14, "transport_daily": 6, "taxi_per_km": 1.5},
    "budapest": {"meal_avg": 12, "transport_daily": 5, "taxi_per_km": 1.2},
    "copenhagen": {"meal_avg": 28, "transport_daily": 16, "taxi_per_km": 3.2},
    "oslo": {"meal_avg": 30, "transport_daily": 18, "taxi_per_km": 3.5},
    "helsinki": {"meal_avg": 26, "transport_daily": 15, "taxi_per_km": 3.0},
    "madrid": {"meal_avg": 18, "transport_daily": 10, "taxi_per_km": 2.0},
    "lisbon": {"meal_avg": 16, "transport_daily": 8, "taxi_per_km": 1.5},
    "athens": {"meal_avg": 14, "transport_daily": 6, "taxi_per_km": 1.2},
    "kyoto": {"meal_avg": 20, "transport_daily": 8, "taxi_per_km": 3.5},
    "seoul": {"meal_avg": 18, "transport_daily": 8, "taxi_per_km": 1.5},
    "mumbai": {"meal_avg": 8, "transport_daily": 3, "taxi_per_km": 0.5},
    "cairo": {"meal_avg": 8, "transport_daily": 2, "taxi_per_km": 0.4},
    "marrakech": {"meal_avg": 10, "transport_daily": 3, "taxi_per_km": 0.6},
    "rio de janeiro": {"meal_avg": 14, "transport_daily": 5, "taxi_per_km": 1.0},
    "buenos aires": {"meal_avg": 12, "transport_daily": 4, "taxi_per_km": 0.9},
    "edirne": {"meal_avg": 8, "transport_daily": 2, "taxi_per_km": 0.5},
    "izmir": {"meal_avg": 10, "transport_daily": 3, "taxi_per_km": 0.7},
    "ankara": {"meal_avg": 9, "transport_daily": 3, "taxi_per_km": 0.6},
    "antalya": {"meal_avg": 12, "transport_daily": 4, "taxi_per_km": 0.8},
    "bursa": {"meal_avg": 9, "transport_daily": 3, "taxi_per_km": 0.6},
    "konya": {"meal_avg": 8, "transport_daily": 2, "taxi_per_km": 0.5},
    "trabzon": {"meal_avg": 8, "transport_daily": 2, "taxi_per_km": 0.5},
    "cappadocia": {"meal_avg": 10, "transport_daily": 3, "taxi_per_km": 0.7},
    "bodrum": {"meal_avg": 15, "transport_daily": 5, "taxi_per_km": 1.0},
    "fethiye": {"meal_avg": 12, "transport_daily": 4, "taxi_per_km": 0.8},
    "pamukkale": {"meal_avg": 9, "transport_daily": 3, "taxi_per_km": 0.6},
    "ephesus": {"meal_avg": 9, "transport_daily": 3, "taxi_per_km": 0.6},
    "goreme": {"meal_avg": 10, "transport_daily": 3, "taxi_per_km": 0.7},
}

# Konsept → Google Places types mapping
CONCEPT_TYPES = {
    "tarihi": ["museum", "tourist_attraction", "historical_landmark", "monument", "church", "mosque", "synagogue", "castle", "palace"],
    "doğa": ["park", "natural_feature", "campground", "zoo", "aquarium", "national_park", "beach", "hiking_area", "waterfall"],
    "sanat": ["art_gallery", "museum", "performing_arts_theater", "cultural_center", "opera_house", "concert_hall"],
    "yemek": ["restaurant", "cafe", "bakery", "food", "bar", "pub", "brewery", "winery"],
    "mix": ["museum", "tourist_attraction", "park", "art_gallery", "restaurant", "cafe", "historical_landmark", "monument"]
}

# Mekan tipine göre tahmini ziyaret süresi (dakika)
PLACE_DURATION = {
    "museum": 150,
    "art_gallery": 90,
    "tourist_attraction": 120,
    "historical_landmark": 60,
    "monument": 45,
    "church": 45,
    "mosque": 45,
    "synagogue": 45,
    "castle": 90,
    "palace": 90,
    "park": 120,
    "natural_feature": 180,
    "national_park": 240,
    "beach": 180,
    "zoo": 180,
    "aquarium": 120,
    "hiking_area": 180,
    "waterfall": 60,
    "restaurant": 90,
    "cafe": 45,
    "bakery": 30,
    "food": 60,
    "bar": 60,
    "pub": 60,
    "brewery": 60,
    "winery": 60,
    "performing_arts_theater": 150,
    "cultural_center": 90,
    "opera_house": 150,
    "concert_hall": 150,
    "default": 90
}

# Google Places price_level → tahmini giriş ücreti (USD)
PRICE_LEVEL_COST = {0: 0, 1: 8, 2: 20, 3: 40, 4: 70}
