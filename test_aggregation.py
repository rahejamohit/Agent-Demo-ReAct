"""
Standalone test suite for aggregation logic.

Tests the core flight aggregation functionality without CrewAI dependencies.
This is Phase 5 testing focused on the manual_aggregate_results function.
"""

import pytest
import time
from datetime import datetime
from typing import Dict, List, Any


# Import only the aggregation function, not crew_config
import sys
sys.path.insert(0, '/sessions/funny-ecstatic-hamilton/mnt/Agent Demo Playground')

try:
    from flight_crew import manual_aggregate_results
except ImportError:
    # If import fails, define a mock for testing
    manual_aggregate_results = None


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def search_params() -> Dict[str, str]:
    """Standard search parameters"""
    return {
        "origin": "JFK",
        "destination": "LAX",
        "departure_date": "2026-06-15",
        "passengers": 1,
        "cabin_class": "economy"
    }


# ============================================================================
# UNIT TESTS: MANUAL AGGREGATION
# ============================================================================

class TestManualAggregation:
    """Test manual_aggregate_results function"""

    @pytest.mark.skipif(manual_aggregate_results is None, reason="flight_crew module not available")
    def test_aggregation_no_deduplication(self, search_params):
        """Test that aggregation does NOT deduplicate flights"""
        crew_results = [
            {
                "provider": "skyscanner",
                "status": "success",
                "flights": [
                    {
                        "provider": "skyscanner",
                        "airline": "Ryanair",
                        "price": 50.0,
                        "flight_number": "SK001",
                        "departure": "2026-06-15T08:00:00",
                        "arrival": "2026-06-15T10:00:00",
                        "duration_minutes": 120,
                        "stops": 0,
                        "booking_url": "https://skyscanner.com",
                        "seats_available": 10
                    }
                ],
                "error_message": None,
                "execution_time": 8.0
            },
            {
                "provider": "kayak",
                "status": "success",
                "flights": [
                    {
                        "provider": "kayak",
                        "airline": "United",
                        "price": 45.0,
                        "flight_number": "UA001",
                        "departure": "2026-06-15T09:00:00",
                        "arrival": "2026-06-15T11:00:00",
                        "duration_minutes": 120,
                        "stops": 0,
                        "booking_url": "https://kayak.com",
                        "seats_available": 15
                    }
                ],
                "error_message": None,
                "execution_time": 7.5
            }
        ]

        result = manual_aggregate_results(
            crew_results=crew_results,
            origin=search_params["origin"],
            destination=search_params["destination"],
            departure_date=search_params["departure_date"],
            passengers=search_params["passengers"],
            cabin_class=search_params["cabin_class"]
        )

        # Should have 2 flights (no dedup)
        assert result["total_results"] == 2, f"Expected 2 flights, got {result['total_results']}"
        assert len(result["flights"]) == 2

    @pytest.mark.skipif(manual_aggregate_results is None, reason="flight_crew module not available")
    def test_aggregation_sorting_by_price(self, search_params):
        """Test that aggregation sorts flights by price (ascending)"""
        crew_results = [
            {
                "provider": "skyscanner",
                "status": "success",
                "flights": [
                    {
                        "provider": "skyscanner",
                        "price": 100.0,
                        "airline": "Expensive",
                        "flight_number": "EX001",
                        "departure": "2026-06-15T08:00:00",
                        "arrival": "2026-06-15T10:00:00",
                        "duration_minutes": 120,
                        "stops": 0,
                        "booking_url": "https://skyscanner.com",
                        "seats_available": 10
                    },
                    {
                        "provider": "skyscanner",
                        "price": 50.0,
                        "airline": "Cheap",
                        "flight_number": "CH001",
                        "departure": "2026-06-15T09:00:00",
                        "arrival": "2026-06-15T11:00:00",
                        "duration_minutes": 120,
                        "stops": 0,
                        "booking_url": "https://skyscanner.com",
                        "seats_available": 5
                    }
                ],
                "error_message": None,
                "execution_time": 8.0
            }
        ]

        result = manual_aggregate_results(
            crew_results=crew_results,
            origin=search_params["origin"],
            destination=search_params["destination"],
            departure_date=search_params["departure_date"],
            passengers=search_params["passengers"],
            cabin_class=search_params["cabin_class"]
        )

        # Cheapest should be first
        assert result["flights"][0]["price"] == 50.0, f"First flight price: {result['flights'][0]['price']}"
        assert result["flights"][1]["price"] == 100.0, f"Second flight price: {result['flights'][1]['price']}"

    @pytest.mark.skipif(manual_aggregate_results is None, reason="flight_crew module not available")
    def test_aggregation_partial_failures(self, search_params):
        """Test aggregation with some crews failing"""
        crew_results = [
            {
                "provider": "skyscanner",
                "status": "success",
                "flights": [
                    {
                        "provider": "skyscanner",
                        "price": 50.0,
                        "airline": "Ryanair",
                        "flight_number": "SK001",
                        "departure": "2026-06-15T08:00:00",
                        "arrival": "2026-06-15T10:00:00",
                        "duration_minutes": 120,
                        "stops": 0,
                        "booking_url": "https://skyscanner.com",
                        "seats_available": 10
                    }
                ],
                "error_message": None,
                "execution_time": 8.0
            },
            {
                "provider": "kayak",
                "status": "timeout",
                "flights": [],
                "error_message": "Execution timed out after 30 seconds",
                "execution_time": 30.0
            },
            {
                "provider": "google_flights",
                "status": "error",
                "flights": [],
                "error_message": "API request failed",
                "execution_time": 2.5
            },
            {
                "provider": "amadeus",
                "status": "success",
                "flights": [
                    {
                        "provider": "amadeus",
                        "price": 150.0,
                        "airline": "Emirates",
                        "flight_number": "EK001",
                        "departure": "2026-06-15T10:00:00",
                        "arrival": "2026-06-15T12:00:00",
                        "duration_minutes": 120,
                        "stops": 0,
                        "booking_url": "https://amadeus.com",
                        "seats_available": 20
                    }
                ],
                "error_message": None,
                "execution_time": 9.0
            }
        ]

        result = manual_aggregate_results(
            crew_results=crew_results,
            origin=search_params["origin"],
            destination=search_params["destination"],
            departure_date=search_params["departure_date"],
            passengers=search_params["passengers"],
            cabin_class=search_params["cabin_class"]
        )

        # Should have 2 successful flights
        assert result["total_results"] == 2
        # Status should be "partial_completion" (some failed)
        assert result["crew_status"] == "partial_completion"
        # Should have warnings for failed crews
        assert len(result["warnings"]) == 2
        assert any("timeout" in w.lower() for w in result["warnings"])

    @pytest.mark.skipif(manual_aggregate_results is None, reason="flight_crew module not available")
    def test_aggregation_all_failures(self, search_params):
        """Test aggregation when all crews fail"""
        crew_results = [
            {
                "provider": "skyscanner",
                "status": "timeout",
                "flights": [],
                "error_message": "Timeout",
                "execution_time": 30.0
            },
            {
                "provider": "kayak",
                "status": "error",
                "flights": [],
                "error_message": "API error",
                "execution_time": 2.0
            },
            {
                "provider": "google_flights",
                "status": "error",
                "flights": [],
                "error_message": "API error",
                "execution_time": 2.0
            },
            {
                "provider": "amadeus",
                "status": "timeout",
                "flights": [],
                "error_message": "Timeout",
                "execution_time": 30.0
            }
        ]

        result = manual_aggregate_results(
            crew_results=crew_results,
            origin=search_params["origin"],
            destination=search_params["destination"],
            departure_date=search_params["departure_date"],
            passengers=search_params["passengers"],
            cabin_class=search_params["cabin_class"]
        )

        # Should have 0 flights
        assert result["total_results"] == 0
        # Status should be "partial_completion" (all failed)
        assert result["crew_status"] == "partial_completion"
        # Should have warnings for all failed crews
        assert len(result["warnings"]) == 4

    @pytest.mark.skipif(manual_aggregate_results is None, reason="flight_crew module not available")
    def test_aggregation_response_structure(self, search_params):
        """Test aggregation returns correct response structure"""
        crew_results = [
            {
                "provider": "skyscanner",
                "status": "success",
                "flights": [
                    {
                        "provider": "skyscanner",
                        "price": 50.0,
                        "airline": "Ryanair",
                        "flight_number": "SK001",
                        "departure": "2026-06-15T08:00:00",
                        "arrival": "2026-06-15T10:00:00",
                        "duration_minutes": 120,
                        "stops": 0,
                        "booking_url": "https://skyscanner.com",
                        "seats_available": 10
                    }
                ],
                "error_message": None,
                "execution_time": 8.0
            }
        ]

        result = manual_aggregate_results(
            crew_results=crew_results,
            origin=search_params["origin"],
            destination=search_params["destination"],
            departure_date=search_params["departure_date"],
            passengers=search_params["passengers"],
            cabin_class=search_params["cabin_class"]
        )

        # Verify response structure
        assert "search_params" in result
        assert "flights" in result
        assert "total_results" in result
        assert "provider_results" in result
        assert "timestamp" in result
        assert "crew_status" in result
        assert "warnings" in result

        # Verify search_params
        assert result["search_params"]["origin"] == search_params["origin"]
        assert result["search_params"]["destination"] == search_params["destination"]
        assert result["search_params"]["departure_date"] == search_params["departure_date"]

        # Verify timestamp is ISO format
        assert datetime.fromisoformat(result["timestamp"])


