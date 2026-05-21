"""
Flight Search Configuration for Flight Price Aggregator
CrewAI agents and tasks with tool integration
Uses CrewAI 1.14.5 native multi-provider LLM support
Supports: Google Gemini, OpenAI, Anthropic
"""

import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from crewai.tools import tool
from crewai import Agent, Task, LLM

# ============================================================================
# PROVIDER CONFIGURATION
# ============================================================================

PROVIDER_CONFIG = {
    "google": {
        "prefix": "gemini",
        "env_var": "GOOGLE_API_KEY",
        "default_model": "gemini-3-flash-preview",
        "description": "Google Gemini"
    },
    "openai": {
        "prefix": "openai",
        "env_var": "OPENAI_API_KEY",
        "default_model": "gpt-4",
        "description": "OpenAI GPT-4"
    },
    "anthropic": {
        "prefix": "anthropic",
        "env_var": "ANTHROPIC_API_KEY",
        "default_model": "claude-3-5-sonnet",
        "description": "Anthropic Claude 3.5 Sonnet"
    }
}

# ============================================================================
# FLIGHT SEARCH TOOLS (with @tool decorator)
# ============================================================================

@tool
def search_skyscanner(origin: str, destination: str, departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """Search flights on Skyscanner for deals and budget airlines."""
    return _search_flights("skyscanner", origin, destination, departure_date, passengers)


@tool
def search_kayak(origin: str, destination: str, departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """Search flights on Kayak for best prices and ratings."""
    return _search_flights("kayak", origin, destination, departure_date, passengers)


@tool
def search_google_flights(origin: str, destination: str, departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """Search flights on Google Flights for flexible options and price trends."""
    return _search_flights("google_flights", origin, destination, departure_date, passengers)


@tool
def search_amadeus(origin: str, destination: str, departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """Search flights on Amadeus for premium options and ancillaries."""
    return _search_flights("amadeus", origin, destination, departure_date, passengers)


def _search_flights(provider: str, origin: str, destination: str,
                   departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """Generate realistic mock flight data for a provider"""
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
# AGENT CONFIGURATION
# ============================================================================

def create_agents(
    provider: str = "google",
    model: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Agent]:
    """
    Create CrewAI Agent objects with multi-provider LLM support using CrewAI 1.14.5

    Args:
        provider: LLM provider to use (default: google)
                 Supported: google, openai, anthropic
        model: LLM model to use (defaults to provider's default model)
               Examples:
               - Google: gemini-3-flash-preview, gemini-2-flash
               - OpenAI: gpt-4, gpt-4-turbo, gpt-3.5-turbo
               - Anthropic: claude-3-5-sonnet, claude-3-opus
        api_key: API key for the provider (defaults to provider's env var)

    Returns:
        Dictionary of CrewAI Agent objects indexed by provider

    Raises:
        ValueError: If provider is not supported or API key is missing
    """
    # Validate provider
    if provider not in PROVIDER_CONFIG:
        supported = ", ".join(PROVIDER_CONFIG.keys())
        raise ValueError(f"Unsupported provider '{provider}'. Supported: {supported}")

    config = PROVIDER_CONFIG[provider]

    # Get or use default model
    if model is None:
        model = config["default_model"]

    # Get API key from parameter or environment
    if api_key is None:
        api_key = os.getenv(config["env_var"])

    if not api_key:
        raise ValueError(
            f"{config['env_var']} environment variable is not set. "
            f"Please set your {config['description']} API key."
        )

    # Type assertion: api_key is guaranteed to be a string after the check above
    assert api_key is not None

    # Create CrewAI's native LLM instance with dynamic provider
    # Format: {provider}/{model}
    llm = LLM(
        model=f"{config['prefix']}/{model}",
        api_key=api_key,
        temperature=0.7
    )

    # Log provider info
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🧠 LLM Provider: {config['description']} ({provider}/{model})")

    # Define agents for each flight provider
    # All agents share the same LLM instance
    agents = {
        "skyscanner": Agent(
            role="Skyscanner Flight Search Specialist",
            goal="Find the cheapest flights and best deals on Skyscanner",
            backstory="You are an expert at finding budget-friendly flights on Skyscanner, specializing in low-cost carriers and special deals.",
            tools=[search_skyscanner],
            llm=llm,
            verbose=True
        ),
        "kayak": Agent(
            role="Kayak Flight Search Specialist",
            goal="Find the best value flights with ratings and customer satisfaction on Kayak",
            backstory="You are skilled at finding flights on Kayak with the best value for money, considering both price and customer ratings.",
            tools=[search_kayak],
            llm=llm,
            verbose=True
        ),
        "google_flights": Agent(
            role="Google Flights Search Specialist",
            goal="Find flexible flight options and analyze price trends on Google Flights",
            backstory="You excel at finding flexible flight options on Google Flights and identifying price trends to help customers find the best time to book.",
            tools=[search_google_flights],
            llm=llm,
            verbose=True
        ),
        "amadeus": Agent(
            role="Amadeus Flight Search Specialist",
            goal="Find premium flights with seat options and ancillaries on Amadeus",
            backstory="You specialize in finding premium flight options on Amadeus with detailed seat configurations and ancillary services.",
            tools=[search_amadeus],
            llm=llm,
            verbose=True
        )
    }

    return agents


# ============================================================================
# TASK CONFIGURATION
# ============================================================================

def create_tasks(agents: Dict[str, Agent], origin: str, destination: str,
                departure_date: str, passengers: int = 1) -> List[Task]:
    """
    Create CrewAI Task objects for each agent

    Args:
        agents: Dictionary of CrewAI Agent objects
        origin: Departure airport code
        destination: Arrival airport code
        departure_date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers

    Returns:
        List of CrewAI Task objects
    """
    tasks = [
        Task(
            description=f"Search for {passengers} passenger(s) flight(s) from {origin} to {destination} on {departure_date} on Skyscanner. Find the cheapest options.",
            agent=agents["skyscanner"],
            expected_output="A list of flights from Skyscanner with prices, airlines, departure/arrival times, and booking URLs"
        ),
        Task(
            description=f"Search for {passengers} passenger(s) flight(s) from {origin} to {destination} on {departure_date} on Kayak. Find the best value options.",
            agent=agents["kayak"],
            expected_output="A list of flights from Kayak with prices, airlines, departure/arrival times, and booking URLs"
        ),
        Task(
            description=f"Search for {passengers} passenger(s) flight(s) from {origin} to {destination} on {departure_date} on Google Flights. Analyze price trends.",
            agent=agents["google_flights"],
            expected_output="A list of flights from Google Flights with prices, airlines, departure/arrival times, and booking URLs"
        ),
        Task(
            description=f"Search for {passengers} passenger(s) flight(s) from {origin} to {destination} on {departure_date} on Amadeus. Find premium options.",
            agent=agents["amadeus"],
            expected_output="A list of flights from Amadeus with prices, airlines, departure/arrival times, and booking URLs"
        )
    ]

    return tasks
