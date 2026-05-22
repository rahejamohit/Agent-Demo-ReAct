"""
Flight Search Configuration for Flight Price Aggregator
CrewAI agents and tasks with tool integration
Uses CrewAI 1.14.5 native multi-provider LLM support
Supports: Google Gemini, OpenAI, Anthropic, Ollama (local)
"""

import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from crewai import Agent, Task, Crew
from crewai.tools import tool

from constants import (
    FLIGHT_PROVIDER_SKYSCANNER,
    FLIGHT_PROVIDER_KAYAK,
    FLIGHT_PROVIDER_GOOGLE_FLIGHTS,
    FLIGHT_PROVIDER_AMADEUS,
    FLIGHT_PROVIDERS,
    FLIGHT_PROVIDER_DISPLAY_NAMES,
    AIRLINES_BY_PROVIDER,
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
# LLM PROVIDER CONFIGURATION
# ============================================================================

LLM_PROVIDER_CONFIG = {
    "google": {
        "prefix": "gemini",
        "env_var": "GOOGLE_API_KEY",
        "default_model": "gemini-2.5-flash",
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
    },
    "ollama": {
        "prefix": "ollama",
        "env_var": None,  # Ollama doesn't require API key
        "default_model": "gemma4:e4b",
        "description": "Ollama (Local LLM)",
        "base_url": "http://localhost:11434"  # Default Ollama port
    }
}

# ============================================================================
# FLIGHT PROVIDER CONFIGURATION
# ============================================================================

FLIGHT_PROVIDER_CONFIG = {
    FLIGHT_PROVIDER_SKYSCANNER: {
        "role": "Skyscanner Flight Search Specialist",
        "goal": "Find the cheapest flights and best deals on Skyscanner",
        "backstory": "You are an expert at finding budget-friendly flights on Skyscanner, specializing in low-cost carriers and special deals.",
        "tools": None  # Tools will be set in create_provider_agent
    },
    FLIGHT_PROVIDER_KAYAK: {
        "role": "Kayak Flight Search Specialist",
        "goal": "Find the best value flights with ratings and customer satisfaction on Kayak",
        "backstory": "You are skilled at finding flights on Kayak with the best value for money, considering both price and customer ratings.",
        "tools": None
    },
    FLIGHT_PROVIDER_GOOGLE_FLIGHTS: {
        "role": "Google Flights Search Specialist",
        "goal": "Find flexible flight options and analyze price trends on Google Flights",
        "backstory": "You excel at finding flexible flight options on Google Flights and identifying price trends to help customers find the best time to book.",
        "tools": None
    },
    FLIGHT_PROVIDER_AMADEUS: {
        "role": "Amadeus Flight Search Specialist",
        "goal": "Find premium flights with seat options and ancillaries on Amadeus",
        "backstory": "You specialize in finding premium flight options on Amadeus with detailed seat configurations and ancillary services.",
        "tools": None
    }
}

# ============================================================================
# FLIGHT SEARCH TOOLS (with @tool decorator)
# ============================================================================

@tool
def search_skyscanner(origin: str, destination: str, departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """Search flights on Skyscanner for deals and budget airlines."""
    return _search_flights(FLIGHT_PROVIDER_SKYSCANNER, origin, destination, departure_date, passengers)


@tool
def search_kayak(origin: str, destination: str, departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """Search flights on Kayak for best prices and ratings."""
    return _search_flights(FLIGHT_PROVIDER_KAYAK, origin, destination, departure_date, passengers)


@tool
def search_google_flights(origin: str, destination: str, departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """Search flights on Google Flights for flexible options and price trends."""
    return _search_flights(FLIGHT_PROVIDER_GOOGLE_FLIGHTS, origin, destination, departure_date, passengers)


@tool
def search_amadeus(origin: str, destination: str, departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """Search flights on Amadeus for premium options and ancillaries."""
    return _search_flights(FLIGHT_PROVIDER_AMADEUS, origin, destination, departure_date, passengers)


def _search_flights(provider: str, origin: str, destination: str,
                   departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """Generate realistic mock flight data for a provider"""
    random.seed(hash(f"{provider}{origin}{destination}{departure_date}"))

    flights = []
    for i in range(random.randint(8, 15)):
        base_price = random.uniform(150, 800)
        duration = random.randint(180, 720)

        flight = {
            "provider": provider,
            "airline": random.choice(AIRLINES_BY_PROVIDER.get(provider, ["Unknown"])),
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
# LLM CONFIGURATION HELPER
# ============================================================================

def create_llm(
    provider: str = "google",
    model: Optional[str] = None,
    api_key: Optional[str] = None
) -> LLM:
    """
    Create a CrewAI LLM instance with multi-provider support.

    This helper is used by provider crews to get the LLM instance without
    creating unnecessary Agent objects.

    Args:
        provider: LLM provider to use (default: google)
                 Supported: google, openai, anthropic, ollama
        model: LLM model to use (defaults to provider's default model)
               Examples:
               - Google: gemini-2.5-flash
               - OpenAI: gpt-4
               - Anthropic: claude-3-5-sonnet
               - Ollama: llama2, mistral, neural-chat, etc.
        api_key: API key for the provider (defaults to provider's env var)
                 Not needed for Ollama

    Returns:
        CrewAI LLM instance configured for the specified provider

    Raises:
        ValueError: If provider is not supported or API key is missing
    """
    # Validate provider
    if provider not in LLM_PROVIDER_CONFIG:
        supported = ", ".join(LLM_PROVIDER_CONFIG.keys())
        raise ValueError(f"Unsupported provider '{provider}'. Supported: {supported}")

    config = LLM_PROVIDER_CONFIG[provider]

    # Get or use default model
    if model is None:
        model = config["default_model"]

    # Validate LLM class is available
    if LLM is None:
        raise ImportError(
            "CrewAI LLM class could not be imported. "
            "Please ensure CrewAI is properly installed."
        )

    # Log provider info
    import logging
    logger = logging.getLogger(__name__)

    # Handle Ollama separately (no API key needed)
    if provider == "ollama":
        logger.info(f"🧠 LLM Provider: {config['description']} (local model: {model})")

        # Create Ollama LLM instance - use format: ollama/model-name
        llm = LLM(
            model=f"{config['prefix']}/{model}",  # e.g., "ollama/gemma4:e4b"
            base_url=config.get("base_url", "http://localhost:11434")
        )
        return llm

    # For cloud providers (google, openai, anthropic), API key is required
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
    logger.info(f"🧠 LLM Provider: {config['description']} ({provider}/{model})")

    llm = LLM(
        model=f"{config['prefix']}/{model}",
        api_key=api_key,
        temperature=0.7
    )

    return llm


# ============================================================================
# PER-PROVIDER CREW FACTORY FUNCTIONS (Option A: Multiple Crews in Parallel)
# ============================================================================

def create_provider_agent(
    provider_name: str,
    llm: LLM
) -> Agent:
    """
    Create a single Agent for a specific flight provider.

    Args:
        provider_name: Provider name ("skyscanner", "kayak", "google_flights", "amadeus")
        llm: CrewAI LLM instance to use for this agent

    Returns:
        Agent configured for the specified provider

    Raises:
        ValueError: If provider_name is not recognized
    """
    # Map provider names to their respective search tools
    flight_tools = {
        FLIGHT_PROVIDER_SKYSCANNER: [search_skyscanner],
        FLIGHT_PROVIDER_KAYAK: [search_kayak],
        FLIGHT_PROVIDER_GOOGLE_FLIGHTS: [search_google_flights],
        FLIGHT_PROVIDER_AMADEUS: [search_amadeus]
    }

    if provider_name not in FLIGHT_PROVIDER_CONFIG:
        supported = ", ".join(FLIGHT_PROVIDER_CONFIG.keys())
        raise ValueError(f"Unknown provider '{provider_name}'. Supported: {supported}")

    config = FLIGHT_PROVIDER_CONFIG[provider_name].copy()
    config["tools"] = flight_tools.get(provider_name, [])

    agent = Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        tools=config["tools"],
        llm=llm,
        verbose=False,
        max_iter=1  # Single iteration to prevent retry loops and reduce LLM calls
    )

    return agent


def create_provider_task(
    agent: Agent,
    origin: str,
    destination: str,
    departure_date: str,
    passengers: int = 1
) -> Task:
    """
    Create a Task for a single provider agent.

    Args:
        agent: Agent to assign the task to
        origin: Departure airport code
        destination: Arrival airport code
        departure_date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers

    Returns:
        Task configured for the provider agent
    """
    # Extract provider name from agent role and get display name
    role = agent.role.lower()
    provider_key = None

    if FLIGHT_PROVIDER_SKYSCANNER in role:
        provider_key = FLIGHT_PROVIDER_SKYSCANNER
    elif FLIGHT_PROVIDER_KAYAK in role:
        provider_key = FLIGHT_PROVIDER_KAYAK
    elif FLIGHT_PROVIDER_GOOGLE_FLIGHTS in role:
        provider_key = FLIGHT_PROVIDER_GOOGLE_FLIGHTS
    elif FLIGHT_PROVIDER_AMADEUS in role:
        provider_key = FLIGHT_PROVIDER_AMADEUS

    provider_display_name = FLIGHT_PROVIDER_DISPLAY_NAMES.get(provider_key, "Unknown")

    task = Task(
        description=f"Search for {passengers} passenger(s) flight(s) from {origin} to {destination} on {departure_date} on {provider_display_name}. Return all available flights with prices, airlines, departure/arrival times, duration, stops, and booking URLs.",
        agent=agent,
        async_execution=False,  # Each crew runs independently, so no async_execution needed
        expected_output=f"A list of flights from {provider_display_name} with prices, airlines, departure/arrival times, and booking URLs"
    )

    return task


def create_provider_crew(
    provider_name: str,
    origin: str,
    destination: str,
    departure_date: str,
    passengers: int = 1,
    llm_config: Optional[Dict[str, Any]] = None
) -> Crew:
    """
    Create a complete Crew for a single flight provider.

    This factory creates an independent crew with:
    - 1 agent (specialized for the provider)
    - 1 task (search for flights on that provider)
    - Process.sequential (simple, single-task execution)

    Args:
        provider_name: Provider name ("skyscanner", "kayak", "google_flights", "amadeus")
        origin: Departure airport code
        destination: Arrival airport code
        departure_date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers
        llm_config: Optional dict with 'llm' key (LLM instance)
                   If not provided, creates LLM from environment variables

    Returns:
        CrewAI Crew configured for single-provider execution

    Raises:
        ValueError: If provider_name is invalid or API key is missing
    """
    from crewai import Crew, Process

    # Determine LLM to use
    if llm_config and "llm" in llm_config:
        llm = llm_config["llm"]
    else:
        # Create LLM from environment (default: google)
        provider = os.getenv("LLM_PROVIDER", "google")
        model = os.getenv("LLM_MODEL")
        api_key = None

        # Create LLM directly without unnecessary agent creation
        llm = create_llm(provider=provider, model=model, api_key=api_key)

    # Create agent and task for this provider
    agent = create_provider_agent(provider_name, llm)
    task = create_provider_task(agent, origin, destination, departure_date, passengers)

    # Create crew with single task (Process.sequential is simple and reliable)
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=False,  # Reduce verbosity to minimize processing overhead
        memory=False,
        process=Process.sequential  # Simple, single-task execution
    )

    return crew
