"""
CrewAI Configuration for Flight Price Aggregator
Defines agents, tools, and tasks for multi-provider flight search
"""

from crewai import Agent, Task
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# ============================================================================
# FLIGHT SEARCH TOOLS
# ============================================================================

@tool("search_skyscanner")
def search_skyscanner(origin: str, destination: str, departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """
    Search flights on Skyscanner for deals and budget airlines.

    Args:
        origin: Departure airport IATA code (e.g., JFK)
        destination: Arrival airport IATA code (e.g., LAX)
        departure_date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers (1-9)

    Returns:
        Dictionary with flights list and metadata
    """
    return _search_flights("skyscanner", origin, destination, departure_date, passengers)


@tool("search_kayak")
def search_kayak(origin: str, destination: str, departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """
    Search flights on Kayak for best prices and ratings.

    Args:
        origin: Departure airport IATA code (e.g., JFK)
        destination: Arrival airport IATA code (e.g., LAX)
        departure_date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers (1-9)

    Returns:
        Dictionary with flights list and metadata
    """
    return _search_flights("kayak", origin, destination, departure_date, passengers)


@tool("search_google_flights")
def search_google_flights(origin: str, destination: str, departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """
    Search flights on Google Flights for flexible options and price trends.

    Args:
        origin: Departure airport IATA code (e.g., JFK)
        destination: Arrival airport IATA code (e.g., LAX)
        departure_date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers (1-9)

    Returns:
        Dictionary with flights list and metadata
    """
    return _search_flights("google_flights", origin, destination, departure_date, passengers)


@tool("search_amadeus")
def search_amadeus(origin: str, destination: str, departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """
    Search flights on Amadeus for premium options and seat availability.

    Args:
        origin: Departure airport IATA code (e.g., JFK)
        destination: Arrival airport IATA code (e.g., LAX)
        departure_date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers (1-9)

    Returns:
        Dictionary with flights list and metadata
    """
    return _search_flights("amadeus", origin, destination, departure_date, passengers)


# ============================================================================
# HELPER FUNCTIONS FOR FLIGHT SEARCH
# ============================================================================

def _search_flights(provider: str, origin: str, destination: str,
                   departure_date: str, passengers: int) -> Dict[str, Any]:
    """Generate realistic mock flight data for providers"""

    flights = _generate_mock_flights(provider, origin, destination, departure_date, passengers)

    return {
        "status": "success",
        "provider": provider,
        "flights": flights,
        "total_results": len(flights),
        "search_params": {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "passengers": passengers
        }
    }


def _generate_mock_flights(provider: str, origin: str, destination: str,
                          departure_date: str, passengers: int) -> List[Dict[str, Any]]:
    """Generate realistic mock flight data"""

    airlines = {
        "skyscanner": ["Budget Air", "EconFly", "ValueJet", "SaveAirlines", "DealWings"],
        "kayak": ["Delta", "United", "American", "Southwest", "JetBlue"],
        "google_flights": ["United", "American", "Frontier", "Spirit", "Alaska"],
        "amadeus": ["Lufthansa", "British Airways", "Air France", "KLM", "Emirates"]
    }

    airlines_list = airlines.get(provider, ["Airline"])
    num_flights = random.randint(8, 16)
    flights = []

    base_price = random.randint(150, 400)

    for i in range(num_flights):
        departure_hour = random.randint(6, 22)
        departure_minute = random.choice([0, 15, 30, 45])
        duration = random.randint(180, 600)  # minutes

        departure_time = datetime.strptime(departure_date, "%Y-%m-%d").replace(
            hour=departure_hour, minute=departure_minute
        )
        arrival_time = departure_time + timedelta(minutes=duration)

        flight = {
            "provider": provider,
            "airline": random.choice(airlines_list),
            "flight_number": f"{random.choice(['DL', 'UA', 'AA', 'SW', 'NK', 'B6', 'AS', 'F9'])}{random.randint(100, 9999)}",
            "departure": departure_time.isoformat(),
            "arrival": arrival_time.isoformat(),
            "duration_minutes": duration,
            "stops": random.choices([0, 1, 2], weights=[60, 30, 10])[0],
            "price": round(base_price + random.uniform(-50, 150), 2),
            "currency": "USD",
            "booking_url": f"https://{provider}.example.com/book/{random.randint(100000, 999999)}",
            "seats_available": random.randint(1, 15)
        }
        flights.append(flight)

    # Sort by price
    flights.sort(key=lambda x: x["price"])
    return flights


# ============================================================================
# CREWAI AGENTS DEFINITION
# ============================================================================

def create_agents(model: str = "claude-3-5-sonnet-20241022", api_key: str = None) -> Dict[str, Agent]:
    """
    Create specialized flight search agents for CrewAI.

    Args:
        model: LLM model to use (e.g., "claude-3-5-sonnet-20241022")
        api_key: API key (defaults to ANTHROPIC_API_KEY env var)

    Returns:
        Dictionary of agents keyed by provider name
    """

    if api_key is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")

    # Initialize the Claude LLM
    llm = ChatAnthropic(
        model=model,
        api_key=api_key,
        temperature=0.7,
        max_tokens=2048
    )

    agents = {
        "skyscanner": Agent(
            role="Skyscanner Flight Search Specialist",
            goal="Find the cheapest flights and best deals on Skyscanner",
            backstory="""You are an expert at finding budget flights and deals.
You specialize in identifying the cheapest fares and alternative airports that can save money.
You excel at analyzing flight deals and recommending budget airlines.""",
            tools=[search_skyscanner],
            llm=llm,
            max_iter=5,
            memory=True,
            verbose=True
        ),

        "kayak": Agent(
            role="Kayak Flight Search Specialist",
            goal="Find the best value flights with ratings and customer satisfaction on Kayak",
            backstory="""You are an expert at finding flights that balance price and quality.
You specialize in flights with good customer ratings and reliable airlines.
You excel at identifying value-for-money flight options.""",
            tools=[search_kayak],
            llm=llm,
            max_iter=5,
            memory=True,
            verbose=True
        ),

        "google_flights": Agent(
            role="Google Flights Search Specialist",
            goal="Find flexible flight options and analyze price trends on Google Flights",
            backstory="""You are an expert at finding flexible flight options and understanding price trends.
You specialize in identifying alternative dates and comparing multiple routing options.
You excel at maximizing travel flexibility and spotting price patterns.""",
            tools=[search_google_flights],
            llm=llm,
            max_iter=5,
            memory=True,
            verbose=True
        ),

        "amadeus": Agent(
            role="Amadeus Flight Search Specialist",
            goal="Find premium flights with seat options and ancillaries on Amadeus",
            backstory="""You are an expert at finding premium flight options with detailed seat and ancillary information.
You specialize in enterprise-grade flight inventory and premium airline offerings.
You excel at identifying flights with excellent seat availability and service options.""",
            tools=[search_amadeus],
            llm=llm,
            max_iter=5,
            memory=True,
            verbose=True
        )
    }

    return agents


# ============================================================================
# CREWAI TASKS DEFINITION
# ============================================================================

def create_tasks(agents: Dict[str, Agent],
                origin: str, destination: str,
                departure_date: str, passengers: int) -> List[Task]:
    """
    Create tasks for each agent to search flights.

    Args:
        agents: Dictionary of Agent objects
        origin: Departure airport code
        destination: Arrival airport code
        departure_date: Travel date
        passengers: Number of passengers

    Returns:
        List of Task objects for the crew
    """

    tasks = [
        Task(
            description=f"""Search for flights from {origin} to {destination} on {departure_date} for {passengers} passenger(s).
Focus on finding the cheapest deals and budget airline options.
Use the search_skyscanner tool to find flights.
Report the top 3 cheapest options with detailed information.""",
            agent=agents["skyscanner"],
            expected_output="A detailed report of the 3 cheapest flights found on Skyscanner with prices and details."
        ),

        Task(
            description=f"""Search for flights from {origin} to {destination} on {departure_date} for {passengers} passenger(s).
Focus on finding flights with the best balance of price and customer ratings.
Use the search_kayak tool to find flights.
Report the top 3 best value options with ratings and details.""",
            agent=agents["kayak"],
            expected_output="A detailed report of the 3 best value flights found on Kayak with prices, ratings, and details."
        ),

        Task(
            description=f"""Search for flights from {origin} to {destination} on {departure_date} for {passengers} passenger(s).
Focus on finding flexible options and analyzing price trends.
Use the search_google_flights tool to find flights.
Report the top 3 most flexible options with price trend analysis.""",
            agent=agents["google_flights"],
            expected_output="A detailed report of the 3 most flexible flights found on Google Flights with price trends and details."
        ),

        Task(
            description=f"""Search for flights from {origin} to {destination} on {departure_date} for {passengers} passenger(s).
Focus on premium options with detailed seat availability and ancillaries.
Use the search_amadeus tool to find flights.
Report the top 3 premium options with seat and service details.""",
            agent=agents["amadeus"],
            expected_output="A detailed report of the 3 premium flights found on Amadeus with seat details and ancillaries."
        )
    ]

    return tasks


# ============================================================================
# AGENT CONFIGURATION METADATA
# ============================================================================

AGENT_CONFIG = {
    "skyscanner": {
        "name": "Skyscanner Agent",
        "provider": "skyscanner",
        "description": "Searches Skyscanner for flight deals",
        "specialty": "Budget flights and deals"
    },
    "kayak": {
        "name": "Kayak Agent",
        "provider": "kayak",
        "description": "Searches Kayak for best value flights",
        "specialty": "Value for money and ratings"
    },
    "google_flights": {
        "name": "Google Flights Agent",
        "provider": "google_flights",
        "description": "Searches Google Flights for flexible options",
        "specialty": "Flexibility and price trends"
    },
    "amadeus": {
        "name": "Amadeus Agent",
        "provider": "amadeus",
        "description": "Searches Amadeus for premium flights",
        "specialty": "Premium options and ancillaries"
    }
}
