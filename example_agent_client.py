"""
Example client for the Flight Price Aggregator Agent System
Demonstrates how to interact with the ReAct agent-based API
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List


class FlightAgentClient:
    """Client for the Flight Price Aggregator Agent System"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.api_v2 = f"{base_url}/api/v2"

    def search_flights(self, origin: str, destination: str,
                      departure_date: str, passengers: int = 1,
                      cabin_class: str = "economy") -> Dict:
        """
        Search flights using ReAct agents

        Args:
            origin: Departure airport IATA code
            destination: Arrival airport IATA code
            departure_date: Travel date (YYYY-MM-DD)
            passengers: Number of passengers
            cabin_class: Cabin class (economy, business, first)

        Returns:
            Aggregated flight results from all agents
        """
        url = f"{self.api_v2}/agents/search"

        payload = {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "passengers": passengers,
            "cabin_class": cabin_class
        }

        print(f"\n🤖 Sending search request to agents...")
        print(f"   Route: {origin} → {destination}")
        print(f"   Date: {departure_date}")
        print(f"   Passengers: {passengers}")
        print(f"   Cabin: {cabin_class}")
        print()

        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()

        return response.json()

    def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        url = f"{self.api_v2}/agents/status"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def display_results(self, results: Dict):
        """Display search results in a nice format"""
        print("=" * 80)
        print("✈️  FLIGHT SEARCH RESULTS (ReAct Agent System)")
        print("=" * 80)
        print()

        search_params = results.get("search_params", {})
        print(f"Search Parameters:")
        print(f"  Route: {search_params.get('origin')} → {search_params.get('destination')}")
        print(f"  Date: {search_params.get('departure_date')}")
        print(f"  Passengers: {search_params.get('passengers')}")
        print()

        flights = results.get("flights", [])
        total = results.get("total_results", 0)

        print(f"📊 Total Results: {total} flights from all providers")
        print()

        if not flights:
            print("❌ No flights found")
            return

        # Group by provider
        flights_by_provider = {}
        for flight in flights:
            provider = flight.get("provider", "unknown")
            if provider not in flights_by_provider:
                flights_by_provider[provider] = []
            flights_by_provider[provider].append(flight)

        # Display summary by provider
        print("📈 Flights by Provider:")
        print("-" * 80)
        for provider, prov_flights in flights_by_provider.items():
            cheapest = min(prov_flights, key=lambda x: x.get("price", float('inf')))
            print(f"\n{provider.upper()}")
            print(f"  Total: {len(prov_flights)} flights")
            print(f"  Cheapest: ${cheapest.get('price')} ({cheapest.get('airline')})")

        # Display top 5 cheapest flights overall
        print()
        print("=" * 80)
        print("💰 TOP 5 CHEAPEST FLIGHTS (All Providers)")
        print("=" * 80)
        print()

        for i, flight in enumerate(flights[:5], 1):
            self._display_flight(flight, i)

    def _display_flight(self, flight: Dict, number: int = 1):
        """Display a single flight"""
        departure = flight.get("departure", "")
        arrival = flight.get("arrival", "")

        try:
            dep_time = datetime.fromisoformat(departure).strftime("%H:%M")
            arr_time = datetime.fromisoformat(arrival).strftime("%H:%M")
        except:
            dep_time = departure
            arr_time = arrival

        duration_mins = flight.get("duration_minutes", 0)
        hours = duration_mins // 60
        mins = duration_mins % 60
        duration_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

        stops = flight.get("stops", 0)
        stops_str = "Non-stop" if stops == 0 else f"{stops} stop" if stops == 1 else f"{stops} stops"

        print(f"Flight #{number}")
        print(f"  Provider: {flight.get('provider', 'Unknown').upper()}")
        print(f"  Airline: {flight.get('airline')} {flight.get('flight_number')}")
        print(f"  Time: {dep_time} - {arr_time} ({duration_str}, {stops_str})")
        print(f"  Price: ${flight.get('price'):.2f} {flight.get('currency', 'USD')}")
        print(f"  Seats: {flight.get('seats_available', 'N/A')} available")
        print(f"  Book: {flight.get('booking_url', 'N/A')}")
        print()

    def display_agent_status(self, status: Dict):
        """Display agent status"""
        print("=" * 80)
        print("🤖 AGENT SYSTEM STATUS")
        print("=" * 80)
        print()

        print(f"System: {status.get('system')}")
        print(f"API Key: {'✅ Configured' if status.get('api_key_configured') else '❌ Not configured'}")
        print()

        print("Agents:")
        print("-" * 80)
        for agent in status.get("agents", []):
            print(f"\n{agent.get('agent')}")
            print(f"  Provider: {agent.get('provider')}")
            print(f"  Model: {agent.get('model')}")
            print(f"  Status: {agent.get('status').upper()}")
            print(f"  Max Iterations: {agent.get('max_iterations')}")
            print(f"  Description: {agent.get('description')}")

        print()


def main():
    """Example usage"""
    print("\n")
    print("🚀 Flight Price Aggregator - Agent System Example")
    print("=" * 80)
    print()

    client = FlightAgentClient()

    # 1. Check agent status
    print("1️⃣  Checking agent system status...")
    print("-" * 80)
    try:
        status = client.get_agent_status()
        client.display_agent_status(status)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure the API is running: python main_agents.py")
        return

    input("Press Enter to continue with flight search...")

    # 2. Search flights
    print("\n2️⃣  Searching flights with ReAct agents...")
    print("-" * 80)

    try:
        # Get tomorrow's date for search
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        # Search flights
        results = client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=tomorrow,
            passengers=1,
            cabin_class="economy"
        )

        # Display results
        client.display_results(results)

        # 3. Show provider breakdown
        print("\n3️⃣  Provider Breakdown")
        print("-" * 80)

        provider_results = results.get("provider_results", {})
        for provider, data in provider_results.items():
            if "error" in data:
                print(f"❌ {provider.upper()}: {data['error']}")
            else:
                print(f"✅ {provider.upper()}: {data.get('total_results', 0)} flights")

        # 4. Calculate statistics
        print("\n4️⃣  Statistics")
        print("-" * 80)

        flights = results.get("flights", [])
        if flights:
            prices = [f.get("price", 0) for f in flights]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)

            print(f"Min Price: ${min_price:.2f}")
            print(f"Max Price: ${max_price:.2f}")
            print(f"Avg Price: ${avg_price:.2f}")
            print(f"Price Range: ${max_price - min_price:.2f}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure ANTHROPIC_API_KEY is set: export ANTHROPIC_API_KEY=sk-ant-...")

    print("\n")
    print("=" * 80)
    print("✨ Example completed!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
