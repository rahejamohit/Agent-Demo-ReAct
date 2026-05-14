"""
ReAct-based Flight Search Agents using Claude API
Each agent specializes in a flight provider and uses tool_use for API calls
"""

import anthropic
import json
import logging
from typing import Optional
from datetime import datetime
from agents_config import (
    FLIGHT_SEARCH_TOOLS,
    AGENT_CONFIG,
    AGENT_SYSTEM_PROMPT,
    PROVIDER_PROMPTS
)

logger = logging.getLogger(__name__)


class FlightSearchAgent:
    """
    Base ReAct Agent for flight searches
    Uses Claude API with tool_use capability
    """

    def __init__(self, provider: str, api_key: Optional[str] = None):
        """
        Initialize flight search agent

        Args:
            provider: Flight provider (skyscanner, kayak, google_flights, amadeus)
            api_key: Anthropic API key (uses env variable if not provided)
        """
        self.provider = provider
        self.config = AGENT_CONFIG.get(provider)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.max_iterations = 5
        self.conversation_history = []

        if not self.config:
            raise ValueError(f"Unknown provider: {provider}")

    def search(self, origin: str, destination: str, departure_date: str,
               passengers: int = 1) -> dict:
        """
        Search for flights using ReAct pattern (Reasoning + Acting)

        Args:
            origin: IATA code (e.g., JFK)
            destination: IATA code (e.g., LAX)
            departure_date: YYYY-MM-DD format
            passengers: Number of passengers

        Returns:
            Dictionary with flight results
        """
        logger.info(f"🔍 [{self.provider.upper()}] Searching {origin} → {destination} on {departure_date}")

        # Build search request
        search_request = f"""
        Search for flights with these parameters:
        - Origin: {origin}
        - Destination: {destination}
        - Departure Date: {departure_date}
        - Passengers: {passengers}
        - Provider: {self.provider}

        Use the {FLIGHT_SEARCH_TOOLS[self.provider]['name']} tool to search flights.
        Return results in JSON format with structured flight data.
        """

        # Initialize messages
        self.conversation_history = []

        # ReAct loop
        for iteration in range(self.max_iterations):
            logger.debug(f"ReAct Iteration {iteration + 1}/{self.max_iterations}")

            # Get tool for this provider
            tool = {
                "name": FLIGHT_SEARCH_TOOLS[self.provider]["name"],
                "description": FLIGHT_SEARCH_TOOLS[self.provider]["description"],
                "input_schema": FLIGHT_SEARCH_TOOLS[self.provider]["input_schema"]
            }

            # Create message
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=AGENT_SYSTEM_PROMPT + "\n\n" + PROVIDER_PROMPTS[self.provider],
                tools=[tool],
                messages=[
                    {
                        "role": "user",
                        "content": search_request
                    }
                ] + self.conversation_history
            )

            logger.debug(f"Response stop reason: {response.stop_reason}")

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })

            # Process response
            if response.stop_reason == "end_turn":
                # Agent finished without using tools
                return self._extract_results(response)

            elif response.stop_reason == "tool_use":
                # Agent wants to use a tool
                tool_result = self._process_tool_use(response, origin, destination, departure_date, passengers)

                # Add tool result to conversation
                self.conversation_history.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_result["tool_use_id"],
                            "content": json.dumps(tool_result["result"])
                        }
                    ]
                })

            else:
                logger.warning(f"Unexpected stop reason: {response.stop_reason}")
                break

        return self._extract_results(response)

    def _process_tool_use(self, response: anthropic.types.Message,
                         origin: str, destination: str, departure_date: str,
                         passengers: int) -> dict:
        """
        Process tool use request from Claude

        Args:
            response: Claude's response message
            origin: Departure airport
            destination: Arrival airport
            departure_date: Travel date
            passengers: Number of passengers

        Returns:
            Tool result dictionary
        """
        for content in response.content:
            if content.type == "tool_use":
                tool_use_id = content.id
                tool_name = content.name

                logger.info(f"Tool Use: {tool_name}")

                # Simulate API call (in production, integrate real APIs)
                result = self._call_flight_api(
                    tool_name,
                    origin,
                    destination,
                    departure_date,
                    passengers
                )

                return {
                    "tool_use_id": tool_use_id,
                    "result": result
                }

        return {"tool_use_id": "", "result": {}}

    def _call_flight_api(self, tool_name: str, origin: str, destination: str,
                        departure_date: str, passengers: int) -> dict:
        """
        Simulate calling flight API (replace with real API calls)

        In production:
        - Integrate actual Skyscanner, Kayak, Google Flights, Amadeus APIs
        - Handle rate limiting and authentication
        - Parse real API responses

        Args:
            tool_name: Name of the tool to use
            origin: Departure airport
            destination: Arrival airport
            departure_date: Travel date
            passengers: Number of passengers

        Returns:
            Flight data
        """
        logger.info(f"📡 Calling {self.provider} API...")

        # TODO: Replace with real API integrations
        # This is a realistic mock for development
        flights = self._generate_mock_flights(origin, destination, departure_date, passengers)

        return {
            "status": "success",
            "provider": self.provider,
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "passengers": passengers,
            "flights": flights,
            "total_results": len(flights)
        }

    def _generate_mock_flights(self, origin: str, destination: str,
                              departure_date: str, passengers: int) -> list:
        """
        Generate realistic mock flight data for development
        (Replace with real API responses in production)
        """
        import random
        from datetime import datetime, timedelta

        flights = []
        departure_dt = datetime.strptime(departure_date, "%Y-%m-%d")

        airlines = {
            "skyscanner": ["Delta", "United", "Southwest", "JetBlue"],
            "kayak": ["United", "American", "Alaska", "Spirit"],
            "google_flights": ["Delta", "Southwest", "United", "Frontier"],
            "amadeus": ["Emirates", "Lufthansa", "Qatar", "Singapore Airlines"]
        }

        base_prices = {
            "skyscanner": 200,
            "kayak": 180,
            "google_flights": 210,
            "amadeus": 350
        }

        for i in range(4):
            departure_hour = random.randint(6, 22)
            departure_time = departure_dt.replace(hour=departure_hour, minute=random.choice([0, 15, 30, 45]))

            duration = random.randint(180, 480)
            arrival_time = departure_time + timedelta(minutes=duration)

            stops = random.randint(0, 2)
            price = base_prices[self.provider] + (stops * 50) + random.uniform(-30, 100)

            flight = {
                "airline": random.choice(airlines[self.provider]),
                "flight_number": f"{random.choice('ABCDEFGH')}{random.randint(100, 999)}",
                "departure": departure_time.isoformat(),
                "arrival": arrival_time.isoformat(),
                "duration_minutes": duration,
                "stops": stops,
                "price": round(price, 2),
                "currency": "USD",
                "booking_url": f"https://{self.provider}.com/book/{origin}/{destination}/{departure_date}?flights={i}",
                "seats_available": random.randint(1, 20)
            }
            flights.append(flight)

        return sorted(flights, key=lambda x: x["price"])

    def _extract_results(self, response: anthropic.types.Message) -> dict:
        """
        Extract flight results from Claude's response

        Args:
            response: Claude's final response

        Returns:
            Structured flight data
        """
        results = {
            "provider": self.provider,
            "flights": [],
            "error": None
        }

        try:
            # Look for text content with JSON
            for content in response.content:
                if hasattr(content, 'text'):
                    text = content.text
                    # Try to extract JSON from response
                    if '```json' in text:
                        json_str = text.split('```json')[1].split('```')[0].strip()
                        results.update(json.loads(json_str))
                    elif '{' in text:
                        # Try to parse JSON directly
                        try:
                            results.update(json.loads(text))
                        except json.JSONDecodeError:
                            logger.warning(f"Could not parse JSON from response")

        except Exception as e:
            logger.error(f"Error extracting results: {e}")
            results["error"] = str(e)

        return results


