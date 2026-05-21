# Multi-Provider LLM Setup Guide

Flight Price Aggregator supports **three LLM providers**: Google Gemini, OpenAI, and Anthropic. Switch between them with environment variables only — no need to modify API requests.

## Quick Start

### Option 1: Google Gemini (Default)

```bash
export GOOGLE_API_KEY="your-google-api-key"
export LLM_PROVIDER="google"
python main_agents.py
```

**API Request (same for all providers):**
```json
{
  "origin": "JFK",
  "destination": "LAX",
  "departure_date": "2026-06-15",
  "passengers": 1,
  "cabin_class": "economy"
}
```

### Option 2: OpenAI (GPT-4)

```bash
export OPENAI_API_KEY="your-openai-api-key"
export LLM_PROVIDER="openai"
python main_agents.py
```

**Same API request as above** — the provider is determined by environment variables only.

### Option 3: Anthropic (Claude)

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export LLM_PROVIDER="anthropic"
python main_agents.py
```

**Same API request as above** — the provider is determined by environment variables only.

---

## Environment Variables

### Required Configuration

| Purpose | Environment Variable | Value | Get API Key |
|---------|-------------------|-------|------------|
| Select Provider | `LLM_PROVIDER` | `google`, `openai`, or `anthropic` | N/A |
| Google Credentials | `GOOGLE_API_KEY` | Your Google API key | https://ai.google.dev |
| OpenAI Credentials | `OPENAI_API_KEY` | Your OpenAI API key | https://platform.openai.com |
| Anthropic Credentials | `ANTHROPIC_API_KEY` | Your Anthropic API key | https://console.anthropic.com |

### Optional Configuration

| Purpose | Environment Variable | Default Value |
|---------|-------------------|----------------|
| Override Model | `LLM_MODEL` | Provider's default model |

---

## Setup Examples

### Setup 1: Use Google Gemini (Default)

```bash
export GOOGLE_API_KEY="sk-proj-abc123xyz..."
export LLM_PROVIDER="google"
python main_agents.py
```

Then send API requests. The system will use Google Gemini.

### Setup 2: Use OpenAI GPT-4

```bash
export OPENAI_API_KEY="sk-proj-abc123xyz..."
export LLM_PROVIDER="openai"
python main_agents.py
```

Then send the same API requests. The system will use OpenAI instead.

### Setup 3: Use Anthropic Claude with Custom Model

```bash
export ANTHROPIC_API_KEY="sk-ant-abc123xyz..."
export LLM_PROVIDER="anthropic"
export LLM_MODEL="claude-3-opus"
python main_agents.py
```

Then send the same API requests. The system will use Anthropic with Claude 3 Opus.

### Setup 4: Have All Keys Ready for Quick Switching

```bash
export GOOGLE_API_KEY="sk-proj-google-key..."
export OPENAI_API_KEY="sk-proj-openai-key..."
export ANTHROPIC_API_KEY="sk-ant-anthropic-key..."

# Start with Google
export LLM_PROVIDER="google"
python main_agents.py
```

**To switch to OpenAI:** Stop the server, run `export LLM_PROVIDER="openai"`, restart.

---

## API Request Format

**All requests use the same format, regardless of provider:**

```json
{
  "origin": "string (required) - IATA code, e.g., JFK",
  "destination": "string (required) - IATA code, e.g., LAX",
  "departure_date": "string (required) - YYYY-MM-DD format",
  "return_date": "string (optional) - YYYY-MM-DD for round trips",
  "passengers": "integer (default: 1) - 1-9 passengers",
  "cabin_class": "string (default: economy) - economy, business, first"
}
```

**Note:** LLM provider and model are NOT part of the API request. They are configured via environment variables only.

---

## Example Requests in Postman

**All three examples below use the exact same API request body:**

### Using Google Gemini
```
POST http://localhost:8080/api/v1/flights/search

{
  "origin": "JFK",
  "destination": "LAX",
  "departure_date": "2026-06-15",
  "passengers": 2,
  "cabin_class": "business"
}
```

Preceded by:
```bash
export GOOGLE_API_KEY="..."
export LLM_PROVIDER="google"
python main_agents.py
```

### Using OpenAI GPT-4
```
POST http://localhost:8080/api/v1/flights/search

