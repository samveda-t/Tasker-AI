#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
VENV_PYTHON="${VENV_DIR}/bin/python"

if [[ ! -x "${VENV_PYTHON}" ]]; then
  echo "Venv not found. Running setup..."
  "${ROOT_DIR}/setup.sh"
fi

# Load env vars from .env if present (optional).
if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.env"
  set +a
fi

if [[ "${1:-}" == "--doctor" ]]; then
  echo "Doctor Report"
  echo "ROOT_DIR=${ROOT_DIR}"
  echo "VENV_PYTHON=${VENV_PYTHON}"
  if [[ -x "${VENV_PYTHON}" ]]; then
    "${VENV_PYTHON}" - <<'PY'
import sys, requests
print("PYTHON", sys.version.split()[0])
print("REQUESTS", requests.__version__)
PY
  else
    echo "PYTHON MISSING (venv not found)"
  fi

  echo "ENV_FILE=${ROOT_DIR}/.env"
  if [[ -f "${ROOT_DIR}/.env" ]]; then
    echo "ENV_EXISTS=true"
  else
    echo "ENV_EXISTS=false"
  fi

  if [[ -n "${WEATHERAPI_KEY:-}" ]]; then
    echo "WEATHERAPI_KEY=SET (len=${#WEATHERAPI_KEY})"
  else
    echo "WEATHERAPI_KEY=MISSING"
  fi

  if [[ -n "${ROUTING_PROVIDER:-}" ]]; then
    echo "ROUTING_PROVIDER=${ROUTING_PROVIDER}"
  else
    echo "ROUTING_PROVIDER=ors (default)"
  fi

  if [[ -n "${WEATHER_CACHE_TTL_SEC:-}" ]]; then
    echo "WEATHER_CACHE_TTL_SEC=${WEATHER_CACHE_TTL_SEC}"
  fi
  if [[ -n "${ROUTE_CACHE_TTL_SEC:-}" ]]; then
    echo "ROUTE_CACHE_TTL_SEC=${ROUTE_CACHE_TTL_SEC}"
  fi
  if [[ -n "${GEOCODE_CACHE_TTL_SEC:-}" ]]; then
    echo "GEOCODE_CACHE_TTL_SEC=${GEOCODE_CACHE_TTL_SEC}"
  fi
  if [[ -n "${WEATHER_CACHE_PATH:-}" ]]; then
    echo "WEATHER_CACHE_PATH=${WEATHER_CACHE_PATH}"
  fi
  if [[ -n "${MAPS_CACHE_PATH:-}" ]]; then
    echo "MAPS_CACHE_PATH=${MAPS_CACHE_PATH}"
  fi

  if [[ -n "${ORS_API_KEY:-}" ]]; then
    echo "ORS_API_KEY=SET (len=${#ORS_API_KEY})"
  else
    echo "ORS_API_KEY=MISSING"
  fi
  if [[ -n "${GOOGLE_MAPS_API_KEY:-}" ]]; then
    echo "GOOGLE_MAPS_API_KEY=SET (len=${#GOOGLE_MAPS_API_KEY})"
  else
    echo "GOOGLE_MAPS_API_KEY=MISSING"
  fi
  if [[ -n "${NEWS_API_KEY:-}" ]]; then
    echo "NEWS_API_KEY=SET (len=${#NEWS_API_KEY})"
  else
    echo "NEWS_API_KEY=MISSING"
  fi
  if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    echo "OPENAI_API_KEY=SET (len=${#OPENAI_API_KEY})"
  else
    echo "OPENAI_API_KEY=MISSING"
  fi
  exit 0
fi

if [[ "${1:-}" == "--serve" ]]; then
  exec "${VENV_PYTHON}" -m backend.api
fi

if [[ $# -lt 2 ]]; then
  echo "Usage: ./run.sh \"<source>\" \"<destination>\""
  echo "       ./run.sh --serve"
  echo "       ./run.sh --doctor"
  exit 2
fi

if [[ -z "${WEATHERAPI_KEY:-}" ]]; then
  echo "Error: WEATHERAPI_KEY is not set"
  exit 3
fi

ROUTING_PROVIDER="${ROUTING_PROVIDER:-ors}"
if [[ "${ROUTING_PROVIDER}" == "ors" ]]; then
  if [[ -z "${ORS_API_KEY:-}" ]]; then
    echo "Error: ORS_API_KEY is not set"
    exit 4
  fi
elif [[ "${ROUTING_PROVIDER}" == "google" ]]; then
  if [[ -z "${GOOGLE_MAPS_API_KEY:-}" ]]; then
    echo "Error: GOOGLE_MAPS_API_KEY is not set"
    exit 5
  fi
fi

exec "${VENV_PYTHON}" -m backend.main "$@"
