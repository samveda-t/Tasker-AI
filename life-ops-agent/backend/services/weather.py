import json
import os
import time
from pathlib import Path
import requests

from backend.services.maps import get_coords

API_KEY = os.getenv("WEATHERAPI_KEY", "YOUR_WEATHERAPI_KEY")
WEATHER_CACHE_TTL_SEC = int(os.getenv("WEATHER_CACHE_TTL_SEC", "600"))
WEATHER_CACHE_PATH = os.getenv("WEATHER_CACHE_PATH")

def _default_cache_path():
    base_dir = Path(__file__).resolve().parents[2]
    return base_dir / ".cache" / "weather.json"

def _load_cache(path):
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return {"weather": {}}

def _save_cache(path, cache):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cache))
    except Exception as e:
        # Log error but don't fail the operation
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to save cache to {path}: {e}")

def _get_cached_weather(cache, key):
    entry = (cache.get("weather") or {}).get(key)
    if not entry:
        return None
    if time.time() - entry.get("ts", 0) > WEATHER_CACHE_TTL_SEC:
        return None
    return entry.get("value")

def _set_cached_weather(cache, key, value):
    cache.setdefault("weather", {})[key] = {"ts": time.time(), "value": value}

def purge_weather_cache(city):
    if not city:
        return False
    cache_path = Path(WEATHER_CACHE_PATH) if WEATHER_CACHE_PATH else _default_cache_path()
    cache = _load_cache(cache_path)
    key = city.strip().lower()
    if (cache.get("weather") or {}).pop(key, None) is not None:
        _save_cache(cache_path, cache)
        return True
    return False

def get_weather(city, timeout=10):
    if not API_KEY or API_KEY.startswith("YOUR_"):
        raise ValueError("WEATHERAPI_KEY is not set")
    if not city:
        raise ValueError("city is required")

    cache_path = Path(WEATHER_CACHE_PATH) if WEATHER_CACHE_PATH else _default_cache_path()
    cache_key = city.strip().lower()
    cache = _load_cache(cache_path)
    cached = _get_cached_weather(cache, cache_key)
    if cached:
        return cached

    try:
        coords = get_coords(city, timeout=timeout)
    except Exception as e:
        raise ValueError(f"Failed to get coordinates for '{city}': {e}") from e
    
    url = "https://api.weatherapi.com/v1/current.json"
    params = {
        "key": API_KEY,
        "q": f"{coords[1]},{coords[0]}",
        "aqi": "no",
    }
    
    try:
        res = requests.get(url, params=params, timeout=timeout)
        data = res.json()
    except requests.exceptions.Timeout:
        raise ValueError(f"Weather API timeout after {timeout}s")
    except Exception as e:
        res.raise_for_status()
        raise

    if res.status_code != 200 or "error" in data:
        error_msg = (data.get("error") or {}).get("message") if isinstance(data, dict) else data
        raise ValueError(f"Weather API error ({res.status_code}): {error_msg}")

    current = data.get("current") or {}
    condition = (current.get("condition") or {}).get("text")
    if condition is None:
        raise ValueError("Weather API error: missing condition text")

    result = {
        "condition": condition,
        "temperature": current.get("temp_c"),
        "source": "weatherapi",
    }
    _set_cached_weather(cache, cache_key, result)
    _save_cache(cache_path, cache)
    return result
