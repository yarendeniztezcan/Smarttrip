from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Tempo(str, Enum):
    yavas = "yavas"
    hizli = "hizli"

class UlasimTipi(str, Enum):
    yuruyus = "yuruyus"
    toplu_tasima = "toplu_tasima"
    taksi = "taksi"

class TripRequest(BaseModel):
    sehir: str = Field(..., description="Gezilecek şehir")
    konseptler: List[str] = Field(..., description=["tarihi", "doğa", "sanat", "yemek", "mix"])
    gun_sayisi: int = Field(..., ge=1, le=14, description="1-14 gün")
    tempo: Tempo = Field(..., description="yavas: 3-4 mekan/gün, hizli: 5-6 mekan/gün")
    butce_limiti: Optional[float] = Field(None, description="USD cinsinden üst limit")
    ulasim_tipi: UlasimTipi = Field(..., description="yuruyus / toplu_tasima / taksi")

class Mekan(BaseModel):
    sirano: int
    isim: str
    kategori: str
    tahmini_sure: int
    tahmini_ucret: float
    bir_onceki_mesafe_km: float
    bir_onceki_yuruyus_dk: int
    bir_onceki_ulasim_dk: int
    bir_onceki_ulasim_ucret: float
    adres: str
    rating: float
    lat: float
    lon: float

class GunPlan(BaseModel):
    gun: int
    konsept: str
    mekanlar: List[Mekan]
    gunluk_toplam_sure: str
    gunluk_yuruyus: str
    gunluk_mekan_ucreti: float
    gunluk_yemek: float
    gunluk_ulasim: float
    gunluk_toplam: float
    yemek_onerisi: str

class TripResponse(BaseModel):
    sehir: str
    gun_sayisi: int
    konseptler: List[str]
    toplam_bütce: float
    toplam_sure: str
    gunler: List[GunPlan]
    ulasim_tipi: str
    butce_limiti: Optional[float] = None
    limit_asildi: bool
    notlar: List[str]
