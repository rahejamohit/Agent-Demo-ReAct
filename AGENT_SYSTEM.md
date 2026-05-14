# Flight Price Aggregator - Agent System (v2.0)

## 🤖 ReAct Pattern with Multi-Agent Architecture

This is a production-grade multi-agent system using the **ReAct (Reasoning + Acting)** design pattern to intelligently fetch flight prices from multiple providers.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│              /api/v2/agents/search endpoint                │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│            Agent Orchestrator (Coordinator)                 │
│  - Manages all agents                                       │
│  - Parallelizes requests (future enhancement)              │
│  - Aggregates & deduplicates results                        │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
    ┌────────┐        ┌────────┐        ┌────────┐
    │Skyscan-│        │ Kayak  │        │Google  │
    │ner Ag. │        │ Agent  │        │Flights │
    └────────┘        └────────┘        │ Agent  │
       │                 │                └────────┘
       └─────────────────┴──────────────────┘
                        │
                ReAct Loop (Reason→Act→Observe)
                        │
        ┌──────────────┬─────────────┐
        ▼              ▼              ▼
    Tool Use:    Tool Use:      Tool Use:
    search_      search_        search_
    skyscanner   kayak          google_flights
```

---

## 🚀 Quick Start

### 1. Set Up API Key

```bash
# Get your Anthropic API key from https://console.anthropic.com
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Agent System

```bash
python main_agents.py
```

You'll see:
```
🚀 Starting Flight Price Aggregator - Agent System
📍 URL: http://localhost:8080
📚 Docs: http://localhost:8080/docs
🤖 Pattern: ReAct (Reasoning + Acting)
```

### 4. Search Flights

Visit http://localhost:8080/docs and use the **Try it Out** button on `/api/v2/agents/search`:

```json
{
  "origin": "JFK",
  "destination": "LAX",
  "departure_date": "2026-06-15",
  "passengers": 1,
  "cabin_class": "economy"
}
```

---

## 🧠 How ReAct Pattern Works

Each agent follows the **Reason → Act → Observe → Repeat** cycle:

### 1. **REASON** 🤔
Agent analyzes the flight search request:
- Understands the origin, destination, date, passengers
- Determines what data is needed
- Plans the API call

### 2. **ACT** 🛠️
Agent uses the appropriate tool:
```
Tool: search_skyscanner
Input: {
  "origin": "JFK",
  "destination": "LAX",
  "departure_date": "2026-06-15",
  "passengers": 1
}
```

### 3. **OBSERVE** 👀
Agent receives results and analyzes them:
```
Results: 12 flights from Skyscanner
- Cheapest: $245.99 (Delta, non-stop)
- Best rated: $298 (United, good reviews)
```

### 4. **REPEAT** 🔄
If needed, agent can:
- Refine search parameters
- Ask for additional data
- Return final results

---

## 🎯 Specialized Agents

### Skyscanner Agent
- **Specialty**: Flight deals and price comparisons
- **Focus**: Budget airlines, alternative airports
- **Strength**: Finding best prices across carriers

### Kayak Agent
- **Specialty**: Best prices + high-rated flights
- **Focus**: Value for money and customer satisfaction
- **Strength**: Traveler reviews and ratings

### Google Flights Agent
- **Specialty**: Comprehensive options with flexibility
- **Focus**: Price trends and alternative dates
- **Strength**: Flexible date matrix and trends

### Amadeus Agent
- **Specialty**: Enterprise-grade inventory
- **Focus**: Premium options and ancillaries
- **Strength**: Seat availability, baggage, seat selection

---

## 📡 API Endpoints

### Search with Agents (v2)
```
POST /api/v2/agents/search
```

**Request:**
```json
{
  "origin": "JFK",
  "destination": "LAX",
  "departure_date": "2026-06-15",
  "passengers": 1,
  "cabin_class": "economy"
}
```

**Response:**
```json
{
  "search_params": {
    "origin": "JFK",
    "destination": "LAX",
    "departure_date": "2026-06-15",
    "passengers": 1
  },
  "flights": [
    {
      "provider": "skyscanner",
      "airline": "Delta",
      "flight_number": "DL123",
      "departure": "2026-06-15T08:00:00",
      "arrival": "2026-06-15T11:30:00",
      "duration_minutes": 330,
      "stops": 0,
      "price": 245.99,
      "currency": "USD",
      "booking_url": "https://skyscanner.com/...",
      "seats_available": 12
    }
  ],
  "total_results": 48,
  "provider_results": {
    "skyscanner": { "flights": [...], "total_results": 12 },
    "kayak": { "flights": [...], "total_results": 15 },
    "google_flights": { "flights": [...], "total_results": 14 },
    "amadeus": { "flights": [...], "total_results": 7 }
  },
  "timestamp": "2026-05-14T10:30:00"
}
```

### Agent Status
```
GET /api/v2/agents/status
```

**Response:**
```json
{
  "system": "ReAct Agent System",
  "agents": [
    {
      "agent": "Skyscanner Agent",
      "provider": "skyscanner",
      "model": "claude-3-5-sonnet-20241022",
      "status": "ready",
      "max_iterations": 5,
      "description": "Searches Skyscanner for flight deals"
    }
  ],
  "timestamp": "2026-05-14T10:30:00",
  "api_key_configured": true
}
```

