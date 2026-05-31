import math
import requests
from typing import List, Dict
from .config import (
    GOOGLE_PLACES_API_KEY, CITY_COSTS, CONCEPT_TYPES,
    PLACE_DURATION, PRICE_LEVEL_COST
)


def get_city_costs(sehir: str) -> dict:
    sehir_lower = sehir.lower().strip()
    return CITY_COSTS.get(sehir_lower, CITY_COSTS["default"])


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def get_concept_for_day(konseptler: List[str], gun_index: int) -> str:
    if not konseptler:
        return "mix"
    if len(konseptler) == 1:
        return konseptler[0]
    return konseptler[gun_index % len(konseptler)]


def fetch_places_google(sehir: str, konsept: str, max_results: int = 20) -> List[Dict]:
    if not GOOGLE_PLACES_API_KEY:
        return []

    types = CONCEPT_TYPES.get(konsept, CONCEPT_TYPES["mix"])
    all_places = []
    seen = set()

    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types,places.priceLevel,places.rating,places.userRatingCount"
    }

    price_map = {
        "PRICE_LEVEL_UNSPECIFIED": 0,
        "PRICE_LEVEL_FREE": 0,
        "PRICE_LEVEL_INEXPENSIVE": 1,
        "PRICE_LEVEL_MODERATE": 2,
        "PRICE_LEVEL_EXPENSIVE": 3,
        "PRICE_LEVEL_VERY_EXPENSIVE": 4
    }

    for place_type in types[:3]:
        payload = {
            "textQuery": f"{place_type} in {sehir}",
            "pageSize": min(max_results, 20),
            "languageCode": "tr"
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                for p in data.get("places", []):
                    loc = p.get("location", {})
                    price_str = p.get("priceLevel", "PRICE_LEVEL_UNSPECIFIED")
                    name = p.get("displayName", {}).get("text", "Bilinmeyen")

                    if name in seen:
                        continue
                    seen.add(name)

                    primary_type = p.get("types", ["default"])[0]
                    price_level = price_map.get(price_str, 0)

                    place = {
                        "name": name,
                        "lat": loc.get("latitude", 0),
                        "lon": loc.get("longitude", 0),
                        "types": p.get("types", []),
                        "price_level": price_level,
                        "rating": p.get("rating", 0),
                        "user_ratings_total": p.get("userRatingCount", 0),
                        "address": p.get("formattedAddress", ""),
                        "duration_minutes": PLACE_DURATION.get(primary_type, PLACE_DURATION["default"]),
                        "entry_cost": PRICE_LEVEL_COST.get(price_level, 0),
                        "assigned_konsept": konsept
                    }
                    all_places.append(place)
        except Exception as e:
            print(f"Google Places API error: {e}")
            continue

    all_places.sort(key=lambda x: (x["rating"], x["user_ratings_total"]), reverse=True)
    return all_places[:max_results]


def fetch_places_nominatim(sehir: str, konsept: str, max_results: int = 20) -> List[Dict]:
    types = CONCEPT_TYPES.get(konsept, CONCEPT_TYPES["mix"])
    query_map = {
        "museum": "museum",
        "park": "park",
        "tourist_attraction": "tourism",
        "art_gallery": "gallery",
        "restaurant": "restaurant",
        "cafe": "cafe",
        "historical_landmark": "historic",
        "monument": "monument",
        "church": "church",
        "mosque": "mosque",
        "zoo": "zoo",
        "aquarium": "aquarium",
        "beach": "beach",
        "castle": "castle",
        "palace": "palace"
    }

    all_places = []
    seen = set()

    for t in types[:4]:
        q = query_map.get(t, t)
        url = f"https://nominatim.openstreetmap.org/search?q={q}+{sehir}&format=json&limit={max_results // 2}"
        headers = {"User-Agent": "SmartTrip/1.0"}
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                for p in resp.json():
                    name = p.get("display_name", "Bilinmeyen").split(",")[0]
                    key = (name, p.get("lat"))
                    if key in seen:
                        continue
                    seen.add(key)

                    lat = float(p.get("lat", 0))
                    lon = float(p.get("lon", 0))
                    place = {
                        "name": name,
                        "lat": lat,
                        "lon": lon,
                        "types": [t],
                        "price_level": 0,
                        "rating": 4.0,
                        "user_ratings_total": 10,
                        "address": p.get("display_name", ""),
                        "duration_minutes": PLACE_DURATION.get(t, 90),
                        "entry_cost": 0.0,
                        "assigned_konsept": konsept
                    }
                    all_places.append(place)
        except Exception as e:
            print(f"Nominatim error: {e}")
            continue

    return all_places


def get_city_center(sehir: str) -> tuple:
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={sehir}&format=json&limit=1"
        headers = {"User-Agent": "SmartTrip/1.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200 and resp.json():
            p = resp.json()[0]
            return float(p["lat"]), float(p["lon"])
    except Exception as e:
        print(f"Geocoding error: {e}")
    return (59.3293, 18.0686)


def plan_greedy_route(places: List[Dict], start_lat: float, start_lon: float,
                      daily_max: int, gun_sayisi: int) -> List[List[Dict]]:
    if not places:
        return [[] for _ in range(gun_sayisi)]

    sorted_places = []
    current_lat, current_lon = start_lat, start_lon
    remaining = places.copy()

    while remaining:
        nearest_idx = min(
            range(len(remaining)),
            key=lambda i: haversine(current_lat, current_lon, remaining[i]["lat"], remaining[i]["lon"])
        )
        nearest = remaining.pop(nearest_idx)
        sorted_places.append(nearest)
        current_lat, current_lon = nearest["lat"], nearest["lon"]

    days = []
    for i in range(gun_sayisi):
        start = i * daily_max
        end = start + daily_max
        day_places = sorted_places[start:end]
        days.append(day_places)

    return days


def calculate_transport_cost(distance_km: float, ulasim_tipi: str, sehir: str) -> float:
    costs = get_city_costs(sehir)
    if ulasim_tipi == "yuruyus":
        return 0.0
    elif ulasim_tipi == "toplu_tasima":
        return costs["transport_daily"] / 4.0
    else:
        return distance_km * costs["taxi_per_km"]


def find_nearby_cafe(lat: float, lon: float, sehir: str) -> Dict:
    if GOOGLE_PLACES_API_KEY:
        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": "places.displayName,places.priceLevel,places.rating"
        }
        payload = {
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lon},
                    "radius": 500.0
                }
            },
            "includedTypes": ["cafe", "restaurant"],
            "maxResultCount": 3
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                places = resp.json().get("places", [])
                if places:
                    p = places[0]
                    price_str = p.get("priceLevel", "PRICE_LEVEL_UNSPECIFIED")
                    price_map = {
                        "PRICE_LEVEL_UNSPECIFIED": 0,
                        "PRICE_LEVEL_FREE": 0,
                        "PRICE_LEVEL_INEXPENSIVE": 1,
                        "PRICE_LEVEL_MODERATE": 2,
                        "PRICE_LEVEL_EXPENSIVE": 3,
                        "PRICE_LEVEL_VERY_EXPENSIVE": 4
                    }
                    cost = PRICE_LEVEL_COST.get(price_map.get(price_str, 0), 0)
                    return {
                        "name": p.get("displayName", {}).get("text", "Kafe"),
                        "rating": p.get("rating", 0),
                        "estimated_cost": cost
                    }
        except Exception:
            pass

    return {"name": "Yerel kafe/restoran", "rating": 4.0, "estimated_cost": 0}


