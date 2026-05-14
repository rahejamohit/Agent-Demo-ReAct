# Flight Price Aggregator API

A production-grade FastAPI backend for fetching and aggregating flight prices from multiple booking providers.

## Architecture

```
FastAPI Application
├── main.py              # FastAPI app with endpoints
├── models.py            # Pydantic models & schemas
├── flight_service.py    # Service layer (business logic)
└── requirements.txt     # Dependencies
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python main.py
```

The API will be available at **http://localhost:8080**

### 3. Access Interactive Documentation
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## API Endpoints

### Health & Status
- `GET /health` - Health check endpoint
- `GET /` - API info and documentation links

### Flight Search
- `POST /api/v1/flights/search` - Search flights
- `GET /api/v1/flights/{flight_id}` - Get flight details
- `GET /api/v1/flights/history` - Get search history
- `POST /api/v1/flights/batch-search` - Batch search multiple routes

### Admin
- `POST /api/v1/admin/cache-clear` - Clear flight cache (admin_key required)

## Usage Examples

### Search Flights
```bash
curl -X POST "http://localhost:8080/api/v1/flights/search" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "JFK",
    "destination": "LAX",
    "departure_date": "2026-06-15",
    "passengers": 1,
    "cabin_class": "economy"
  }'
```

### Response Example
```json
{
  "search_params": {
    "origin": "JFK",
    "destination": "LAX",
    "departure_date": "2026-06-15",
    "passengers": 1,
    "cabin_class": "economy"
  },
  "flights": [
    {
      "id": "skyscanner_JFK_LAX_0_a1b2c3d4",
      "provider": "skyscanner",
      "provider_url": "https://www.skyscanner.com/transport/flights?origin=JFK&destination=LAX&date=2026-06-15&passengers=1&cabin=economy",
      "origin": "JFK",
      "destination": "LAX",
      "departure": "2026-06-15T08:30:00",
      "arrival": "2026-06-15T11:45:00",
      "duration_minutes": 315,
      "stops": 0,
      "airline": "Delta",
      "flight_number": "DL123",
      "price": 245.99,
      "currency": "USD",
      "seat_available": 12
    }
  ],
  "total_results": 12,
  "timestamp": "2026-05-13T10:30:00"
}
```

### Batch Search Multiple Routes
```bash
curl -X POST "http://localhost:8080/api/v1/flights/batch-search" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "origin": "JFK",
      "destination": "LAX",
      "departure_date": "2026-06-15",
      "passengers": 1,
      "cabin_class": "economy"
    },
    {
      "origin": "LAX",
      "destination": "SFO",
      "departure_date": "2026-06-20",
      "passengers": 1,
      "cabin_class": "economy"
    }
  ]'
```

## Key Features

✅ **Multi-Provider Aggregation** - Searches across Skyscanner, Kayak, Google Flights, Expedia  
✅ **Price Sorting** - Results automatically sorted by price  
✅ **Direct Booking Links** - Each flight includes provider booking URL  
✅ **Batch Operations** - Process multiple searches in one request  
✅ **Search History** - Track recent searches  
✅ **CORS Enabled** - Ready for frontend integration  
✅ **Interactive API Docs** - Auto-generated Swagger UI  
✅ **Structured Logging** - Monitoring-ready logs  
✅ **Error Handling** - Comprehensive error responses  

## Project Integration

This backend is designed for the **Flight Price Agentic System**:

1. **Agent** fetches flights via REST API
2. **Service** aggregates from multiple providers
3. **Frontend** displays results with booking links

## Configuration

### Environment Variables (future)
```
SKYSCANNER_API_KEY=xxx
KAYAK_API_KEY=xxx
CORS_ORIGINS=["http://localhost:3000"]
ADMIN_KEY=secure-key
```

### CORS Configuration
Currently set to allow all origins (`allow_origins=["*"]`). For production:

```python
allow_origins=[
    "http://localhost:3000",
    "https://yourdomain.com"
]
```

## Next Steps

1. **Replace Mock Data** - Integrate real flight search APIs
2. **Add Database** - Replace in-memory cache with PostgreSQL
3. **Authentication** - Implement API key or OAuth
4. **Caching Strategy** - Add Redis for distributed caching
5. **Rate Limiting** - Implement request throttling
6. **Monitoring** - Add Prometheus metrics
7. **Deployment** - Deploy to Docker/Kubernetes

## Development

### Code Structure Best Practices
- **Models** (`models.py`) - Type definitions and validation
- **Service** (`flight_service.py`) - Business logic
- **API** (`main.py`) - HTTP handlers and routes

### Testing (future)
```bash
pytest tests/
```

### Linting
```bash
black .
flake8 .
```

## Performance Notes

- In-memory cache suitable for prototyping
- Production deployments should use Redis or database caching
- Current mock data generates ~12-20 results per search
- Consider implementing pagination for large result sets

## License

Internal League Flight System

## Support

For issues or questions, contact the backend team.
