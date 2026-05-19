"""
CrewAI Configuration for Flight Price Aggregator
Defines agents, tools, and tasks for multi-provider flight search
"""

from crewai import Agent, Task
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
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
    Search flights on Amadeus for premium options and ancillaries.

    Args:
        origin: Departure airport IATA code (e.g., JFK)
        destination: Arrival airport IATA code (e.g., LAX)
        departure_date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers (1-9)

    Returns:
        Dictionary with flights list and metadata
    """
    return _search_flights("amadeus", origin, destination, departure_date, passengers)


def _search_flights(provider: str, origin: str, destination: str,
                   departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """Generate mock flight data"""
    random.seed(hash(f"{provider}{origin}{destination}{departure_date}"))

    airlines = {
        "skyscanner": ["Ryanair", "EasyJet", "Wizz Air", "Southwest", "Spirit"],
        "kayak": ["United", "Delta", "American", "Southwest", "JetBlue"],
        "google_flights": ["Lufthansa", "KLM", "Air France", "Turkish", "Emirates"],
        "amadeus": ["British Airways", "Lufthansa", "Singapore Airlines", "Qatar", "ANA"]
    }

    flights = []
    for i in range(random.randint(8, 15)):
        base_price = random.uniform(150, 800)
        duration = random.randint(180, 720)

        flight = {
            "provider": provider,
            "airline": random.choice(airlines.get(provider, ["Unknown"])),
            "flight_number": f"{provider.upper()[:2]}{i:03d}",
            "departure": f"{departure_date}T{random.randint(6,22):02d}:{random.choice([0,15,30,45]):02d}:00",
            "arrival": f"{departure_date}T{random.randint(8,23):02d}:{random.choice([0,15,30,45]):02d}:00",
            "duration_minutes": duration,
            "stops": random.choice([0, 0, 0, 1, 1, 2]),
            "price": round(base_price, 2),
            "currency": "USD",
            "booking_url": f"https://{provider}.com/book?flight={i}",
            "seats_available": random.randint(1, 50)
        }
        flights.append(flight)

    flights.sort(key=lambda x: x['price'])
    return {"flights": flights, "total_results": len(flights)}


# ============================================================================
# CREWAI AGENTS DEFINITION
# ============================================================================

AGENT_CONFIG = {
    "model": "gemini-3-flash-preview",
    "max_iterations": 5,
    "memory": True,
    "verbose": True
}


def create_agents(model: str = "gemini-3-flash-preview", api_key: str = None) -> Dict[str, Agent]:
    """
    Create specialized flight search agents for CrewAI.

    Args:
        model: LLM model to use
        api_key: API key (defaults to GOOGLE_API_KEY env var)

    Returns:
        Dictionary of agents keyed by provider name
    """
    if api_key is None:
        api_key = os.getenv("GOOGLE_API_KEY")

    # Initialize the Google Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
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

def create_tasks(agents: Dict[str, Agent], origin: str, destination: str,
                departure_date: str, passengers: int = 1) -> List[Task]:
    """
    Create tasks for each agent to execute.

    Args:
        agents: Dictionary of Agent objects
        origin: Departure airport code
        destination: Arrival airport code
        departure_date: Travel date
        passengers: Number of passengers

    Returns:
        List of Task objects
    """

    tasks = [
        Task(
            description=f"Search for flights from {origin} to {destination} on {departure_date} for {passengers} passenger(s) on Skyscanner. Find budget-friendly options and report the cheapest flights.",
            agent=agents["skyscanner"],
            expected_output="List of flights with prices, airlines, and booking links from Skyscanner"
        ),
        Task(
            description=f"Search for flights from {origin} to {destination} on {departure_date} for {passengers} passenger(s) on Kayak. Focus on value and customer ratings.",
            agent=agents["kayak"],
            expected_output="List of flights with prices, airlines, and booking links from Kayak"
        ),
        Task(
            description=f"Search for flights from {origin} to {destination} on {departure_date} for {passengers} passenger(s) on Google Flights. Look for flexible options and price trends.",
            agent=agents["google_flights"],
            expected_output="List of flights with prices, airlines, and booking links from Google Flights"
        ),
        Task(
            description=f"Search for flights from {origin} to {destination} on {departure_date} for {passengers} passenger(s) on Amadeus. Find premium options with seat details.",
            agent=agents["amadeus"],
            expected_output="List of flights with prices, airlines, and booking links from Amadeus"
        )
    ]

    return tasks
