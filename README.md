# Life Ops Agent

**Overview**
Life Ops Agent is a lightweight travel decision assistant. It gathers live weather, ETA, and air quality for a destination, then recommends the best way to travel and provides an actionable deep link.

**Features**
- Source and destination input
- Weather, ETA, and AQI context aggregation
- LLM-based decisioning with rule-based fallback
- Action planning with Uber deep link
- FastAPI backend with CORS and structured logging
- React + Tailwind frontend with responsive UI
- Cache layer for external API calls

**Tech Stack**
- Frontend: React, Vite, Tailwind CSS, Axios
- Backend: Python, FastAPI, Uvicorn
- Integrations: WeatherAPI, OpenRouteService or OSRM or Google Maps, Open-Meteo AQI, NewsAPI, OpenAI API

**Architecture**
- Frontend
  - UI for collecting source and destination
  - Calls backend `/context` endpoint
  - Renders recommendation card with action, reason, confidence, and CTA
- Backend
  - `backend/api.py` exposes `GET /context`
  - `backend/agent/context_builder.py` aggregates context
  - `backend/agent/decision_engine.py` generates decision
  - `backend/agent/action_planner.py` builds deep links
- Services
  - `backend/services/weather.py` fetches current weather
  - `backend/services/maps.py` handles geocode + routes
  - `backend/services/aqi.py` fetches air quality
  - `backend/services/llm.py` calls OpenAI for reasoning

**Screenshots**
![Landing](docs/screenshots/placeholder-1.png)
![Recommendation](docs/screenshots/placeholder-2.png)

**Setup Instructions**
1. Backend
1.1 Create and configure env file
```
cd life-ops-agent
cp .env.example .env
```
1.2 Add API keys to `.env`
```
WEATHERAPI_KEY=your_weatherapi_key
ORS_API_KEY=your_ors_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
OPENAI_API_KEY=your_openai_api_key
NEWS_API_KEY=your_newsapi_key
ROUTING_PROVIDER=google
```
1.3 Install and run
```
./setup.sh
./run.sh --serve
```

2. Frontend
2.1 Install deps
```
cd life-ops-agent/frontend
npm install
```
2.2 Configure API base
```
cp .env.example .env
```
2.3 Start dev server
```
npm run dev
```

**API**
- `GET /context`
  - Query params: `source`, `destination`, optional `debug`
  - Response: `context`, `decision`, `plan`
- `GET /decision`
  - Query params: `query`, optional `debug`
  - Response: `query`, `interpretation`, `context`, `risk`, `decision`, `plan`

**Future Roadmap**
- Personalization and user preferences
- Multi-modal inputs (voice, calendar, location history)
- Smarter traffic and ETA trend detection
- Multi-provider ride support
- Notifications and proactive advisories
