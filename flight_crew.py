"""
Flight Price Aggregator using CrewAI framework
Multi-agent orchestration with Google Gemini 3 Flash
"""

import os
import logging
import sys
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from crewai import Crew, Process

from constants import (
    FLIGHT_PROVIDER_SKYSCANNER,
    FLIGHT_PROVIDER_KAYAK,
    FLIGHT_PROVIDER_GOOGLE_FLIGHTS,
    FLIGHT_PROVIDER_AMADEUS,
    FLIGHT_PROVIDERS,
)

# Handle LLM import - may be in different location depending on CrewAI version
try:
    from crewai import LLM
except ImportError:
    try:
        from crewai.llm import LLM
    except ImportError:
        # Mock LLM for testing if not available
        LLM = None


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def setup_logging(verbose: bool = True) -> logging.Logger:
    """Configure logging with custom formatter for real-time agent reasoning"""

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler with custom formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Custom formatter for better readability
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # Set CrewAI logging level if verbose
    if verbose:
        crew_logger = logging.getLogger("crewai")
        crew_logger.setLevel(logging.INFO)
        crew_handler = logging.StreamHandler(sys.stdout)
        crew_handler.setFormatter(formatter)
        crew_logger.addHandler(crew_handler)

    return logger


# Initialize logger
logger = setup_logging(verbose=True)


# ============================================================================
# PROVIDER CREW (Single-Provider Execution)
# ============================================================================

class ProviderCrew:
    """
    Encapsulates a single-provider crew for parallel flight search execution.

    Each ProviderCrew is an independent crew that:
    - Has 1 agent (specialized for a specific provider)
    - Has 1 task (search flights on that provider)
    - Executes asynchronously with a 5-minute timeout
    - Never raises exceptions—always returns a result dict with status

    Used by FlightAggregatorOrchestrator to run 4 crews in parallel.
    """

    def __init__(
        self,
        provider_name: str,
        origin: str,
        destination: str,
        departure_date: str,
        passengers: int,
        llm_config: Dict[str, Any]
    ):
        """
        Initialize ProviderCrew for a specific flight provider.

        Args:
            provider_name: Provider name ("skyscanner", "kayak", "google_flights", "amadeus")
            origin: Departure airport code
            destination: Arrival airport code
            departure_date: Travel date in YYYY-MM-DD format
            passengers: Number of passengers
            llm_config: Dict with 'llm' key containing LLM instance and config

        Raises:
            ValueError: If provider_name is invalid
        """
        from crew_config import create_provider_crew

        self.provider_name = provider_name
        self.origin = origin
        self.destination = destination
        self.departure_date = departure_date
        self.passengers = passengers
        self.llm_config = llm_config

        # Create the crew via factory function
        try:
            self.crew = create_provider_crew(
                provider_name=provider_name,
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                passengers=passengers,
                llm_config=llm_config
            )
            logger.debug(f"✓ ProviderCrew created for {provider_name}")
        except Exception as e:
            logger.error(f"✗ Failed to create ProviderCrew for {provider_name}: {str(e)}")
            raise

    async def execute(self) -> Dict[str, Any]:
        """
        Execute this provider's crew asynchronously with timeout protection.

        Returns a result dict with:
        - provider: Provider name
        - status: "success" | "error" | "timeout"
        - flights: List of flight dicts (empty if error/timeout)
        - error_message: Error description (None if success)
        - execution_time: Time taken in seconds

        Never raises exceptions—always returns a status dict.
        """
        execution_start = datetime.now()

        try:
            logger.info(f"⏱️  {self.provider_name} crew starting (timeout: 5min)...")

            # Execute crew with 5-minute timeout
            try:
                crew_output = await asyncio.wait_for(
                    self.crew.kickoff_async(),
                    timeout=300.0  # 5 minutes per crew
                )
            except asyncio.TimeoutError:
                execution_time = (datetime.now() - execution_start).total_seconds()
                logger.warning(f"⏱️  {self.provider_name} crew timed out after {execution_time:.1f}s")
                return {
                    "provider": self.provider_name,
                    "status": "timeout",
                    "flights": [],
                    "error_message": f"Crew execution timed out after 5 minutes",
                    "execution_time": execution_time
                }

            execution_time = (datetime.now() - execution_start).total_seconds()

            # Parse crew output to extract flights
            # The crew returns results as a dict or string with flight information
            flights = self._extract_flights_from_output(crew_output)

            logger.info(f"✓ {self.provider_name} crew completed in {execution_time:.1f}s ({len(flights)} flights)")

            return {
                "provider": self.provider_name,
                "status": "success",
                "flights": flights,
                "error_message": None,
                "execution_time": execution_time
            }

        except Exception as e:
            execution_time = (datetime.now() - execution_start).total_seconds()
            error_msg = str(e)
            logger.error(f"✗ {self.provider_name} crew error after {execution_time:.1f}s: {error_msg}")

            return {
                "provider": self.provider_name,
                "status": "error",
                "flights": [],
                "error_message": error_msg,
                "execution_time": execution_time
            }

    def _extract_flights_from_output(self, crew_output: Any) -> List[Dict[str, Any]]:
        """
        Extract flight list from crew execution output.

        The crew.kickoff() returns either a dict or string with flight data.
        This method parses it to extract the flights list.

        Args:
            crew_output: Output from crew.kickoff_async()

        Returns:
            List of flight dictionaries
        """
        try:
            # If output is dict with "flights" key, return it
            if isinstance(crew_output, dict) and "flights" in crew_output:
                return crew_output.get("flights", [])

            # If output is dict with "output" key containing flights
            if isinstance(crew_output, dict) and "output" in crew_output:
                output = crew_output["output"]
                if isinstance(output, dict) and "flights" in output:
                    return output["flights"]

            # For string output, call the provider's search function directly
            # (This is a fallback when crew returns text instead of structured data)
            from crew_config import _search_flights

            if self.provider_name in FLIGHT_PROVIDERS:
                result = _search_flights(
                    provider=self.provider_name,
                    origin=self.origin,
                    destination=self.destination,
                    departure_date=self.departure_date,
                    passengers=self.passengers
                )
                return result.get("flights", [])

            return []

        except Exception as e:
            logger.error(f"Error extracting flights for {self.provider_name}: {str(e)}")
            return []


