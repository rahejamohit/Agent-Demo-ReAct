"""
FastAPI backend with ReAct Agent system for flight price fetching
Runs on localhost:8080

This version uses Claude API agents with ReAct pattern for intelligent flight searching
Each agent specializes in a flight provider (Skyscanner, Kayak, Google Flights, Amadeus)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import os

from models import FlightSearch, HealthCheck
from flight_agents import agent_orchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Flight Price API with Agent System starting up...")
    logger.info("📡 Agents: Skyscanner, Kayak, Google Flights, Amadeus")
    logger.info("🧠 Pattern: ReAct (Reasoning + Acting)")
    yield
    logger.info("🛑 Flight Price API shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Flight Price Aggregator API - Agent System",
    description="Multi-agent system using ReAct pattern to fetch and aggregate flight prices",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        version="2.0.0"
    )


@app.get("/", tags=["Info"])
async def root():
    """API info endpoint"""
    return {
        "name": "Flight Price Aggregator API - Agent System",
        "version": "2.0.0",
        "architecture": "ReAct (Reasoning + Acting)",
        "agents": ["Skyscanner", "Kayak", "Google Flights", "Amadeus"],
        "endpoints": {
            "health": "/health",
            "search_with_agents": "/api/v2/agents/search",
            "agent_status": "/api/v2/agents/status",
            "docs": "/docs"
        },
        "docs": "Visit /docs for interactive API documentation"
    }


# ============================================================================
# Agent-based Search Endpoints (v2)
# ============================================================================

@app.post(
    "/api/v2/agents/search",
    tags=["Agents", "Flights"],
    summary="Search flights using ReAct agents"
)
async def search_with_agents(search: FlightSearch):
    """
    Search flights using multi-agent ReAct system.

    Each flight provider has a dedicated agent that:
    1. REASONS about the search parameters
    2. ACTS by calling the provider API
    3. OBSERVES the results
    4. REPEATS if refinement is needed

    **Parameters:**
    - **origin**: Departure airport IATA code (e.g., JFK)
    - **destination**: Arrival airport IATA code (e.g., LAX)
    - **departure_date**: Travel date in YYYY-MM-DD format
    - **return_date**: Return date for round trips (optional)
    - **passengers**: Number of passengers (1-9)
    - **cabin_class**: Cabin class (economy, business, first)

    **Returns:**
    - Aggregated flights from all providers
    - Sorted by price (cheapest first)
    - Each flight includes booking URL
    - Provider information for each flight

    **Note**: Requires ANTHROPIC_API_KEY environment variable
    """
    try:
        # Verify API key is configured
        if not os.getenv("ANTHROPIC_API_KEY"):
            logger.error("❌ ANTHROPIC_API_KEY not configured")
            raise HTTPException(
                status_code=500,
                detail="Agent system not configured: ANTHROPIC_API_KEY required"
            )

        logger.info(f"🤖 Agent Search: {search.origin} → {search.destination} on {search.departure_date}")

        # Orchestrator searches all providers with agents
        result = agent_orchestrator.search_all_providers(
            origin=search.origin,
            destination=search.destination,
            departure_date=search.departure_date,
            passengers=search.passengers
        )

        logger.info(f"✅ Agents found {result['total_results']} total flights")
        return result

    except ValueError as e:
        logger.error(f"❌ Invalid parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Agent search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent search failed: {str(e)}")


@app.get(
    "/api/v2/agents/status",
    tags=["Agents"],
    summary="Get agent system status"
)
async def agent_status():
    """
    Get status of all flight search agents

    Returns:
    - Agent names and providers
    - Configuration status
    - Model information
    """
    agents_info = []

    for provider_name, agent in agent_orchestrator.agents.items():
        agents_info.append({
            "agent": agent.config["name"],
            "provider": provider_name,
            "model": agent.model,
            "status": "ready",
            "max_iterations": agent.max_iterations,
            "description": agent.config["description"]
        })

    return {
        "system": "ReAct Agent System",
        "agents": agents_info,
        "timestamp": datetime.now().isoformat(),
        "api_key_configured": bool(os.getenv("ANTHROPIC_API_KEY"))
    }


# ============================================================================
# Legacy API Endpoints (v1) - kept for compatibility
# ============================================================================

@app.post(
    "/api/v1/flights/search",
    tags=["Flights", "Deprecated"],
    summary="[DEPRECATED] Use /api/v2/agents/search instead"
)
async def search_flights_legacy(search: FlightSearch):
    """
    Legacy endpoint - redirects to agent-based search.
    Use /api/v2/agents/search for new implementations.
    """
    return await search_with_agents(search)


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions"""
    logger.error(f"💥 Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn

    print("""
    🚀 Starting Flight Price Aggregator - Agent System
    📍 URL: http://localhost:8080
    📚 Docs: http://localhost:8080/docs
    🤖 Pattern: ReAct (Reasoning + Acting)
    🧠 Agents: Skyscanner, Kayak, Google Flights, Amadeus

    ⚠️  Important: Set ANTHROPIC_API_KEY environment variable
       export ANTHROPIC_API_KEY="your-api-key-here"
    """)

    uvicorn.run(
        "main_agents:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
