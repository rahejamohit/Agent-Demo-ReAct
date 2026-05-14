"""
Flight service layer for fetching and aggregating flight data
"""
import random
from datetime import datetime, timedelta
from typing import Optional
from models import Flight, FlightSearch, FlightSearchResponse, FlightProvider
import uuid


class FlightService:
    """Service for managing flight searches and data"""

    def __init__(self):
        """Initialize the flight service with in-memory storage"""
        self.flights_cache = {}
        self.search_history = []

    def search_flights(self, search: FlightSearch) -> FlightSearchResponse:
        """
        Search for flights across multiple providers

        Args:
            search: FlightSearch parameters

        Returns:
            FlightSearchResponse with matching flights
        """
        # Generate flights from multiple providers
        flights = []

        # Fetch from each provider (mock implementation)
        providers = [
            FlightProvider.SKYSCANNER,
            FlightProvider.KAYAK,
            FlightProvider.GOOGLE_FLIGHTS,
            FlightProvider.EXPEDIA
        ]

        for provider in providers:
            provider_flights = self._fetch_from_provider(search, provider)
            flights.extend(provider_flights)

        # Sort by price
        flights.sort(key=lambda x: x.price)

        # Store in cache
        search_id = str(uuid.uuid4())
        self.flights_cache[search_id] = flights

        # Record search
        self.search_history.append({
            "search_id": search_id,
            "params": search,
            "timestamp": datetime.now(),
            "results_count": len(flights)
        })

        response = FlightSearchResponse(
            search_params=search,
            flights=flights,
            total_results=len(flights),
            timestamp=datetime.now()
        )

        return response

    def _fetch_from_provider(self, search: FlightSearch, provider: FlightProvider) -> list[Flight]:
        """
        Fetch flights from a specific provider (mock implementation)

        Args:
            search: FlightSearch parameters
            provider: Flight provider to fetch from

        Returns:
            List of Flight objects
        """
        flights = []

        # Parse departure date
        departure_date = datetime.strptime(search.departure_date, "%Y-%m-%d")

        # Generate 3-5 mock flights per provider
        num_flights = random.randint(3, 5)

        airlines = ["Delta", "United", "American", "Southwest", "JetBlue", "Alaska"]

        for i in range(num_flights):
            # Randomize departure time within the day
            departure_hour = random.randint(6, 22)
            departure = departure_date.replace(hour=departure_hour, minute=random.choice([0, 15, 30, 45]))

            # Duration varies by route (mock)
            duration_minutes = random.randint(180, 480)
            arrival = departure + timedelta(minutes=duration_minutes)

            # Stops and price correlation
            stops = random.randint(0, 2)
            base_price = 150 + (stops * 50)  # More stops = more expensive
            price = base_price + random.uniform(-30, 100)

            flight = Flight(
                id=f"{provider.value}_{search.origin}_{search.destination}_{i}_{uuid.uuid4().hex[:8]}",
                provider=provider,
                provider_url=self._generate_provider_url(search, provider),
                origin=search.origin,
                destination=search.destination,
                departure=departure,
                arrival=arrival,
                duration_minutes=duration_minutes,
                stops=stops,
                airline=random.choice(airlines),
                flight_number=f"{random.choice('ABCDEFGH')}{random.randint(100, 999)}",
                price=round(price, 2),
                currency="USD",
                seat_available=random.randint(1, 20)
            )
            flights.append(flight)

        return flights

    def _generate_provider_url(self, search: FlightSearch, provider: FlightProvider) -> str:
        """Generate booking URL for a provider"""
        base_urls = {
            FlightProvider.SKYSCANNER: "https://www.skyscanner.com/transport/flights",
            FlightProvider.KAYAK: "https://www.kayak.com/flights",
            FlightProvider.GOOGLE_FLIGHTS: "https://www.google.com/travel/flights",
            FlightProvider.EXPEDIA: "https://www.expedia.com/flights",
            FlightProvider.BOOKING: "https://www.booking.com/flights"
        }

        base_url = base_urls.get(provider, "https://www.example.com")

        return (f"{base_url}?"
                f"origin={search.origin}&"
                f"destination={search.destination}&"
                f"date={search.departure_date}&"
                f"passengers={search.passengers}&"
                f"cabin={search.cabin_class}")

    def get_flight_details(self, flight_id: str) -> Optional[Flight]:
        """Get details for a specific flight"""
        for flights in self.flights_cache.values():
            for flight in flights:
                if flight.id == flight_id:
                    return flight
        return None

    def get_search_history(self) -> list[dict]:
        """Get recent search history"""
        return self.search_history[-10:]  # Last 10 searches

    def clear_cache(self):
        """Clear the flight cache"""
        self.flights_cache.clear()
        self.search_history.clear()


# Global service instance
flight_service = FlightService()