---

## 🔧 Implementation Details

### Tool Definitions
Each agent has access to a specialized search tool:

```python
Tool: search_skyscanner {
  "origin": str,          # IATA code
  "destination": str,     # IATA code
  "departure_date": str,  # YYYY-MM-DD
  "passengers": int       # 1-9
}
```

### Claude API Model
- **Model**: `claude-3-5-sonnet-20241022`
- **Max Tokens**: 1024 per iteration
- **Tool Use**: Enabled for intelligent API calls
- **System Prompts**: Specialized per agent

### Iteration Loop
- **Max Iterations**: 5 per search
- **Stop Conditions**: 
  - Agent finishes reasoning (`end_turn`)
  - Agent uses tool (`tool_use`)
  - Max iterations reached

---

## 🔌 Real API Integration

### Current Status
- ✅ Agent framework fully implemented
- ✅ Tool use patterns established
- ⏳ Mock data generators in place
- ⏳ Ready for real API integration

### To Add Real APIs

Replace mock data calls in `flight_agents.py`:

```python
def _call_flight_api(self, tool_name: str, ...):
    # Mock data (remove this)
    # flights = self._generate_mock_flights(...)
    
    # Real API (add this)
    if self.provider == "skyscanner":
        flights = self._call_skyscanner_api(origin, destination, departure_date)
    elif self.provider == "kayak":
        flights = self._call_kayak_api(origin, destination, departure_date)
    # ...
    
    return {"status": "success", "flights": flights}
```

### Supported Real APIs

1. **Skyscanner API** (RapidAPI)
   - Base URL: `https://skyscanner-api.p.rapidapi.com`
   - Requires: API key + headers

2. **Amadeus API** (Enterprise)
   - Base URL: `https://api.amadeus.com`
   - Requires: OAuth token

3. **Google Flights API** (RapidAPI)
   - Base URL: `https://google-flights-api.p.rapidapi.com`
   - Requires: API key

4. **Kayak API** (RapidAPI)
   - Base URL: `https://kayak-api.p.rapidapi.com`
   - Requires: API key

---

## 📊 Request Flow

```
1. User sends search request
   POST /api/v2/agents/search
   {origin: "JFK", destination: "LAX", ...}
   
2. Orchestrator initializes all agents
   - Skyscanner Agent
   - Kayak Agent
   - Google Flights Agent
   - Amadeus Agent
   
3. Each agent starts ReAct loop
   - REASON: Analyze search params
   - ACT: Call search tool
   - OBSERVE: Get results
   - REPEAT: If needed
   
4. Orchestrator aggregates results
   - Combines all flights
   - Sorts by price
   - Adds provider info
   
5. Returns aggregated response
   [
     {provider: "skyscanner", price: 245.99, ...},
     {provider: "kayak", price: 258.50, ...},
     ...
   ]
```

---

## 🧪 Testing

### Using curl
```bash
curl -X POST "http://localhost:8080/api/v2/agents/search" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "JFK",
    "destination": "LAX",
    "departure_date": "2026-06-15",
    "passengers": 1,
    "cabin_class": "economy"
  }'
```

### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8080/api/v2/agents/search",
    json={
        "origin": "JFK",
        "destination": "LAX",
        "departure_date": "2026-06-15",
        "passengers": 1,
        "cabin_class": "economy"
    }
)

flights = response.json()["flights"]
for flight in flights[:3]:
    print(f"{flight['provider']}: ${flight['price']} ({flight['airline']})")
```

---

## 📈 Monitoring & Debugging

### Logs
The system logs each step:
```
🔍 [SKYSCANNER] Searching JFK → LAX on 2026-06-15
ReAct Iteration 1/5
Tool Use: search_skyscanner
📡 Calling skyscanner API...
✅ [SKYSCANNER] Found 12 flights
```

### Agent Status Check
```bash
curl http://localhost:8080/api/v2/agents/status
```

Returns:
```json
{
  "system": "ReAct Agent System",
  "agents": [...],
  "api_key_configured": true
}
```

---

## ⚠️ Important Notes

### API Key Required
Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Rate Limiting
Current implementation is sequential. For production:
- Use `asyncio` for concurrent agent execution
- Implement rate limiting per provider
- Add caching for repeated searches

### Cost Considerations
- Each search uses Claude API (billable)
- Multiple agents = multiple API calls
- Estimated: 0.1-0.5¢ per search

### Latency
- Sequential agents: 5-15 seconds per search
- Future: Parallel execution will reduce to 3-5 seconds

---

## 🚀 Next Steps

1. **Add Real APIs**: Integrate actual flight provider APIs
2. **Parallel Execution**: Use `concurrent.futures` for simultaneous agent searches
3. **Caching**: Implement Redis for result caching
4. **Advanced Reasoning**: Enhanced system prompts for better agent decisions
5. **Monitoring**: Add telemetry and metrics
6. **Optimization**: Fine-tune agent behavior and prompts

---

## 📚 Resources

- [Anthropic API Documentation](https://docs.anthropic.com)
- [ReAct Pattern Paper](https://arxiv.org/abs/2210.03629)
- [Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)

---

**Built with ❤️ using Claude API and ReAct Pattern**