# ============================================================================
# MANUAL AGGREGATION (No LLM, Deterministic)
# ============================================================================

def manual_aggregate_results(
    crew_results: List[Dict[str, Any]],
    origin: str,
    destination: str,
    departure_date: str,
    passengers: int,
    cabin_class: str
) -> Dict[str, Any]:
    """
    Manually aggregate results from all ProviderCrew executions.

    Does NOT deduplicate—keeps all flights from all providers.
    Simply combines and sorts by price.

    Args:
        crew_results: List of result dicts from ProviderCrew.execute()
        origin: Departure airport code
        destination: Arrival airport code
        departure_date: Travel date
        passengers: Number of passengers
        cabin_class: Cabin class

    Returns:
        Aggregated response dict with flights sorted by price
    """
    logger.info("=" * 70)
    logger.info("📊 AGGREGATING RESULTS FROM ALL PROVIDERS")
    logger.info("=" * 70)

    all_flights = []
    provider_results = {}
    warnings = []

    # Extract flights from all crews (successful and failed)
    for crew_result in crew_results:
        provider = crew_result.get("provider", "unknown")
        status = crew_result.get("status", "unknown")
        flights = crew_result.get("flights", [])
        error_msg = crew_result.get("error_message")

        provider_results[provider] = {
            "status": status,
            "flights": len(flights)
        }

        if status == "success":
            all_flights.extend(flights)
            logger.info(f"✓ {provider.upper()}: {len(flights)} flights")
        else:
            logger.warning(f"✗ {provider.upper()}: {status} ({error_msg})")
            if error_msg:
                warnings.append(f"{provider.capitalize()} crew {status}: {error_msg}")

    # Sort ALL flights by price (ascending) - NO deduplication
    logger.info(f"🔀 Sorting {len(all_flights)} flights by price (ascending)...")
    all_flights.sort(key=lambda f: float(f.get("price", float("inf"))))

    # Determine overall status
    crew_status = "completed"
    if len(crew_results) > 0 and any(r.get("status") != "success" for r in crew_results):
        crew_status = "partial_completion"

    logger.info(f"✓ Aggregation complete: {len(all_flights)} total flights")
    if warnings:
        for warning in warnings:
            logger.warning(f"⚠️  {warning}")

    logger.info("=" * 70 + "\n")

    return {
        "search_params": {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "passengers": passengers,
            "cabin_class": cabin_class
        },
        "flights": all_flights,
        "total_results": len(all_flights),
        "provider_results": provider_results,
        "timestamp": datetime.now().isoformat(),
        "crew_status": crew_status,
        "warnings": warnings if warnings else []
    }


# ============================================================================
# FLIGHT AGGREGATOR ORCHESTRATOR (Multiple Crews in Parallel)
# ============================================================================

