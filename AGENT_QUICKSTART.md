# 🤖 Flight Search Quick Start Guide

Get the CrewAI-based flight search system running in 5 minutes with your preferred LLM provider.

## Step 1: Choose Your LLM Provider

Pick **one** of the three options below:

### Option A: Google Gemini (Recommended for cost) 💰
```bash
# Get key from https://ai.google.dev
export GOOGLE_API_KEY="your-google-api-key"
export LLM_PROVIDER="google"

# Verify it's set
echo $GOOGLE_API_KEY
```

### Option B: OpenAI GPT-4 (Recommended for quality) ✨
```bash
# Get key from https://platform.openai.com
export OPENAI_API_KEY="your-openai-api-key"
export LLM_PROVIDER="openai"

# Verify it's set
echo $OPENAI_API_KEY
```

### Option C: Anthropic Claude (Recommended for balance) ⚖️
```bash
# Get key from https://console.anthropic.com
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export LLM_PROVIDER="anthropic"

# Verify it's set
echo $ANTHROPIC_API_KEY
```

## Step 2: Install Dependencies

```bash
cd "Agent Demo Playground"
pip install -r requirements.txt
```

## Step 3: Start the System

```bash
python main_agents.py
```

You should see:
```
🚀 Starting Flight Price Aggregator - CrewAI System
📍 URL: http://localhost:8080
📚 Docs: http://localhost:8080/docs
🎯 Framework: CrewAI
🧠 LLM Provider: google (or openai/anthropic based on your choice)
🤖 Agents: Skyscanner, Kayak, Google Flights, Amadeus
```

## Step 4: Test the System

### Option A: Using Interactive Docs (Easiest)
1. Open http://localhost:8080/docs
2. Click "Try it out" on `/api/v1/flights/search`
3. Enter search parameters:
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
5. Watch agents search with your chosen LLM! 🚀

### Option B: Using Python Client
```bash
python example_agent_client.py
```

Demonstrates:
- ✅ Agent status check
- ✅ Flight search with agents
- ✅ Results from all providers
- ✅ Statistics and comparison

### Option C: Using curl
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

**Note:** The request is identical regardless of which LLM provider you configured!

## How It Works

When you search, the system activates:

```
1. Your configured LLM Provider
   → Google Gemini, OpenAI GPT-4, or Anthropic Claude
   → Powers agent reasoning

2. Four Specialized Agents (in parallel)
   ├─ 🟦 Skyscanner Agent → Gets budget flights
   ├─ 🟨 Kayak Agent → Gets best prices + ratings
   ├─ 🟩 Google Flights Agent → Gets flexible options
   └─ 🟧 Amadeus Agent → Gets premium flights

3. Crew Aggregator
   → Combines all results
   → Removes duplicates
   → Sorts by price (cheapest first)

Final Result: ~48 flights from all providers ✅
```

## Response Example

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
    ... more flights sorted by price
  ],
  "total_results": 48,
  "timestamp": "2026-05-21T..."
}
```

## Check System Status

```bash
curl http://localhost:8080/api/v1/agents/status
```

Returns:
- Active agents and their configuration
- Which LLM provider is in use
- Agent status and capabilities

## Switching LLM Providers

To switch from Google to OpenAI (or any other provider):

1. **Stop the server** (Ctrl+C)
2. **Set new environment variables:**
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export LLM_PROVIDER="openai"
   ```
3. **Start the server again:**
   ```bash
   python main_agents.py
   ```
4. **Make requests** — they'll use your new provider

No code changes needed! ✨

## ⚠️ Troubleshooting

### "LLM_PROVIDER not set or invalid"
```bash
# Set the provider (google, openai, or anthropic)
export LLM_PROVIDER="google"
```

### "API_KEY not configured"
Make sure you set the correct API key for your chosen provider:

```bash
# For Google
export GOOGLE_API_KEY="your-key"

# For OpenAI
export OPENAI_API_KEY="your-key"

# For Anthropic
export ANTHROPIC_API_KEY="your-key"
```

Verify with:
```bash
echo $GOOGLE_API_KEY  # or your provider
```

### "Connection refused: 127.0.0.1:8080"
The server isn't running. Start it:
```bash
python main_agents.py
```

### "401 Unauthorized" or API key error
- Double-check your API key is correct
- Ensure you're using the right key for your chosen provider
- Get new key from:
  - Google: https://ai.google.dev
  - OpenAI: https://platform.openai.com
  - Anthropic: https://console.anthropic.com

### Agents are slow
- First request initializes agents (normal)
- Subsequent requests are faster
- Each LLM provider has different latencies:
  - Google Gemini: Fast (~5-8s)
  - OpenAI GPT-4: Thorough (~8-12s)
  - Anthropic Claude: Balanced (~6-10s)

## 📚 Next Steps

1. **Production Setup**: See [MULTI_PROVIDER_SETUP.md](MULTI_PROVIDER_SETUP.md) for advanced configuration
2. **Full Documentation**: Read [README.md](README.md)
3. **CrewAI Details**: See [README_CREWAI.md](README_CREWAI.md)
4. **Add Real APIs**: Replace mock data with actual flight provider APIs
5. **Build Frontend**: Create web UI for flight search results

## ✨ Key Features

- ✅ **Multi-LLM Support**: Google, OpenAI, Anthropic with instant switching
- ✅ **CrewAI Framework**: Agent orchestration with task management
- ✅ **Multi-Provider**: Skyscanner, Kayak, Google Flights, Amadeus
- ✅ **Smart Aggregation**: Results combined and sorted by price
- ✅ **Direct Booking**: Links to book on each provider
- ✅ **Interactive API Docs**: Swagger UI at /docs
- ✅ **Clean API**: Same request format for all providers
- ✅ **Production Ready**: Type hints, error handling, logging

---

**Ready to search flights? Pick your LLM and start in Step 1!** 🚀
