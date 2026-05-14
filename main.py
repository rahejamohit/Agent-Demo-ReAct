"""
FastAPI backend for flight price fetching and aggregation
Runs on localhost:8080

Author: Senior Backend Engineer
Version: 1.0.0
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from models import (
    FlightSearch, FlightSearchResponse, HealthCheck,
    ErrorResponse, Flight
)
from flight_service import flight_service


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    logger.info("🚀 Flight Price API starting up...")
    yield
    logger.info("🛑 Flight Price API shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Flight Price Aggregator API",
    description="Agentic system to fetch and aggregate flight prices from multiple providers",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@app.get("/", tags=["Info"])
async def root():
    """API root endpoint with documentation links"""
    return {
        "name": "Flight Price Aggregator API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "search_flights": "/api/v1/flights/search",
            "flight_details": "/api/v1/flights/{flight_id}",
            "search_history": "/api/v1/flights/history",
            "docs": "/docs"
        },
        "docs": "Visit /docs for interactive API documentation"
    }


# ============================================================================
# Flight Search Endpoints
# ============================================================================

@app.post(
    "/api/v1/flights/search",
    response_model=FlightSearchResponse,
    tags=["Flights"],
    summary="Search flights across multiple providers"
)
async def search_flights(search: FlightSearch):
    """
    Search for flights across multiple booking providers.

    **Parameters:**
    - **origin**: Departure airport IATA code (e.g., JFK, LAX)
    - **destination**: Arrival airport IATA code (e.g., LAX, LHR)
    - **departure_date**: Travel date in YYYY-MM-DD format
    - **return_date**: Return date for round trips (optional)
    - **passengers**: Number of passengers (1-9)
    - **cabin_class**: Cabin class (economy, business, first)

    **Returns:**
    - Aggregated flights from all providers, sorted by price
    - Each flight includes booking URL to the provider
    """
    try:
        logger.info(f"🔍 Searching flights: {search.origin} -> {search.destination} on {search.departure_date}")

        response = flight_service.search_flights(search)

        logger.info(f"✅ Found {response.total_results} flights")
        return response

    except ValueError as e:
        logger.error(f"❌ Invalid search parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Flight search failed")


@app.get(
    "/api/v1/flights/{flight_id}",
    response_model=Flight,
    tags=["Flights"],
    summary="Get flight details"
)
async def get_flight(flight_id: str):
    """
    Get detailed information about a specific flight.

    **Parameters:**
    - **flight_id**: Unique flight identifier from search results

    **Returns:**
    - Complete flight details including booking URL
    """
    flight = flight_service.get_flight_details(flight_id)

    if not flight:
        logger.warning(f"Flight not found: {flight_id}")
        raise HTTPException(status_code=404, detail="Flight not found")

    return flight


@app.get(
    "/api/v1/flights/history",
    tags=["Flights"],
    summary="Get search history"
)
async def get_search_history():
    """
    Retrieve recent flight search history.

    **Returns:**
    - Last 10 searches with parameters and result counts
    """
    history = flight_service.get_search_history()
    return {
        "searches": history,
        "total_searches": len(history),
        "timestamp": datetime.now()
    }


# ============================================================================
# Bulk Search Endpoint (for agents)
# ============================================================================

@app.post(
    "/api/v1/flights/batch-search",
    tags=["Flights", "Agent"],
    summary="Batch search multiple routes"
)
async def batch_search(searches: list[FlightSearch]):
    """
    Search multiple routes in a single request.
    Useful for agentic systems processing multiple itineraries.

    **Parameters:**
    - **searches**: List of FlightSearch objects

    **Returns:**
    - Dictionary mapping search parameters to results
    """
    if len(searches) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 searches per batch")

    results = {}
    for search in searches:
        try:
            result = flight_service.search_flights(search)
            key = f"{search.origin}-{search.destination}-{search.departure_date}"
            results[key] = result
        except Exception as e:
            logger.error(f"Batch search failed for {search}: {str(e)}")
            continue

    return {
        "results": results,
        "total_batches": len(searches),
        "successful": len(results),
        "timestamp": datetime.now()
    }


# ============================================================================
# Admin Endpoints
# ============================================================================

@app.post(
    "/api/v1/admin/cache-clear",
    tags=["Admin"],
    summary="Clear flight cache"
)
async def clear_cache(admin_key: str = Query(...)):
    """
    Clear the in-memory flight cache.
    Requires admin key for security.
    """
    # In production, implement proper authentication
    if admin_key != "dev-admin-key":
        raise HTTPException(status_code=403, detail="Unauthorized")

    flight_service.clear_cache()
    logger.info("🧹 Cache cleared")

    return {
        "status": "success",
        "message": "Cache cleared successfully",
        "timestamp": datetime.now()
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
    🚀 Starting Flight Price Aggregator API
    📍 URL: http://localhost:8080
    📚 Docs: http://localhost:8080/docs
    🔄 ReDoc: http://localhost:8080/redoc
    """)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