class FlightAggregatorOrchestrator:
    """
    Orchestrates 4 parallel ProviderCrew instances for fast flight aggregation.

    Replaces the old FlightAggregatorCrew which used CrewAI's hierarchical
    process (which had executor conflicts). This orchestrator:
    - Creates 4 independent ProviderCrew instances (one per provider)
    - Runs all 4 in parallel using asyncio.gather()
    - Aggregates results using deterministic Python function (not LLM)
    - Completes in ~30-35 seconds (not 60-120s)
    """

    def __init__(
        self,
        provider: str = "google",
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the orchestrator with LLM configuration.

        Args:
            provider: LLM provider (google, openai, anthropic, ollama)
            model: LLM model (optional override)
            api_key: API key (optional, defaults to env var; not needed for Ollama)
        """
        from crew_config import LLM_PROVIDER_CONFIG

        self.provider = provider
        self.model = model or LLM_PROVIDER_CONFIG[provider]["default_model"]

        # Handle API key - Ollama doesn't need one
        if provider == "ollama":
            self.api_key = None
        else:
            self.api_key = api_key or os.getenv(LLM_PROVIDER_CONFIG[provider]["env_var"])
            if not self.api_key:
                logger.warning(
                    f"⚠️  {LLM_PROVIDER_CONFIG[provider]['env_var']} not set. Operations will fail."
                )

        # Prepare LLM config for ProviderCrew instances
        config = LLM_PROVIDER_CONFIG[provider]

        # Validate LLM class is available
        if LLM is None:
            raise ImportError(
                "CrewAI LLM class could not be imported. "
                "Please ensure CrewAI is properly installed."
            )

        self.llm = LLM(
            model=f"{config['prefix']}/{self.model}",
            api_key=self.api_key,
            temperature=0.7
        )

        self.llm_config = {"llm": self.llm}
        self.providers = FLIGHT_PROVIDERS

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        passengers: int = 1,
        cabin_class: str = "economy"
    ) -> Dict[str, Any]:
        """
        Search flights from all providers using 4 parallel crews.

        Execution: ~30-35 seconds total (all crews run simultaneously)

        Args:
            origin: Departure airport code
            destination: Arrival airport code
            departure_date: Travel date (YYYY-MM-DD)
            passengers: Number of passengers
            cabin_class: Cabin class

        Returns:
            Aggregated flight results from all providers
        """
        search_start = datetime.now()

        logger.info("\n" + "=" * 70)
        logger.info("🌍 FLIGHT SEARCH REQUEST (Option A: Multiple Crews in Parallel)")
        logger.info("=" * 70)
        logger.info(f"📍 Route: {origin} → {destination}")
        logger.info(f"📅 Date: {departure_date}")
        logger.info(f"👥 Passengers: {passengers} | Cabin: {cabin_class}")
        logger.info("=" * 70)

        try:
            # Validate inputs
            if not origin or not destination or not departure_date:
                raise ValueError("origin, destination, and departure_date are required")

            if passengers < 1 or passengers > 9:
                raise ValueError("passengers must be between 1 and 9")

            if cabin_class not in ["economy", "business", "first"]:
                raise ValueError("cabin_class must be: economy, business, or first")

            logger.info("✅ Parameters validated")

            # PHASE 1: Create 4 ProviderCrew instances
            logger.info("\n" + "=" * 70)
            logger.info("📋 PHASE 1: Creating 4 ProviderCrew instances")
            logger.info("=" * 70)

            crews = []
            for provider_name in self.providers:
                logger.info(f"Creating crew for {provider_name}...")
                crew = ProviderCrew(
                    provider_name=provider_name,
                    origin=origin,
                    destination=destination,
                    departure_date=departure_date,
                    passengers=passengers,
                    llm_config=self.llm_config
                )
                crews.append(crew)

            logger.info(f"✅ All 4 crews created")

            # PHASE 2: Run all crews in parallel
            logger.info("\n" + "=" * 70)
            logger.info("⚡ PHASE 2: Running 4 crews in parallel (5min timeout each)")
            logger.info("=" * 70)
            logger.info("├─ 🟦 Skyscanner Crew")
            logger.info("├─ 🟨 Kayak Crew")
            logger.info("├─ 🟩 Google Flights Crew")
            logger.info("└─ 🟧 Amadeus Crew")
            logger.info("")

            execution_start = datetime.now()

            # Execute all crews in parallel using asyncio.gather()
            crew_results = await asyncio.gather(*[crew.execute() for crew in crews])

            execution_time = (datetime.now() - execution_start).total_seconds()
            logger.info(f"✅ All crews completed in {execution_time:.1f}s")

            # PHASE 3: Aggregate results
            logger.info("\n" + "=" * 70)
            logger.info("📊 PHASE 3: Aggregating results from all crews")
            logger.info("=" * 70)

            aggregated = manual_aggregate_results(
                crew_results=crew_results,
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                passengers=passengers,
                cabin_class=cabin_class
            )

            # Final summary
            total_time = (datetime.now() - search_start).total_seconds()
            logger.info("=" * 70)
            logger.info("🎉 SEARCH COMPLETED")
            logger.info("=" * 70)
            logger.info(f"📊 Total flights: {aggregated['total_results']}")
            logger.info(f"⏱️  Execution time: {execution_time:.1f}s")
            logger.info(f"⏱️  Total time: {total_time:.1f}s")

            if aggregated['flights']:
                cheapest = aggregated['flights'][0]
                logger.info(
                    f"💰 Cheapest option: ${cheapest['price']} "
                    f"on {cheapest['airline']} ({cheapest['provider']})"
                )

            logger.info("=" * 70 + "\n")

            return aggregated

        except ValueError as e:
            logger.error(f"❌ Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Orchestration failed: {str(e)}", exc_info=True)
            raise

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the orchestration system.

        Returns:
            Dictionary with system information
        """
        return {
            "system": "Flight Price Aggregator (Option A: Multiple Crews in Parallel)",
            "framework": "CrewAI",
            "architecture": "4 Independent ProviderCrew instances + asyncio.gather() orchestration",
            "providers": self.providers,
            "llm_provider": self.provider,
            "llm_model": self.model,
            "api_key_configured": bool(self.api_key),
            "timeout_per_crew": "5 minutes",
            "execution_strategy": "Parallel with asyncio.gather()",
            "aggregation": "Deterministic Python function (no LLM)",
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# CREW FACTORY (Fresh Instance Per Request - No Singleton)
# ============================================================================

def get_crew(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None
) -> FlightAggregatorOrchestrator:
    """
    Create a fresh flight aggregator orchestrator instance for each request.

    IMPORTANT: This creates a NEW orchestrator instance every time to avoid executor conflicts.
    Each request gets its own isolated orchestrator with 4 parallel ProviderCrew instances.

    Architecture: Option A - 4 Independent Crews in Parallel
    - Creates 4 ProviderCrew instances (one per provider)
    - Runs all 4 in parallel using asyncio.gather()
    - Completes in ~30-35 seconds (not sequential)

    Args:
        provider: LLM provider (google, openai, anthropic) - defaults to LLM_PROVIDER env var or google
        model: LLM model to use - defaults to LLM_MODEL env var or provider's default
        api_key: API key (defaults to provider's env var)

    Returns:
        Fresh FlightAggregatorOrchestrator instance (not cached)
    """
    # Read from environment variables if not explicitly provided
    env_provider = provider or os.getenv("LLM_PROVIDER", "google")
    env_model = model or os.getenv("LLM_MODEL")

    # Create and return a FRESH orchestrator instance for this request
    # No singleton caching - each request gets its own isolated orchestrator
    return FlightAggregatorOrchestrator(
        provider=env_provider,
        model=env_model,
        api_key=api_key
    )


if __name__ == "__main__":
    # Test the crew with full logging
    print("\n" + "=" * 70)
    print("🚀 FLIGHT PRICE AGGREGATOR - CrewAI SYSTEM TEST")
    print("=" * 70)

    crew = get_crew()

    # Show agent system info
    agent_info = crew.get_agent_info()

    # Run flight search with full logging
    try:
        import asyncio
        results = asyncio.run(crew.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date="2026-06-15",
            passengers=1,
            cabin_class="economy"
        ))

        # Display results summary
        logger.info("📋 SEARCH RESULTS SUMMARY")
        logger.info("-" * 70)
        logger.info(f"Total flights found: {results['total_results']}")
        logger.info(f"Search parameters: {results['search_params']}")

        if results['flights']:
            logger.info("\n💰 TOP 5 CHEAPEST FLIGHTS:")
            for i, flight in enumerate(results['flights'][:5], 1):
                logger.info(f"   {i}. ${flight['price']} - {flight['airline']} ({flight['provider']})")
                logger.info(f"      {flight['departure']} → {flight['arrival']} ({flight['duration_minutes']}min, {flight['stops']} stops)")

        logger.info("-" * 70 + "\n")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
