"""
Flight Price Aggregator using CrewAI framework
Multi-agent orchestration with Google Gemini 3 Flash
"""

import os
import logging
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from crewai import Crew, Process
from crew_config import create_agents, create_tasks


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


class FlightAggregatorCrew:
    """Orchestrates multiple flight search agents using CrewAI framework with Google Gemini 3 Flash"""

    def __init__(
        self,
        provider: str = "google",
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the flight aggregator crew

        Args:
            provider: LLM provider (google, openai, anthropic) - default: google
            model: LLM model to use (defaults to provider's default)
            api_key: API key (defaults to provider's env var)
        """
        from crew_config import PROVIDER_CONFIG

        self.provider = provider
        self.model = model or PROVIDER_CONFIG[provider]["default_model"]
        self.api_key = api_key or os.getenv(PROVIDER_CONFIG[provider]["env_var"])

        if not self.api_key:
            logger.warning(
                f"⚠️  {PROVIDER_CONFIG[provider]['env_var']} not set. Crew operations will fail."
            )

        self.crew = None
        self.agents = None
        self.providers = ["skyscanner", "kayak", "google_flights", "amadeus"]

    def _initialize_crew(self, origin: str, destination: str,
                        departure_date: str, passengers: int = 1) -> Crew:
        """
        Initialize and return a CrewAI Crew instance with detailed logging

        Args:
            origin: Departure airport code
            destination: Arrival airport code
            departure_date: Travel date in YYYY-MM-DD format
            passengers: Number of passengers

        Returns:
            CrewAI Crew instance ready to execute
        """
        logger.info("=" * 70)
        logger.info("🔧 INITIALIZING CREWAI SYSTEM")
        logger.info("=" * 70)

        # Create agents with the configured provider, model, and API key
        logger.info(f"🤖 Creating agents with {self.provider}/{self.model}")
        self.agents = create_agents(
            provider=self.provider,
            model=self.model,
            api_key=self.api_key
        )

        logger.info(f"✅ {len(self.agents)} agents created:")
        for provider_name, agent in self.agents.items():
            logger.info(f"   • {agent.role}")
            logger.info(f"     └─ Provider: {provider_name}")
            logger.info(f"     └─ Tools: {len(agent.tools) if hasattr(agent, 'tools') and agent.tools is not None else 0}")

        # Create tasks for each agent
        logger.info(f"\n📋 Creating {len(self.agents)} tasks for agents...")
        tasks = create_tasks(
            agents=self.agents,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            passengers=passengers
        )

        logger.info(f"✅ {len(tasks)} tasks created")
        for i, task in enumerate(tasks, 1):
            logger.debug(f"   Task {i}: {task.description[:60]}...")

        # Create and return the crew with parallel execution
        logger.info(f"\n🔗 Binding agents and tasks into Crew with parallel execution...")

        # Create LLM instance for the manager (uses same provider as agents)
        from crewai import LLM
        from crew_config import PROVIDER_CONFIG

        config = PROVIDER_CONFIG[self.provider]
        manager_llm = LLM(
            model=f"{config['prefix']}/{self.model}",
            api_key=self.api_key,
            temperature=0.7
        )

        crew = Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            verbose=True,
            memory=False,
            process=Process.hierarchical,  # Run agents in parallel
            manager_llm=manager_llm  # Manager coordinates parallel agents
        )

        logger.info("✅ Crew initialized with hierarchical (parallel) execution")
        logger.info("=" * 70)

        return crew

    async def search_flights(self, origin: str, destination: str, departure_date: str,
                             passengers: int = 1, cabin_class: str = "economy") -> Dict[str, Any]:
        """
        Search flights from all providers using CrewAI agents

        Args:
            origin: Departure airport code (e.g., JFK)
            destination: Arrival airport code (e.g., LAX)
            departure_date: Travel date in YYYY-MM-DD format
            passengers: Number of passengers (default: 1)
            cabin_class: Cabin class - economy, business, first (default: economy)

        Returns:
            Dictionary with aggregated flight results from all providers
        """
        search_start_time = datetime.now()

        logger.info("\n" + "=" * 70)
        logger.info("🌍 FLIGHT SEARCH REQUEST")
        logger.info("=" * 70)
        logger.info(f"📍 Route: {origin} → {destination}")
        logger.info(f"📅 Date: {departure_date}")
        logger.info(f"👥 Passengers: {passengers} | Cabin: {cabin_class}")
        logger.info("=" * 70)

        try:
            # Validate inputs
            logger.info("🔍 Validating search parameters...")
            if not origin or not destination or not departure_date:
                raise ValueError("origin, destination, and departure_date are required")

            if passengers < 1 or passengers > 9:
                raise ValueError("passengers must be between 1 and 9")

            if cabin_class not in ["economy", "business", "first"]:
                raise ValueError("cabin_class must be: economy, business, or first")

            logger.info("✅ Parameters validated")

            # Initialize crew for this search
            logger.info("\n🔧 Setting up CrewAI agents and tasks...")
            crew = self._initialize_crew(origin, destination, departure_date, passengers)

            # Execute the crew - this runs all agent tasks in parallel
            logger.info("\n" + "=" * 70)
            logger.info("🚀 CREW EXECUTION STARTING (PARALLEL)")
            logger.info("=" * 70)
            logger.info("⚡ All 4 agents will now search in PARALLEL...")
            logger.info("   🟦 Skyscanner Agent")
            logger.info("   🟨 Kayak Agent")
            logger.info("   🟩 Google Flights Agent")
            logger.info("   🟧 Amadeus Agent")
            logger.info("💭 Watch for agent reasoning and tool calls below:\n")

            execution_start = datetime.now()

            # Execute crew asynchronously - required because FastAPI endpoint is async
            crew_output: Any = await crew.kickoff_async()

            execution_time = (datetime.now() - execution_start).total_seconds()
            logger.info(f"\n✅ CrewAI crew execution completed in {execution_time:.2f}s")

            # Aggregate results from all agents
            logger.info("\n📊 Aggregating results from all providers...")
            aggregated_results = self._aggregate_crew_results(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                passengers=passengers,
                cabin_class=cabin_class,
                crew_output=crew_output
            )

            # Final summary
            total_time = (datetime.now() - search_start_time).total_seconds()
            logger.info("\n" + "=" * 70)
            logger.info("🎉 SEARCH COMPLETED")
            logger.info("=" * 70)
            logger.info(f"📊 Total flights found: {aggregated_results['total_results']}")
            logger.info(f"⏱️  Total execution time: {total_time:.2f}s")

            if aggregated_results['flights']:
                cheapest = aggregated_results['flights'][0]
                logger.info(f"💰 Cheapest option: ${cheapest['price']} on {cheapest['airline']} ({cheapest['provider']})")

            logger.info("=" * 70 + "\n")

            return aggregated_results

        except ValueError as e:
            logger.error(f"❌ Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"\n❌ CrewAI execution failed: {str(e)}", exc_info=True)
            raise

    def _aggregate_crew_results(self, origin: str, destination: str,
                               departure_date: str, passengers: int,
                               cabin_class: str, crew_output: Any) -> Dict[str, Any]:
        """
        Aggregate results from CrewAI crew execution with detailed logging

        Args:
            origin: Departure airport code
            destination: Arrival airport code
            departure_date: Travel date
            passengers: Number of passengers
            cabin_class: Cabin class
            crew_output: Raw output from crew.kickoff()

        Returns:
            Aggregated and sorted flight results
        """
        logger.info("📈 AGGREGATING RESULTS FROM ALL AGENTS")
        logger.info("-" * 70)

        all_flights = []
        provider_results = {}

        # Process results from each agent
        for provider in self.providers:
            try:
                logger.info(f"🔄 Processing {provider.upper()} agent results...")

                if self.agents and provider in self.agents:
                    agent = self.agents[provider]
                    # Extract flights from agent's task output
                    # The crew_output typically contains results from each task

                    # For now, we collect from the flight search tools
                    # In a production system, you'd parse the crew_output more carefully
                    provider_data = self._extract_provider_flights(provider, crew_output)

                    if provider_data:
                        flight_count = len(provider_data["flights"])
                        all_flights.extend(provider_data["flights"])
                        provider_results[provider] = {
                            "flights": provider_data["flights"],
                            "total_results": flight_count
                        }
                        logger.info(f"   ✅ {provider.upper()}: {flight_count} flights extracted")

                        # Show price range for this provider
                        if flight_count > 0:
                            prices = [f.get("price", 0) for f in provider_data["flights"]]
                            min_price = min(prices)
                            max_price = max(prices)
                            avg_price = sum(prices) / len(prices)
                            logger.info(f"      Price range: ${min_price} - ${max_price} (avg: ${avg_price:.2f})")
                    else:
                        provider_results[provider] = {
                            "flights": [],
                            "total_results": 0
                        }
                        logger.info(f"   ⚠️  {provider.upper()}: No data extracted")

            except Exception as e:
                logger.error(f"   ❌ Error processing {provider.upper()} results: {str(e)}")
                provider_results[provider] = {"error": str(e)}

        # Sort all flights by price
        logger.info("-" * 70)
        logger.info(f"🔀 Sorting {len(all_flights)} total flights by price...")
        all_flights.sort(key=lambda x: x.get("price", float("inf")))

        logger.info(f"✅ Sorting complete")

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
            "crew_status": "completed"
        }

    def _extract_provider_flights(self, provider: str, crew_output: Any) -> Optional[Dict]:
        """
        Extract flights for a specific provider from crew output

        Args:
            provider: Provider name (skyscanner, kayak, etc.)
            crew_output: Raw output from crew.kickoff()

        Returns:
            Dictionary with flights and metadata, or None if not found
        """
        try:
            # CrewAI crew.kickoff() returns a string or dict with results
            # Parse the output to extract flight data for this provider

            if isinstance(crew_output, dict):
                return crew_output.get(provider)
            elif isinstance(crew_output, str):
                # If output is a string, it contains agent summaries
                # In production, you'd parse this more carefully
                logger.debug(f"Processing string output for {provider}")
                return {"flights": [], "total_results": 0}
            else:
                return {"flights": [], "total_results": 0}

        except Exception as e:
            logger.error(f"Error extracting flights for {provider}: {str(e)}")
            return None

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the agent system with detailed logging

        Returns:
            Dictionary with agent system status and configuration
        """
        logger.info("\n" + "=" * 70)
        logger.info("ℹ️  AGENT SYSTEM INFO")
        logger.info("=" * 70)

        try:
            # Initialize agents if not already done
            if not self.agents:
                logger.info("🤖 Initializing agents...")
                self.agents = create_agents(model=self.model, api_key=self.api_key)

            logger.info(f"📊 System: Flight Price Aggregator")
            logger.info(f"🔧 Framework: CrewAI")
            logger.info(f"🧠 LLM Model: {self.model}")
            logger.info(f"🔑 API Key Configured: {'✅ Yes' if self.api_key else '❌ No'}")

            logger.info("\n👥 Agents in System:")
            agent_list = []
            for provider_name, agent in self.agents.items():
                tools_count = len(agent.tools) if hasattr(agent, 'tools') and agent.tools is not None else 0
                logger.info(f"   • {agent.role}")
                logger.info(f"     └─ Provider: {provider_name}")
                logger.info(f"     └─ Goal: {agent.goal}")
                logger.info(f"     └─ Tools: {tools_count}")

                agent_list.append({
                    "name": agent.role,
                    "provider": provider_name,
                    "goal": agent.goal,
                    "tools_count": tools_count
                })

            logger.info("=" * 70 + "\n")

            return {
                "system": "Flight Price Aggregator",
                "framework": "CrewAI",
                "agents": agent_list,
                "total_agents": len(agent_list),
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "api_key_configured": bool(self.api_key)
            }

        except Exception as e:
            logger.error(f"❌ Error getting agent info: {str(e)}", exc_info=True)
            return {
                "system": "Flight Price Aggregator",
                "framework": "CrewAI",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# ============================================================================
# SINGLETON CREW INSTANCE
# ============================================================================

_crew_instance = None


def get_crew(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None
) -> FlightAggregatorCrew:
    """
    Get or create the flight aggregator crew (singleton pattern)

    Args:
        provider: LLM provider (google, openai, anthropic) - defaults to LLM_PROVIDER env var or google
        model: LLM model to use - defaults to LLM_MODEL env var or provider's default
        api_key: API key (defaults to provider's env var)

    Returns:
        FlightAggregatorCrew instance
    """
    global _crew_instance
    if _crew_instance is None:
        # Read from environment variables if not explicitly provided
        env_provider = provider or os.getenv("LLM_PROVIDER", "google")
        env_model = model or os.getenv("LLM_MODEL")

        _crew_instance = FlightAggregatorCrew(
            provider=env_provider,
            model=env_model,
            api_key=api_key
        )
    return _crew_instance


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