def generate_trip_plan(req: dict) -> dict:
    sehir = req["sehir"]
    konseptler = req["konseptler"]
    gun_sayisi = req["gun_sayisi"]
    tempo = req["tempo"]
    butce_limiti = req.get("butce_limiti")
    ulasim_tipi = req["ulasim_tipi"]

    daily_max = 4 if tempo == "yavas" else 6
    center_lat, center_lon = get_city_center(sehir)
    city_costs = get_city_costs(sehir)

    # ADIM 1: Hangi konseptten toplam kaç mekana ihtiyacımız var hesaplayalım
    concept_counts = {}
    for i in range(gun_sayisi):
        k = get_concept_for_day(konseptler, i)
        concept_counts[k] = concept_counts.get(k, 0) + 1

    # ADIM 2: Konsept bazlı mekanları çekelim (Tükenmemesi için günlük limitin 3 katını çekiyoruz)
    places_by_concept = {}
    for k, count in concept_counts.items():
        needed_places = count * daily_max * 3 
        p = fetch_places_google(sehir, k, max_results=needed_places)
        if not p:
            p = fetch_places_nominatim(sehir, k, max_results=needed_places)
        places_by_concept[k] = p

    # ADIM 3: Gün gün planlama ve coğrafi rotalama (Greedy Nearest Neighbor)
    days_places = []
    seen_names = set()
    
    for i in range(gun_sayisi):
        konsept = get_concept_for_day(konseptler, i)
        current_lat, current_lon = center_lat, center_lon # Her gün merkezden (veya otelden) başlar
        
        # O günkü konsepte uygun, daha önce gitmediğimiz mekanları ayıkla
        available_places = [p for p in places_by_concept[konsept] if p["name"] not in seen_names]
        
        # Eğer yeterli mekan kalmadıysa, "mix" konseptiyle tamamla
        if len(available_places) < daily_max:
            mix_places = fetch_places_nominatim(sehir, "mix", max_results=daily_max * 2)
            for mp in mix_places:
                if mp["name"] not in seen_names and mp["name"] not in [a["name"] for a in available_places]:
                    mp["assigned_konsept"] = konsept
                    available_places.append(mp)

        # Bu gün için en yakın mekanları seçerek rotayı oluştur
        day_route = []
        for _ in range(daily_max):
            if not available_places:
                break
            
            # Kalan mekanlar arasından o anki konumumuza en yakın olanı bul
            nearest_idx = min(
                range(len(available_places)),
                key=lambda idx: haversine(current_lat, current_lon, available_places[idx]["lat"], available_places[idx]["lon"])
            )
            nearest = available_places.pop(nearest_idx)
            seen_names.add(nearest["name"])
            day_route.append(nearest)
            
            # Yeni konumumuz artık bu mekan
            current_lat, current_lon = nearest["lat"], nearest["lon"]
            
        days_places.append(day_route)

    gunler = []
    toplam_butce = 0.0
    toplam_dakika = 0
    notlar = []

    if not GOOGLE_PLACES_API_KEY:
        notlar.append("Google Places API key tanımlı değil. OpenStreetMap verileri kullanılıyor.")

    empty_days = sum(1 for d in days_places if not d)
    if empty_days > 0:
        notlar.append(f"{empty_days} gün için yeterli mekan bulunamadı. Daha fazla konsept eklemeyi veya 'mix' kullanmayı deneyin.")

    for gun_idx, day_places in enumerate(days_places):
        konsept = get_concept_for_day(konseptler, gun_idx)
        mekanlar = []
        gunluk_mekan_ucreti = 0.0
        gunluk_mekan_sure = 0
        gunluk_yuruyus_km = 0.0
        gunluk_ulasim = 0.0

        prev_lat, prev_lon = center_lat, center_lon

        for idx, p in enumerate(day_places):
            dist = haversine(prev_lat, prev_lon, p["lat"], p["lon"])
            yuruyus_dk = int((dist / 5.0) * 60) if dist < 2.0 else 0
            ulasim_dk = int((dist / 30.0) * 60) if dist >= 2.0 else 0
            ulasim_maliyet = calculate_transport_cost(dist, ulasim_tipi, sehir)

            gunluk_yuruyus_km += dist
            gunluk_ulasim += ulasim_maliyet

            mekan = {
                "sirano": idx + 1,
                "isim": p["name"],
                "kategori": p["types"][0] if p["types"] else "mekan",
                "tahmini_sure": p["duration_minutes"],
                "tahmini_ucret": p["entry_cost"],
                "bir_onceki_mesafe_km": round(dist, 2),
                "bir_onceki_yuruyus_dk": yuruyus_dk,
                "bir_onceki_ulasim_dk": ulasim_dk,
                "bir_onceki_ulasim_ucret": round(ulasim_maliyet, 2),
                "adres": p["address"],
                "rating": p["rating"],
                "lat": p["lat"],
                "lon": p["lon"]
            }
            mekanlar.append(mekan)

            gunluk_mekan_ucreti += p["entry_cost"]
            gunluk_mekan_sure += p["duration_minutes"]
            prev_lat, prev_lon = p["lat"], p["lon"]

        if ulasim_tipi == "toplu_tasima":
            gunluk_ulasim = city_costs["transport_daily"]

        gunluk_yemek = city_costs["meal_avg"] * 2
        gunluk_toplam = gunluk_mekan_ucreti + gunluk_yemek + gunluk_ulasim
        toplam_butce += gunluk_toplam

        yuruyus_sure = int((gunluk_yuruyus_km / 5.0) * 60)
        gunluk_toplam_sure = gunluk_mekan_sure + yuruyus_sure + 120

        if day_places:
            mid_idx = len(day_places) // 2
            mid_place = day_places[mid_idx]
            cafe = find_nearby_cafe(mid_place["lat"], mid_place["lon"], sehir)
            yemek_onerisi = f"Öğle yemeği: {cafe['name']} (~${cafe['estimated_cost']}, ⭐{cafe['rating']})"
        else:
            yemek_onerisi = f"Şehir merkezinde yerel restoranlar (~${city_costs['meal_avg']}/öğün)"

        gunler.append({
            "gun": gun_idx + 1,
            "konsept": konsept,
            "mekanlar": mekanlar,
            "gunluk_toplam_sure": f"{gunluk_toplam_sure // 60} saat {gunluk_toplam_sure % 60} dk",
            "gunluk_yuruyus": f"{gunluk_yuruyus_km:.1f} km",
            "gunluk_mekan_ucreti": round(gunluk_mekan_ucreti, 2),
            "gunluk_yemek": round(gunluk_yemek, 2),
            "gunluk_ulasim": round(gunluk_ulasim, 2),
            "gunluk_toplam": round(gunluk_toplam, 2),
            "yemek_onerisi": yemek_onerisi
        })

        toplam_dakika += gunluk_toplam_sure

    limit_asildi = False
    if butce_limiti is not None and toplam_butce > butce_limiti:
        limit_asildi = True
        notlar.append(f"UYARI: Tahmini toplam bütçe (${round(toplam_butce, 2)}) belirtilen limiti (${butce_limiti}) aşıyor.")

    if not all_places:
        notlar.append(f"{sehir} için mekan bulunamadı.")

    return {
        "sehir": sehir,
        "gun_sayisi": gun_sayisi,
        "konseptler": konseptler,
        "toplam_bütce": round(toplam_butce, 2),
        "toplam_sure": f"{toplam_dakika // 60} saat {toplam_dakika % 60} dk",
        "gunler": gunler,
        "ulasim_tipi": ulasim_tipi,
        "butce_limiti": butce_limiti,
        "limit_asildi": limit_asildi,
        "notlar": notlar
    }
