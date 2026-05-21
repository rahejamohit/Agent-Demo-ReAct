# Flight Price Aggregator API - CrewAI Multi-Provider System (v2.0)

A **production-ready multi-agent system** using **CrewAI** to intelligently fetch and aggregate flight prices from multiple providers with **flexible LLM support** (Google Gemini, OpenAI GPT-4, Anthropic Claude).

## 🎯 Architecture: CrewAI Multi-Agent Orchestration with Multi-Provider LLM

```
FastAPI Backend (localhost:8080)
│
├── API Endpoints
│   ├── POST /api/v1/flights/search     (Flight search - LLM provider from env)
│   ├── GET /api/v1/agents/status       (Crew & LLM status)
│   └── GET /health                     (Health check)
│
├── Environment Configuration
│   ├── LLM_PROVIDER (google, openai, anthropic)
│   ├── LLM_MODEL (optional override)
│   └── Corresponding API Key
│
└── CrewAI System
    │
    ├── Crew (Orchestrator)
    │   ├── Skyscanner Agent → search_skyscanner tool
    │   ├── Kayak Agent → search_kayak tool
    │   ├── Google Flights Agent → search_google_flights tool
    │   └── Amadeus Agent → search_amadeus tool
    │
    ├── LLM Provider (Dynamic)
    │   ├── Google Gemini
    │   ├── OpenAI GPT-4
    │   └── Anthropic Claude
    │
    └── Task Manager
        ├── Skyscanner Flight Search Task
        ├── Kayak Flight Search Task
        ├── Google Flights Search Task
        └── Amadeus Flight Search Task
```

## 🚀 Quick Start (5 Minutes)

### Step 1: Choose Your LLM Provider

**Option A: Google Gemini (Recommended for cost)**
```bash
export GOOGLE_API_KEY="your-google-api-key"
export LLM_PROVIDER="google"
```

**Option B: OpenAI GPT-4 (Recommended for quality)**
```bash
export OPENAI_API_KEY="your-openai-api-key"
export LLM_PROVIDER="openai"
```

**Option C: Anthropic Claude (Recommended for balance)**
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export LLM_PROVIDER="anthropic"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the CrewAI System
```bash
python main_agents.py
```

You should see:
```
🚀 Starting Flight Price Aggregator - CrewAI System
📍 URL: http://localhost:8080
📚 Docs: http://localhost:8080/docs
🎯 Framework: CrewAI
🧠 LLM Provider: google (or openai/anthropic)
🤖 Agents: Skyscanner, Kayak, Google Flights, Amadeus
```

### Step 4: Test the System
**Option A: Interactive API Docs**
- Open http://localhost:8080/docs
- Click "Try it out" on `/api/v1/flights/search`
- Click "Execute"

**Option B: Python Client**
```bash
python example_agent_client.py
```

**Option C: curl**
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

## 📡 API Endpoints

### Flight Search
- `POST /api/v1/flights/search` - Search flights using CrewAI with configured LLM
  - **LLM Provider:** Set via `LLM_PROVIDER` environment variable
  - **Request:** origin, destination, departure_date, passengers, cabin_class
  - **Response:** Aggregated flights sorted by price with booking URLs

### Agent Status
- `GET /api/v1/agents/status` - Get crew and agent system status

### Health & Info
- `GET /health` - Health check endpoint
- `GET /` - API info and documentation links

## 📖 Usage Examples

### Search Flights with Configured LLM
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

**Note:** Same API request works with any LLM provider configured via environment variables!

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
      "provider": "skyscanner",
      "airline": "Delta",
      "flight_number": "DL123",
      "departure": "2026-06-15T08:00:00",
      "arrival": "2026-06-15T11:30:00",
      "duration_minutes": 330,
      "stops": 0,
      "price": 245.99,
      "currency": "USD",
      "booking_url": "https://skyscanner.com/book/...",
      "seats_available": 12
    },
    {
      "provider": "kayak",
      "airline": "United",
      "flight_number": "UA456",
      "departure": "2026-06-15T10:00:00",
      "arrival": "2026-06-15T13:45:00",
      "duration_minutes": 345,
      "stops": 1,
      "price": 258.50,
      "currency": "USD",
      "booking_url": "https://kayak.com/book/...",
      "seats_available": 8
    }
  ],
  "total_results": 48,
  "timestamp": "2026-05-21T..."
}
```

### Check Crew Status
```bash
curl http://localhost:8080/api/v1/agents/status
```

Returns information about agents, LLM provider, and model in use.

### Python Client Example
```python
from example_agent_client import FlightAgentClient

client = FlightAgentClient()
results = client.search_flights(
    origin="JFK",
    destination="LAX",
    departure_date="2026-06-15",
    passengers=1
)

for flight in results["flights"][:3]:
    print(f"{flight['provider']}: ${flight['price']} ({flight['airline']})")