class AgentOrchestrator:
    """
    Orchestrates multiple flight search agents in parallel
    Aggregates and deduplicates results
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize orchestrator

        Args:
            api_key: Anthropic API key
        """
        self.api_key = api_key
        self.agents = {
            "skyscanner": FlightSearchAgent("skyscanner", api_key),
            "kayak": FlightSearchAgent("kayak", api_key),
            "google_flights": FlightSearchAgent("google_flights", api_key),
            "amadeus": FlightSearchAgent("amadeus", api_key)
        }

    def search_all_providers(self, origin: str, destination: str,
                            departure_date: str, passengers: int = 1) -> dict:
        """
        Search all flight providers in parallel

        Args:
            origin: Departure airport
            destination: Arrival airport
            departure_date: Travel date
            passengers: Number of passengers

        Returns:
            Aggregated flight results from all providers
        """
        logger.info(f"🔄 Orchestrating search across all providers...")

        all_results = {}
        combined_flights = []

        # Search each provider (in production, use concurrent.futures for parallelization)
        for provider_name, agent in self.agents.items():
            try:
                logger.info(f"Searching {provider_name}...")
                result = agent.search(origin, destination, departure_date, passengers)
                all_results[provider_name] = result

                # Aggregate flights with provider info
                if "flights" in result:
                    for flight in result["flights"]:
                        flight["provider"] = provider_name
                        combined_flights.append(flight)

            except Exception as e:
                logger.error(f"Error searching {provider_name}: {e}")
                all_results[provider_name] = {"error": str(e), "flights": []}

        # Sort combined results by price
        combined_flights.sort(key=lambda x: x.get("price", float('inf')))

        return {
            "search_params": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "passengers": passengers
            },
            "flights": combined_flights,
            "total_results": len(combined_flights),
            "provider_results": all_results,
            "timestamp": datetime.now().isoformat()
        }


# Global orchestrator instance
agent_orchestrator = AgentOrchestrator()
