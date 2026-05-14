"""
Example usage of the Flight Price Aggregator API
This demonstrates how to interact with the API programmatically
"""

import requests
import json
from datetime import datetime, timedelta


# API Configuration
API_BASE_URL = "http://localhost:8080"
API_V1 = f"{API_BASE_URL}/api/v1"


class FlightAPIClient:
    """Simple client for the Flight API"""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.api_v1 = f"{base_url}/api/v1"

    def search_flights(self, origin: str, destination: str, departure_date: str,
                      passengers: int = 1, cabin_class: str = "economy",
                      return_date: str = None) -> dict:
        """Search for flights"""
        url = f"{self.api_v1}/flights/search"

        payload = {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "passengers": passengers,
            "cabin_class": cabin_class
        }

        if return_date:
            payload["return_date"] = return_date

        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_flight_details(self, flight_id: str) -> dict:
        """Get details for a specific flight"""
        url = f"{self.api_v1}/flights/{flight_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_search_history(self) -> dict:
        """Get search history"""
        url = f"{self.api_v1}/flights/history"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def batch_search(self, searches: list) -> dict:
        """Perform batch searches"""
        url = f"{self.api_v1}/flights/batch-search"
        response = requests.post(url, json=searches)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict:
        """Check API health"""
        url = f"{self.base_url}/health"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


def main():
    """Example usage"""
    print("=" * 70)
    print("Flight Price Aggregator API - Example Usage")
    print("=" * 70)
    print()

    client = FlightAPIClient()

    # 1. Health Check
    print("1️⃣  Health Check")
    print("-" * 70)
    try:
        health = client.health_check()
        print(f"✅ API Status: {health['status']}")
        print(f"   Version: {health['version']}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure the API is running on http://localhost:8080")
        return

    # 2. Single Flight Search
    print("2️⃣  Single Flight Search")
    print("-" * 70)
    try:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        result = client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=tomorrow,
            passengers=1,
            cabin_class="economy"
        )

        print(f"Search Parameters:")
        print(f"  Origin: {result['search_params']['origin']}")
        print(f"  Destination: {result['search_params']['destination']}")
        print(f"  Date: {result['search_params']['departure_date']}")
        print()

        print(f"Results: Found {result['total_results']} flights")
        print()

        # Show cheapest 3 flights
        for i, flight in enumerate(result['flights'][:3], 1):
            print(f"  Flight #{i}")
            print(f"    Provider: {flight['provider']}")
            print(f"    Airline: {flight['airline']} {flight['flight_number']}")
            print(f"    Departure: {flight['departure']}")
            print(f"    Arrival: {flight['arrival']}")
            print(f"    Duration: {flight['duration_minutes']} min | Stops: {flight['stops']}")
            print(f"    Price: ${flight['price']}")
            print(f"    Book: {flight['provider_url']}")
            print()

    except Exception as e:
        print(f"❌ Error: {e}")

    # 3. Get Flight Details
    print("3️⃣  Get Flight Details")
    print("-" * 70)
    try:
        if result['total_results'] > 0:
            flight_id = result['flights'][0]['id']
            flight_detail = client.get_flight_details(flight_id)

            print(f"Flight ID: {flight_detail['id']}")
            print(f"Provider: {flight_detail['provider']}")
            print(f"Price: ${flight_detail['price']} {flight_detail['currency']}")
            print(f"Seats Available: {flight_detail['seat_available']}")
            print(f"Booking Link: {flight_detail['provider_url']}")
            print()
    except Exception as e:
        print(f"❌ Error: {e}")

    # 4. Batch Search
    print("4️⃣  Batch Search (Multiple Routes)")
    print("-" * 70)
    try:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        searches = [
            {
                "origin": "JFK",
                "destination": "LAX",
                "departure_date": tomorrow,
                "passengers": 1,
                "cabin_class": "economy"
            },
            {
                "origin": "LAX",
                "destination": "SFO",
                "departure_date": next_week,
                "passengers": 2,
                "cabin_class": "economy"
            }
        ]

        batch_result = client.batch_search(searches)

        print(f"Batch Search Results:")
        print(f"  Requested: {batch_result['total_batches']} routes")
        print(f"  Successful: {batch_result['successful']} routes")
        print()

        for route, data in batch_result['results'].items():
            print(f"  {route}: {data['total_results']} flights")

        print()

    except Exception as e:
        print(f"❌ Error: {e}")

    # 5. Search History
    print("5️⃣  Search History")
    print("-" * 70)
    try:
        history = client.get_search_history()

        print(f"Recent Searches: {len(history['searches'])}")
        for i, search in enumerate(history['searches'][-3:], 1):
            params = search['params']
            print(f"  {i}. {params['origin']} → {params['destination']} "
                  f"({params['departure_date']}) - "
                  f"{search['results_count']} results")

        print()

    except Exception as e:
        print(f"❌ Error: {e}")

    print("=" * 70)
    print("Example completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