{
  "origin": "ORD",
  "destination": "DEN",
  "departure_date": "2026-07-20",
  "passengers": 1,
  "cabin_class": "economy"
}
```

Preceded by:
```bash
export OPENAI_API_KEY="..."
export LLM_PROVIDER="openai"
python main_agents.py
```

### Using Anthropic Claude
```
POST http://localhost:8080/api/v1/flights/search

{
  "origin": "LAX",
  "destination": "JFK",
  "departure_date": "2026-08-10",
  "passengers": 3,
  "cabin_class": "economy"
}
```

Preceded by:
```bash
export ANTHROPIC_API_KEY="..."
export LLM_PROVIDER="anthropic"
python main_agents.py
```

---

## Default Models by Provider

If `LLM_MODEL` environment variable is not set, these defaults are used:

| Provider | Default Model |
|----------|--------------|
| Google | `gemini-3-flash-preview` |
| OpenAI | `gpt-4` |
| Anthropic | `claude-3-5-sonnet` |

---

## How It Works

1. **Backend reads environment variables:**
   - `LLM_PROVIDER` determines which provider to use
   - `LLM_MODEL` (optional) overrides the provider's default model
   - Corresponding API key (`GOOGLE_API_KEY`, etc.) is validated

2. **Frontend sends clean requests:**
   - No LLM provider information in the API request
   - Same request format for all providers
   - Frontend has no visibility into which LLM is being used

3. **Backend initializes CrewAI:**
   - `get_crew()` reads from environment variables
   - Creates agents with the configured LLM provider
   - Executes flight search using the selected provider

---

## Switching Providers Without Restarting

Since provider is configured via environment variables:

1. **Stop the server** (Ctrl+C)
2. **Set new environment variables:**
   ```bash
   export LLM_PROVIDER="openai"
   export OPENAI_API_KEY="your-key"
   ```
3. **Start the server again:**
   ```bash
   python main_agents.py
   ```
4. **Send API requests** — they will use the new provider

---

## Error Handling

### Missing API Key for Selected Provider
```json
{
  "error": "Crew system not configured: OPENAI_API_KEY required",
  "timestamp": "2026-05-20T..."
}
```

**Fix:** Set the required API key and restart the server.

### Invalid Provider Value
```json
{
  "error": "Unsupported provider 'invalid'. Supported: google, openai, anthropic",
  "timestamp": "2026-05-20T..."
}
```

**Fix:** Set `LLM_PROVIDER` to one of: `google`, `openai`, `anthropic`.

---

## Security Considerations

✅ **LLM provider is NOT exposed to clients** — only backend knows which provider is configured  
✅ **API requests are clean** — no sensitive configuration in request body  
✅ **Only admins can change LLM provider** — requires server restart with new env vars  
✅ **API keys are environment variables** — not hardcoded or sent in requests  

---

## Troubleshooting

### "API key not configured" error

Check that the API key for your selected provider is set:

```bash
# For Google
echo $GOOGLE_API_KEY

# For OpenAI
echo $OPENAI_API_KEY

# For Anthropic
echo $ANTHROPIC_API_KEY
```

If empty, set it and restart the server.

### Provider not being used

Verify the `LLM_PROVIDER` environment variable is set:

```bash
echo $LLM_PROVIDER
```

If empty or wrong, set it to `google`, `openai`, or `anthropic` and restart.

### Different results from different providers

Expected! Different LLMs have different reasoning styles:
- **Google Gemini**: Fast, cost-effective
- **OpenAI GPT-4**: Most capable, thorough
- **Anthropic Claude**: Balanced quality and speed

Test all three for your use case.

---

## Recommended Model Choices

| Task | Provider | Model | Why |
|------|----------|-------|-----|
| Cost-Effective | Google | `gemini-3-flash-preview` | Fast, cheap |
| Best Quality | OpenAI | `gpt-4` | Most capable |
| Balanced | Anthropic | `claude-3-5-sonnet` | Good quality/speed |
| Latest | Google | `gemini-2-flash` | Newest model |

---

## Summary

✅ **Set environment variables before starting server:**
```bash
export LLM_PROVIDER="google"  # or openai, anthropic
export GOOGLE_API_KEY="..."    # Set the corresponding API key
python main_agents.py
```

✅ **Send standard API requests** (no LLM info needed):
```json
{
  "origin": "JFK",
  "destination": "LAX",
  "departure_date": "2026-06-15",
  "passengers": 1,
  "cabin_class": "economy"
}
```

✅ **Switch providers** by restarting with different env vars.

That's it! The system handles the rest.