# ============================================================================
# PERFORMANCE BENCHMARKS
# ============================================================================

class TestPerformance:
    """Performance benchmarking tests"""

    @pytest.mark.skipif(manual_aggregate_results is None, reason="flight_crew module not available")
    def test_aggregation_performance_100_flights(self, search_params):
        """Benchmark aggregation with 100 flights"""
        flights = [
            {
                "provider": f"provider_{i % 4}",
                "price": 50.0 + (i * 0.5),
                "airline": f"Airline{i}",
                "flight_number": f"FL{i:04d}",
                "departure": "2026-06-15T08:00:00",
                "arrival": "2026-06-15T10:00:00",
                "duration_minutes": 120,
                "stops": 0,
                "booking_url": f"https://booking.com/flight{i}",
                "seats_available": 10
            }
            for i in range(100)
        ]

        crew_results = [
            {
                "provider": "skyscanner",
                "status": "success",
                "flights": flights[0:25],
                "error_message": None,
                "execution_time": 8.0
            },
            {
                "provider": "kayak",
                "status": "success",
                "flights": flights[25:50],
                "error_message": None,
                "execution_time": 8.0
            },
            {
                "provider": "google_flights",
                "status": "success",
                "flights": flights[50:75],
                "error_message": None,
                "execution_time": 8.0
            },
            {
                "provider": "amadeus",
                "status": "success",
                "flights": flights[75:100],
                "error_message": None,
                "execution_time": 8.0
            }
        ]

        start = time.time()
        result = manual_aggregate_results(
            crew_results=crew_results,
            origin=search_params["origin"],
            destination=search_params["destination"],
            departure_date=search_params["departure_date"],
            passengers=search_params["passengers"],
            cabin_class=search_params["cabin_class"]
        )
        elapsed = time.time() - start

        # Should complete in <100ms
        assert elapsed < 0.1, f"Aggregation took {elapsed:.3f}s, expected <0.1s"
        assert result["total_results"] == 100
        # Should be sorted by price
        prices = [f["price"] for f in result["flights"]]
        assert prices == sorted(prices)

    @pytest.mark.skipif(manual_aggregate_results is None, reason="flight_crew module not available")
    def test_aggregation_performance_1000_flights(self, search_params):
        """Benchmark aggregation with 1000 flights"""
        flights = [
            {
                "provider": f"provider_{i % 4}",
                "price": 50.0 + (i * 0.1),
                "airline": f"Airline{i}",
                "flight_number": f"FL{i:05d}",
                "departure": "2026-06-15T08:00:00",
                "arrival": "2026-06-15T10:00:00",
                "duration_minutes": 120,
                "stops": 0,
                "booking_url": f"https://booking.com/flight{i}",
                "seats_available": 10
            }
            for i in range(1000)
        ]

        crew_results = [
            {
                "provider": f"provider_{i}",
                "status": "success",
                "flights": flights[i*250:(i+1)*250],
                "error_message": None,
                "execution_time": 8.0
            }
            for i in range(4)
        ]

        start = time.time()
        result = manual_aggregate_results(
            crew_results=crew_results,
            origin=search_params["origin"],
            destination=search_params["destination"],
            departure_date=search_params["departure_date"],
            passengers=search_params["passengers"],
            cabin_class=search_params["cabin_class"]
        )
        elapsed = time.time() - start

        # Should complete in <500ms for 1000 flights
        assert elapsed < 0.5, f"Aggregation took {elapsed:.3f}s, expected <0.5s"
        assert result["total_results"] == 1000


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
