# SmartTrip v2 - Duzeltilmis Surum

## Hatalar Giderildi
- Google Places API key .env'den okunuyor
- Gun sayisi sorunu cozuldu (2 konsept + 3 gun = 3 gun calisir)
- Bos gunler icin mix konsepti fallback eklendi

## Kurulum
```bash
cd smarttrip_v2
docker compose up --build -d
```

## Test
http://localhost/

## API Key
.env dosyasinda GOOGLE_PLACES_API_KEY tanimli
