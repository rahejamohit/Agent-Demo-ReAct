"""
FastAPI backend with CrewAI for intelligent multi-agent flight price aggregation
Runs on localhost:8080

This version uses CrewAI to coordinate specialized agents for each flight provider
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
from flight_crew import get_crew

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Flight Price API with CrewAI System starting up...")
    logger.info("📡 Framework: CrewAI")
    logger.info("🤖 Agents: Skyscanner, Kayak, Google Flights, Amadeus")
    logger.info("🧠 Pattern: Multi-Agent Task-Based Orchestration")
    yield
    logger.info("🛑 Flight Price API shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Flight Price Aggregator API - CrewAI System",
    description="Multi-agent system using CrewAI framework to fetch and aggregate flight prices",
    version="1.0.0",
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
        version="1.0.0"
    )


@app.get("/", tags=["Info"])
async def root():
    """API info endpoint"""
    return {
        "name": "Flight Price Aggregator API - CrewAI System",
        "version": "1.0.0",
        "framework": "CrewAI",
        "architecture": "Multi-Agent Task-Based Orchestration",
        "agents": ["Skyscanner", "Kayak", "Google Flights", "Amadeus"],
        "endpoints": {
            "health": "/health",
            "search_flights": "/api/v1/flights/search",
            "agent_status": "/api/v1/agents/status",
            "docs": "/docs"
        },
        "docs": "Visit /docs for interactive API documentation"
    }


# ============================================================================
# Flight Search Endpoints (v1)
# ============================================================================

@app.post(
    "/api/v1/flights/search",
    tags=["Flights"],
    summary="Search flights using CrewAI agents"
)
async def search_flights(search: FlightSearch):
    """
    Search flights using CrewAI multi-agent system.

    CrewAI coordinates multiple specialized agents that:
    1. Each agent focuses on a specific flight provider
    2. Agents work on parallel tasks for speed
    3. Results are aggregated and sorted by price

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

    **Note**: Requires GOOGLE_API_KEY environment variable
    """
    try:
        # Verify API key is configured
        if not os.getenv("GOOGLE_API_KEY"):
            logger.error("❌ GOOGLE_API_KEY not configured")
            raise HTTPException(
                status_code=500,
                detail="Crew system not configured: GOOGLE_API_KEY required"
            )

        logger.info(f"🤖 CrewAI Search: {search.origin} → {search.destination} on {search.departure_date}")

        # Get the crew and execute search
        crew = get_crew()
        result = crew.search_flights(
            origin=search.origin,
            destination=search.destination,
            departure_date=search.departure_date,
            passengers=search.passengers,
            cabin_class=search.cabin_class
        )

        logger.info(f"✅ Crew found {result['total_results']} total flights")
        return result

    except ValueError as e:
        logger.error(f"❌ Invalid parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Crew search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Crew search failed: {str(e)}")


@app.get(
    "/api/v1/agents/status",
    tags=["Agents"],
    summary="Get agent system status"
)
async def agent_status():
    """
    Get status of all flight search agents in the CrewAI system

    Returns:
    - Agent names and providers
    - Configuration status
    - Model information
    - Agent specialties
    """
    crew = get_crew()
    crew_info = crew.get_agent_info()

    return {
        "system": crew_info["system"],
        "framework": crew_info["framework"],
        "agents": crew_info["agents"],
        "total_agents": crew_info["total_agents"],
        "timestamp": crew_info["timestamp"],
        "api_key_configured": bool(os.getenv("GOOGLE_API_KEY"))
    }


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
    🚀 Starting Flight Price Aggregator - CrewAI System
    📍 URL: http://localhost:8080
    📚 Docs: http://localhost:8080/docs
    🎯 Framework: CrewAI
    🧠 Agents: Skyscanner, Kayak, Google Flights, Amadeus
    🌐 LLM: Google Gemini 3 Flash

    ⚠️  Important: Set GOOGLE_API_KEY environment variable
       export GOOGLE_API_KEY="your-google-api-key-here"
    """)

    uvicorn.run(
        "main_agents:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
