"""
Flight Price Aggregator Crew - Multi-agent orchestration with CrewAI
Coordinates specialized agents for flight search across multiple providers
"""

from crewai import Crew
from datetime import datetime
import logging
from typing import Dict, List, Any

from crew_config import create_agents, create_tasks, AGENT_CONFIG

logger = logging.getLogger(__name__)


class FlightAggregatorCrew:
    """Manages flight search crew with CrewAI"""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: str = None):
        """
        Initialize the flight aggregator crew.

        Args:
            model: LLM model to use
            api_key: Anthropic API key (optional, defaults to env var)
        """
        self.model = model
        self.api_key = api_key
        self.agents = create_agents(model=model, api_key=api_key)
        logger.info(f"🤖 Initialized {len(self.agents)} specialized agents")

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        passengers: int = 1,
        cabin_class: str = "economy"
    ) -> Dict[str, Any]:
        """
        Search flights across all providers using the crew.

        Args:
            origin: Departure airport IATA code
            destination: Arrival airport IATA code
            departure_date: Travel date in YYYY-MM-DD format
            passengers: Number of passengers
            cabin_class: Cabin class preference

        Returns:
            Aggregated results from all agents
        """

        logger.info(f"🔍 Starting crew flight search: {origin} → {destination} on {departure_date}")

        # Create tasks for this specific search
        tasks = create_tasks(
            agents=self.agents,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            passengers=passengers
        )

        # Create and execute the crew
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            verbose=True,
            max_rpm=100  # Max API calls per minute
        )

        # Execute the crew
        try:
            logger.info("👥 Executing crew with all 4 agents...")
            result = crew.kickoff()
            logger.info("✅ Crew execution completed")
        except Exception as e:
            logger.error(f"❌ Crew execution failed: {str(e)}")
            raise

        # Aggregate and structure results
        aggregated = self._aggregate_results(
            crew_output=result,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            passengers=passengers
        )

        return aggregated

    def _aggregate_results(
        self,
        crew_output: str,
        origin: str,
        destination: str,
        departure_date: str,
        passengers: int
    ) -> Dict[str, Any]:
        """
        Parse crew output and aggregate flight results.

        Args:
            crew_output: Raw output from crew execution
            origin: Search origin
            destination: Search destination
            departure_date: Travel date
            passengers: Number of passengers

        Returns:
            Structured aggregated results
        """

        # Since CrewAI agents call our tools directly, we collect results from tool calls
        # The tools (_search_flights) return structured data which we aggregate here

        all_flights = []
        provider_results = {}

        # Collect results from each provider's agent
        for provider_name, agent in self.agents.items():
            try:
                # Agent has executed its task and called the appropriate search tool
                # We reconstruct the results from the agent's action
                logger.info(f"📊 Collecting results from {provider_name} agent...")

                # In CrewAI, tool results are captured in the task output
                # For this implementation, we'll fetch fresh data from each provider
                flights = self._get_provider_flights(provider_name, origin, destination, departure_date, passengers)

                all_flights.extend(flights)
                provider_results[provider_name] = {
                    "flights": flights,
                    "total_results": len(flights)
                }

            except Exception as e:
                logger.error(f"❌ Error collecting results from {provider_name}: {str(e)}")
                provider_results[provider_name] = {"error": str(e), "flights": []}

        # Sort all flights by price
        all_flights.sort(key=lambda x: x.get("price", float("inf")))

        return {
            "search_params": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "passengers": passengers
            },
            "flights": all_flights,
            "total_results": len(all_flights),
            "provider_results": provider_results,
            "timestamp": datetime.now().isoformat()
        }

    def _get_provider_flights(
        self,
        provider: str,
        origin: str,
        destination: str,
        departure_date: str,
        passengers: int
    ) -> List[Dict[str, Any]]:
        """
        Get flights from a specific provider.
        This would call the actual API or mock data.

        Args:
            provider: Provider name (skyscanner, kayak, google_flights, amadeus)
            origin: Departure airport code
            destination: Arrival airport code
            departure_date: Travel date
            passengers: Number of passengers

        Returns:
            List of flight dictionaries
        """

        from crew_config import _search_flights

        result = _search_flights(
            provider=provider,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            passengers=passengers
        )

        return result["flights"]

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about all agents in the crew.

        Returns:
            Agent information and configuration
        """

        agents_info = []

        for provider_name, agent in self.agents.items():
            config = AGENT_CONFIG.get(provider_name, {})
            agents_info.append({
                "agent": config.get("name", provider_name),
                "provider": provider_name,
                "model": self.model,
                "status": "ready",
                "role": agent.role,
                "goal": agent.goal,
                "description": config.get("description", ""),
                "specialty": config.get("specialty", "")
            })

        return {
            "system": "CrewAI Flight Aggregator",
            "framework": "CrewAI",
            "agents": agents_info,
            "total_agents": len(self.agents),
            "timestamp": datetime.now().isoformat()
        }


# Global crew instance
_crew_instance = None


def get_crew(model: str = "claude-3-5-sonnet-20241022", api_key: str = None) -> FlightAggregatorCrew:
    """
    Get or create the global crew instance.

    Args:
        model: LLM model to use
        api_key: API key (optional)

    Returns:
        FlightAggregatorCrew instance
    """

    global _crew_instance

    if _crew_instance is None:
        _crew_instance = FlightAggregatorCrew(model=model, api_key=api_key)

    return _crew_instance
