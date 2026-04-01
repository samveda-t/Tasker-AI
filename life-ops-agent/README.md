## Quick Run

```bash
./run.sh "Indiranagar, Bangalore" "MG Road, Bangalore"
```

The first run will auto-create a local venv and install dependencies.

## CLI Options

```bash
./run.sh "Indiranagar, Bangalore" "MG Road, Bangalore" --format json
./run.sh "Indiranagar, Bangalore" "MG Road, Bangalore" --provider osrm
./run.sh "Indiranagar, Bangalore" "MG Road, Bangalore" --provider google
./run.sh --query "Should I travel from Indiranagar to MG Road today?"
./run.sh "Indiranagar, Bangalore" "MG Road, Bangalore" --quiet
./run.sh --purge-cache "Indiranagar, Bangalore"
./run.sh --clear-route-cache
```

## Caching (Auto)

The app caches geocoding, routes, and weather responses to reduce API calls.
Defaults:
- Weather cache TTL: 10 minutes
- Route cache TTL: 15 minutes
- Geocode cache TTL: 7 days

You can override in `.env`:
```
WEATHER_CACHE_TTL_SEC=600
ROUTE_CACHE_TTL_SEC=900
GEOCODE_CACHE_TTL_SEC=604800
```

## One-Time Setup (Optional)

```bash
./setup.sh
```

Then add your keys in `.env` (created from `.env.example`):

```
WEATHERAPI_KEY=your_weatherapi_key
ORS_API_KEY=your_ors_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
NEWS_API_KEY=your_newsapi_key
OPENAI_API_KEY=your_openai_api_key
ORS_BASE_URL=https://api.openrouteservice.org
# Staging hosts may require the /ors base path:
# ORS_BASE_URL=https://staging.openrouteservice.org/ors
# Routing provider: ors (default), osrm (no key needed), or google
# ROUTING_PROVIDER=google
# Optional: traffic model for Google Directions (best_guess, optimistic, pessimistic)
# GOOGLE_TRAFFIC_MODEL=best_guess
# Optional: Google Geocoding API host
# GOOGLE_GEOCODE_BASE_URL=https://maps.googleapis.com/maps/api/geocode/json
# Optional: parser model for query understanding
# OPENAI_PARSER_MODEL=gpt-5
# Optional: News API host
# NEWS_API_BASE_URL=https://newsapi.org/v2/everything
# If ORS_BASE_URL is a staging host without geocoding, set:
# ORS_GEOCODE_BASE_URL=https://api.openrouteservice.org
# Optional Open-Meteo geocoding (key-free)
# OPEN_METEO_GEOCODE_BASE_URL=https://geocoding-api.open-meteo.com/v1/search
# Optional: Nominatim fallback settings
# NOMINATIM_USER_AGENT=life-ops-agent/1.0 (you@example.com)
```

## API
- `GET /context` (source/destination)
- `GET /decision` (natural-language query)

## Tests

```bash
cd life-ops-agent
./.venv/bin/python -m pytest -q
```
```
