# 🤖 Agent System Quick Start

Get the ReAct-based flight search system running in 5 minutes.

## Step 1: Set API Key

```bash
# Get key from https://console.anthropic.com
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Verify it's set:**
```bash
echo $ANTHROPIC_API_KEY
```

## Step 2: Install Dependencies

```bash
cd "Agent Demo Playground"
pip install -r requirements.txt
```

## Step 3: Start the Agent System

```bash
python main_agents.py
```

You should see:
```
🚀 Starting Flight Price Aggregator - Agent System
📍 URL: http://localhost:8080
📚 Docs: http://localhost:8080/docs
🤖 Pattern: ReAct (Reasoning + Acting)
```

## Step 4: Test Agents

### Option A: Using Interactive Docs
1. Open http://localhost:8080/docs
2. Click "Try it out" on `/api/v2/agents/search`
3. Fill in:
   ```json
   {
     "origin": "JFK",
     "destination": "LAX",
     "departure_date": "2026-06-15",
     "passengers": 1,
     "cabin_class": "economy"
   }
   ```
4. Click "Execute"
5. Watch agents search all providers!

### Option B: Using Example Client
```bash
python example_agent_client.py
```

This runs a complete example showing:
- ✅ Agent status check
- ✅ Flight search with agents
- ✅ Results from all providers
- ✅ Statistics and comparison

### Option C: Using curl
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

## What Happens

When you search, 4 agents activate simultaneously (in future):

```
1. 🟦 Skyscanner Agent
   → Reasons about search
   → Calls search_skyscanner tool
   → Gets 12 flights
   
2. 🟨 Kayak Agent
   → Reasons about search
   → Calls search_kayak tool
   → Gets 15 flights
   
3. 🟩 Google Flights Agent
   → Reasons about search
   → Calls search_google_flights tool
   → Gets 14 flights
   
4. 🟧 Amadeus Agent
   → Reasons about search
   → Calls search_amadeus tool
   → Gets 7 flights

Final Result: 48 flights, sorted by price ✅
```

## Response Example

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
      "booking_url": "https://skyscanner.com/book/...",
      "seats_available": 12
    },
    ... more flights
  ],
  "total_results": 48,
  "provider_results": {
    "skyscanner": { "flights": [...], "total_results": 12 },
    "kayak": { "flights": [...], "total_results": 15 },
    "google_flights": { "flights": [...], "total_results": 14 },
    "amadeus": { "flights": [...], "total_results": 7 }
  }
}
```

## Check Agent Status

```bash
curl http://localhost:8080/api/v2/agents/status
```

Returns info about each agent and their configuration.

## ⚠️ Troubleshooting

### "ANTHROPIC_API_KEY not configured"
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### "Agent search failed: 401 Unauthorized"
Your API key is invalid. Get a new one from https://console.anthropic.com

### "Connection refused: 127.0.0.1:8080"
Make sure the server is running:
```bash
python main_agents.py
```

### Agents are slow
- First request initializes agents (takes longer)
- Subsequent requests are faster
- Eventually we'll parallelize agents (reducing latency)

## 📚 Next Steps

1. **Read Full Guide**: [AGENT_SYSTEM.md](AGENT_SYSTEM.md)
2. **Add Real APIs**: Replace mock data with actual flight APIs
3. **Parallelize**: Execute agents concurrently
4. **Optimize**: Fine-tune agent prompts
5. **Monitor**: Add logging and metrics

## 🚀 Key Features

- ✅ **ReAct Pattern**: Agents reason → act → observe
- ✅ **Multi-Provider**: Skyscanner, Kayak, Google Flights, Amadeus
- ✅ **Real Results**: Mock data generator (ready for real APIs)
- ✅ **Smart Sorting**: Results sorted by price
- ✅ **Booking URLs**: Direct links to each provider
- ✅ **Interactive Docs**: Swagger UI at /docs

---

**Happy Searching! 🎉**
