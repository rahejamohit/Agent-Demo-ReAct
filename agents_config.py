"""
Tool definitions for Claude API ReAct agents
"""

# Flight Search Tools for each provider
FLIGHT_SEARCH_TOOLS = {
    "skyscanner": {
        "name": "search_skyscanner",
        "description": "Search flights on Skyscanner for given route and dates. Returns available flights with prices.",
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "IATA code for departure airport (e.g., JFK)"
                },
                "destination": {
                    "type": "string",
                    "description": "IATA code for arrival airport (e.g., LAX)"
                },
                "departure_date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format"
                },
                "passengers": {
                    "type": "integer",
                    "description": "Number of passengers",
                    "default": 1
                }
            },
            "required": ["origin", "destination", "departure_date"]
        }
    },
    "kayak": {
        "name": "search_kayak",
        "description": "Search flights on Kayak. Returns cheapest and best-rated flights.",
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "IATA code for departure airport"
                },
                "destination": {
                    "type": "string",
                    "description": "IATA code for arrival airport"
                },
                "departure_date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format"
                },
                "passengers": {
                    "type": "integer",
                    "description": "Number of passengers",
                    "default": 1
                }
            },
            "required": ["origin", "destination", "departure_date"]
        }
    },
    "google_flights": {
        "name": "search_google_flights",
        "description": "Search flights on Google Flights. Returns flights with flexible date options.",
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "IATA code for departure airport"
                },
                "destination": {
                    "type": "string",
                    "description": "IATA code for arrival airport"
                },
                "departure_date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format"
                },
                "passengers": {
                    "type": "integer",
                    "description": "Number of passengers",
                    "default": 1
                }
            },
            "required": ["origin", "destination", "departure_date"]
        }
    },
    "amadeus": {
        "name": "search_amadeus",
        "description": "Search flights on Amadeus. Returns comprehensive flight inventory with ancillaries.",
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "IATA code for departure airport"
                },
                "destination": {
                    "type": "string",
                    "description": "IATA code for arrival airport"
                },
                "departure_date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format"
                },
                "passengers": {
                    "type": "integer",
                    "description": "Number of passengers",
                    "default": 1
                }
            },
            "required": ["origin", "destination", "departure_date"]
        }
    }
}

# Agent configurations
AGENT_CONFIG = {
    "skyscanner": {
        "name": "Skyscanner Agent",
        "provider": "skyscanner",
        "description": "Searches Skyscanner for flight deals and price comparisons",
        "api_base_url": "https://skyscanner-api.p.rapidapi.com",
        "timeout": 10
    },
    "kayak": {
        "name": "Kayak Agent",
        "provider": "kayak",
        "description": "Searches Kayak for best prices and ratings",
        "api_base_url": "https://kayak-api.p.rapidapi.com",
        "timeout": 10
    },
    "google_flights": {
        "name": "Google Flights Agent",
        "provider": "google_flights",
        "description": "Searches Google Flights for comprehensive options",
        "api_base_url": "https://google-flights-api.p.rapidapi.com",
        "timeout": 10
    },
    "amadeus": {
        "name": "Amadeus Agent",
        "provider": "amadeus",
        "description": "Searches Amadeus for enterprise-grade flight data",
        "api_base_url": "https://api.amadeus.com",
        "timeout": 10
    }
}

# System prompt for ReAct agents
AGENT_SYSTEM_PROMPT = """You are a specialized flight search agent using the ReAct (Reasoning + Acting) pattern.

Your role:
1. REASON: Understand the flight search requirements
2. ACT: Use available tools to search flights
3. OBSERVE: Analyze the results
4. REPEAT: Refine search if needed

Guidelines:
- Always extract and use the provided origin, destination, and departure_date
- Handle multiple passengers appropriately
- For missing information, make reasonable assumptions
- Return structured JSON with flight results
- Include booking URLs from the provider
- Sort results by price (cheapest first)
- Always provide flight details: price, duration, airline, stops, departure/arrival times

When you have results, format them as JSON with this structure:
{
    "provider": "provider_name",
    "flights": [
        {
            "airline": "Airline Name",
            "flight_number": "XX123",
            "departure": "2026-06-15T08:00:00",
            "arrival": "2026-06-15T11:30:00",
            "duration_minutes": 210,
            "stops": 0,
            "price": 245.99,
            "currency": "USD",
            "booking_url": "https://provider.com/book/...",
            "seats_available": 5
        }
    ],
    "search_params": {
        "origin": "JFK",
        "destination": "LAX",
        "departure_date": "2026-06-15",
        "passengers": 1
    }
}
"""

# Provider-specific prompts
PROVIDER_PROMPTS = {
    "skyscanner": """You are the Skyscanner Flight Search Agent.
Your specialty: Finding flight deals and price comparisons across multiple carriers.
Always look for flexible date options and alert if prices might drop soon.
Focus on: Budget airlines and alternative airports near the destination.""",

    "kayak": """You are the Kayak Flight Search Agent.
Your specialty: Finding best prices and high-rated flights.
Always consider traveler ratings and reviews.
Focus on: Value for money and customer satisfaction scores.""",

    "google_flights": """You are the Google Flights Search Agent.
Your specialty: Comprehensive flight options with flexible date matrix.
Always show price trends and flexible date options.
Focus on: Price trends over time and alternative dates.""",

    "amadeus": """You are the Amadeus Flight Search Agent.
Your specialty: Enterprise-grade flight inventory with ancillary services.
Always include seat availability and additional services.
Focus on: Premium options and ancillary revenue products (seats, baggage, etc)."""
}