```

## ✨ Key Features

✅ **Multi-LLM Support** - Google Gemini, OpenAI, Anthropic with instant switching  
✅ **CrewAI Framework** - Higher-level agent orchestration with tasks  
✅ **Multi-Agent System** - 4 specialized agents (Skyscanner, Kayak, Google Flights, Amadeus)  
✅ **Task-Based Workflow** - Tasks define what agents need to accomplish  
✅ **Built-in Memory** - CrewAI provides memory management per agent  
✅ **Multi-Provider Aggregation** - Fetches from all providers simultaneously  
✅ **Price Sorting** - Results automatically sorted by price (cheapest first)  
✅ **Direct Booking Links** - Each flight includes provider booking URL  
✅ **Provider Information** - Each result tagged with its source  
✅ **Clean API** - Same request format for all LLM providers  
✅ **CORS Enabled** - Ready for frontend integration  
✅ **Interactive API Docs** - Swagger UI with "Try it out" buttons  
✅ **Structured Logging** - Monitoring-ready logs for debugging  
✅ **Error Handling** - Comprehensive error responses  
✅ **Production Ready** - Clean code, type hints, documentation  

## 🤖 How CrewAI Works

### Agent Architecture
Each agent is specialized with:
- **Role**: What the agent does (e.g., "Skyscanner Flight Search Specialist")
- **Goal**: What it's trying to achieve (e.g., "Find the cheapest flights")
- **Backstory**: Context about its expertise
- **Tools**: Available actions (flight search functions)
- **LLM**: Shared LLM instance configured via environment variables

### Task-Based Workflow
1. **Task Definition** - Define what needs to be done
2. **Agent Assignment** - Assign agent(s) to the task
3. **Crew Execution** - CrewAI orchestrates agent collaboration using configured LLM
4. **Result Aggregation** - Combine results from all agents

### Specialized Agents

| Agent | Provider | Specialty | Focus |
|-------|----------|-----------|-------|
| 🟦 **Skyscanner Agent** | Skyscanner | Price comparisons | Budget flights, deals |
| 🟨 **Kayak Agent** | Kayak | Best prices + ratings | Value for money |
| 🟩 **Google Flights Agent** | Google | Flexible options | Price trends, alternatives |
| 🟧 **Amadeus Agent** | Amadeus | Enterprise inventory | Premium, ancillaries |

## 📊 System Architecture

### Request Flow
```
1. User sends search request (same for all providers)
   POST /api/v1/flights/search
   {origin: "JFK", destination: "LAX", ...}
   
2. Backend reads LLM provider from environment
   - LLM_PROVIDER determines which provider to use
   - Validates corresponding API key is set
   
3. Crew initializes agents with configured LLM
   - All 4 agents share the same LLM instance
   - Each agent gets specialized role and goal
   
4. Crew creates and executes tasks
   - Each agent gets a task
   - Tools execute flight searches
   - Results collected by crew
   
5. Crew aggregates results
   - Combines all flights
   - Removes duplicates
   - Sorts by price
   - Adds provider info
   
6. Returns aggregated response to user
   [~48 flights from all providers, sorted by price]
```

## 🔌 Integration with Frontend

This backend is designed for the **Flight Price Aggregator UI**:

1. **Frontend** sends clean search request (no LLM info)
2. **Crew** uses configured LLM to orchestrate agents
3. **Agents** fetch flights from multiple providers
4. **Aggregator** collects and sorts results
5. **Frontend** displays results with direct booking links

## ⚙️ Configuration

### Required Environment Variables

Choose **one** LLM provider and set its API key:

```bash
# Option 1: Google Gemini
export GOOGLE_API_KEY="your-key"
export LLM_PROVIDER="google"

# Option 2: OpenAI GPT-4
export OPENAI_API_KEY="your-key"
export LLM_PROVIDER="openai"

# Option 3: Anthropic Claude
export ANTHROPIC_API_KEY="your-key"
export LLM_PROVIDER="anthropic"
```

### Optional Environment Variables
```bash
# Override default model for the selected provider
export LLM_MODEL="gemini-2-flash"  # or gpt-4-turbo, claude-3-opus, etc.
```

### Using .env File
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

### Agent Configuration
Agents are configured in `crew_config.py`:
- Default models by provider (see MULTI_PROVIDER_SETUP.md)
- Tool use: Enabled
- Memory: Enabled per agent
- Verbose logging: Enabled for debugging

## 🚀 Next Steps & Enhancements

### Phase 1: Immediate (Production Ready)
- [x] CrewAI framework implemented
- [x] Multi-provider LLM support (Google, OpenAI, Anthropic)
- [x] Multi-agent system (4 specialized agents)
- [x] Tool use capability enabled
- [x] Mock data generators (realistic)
- [ ] Real API integrations (Skyscanner, Amadeus, Google Flights, Kayak)

### Phase 2: Frontend (Coming Soon)
- [ ] React/Vue frontend for flight search
- [ ] Real-time flight price updates
- [ ] Booking redirection

### Phase 3: Optimization & Scaling
- [ ] **Parallel Task Execution** - Execute all 4 tasks concurrently → 3-5 seconds
- [ ] **Caching** - Add Redis for result caching
- [ ] **Database** - Add PostgreSQL for persistent storage
- [ ] **Rate Limiting** - Request throttling per user
- [ ] **Monitoring** - Prometheus metrics and health checks
- [ ] **Logging** - Enhanced structured logging
- [ ] **Deployment** - Docker, Kubernetes, cloud platforms

### Phase 4: Advanced Features
- [ ] **Round-trip Flights** - Handle return flights intelligently
- [ ] **Seat Selection** - Agents can compare seat options
- [ ] **Price Monitoring** - Track price changes over time
- [ ] **Alternative Airports** - Expand search to nearby airports
- [ ] **Multi-language** - Support for different languages and currencies
- [ ] **ML Optimization** - Learn which providers are best for certain routes

## 📝 Development

### Code Structure
- **`models.py`** - Type definitions and validation (Pydantic)
- **`crew_config.py`** - Agent configurations and tool definitions
- **`flight_crew.py`** - CrewAI crew orchestrator (multi-agent manager)
- **`main_agents.py`** - FastAPI endpoints and server
- **`example_agent_client.py`** - Example client demonstrating usage

### Key Classes
- `FlightAggregatorCrew` - Manages the CrewAI crew and LLM configuration
- `create_agents()` - Factory for creating specialized agents with configured LLM
- `create_tasks()` - Factory for creating flight search tasks
- `get_crew()` - Singleton pattern to get/create crew with env-configured LLM
- Tool decorators for flight search APIs

### Testing
```bash
# Run example client
python example_agent_client.py

