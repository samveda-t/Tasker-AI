import logging
import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.agent.context_builder import get_context
from backend.agent.decision_engine import make_decision
from backend.agent.action_planner import plan_action
from backend.agent.query_handler import get_decision_from_query


app = FastAPI(title="Life Ops Agent", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("life_ops_api")


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Life Ops Agent API is running.",
        "endpoints": ["/context", "/decision", "/docs"],
    }


@app.get("/context")
def get_context_endpoint(
    source: str = Query(..., description="Origin address or 'lat,lon'"),
    destination: str = Query(..., description="Destination address or 'lat,lon'"),
    debug: bool = Query(False, description="Include decision debug info"),
):
    try:
        logger.info("request source=%s destination=%s", source, destination)
        context = get_context(source, destination)
        logger.info("context %s", context)
        decision = make_decision(context, debug=debug, news=context.get("news"))
        logger.info("decision %s", decision)
        plan = plan_action(decision, destination=destination)
        return {
            "context": context,
            "decision": decision,
            "plan": plan,
        }
    except Exception as exc:
        logger.exception("error source=%s destination=%s", source, destination)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/decision")
def get_decision_endpoint(
    query: str = Query(..., description="Natural-language decision query"),
    debug: bool = Query(False, description="Include decision debug info"),
):
    try:
        logger.info("request query=%s", query)
        return get_decision_from_query(query, debug=debug)
    except Exception as exc:
        logger.exception("error query=%s", query)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def run():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    run()
