from urllib.parse import quote_plus


def _build_uber_link(destination):
    if not destination:
        return "https://m.uber.com/ul/"
    encoded = quote_plus(destination)
    return (
        "https://m.uber.com/ul/?action=setPickup"
        f"&dropoff[formatted_address]={encoded}"
    )


def plan_action(decision, destination=None):
    action = ""
    if isinstance(decision, dict):
        action = decision.get("action", "") or ""

    if "flight" in action.lower():
        return {
            "type": "flight",
            "link": "https://www.google.com/flights",
            "label": "Search Flights",
        }
    
    if "train" in action.lower():
        return {
            "type": "train",
            "link": "https://www.irctc.co.in",
            "label": "Book Train",
        }
    
    if "cab" in action.lower():
        return {
            "type": "ride",
            "link": _build_uber_link(destination),
            "label": "Book Uber",
        }
    
    # Handle bike recommendations
    if "bike" in action.lower() or "bicycle" in action.lower():
        return {
            "type": "bike",
            "link": None,
            "label": "Use Bike",
        }
    
    # Handle walk recommendations
    if "walk" in action.lower():
        return {
            "type": "walk",
            "link": None,
            "label": "Walk",
        }

    return {
        "type": "none",
        "link": None,
        "label": "No action",
    }