# Test with curl
curl -X POST http://localhost:8080/api/v1/flights/search \
  -H "Content-Type: application/json" \
  -d '{"origin": "JFK", "destination": "LAX", "departure_date": "2026-06-15"}'

# Check agent status
curl http://localhost:8080/api/v1/agents/status
```

### Code Quality
```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

## 📈 Performance Notes

### Current Performance
- **Latency**: 5-15 seconds per search (sequential tasks)
- **Results**: ~48 flights from 4 providers combined
- **Mock Data**: Realistic pricing and airline simulation
- **Cost**: Varies by LLM provider (Google cheapest, OpenAI middle, Anthropic comparable)

### Performance by LLM Provider
- **Google Gemini**: Fast (~5-8s), cost-effective
- **OpenAI GPT-4**: Thorough (~8-12s), high quality
- **Anthropic Claude**: Balanced (~6-10s), good quality/speed trade-off

### Future Optimizations
- **Parallel Tasks** - Execute all 4 tasks concurrently → 3-5 seconds
- **Caching** - Cache results for identical searches
- **Result Limiting** - Return top N results instead of all
- **LLM Optimization** - Use faster/cheaper models for initial filtering

## 🧠 Understanding CrewAI

**CrewAI** = Framework for orchestrating AI agents with roles, goals, and tools

### Why CrewAI?
- **Abstraction** - Hide complexity of agent orchestration
- **Collaboration** - Agents work together effectively
- **Scalability** - Easy to add more agents
- **Flexibility** - Works with multiple LLMs dynamically (Claude, Gemini, GPT-4, etc.)
- **Memory** - Built-in memory management per agent
- **Tools** - Simple tool definition and execution

### In Our System
1. **Agents** are specialized by role and goal
2. **Tasks** define what needs to be done
3. **Crew** orchestrates agent collaboration with configured LLM
4. **Tools** enable agents to search flights
5. **Results** are aggregated and returned

## 📚 Documentation

- **[README.md](README.md)** - Main project documentation
- **[MULTI_PROVIDER_SETUP.md](MULTI_PROVIDER_SETUP.md)** ⭐ - Multi-provider LLM configuration guide
- **[AGENT_QUICKSTART.md](AGENT_QUICKSTART.md)** - 5-minute setup guide
- **[README_CREWAI.md](README_CREWAI.md)** - This file (CrewAI detailed guide)

## 🔗 Resources

### CrewAI & Documentation
- [CrewAI Official Docs](https://docs.crewai.com)
- [CrewAI GitHub Repository](https://github.com/joaomdmoura/crewAI)

### LLM Providers
- [Google Gemini API](https://ai.google.dev)
- [OpenAI API](https://platform.openai.com)
- [Anthropic API](https://console.anthropic.com)

### Flight APIs (for future integration)
- [Skyscanner API](https://rapidapi.com/skyscanner/api/skyscanner1)
- [Amadeus API](https://developers.amadeus.com/)
- [Google Flights API](https://rapidapi.com/apidojo/api/google-flights)
- [Kayak API](https://rapidapi.com/apidojo/api/kayak)

## 📄 License

Internal League Flight System

## 💬 Support

For issues or questions:
1. Check [AGENT_QUICKSTART.md](AGENT_QUICKSTART.md) for setup issues
2. Check [MULTI_PROVIDER_SETUP.md](MULTI_PROVIDER_SETUP.md) for LLM configuration
3. Verify environment variables are set: `echo $LLM_PROVIDER`
4. Check corresponding API key: `echo $GOOGLE_API_KEY` (or your provider)
5. Review logs from `python main_agents.py` for debugging

---

**Built with ❤️ using CrewAI, Multi-Provider LLM Support, and Multi-Agent Architecture**
