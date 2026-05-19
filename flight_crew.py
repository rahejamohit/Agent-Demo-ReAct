"""
Flight Price Aggregator using CrewAI framework
Multi-agent orchestration with Google Gemini 3 Flash
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from crewai import Crew
from crew_config import create_agents, create_tasks

# Configure logging
logger = logging.getLogger(__name__)


class FlightAggregatorCrew:
    """Orchestrates multiple flight search agents using CrewAI framework with Google Gemini 3 Flash"""

    def __init__(self, model: str = "gemini-3-flash-preview", api_key: str = None):
        """
        Initialize the flight aggregator crew

        Args:
            model: LLM model to use (default: gemini-3-flash-preview)
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
        """
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            logger.warning("⚠️  GOOGLE_API_KEY not set. Crew operations will fail.")

        self.model = model
        self.api_key = api_key
        self.crew = None
        self.agents = None
        self.providers = ["skyscanner", "kayak", "google_flights", "amadeus"]

    def _initialize_crew(self, origin: str, destination: str,
                        departure_date: str, passengers: int = 1) -> Crew:
        """
        Initialize and return a CrewAI Crew instance

        Args:
            origin: Departure airport code
            destination: Arrival airport code
            departure_date: Travel date in YYYY-MM-DD format
            passengers: Number of passengers

        Returns:
            CrewAI Crew instance ready to execute
        """
        # Create agents with the configured model and API key
        self.agents = create_agents(model=self.model, api_key=self.api_key)

        # Create tasks for each agent
        tasks = create_tasks(
            agents=self.agents,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            passengers=passengers
        )

        # Create and return the crew
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            verbose=True,
            max_retries=2
        )

        return crew

    def search_flights(self, origin: str, destination: str, departure_date: str,
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
        logger.info(f"🤖 CrewAI Flight Search: {origin} → {destination} on {departure_date}")
        logger.info(f"   Passengers: {passengers} | Cabin: {cabin_class}")

        try:
            # Validate inputs
            if not origin or not destination or not departure_date:
                raise ValueError("origin, destination, and departure_date are required")

            if passengers < 1 or passengers > 9:
                raise ValueError("passengers must be between 1 and 9")

            if cabin_class not in ["economy", "business", "first"]:
                raise ValueError("cabin_class must be: economy, business, or first")

            # Initialize crew for this search
            crew = self._initialize_crew(origin, destination, departure_date, passengers)

            logger.info("🚀 Executing CrewAI crew tasks...")

            # Execute the crew - this runs all agent tasks
            crew_output = crew.kickoff()

            logger.info("✅ CrewAI crew execution completed")

            # Aggregate results from all agents
            aggregated_results = self._aggregate_crew_results(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                passengers=passengers,
                cabin_class=cabin_class,
                crew_output=crew_output
            )

            logger.info(f"📊 Total flights found: {aggregated_results['total_results']}")

            return aggregated_results

        except ValueError as e:
            logger.error(f"❌ Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ CrewAI execution failed: {str(e)}", exc_info=True)
            raise

    def _aggregate_crew_results(self, origin: str, destination: str,
                               departure_date: str, passengers: int,
                               cabin_class: str, crew_output: Any) -> Dict[str, Any]:
        """
        Aggregate results from CrewAI crew execution

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
        all_flights = []
        provider_results = {}

        # Process results from each agent
        for provider in self.providers:
            try:
                if self.agents and provider in self.agents:
                    agent = self.agents[provider]
                    # Extract flights from agent's task output
                    # The crew_output typically contains results from each task

                    # For now, we collect from the flight search tools
                    # In a production system, you'd parse the crew_output more carefully
                    provider_data = self._extract_provider_flights(provider, crew_output)

                    if provider_data:
                        all_flights.extend(provider_data["flights"])
                        provider_results[provider] = {
                            "flights": provider_data["flights"],
                            "total_results": len(provider_data["flights"])
                        }
                    else:
                        provider_results[provider] = {
                            "flights": [],
                            "total_results": 0
                        }

            except Exception as e:
                logger.error(f"❌ Error processing {provider} results: {str(e)}")
                provider_results[provider] = {"error": str(e)}

        # Sort all flights by price
        all_flights.sort(key=lambda x: x.get("price", float("inf")))

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
        Get information about the agent system

        Returns:
            Dictionary with agent system status and configuration
        """
        try:
            # Initialize agents if not already done
            if not self.agents:
                self.agents = create_agents(model=self.model, api_key=self.api_key)

            agent_list = []
            for provider_name, agent in self.agents.items():
                agent_list.append({
                    "name": agent.role,
                    "provider": provider_name,
                    "goal": agent.goal,
                    "tools_count": len(agent.tools) if hasattr(agent, 'tools') else 0
                })

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
            logger.error(f"Error getting agent info: {str(e)}")
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


def get_crew(model: str = "gemini-3-flash-preview", api_key: str = None) -> FlightAggregatorCrew:
    """
    Get or create the flight aggregator crew (singleton pattern)

    Args:
        model: LLM model to use
        api_key: Google API key

    Returns:
        FlightAggregatorCrew instance
    """
    global _crew_instance
    if _crew_instance is None:
        _crew_instance = FlightAggregatorCrew(model=model, api_key=api_key)
    return _crew_instance


if __name__ == "__main__":
    # Test the crew
    logging.basicConfig(level=logging.INFO)

    print("\n🚀 Testing Flight Aggregator Crew with CrewAI\n")

    crew = get_crew()
    print("📊 Crew Agent Information:")
    agent_info = crew.get_agent_info()
    print(f"  Agents: {agent_info['total_agents']}")
    for agent in agent_info['agents']:
        print(f"    - {agent['name']} ({agent['provider']})")

    print("\n🔍 Searching flights: JFK → LAX on 2026-06-15...")
    results = crew.search_flights(
        origin="JFK",
        destination="LAX",
        departure_date="2026-06-15",
        passengers=1,
        cabin_class="economy"
    )

    print(f"\n✅ Found {results['total_results']} flights total")
    if results['flights']:
        cheapest = results['flights'][0]
        print(f"💰 Cheapest: ${cheapest['price']} on {cheapest['airline']}")
        print(f"📍 Provider: {cheapest['provider']}")
