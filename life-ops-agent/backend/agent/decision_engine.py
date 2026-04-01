def _parse_duration_minutes(duration_text):
    if not duration_text:
        return None
    text = str(duration_text).lower()
    minutes = 0
    parts = text.replace(",", " ").split()
    i = 0
    while i < len(parts):
        token = parts[i]
        if token.isdigit():
            value = int(token)
            unit = parts[i + 1] if i + 1 < len(parts) else ""
            if unit.startswith("hour") or unit == "hr":
                minutes += value * 60
            elif unit.startswith("min"):
                minutes += value
            i += 2
        else:
            i += 1
    return minutes or None

def _parse_distance_km(distance_text):
    if not distance_text:
        return None
    text = str(distance_text).lower().strip()
    try:
        value = float(text.split()[0])
    except Exception:
        return None
    if "km" in text:
        return value
    if "m" in text:
        return value / 1000.0
    return None

from backend.services.llm import generate_decision


def _rule_based_decision(
    weather,
    distance_km,
    duration_min,
    aqi_value,
    aqi_category,
):
    score = 0.0
    reasons = []
    breakdown = {
        "aqi_poor": 0.0,
        "rain": 0.0,
        "distance_ge_6_km": 0.0,
        "distance_ge_3_km": 0.0,
        "duration_ge_30_min": 0.0,
        "duration_ge_15_min": 0.0,
    }

    weather_lc = weather.lower()
    if any(term in weather_lc for term in ["rain", "thunder", "storm", "drizzle"]):
        score += 0.5
        breakdown["rain"] = 0.5
        reasons.append("Rainy weather")

    is_aqi_poor = False
    if isinstance(aqi_value, (int, float)):
        is_aqi_poor = aqi_value >= 151
    if aqi_category in {"unhealthy", "very_unhealthy", "hazardous"}:
        is_aqi_poor = True
    if is_aqi_poor:
        score += 0.6
        breakdown["aqi_poor"] = 0.6
        reasons.append("Poor air quality")

    # Handle very long distances (intercity travel)
    if distance_km is not None and distance_km >= 300:
        if distance_km >= 1000:
            action = "Take a flight"
            reasons.insert(0, f"Extremely long distance ({distance_km:.1f} km) - requires air travel")
        elif distance_km >= 500:
            action = "Take a train or flight"
            reasons.insert(0, f"Very long distance ({distance_km:.1f} km) - requires train or flight")
        else:
            action = "Take a train"
            reasons.insert(0, f"Long distance ({distance_km:.1f} km) - train recommended")
        return {
            "action": action,
            "reason": "; ".join(reasons),
            "confidence": 0.9,
            "debug": {
                "duration_minutes": duration_min,
                "distance_km": distance_km,
                "aqi": aqi_value,
                "aqi_category": aqi_category,
                "score_breakdown": breakdown,
                "total_score": round(score, 2),
            },
        }

    # More nuanced distance scoring for shorter distances
    if distance_km is not None:
        if distance_km >= 15:
            score += 0.4
            breakdown["distance_ge_15_km"] = 0.4
            reasons.append(f"Long distance ({distance_km:.1f} km)")
        elif distance_km >= 8:
            score += 0.3
            breakdown["distance_ge_8_km"] = 0.3
            reasons.append(f"Long distance ({distance_km:.1f} km)")
        elif distance_km >= 4:
            score += 0.2
            breakdown["distance_ge_4_km"] = 0.2
            reasons.append(f"Moderate distance ({distance_km:.1f} km)")
        elif distance_km >= 2:
            score += 0.1
            breakdown["distance_ge_2_km"] = 0.1
            reasons.append(f"Short distance ({distance_km:.1f} km)")
        else:
            reasons.append(f"Very short distance ({distance_km:.1f} km)")

    # More nuanced time scoring
    if duration_min is not None:
        if duration_min >= 45:
            score += 0.4
            breakdown["duration_ge_45_min"] = 0.4
            reasons.append(f"Very long travel time ({duration_min} min)")
        elif duration_min >= 25:
            score += 0.3
            breakdown["duration_ge_25_min"] = 0.3
            reasons.append(f"Long travel time ({duration_min} min)")
        elif duration_min >= 12:
            score += 0.2
            breakdown["duration_ge_12_min"] = 0.2
            reasons.append(f"Moderate travel time ({duration_min} min)")
        elif duration_min >= 5:
            score += 0.1
            breakdown["duration_ge_5_min"] = 0.1
            reasons.append(f"Short travel time ({duration_min} min)")
        else:
            reasons.append(f"Very short travel time ({duration_min} min)")

    if score >= 0.6:
        action = "Book a cab"
    elif score >= 0.3:
        action = "Take a bike or cab"
    else:
        action = "You can walk"

    if reasons:
        reason = "; ".join(reasons)
    else:
        reason = "Clear conditions and short trip"

    return {
        "action": action,
        "reason": reason,
        "confidence": round(min(score, 1.0), 2),
        "debug": {
            "duration_minutes": duration_min,
            "distance_km": distance_km,
            "aqi": aqi_value,
            "aqi_category": aqi_category,
            "score_breakdown": breakdown,
            "total_score": round(score, 2),
        },
    }


def _clamp_confidence(value):
    try:
        num = float(value)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, num))


def make_decision(context, debug=False, user_query=None, news=None, risk=None):
    if not isinstance(context, dict):
        raise ValueError("context must be a dict")

    weather_data = context.get("weather") or {}
    weather = weather_data.get("condition")
    
    # Handle missing weather condition gracefully
    if not weather:
        weather = "Unknown"  # Default fallback
    
    eta_data = context.get("eta") or {}
    distance = eta_data.get("distance")
    eta = eta_data.get("duration")
    
    aqi_info = context.get("aqi") or {}
    aqi_value = aqi_info.get("aqi")
    aqi_category = aqi_info.get("category")
    
    duration_min = _parse_duration_minutes(eta)
    distance_km = _parse_distance_km(distance)

    fallback = _rule_based_decision(
        weather=weather,
        distance_km=distance_km,
        duration_min=duration_min,
        aqi_value=aqi_value,
        aqi_category=aqi_category,
    )

    if (
        (weather is None or weather == "Unknown")
        and distance_km is None
        and duration_min is None
        and aqi_value is None
    ):
        fallback = {
            "action": "Provide more details",
            "reason": "I need a destination or timing details to fetch live data.",
            "confidence": 0.2,
            "debug": fallback["debug"],
        }

    llm_used = False
    llm_model = None
    decision = None
    try:
        llm_result = generate_decision(
            weather=weather,
            distance=distance,
            duration=eta,
            aqi=aqi_value,
            news=news,
            query=user_query,
            risk=risk,
        )
        decision = {
            "action": llm_result.get("action"),
            "reason": llm_result.get("reason"),
            "confidence": _clamp_confidence(llm_result.get("confidence")),
        }
        llm_model = llm_result.get("model")
        llm_used = True
    except Exception:
        decision = {
            "action": fallback["action"],
            "reason": fallback["reason"],
            "confidence": fallback["confidence"],
        }

    if debug:
        decision["debug"] = fallback["debug"]
        decision["debug"]["llm_used"] = llm_used
        if llm_model:
            decision["debug"]["llm_model"] = llm_model
    return decision
