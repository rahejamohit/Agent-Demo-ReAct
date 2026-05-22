"""
Constants for Flight Price Aggregator System
Centralized definitions for flight provider names and configurations
"""

# ============================================================================
# FLIGHT PROVIDER NAMES (Use these constants instead of hardcoded strings)
# ============================================================================

FLIGHT_PROVIDER_SKYSCANNER = "skyscanner"
FLIGHT_PROVIDER_KAYAK = "kayak"
FLIGHT_PROVIDER_GOOGLE_FLIGHTS = "google_flights"
FLIGHT_PROVIDER_AMADEUS = "amadeus"

# List of all available flight providers
FLIGHT_PROVIDERS = [
    FLIGHT_PROVIDER_SKYSCANNER,
    FLIGHT_PROVIDER_KAYAK,
    FLIGHT_PROVIDER_GOOGLE_FLIGHTS,
    FLIGHT_PROVIDER_AMADEUS,
]

# Provider display names (human-readable)
FLIGHT_PROVIDER_DISPLAY_NAMES = {
    FLIGHT_PROVIDER_SKYSCANNER: "Skyscanner",
    FLIGHT_PROVIDER_KAYAK: "Kayak",
    FLIGHT_PROVIDER_GOOGLE_FLIGHTS: "Google Flights",
    FLIGHT_PROVIDER_AMADEUS: "Amadeus",
}

# Airlines by provider (used for mock data generation)
AIRLINES_BY_PROVIDER = {
    FLIGHT_PROVIDER_SKYSCANNER: ["Ryanair", "EasyJet", "Wizz Air", "Southwest", "Spirit"],
    FLIGHT_PROVIDER_KAYAK: ["United", "Delta", "American", "Southwest", "JetBlue"],
    FLIGHT_PROVIDER_GOOGLE_FLIGHTS: ["Lufthansa", "KLM", "Air France", "Turkish", "Emirates"],
    FLIGHT_PROVIDER_AMADEUS: ["British Airways", "Lufthansa", "Singapore Airlines", "Qatar", "ANA"]
}
