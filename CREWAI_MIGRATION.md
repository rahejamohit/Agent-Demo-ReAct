# CrewAI Migration Guide

## Overview
This document explains the migration from a custom Claude API + ReAct pattern implementation to the **CrewAI framework** for multi-agent orchestration.

## What Changed

### ✅ Key Improvements

| Aspect | ReAct (Custom) | CrewAI |
|--------|---|---|
| **Agent Orchestration** | Manual loops with max iterations | Built-in Crew class handles orchestration |
| **Task Management** | Implicit in agent logic | Explicit Task objects with descriptions |
| **Memory** | Manual context tracking | Automatic memory per agent |
| **Tool Definition** | Anthropic SDK tool_use schema | Simple `@tool` decorator |
| **Parallel Execution** | Sequential agents | Built-in support for parallel tasks |
| **Error Handling** | Manual exception handling | Built-in error recovery |
| **LLM Flexibility** | Anthropic-only | Any LLM via LangChain support |
| **Code Complexity** | 250+ lines per agent | Simplified with framework abstractions |

### 📁 File Structure Changes

#### Removed
- `flight_agents.py` - Custom ReAct implementation (250+ lines)
- `agents_config.py` - Custom tool/agent configuration

#### Added
- `crew_config.py` - CrewAI agents, tools, and configurations
- `flight_crew.py` - Crew orchestration with FlightAggregatorCrew class

#### Updated
- `main_agents.py` - Replace imports and endpoint implementations
- `requirements.txt` - Add CrewAI dependencies
- `example_agent_client.py` - Update documentation and print statements
- Documentation files

### 🔄 Architecture Comparison

#### ReAct Pattern (Old)
```
User Request
    ↓
Agent 1 (manual ReAct loop)
├─ REASON about request
├─ ACT using tool
├─ OBSERVE results
└─ REPEAT up to 5 times
    ↓
Agent 2 (same pattern)
    ↓
Agent 3 (same pattern)
    ↓
Agent 4 (same pattern)
    ↓
Orchestrator aggregates results
```

#### CrewAI Pattern (New)
```
User Request
    ↓
Crew.kickoff()
├─ Agent 1 executes Task 1
├─ Agent 2 executes Task 2
├─ Agent 3 executes Task 3
└─ Agent 4 executes Task 4
    ↓
Crew aggregates results from all tasks
```

### 🛠️ Code Migration Examples

#### Tool Definition

**Before (ReAct with Anthropic SDK):**
```python
FLIGHT_SEARCH_TOOLS = {
    "search_skyscanner": {
        "name": "search_skyscanner",
        "description": "Search flights on Skyscanner",
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {"type": "string"},
                "destination": {"type": "string"},
                "departure_date": {"type": "string"},
                "passengers": {"type": "integer"}
            },
            "required": ["origin", "destination", "departure_date"]
        }
    }
}
```

**After (CrewAI):**
```python
@tool("search_skyscanner")
def search_skyscanner(origin: str, destination: str, departure_date: str, passengers: int = 1) -> Dict[str, Any]:
    """Search flights on Skyscanner for deals and budget airlines."""
    return _search_flights("skyscanner", origin, destination, departure_date, passengers)
```

#### Agent Definition

**Before (ReAct):**
```python
class FlightSearchAgent:
    def __init__(self, provider, api_key, model):
        self.provider = provider
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
    def search(self, origin, destination, departure_date):
        for iteration in range(self.max_iterations):
            # Manual ReAct loop
            response = self.client.messages.create(
                model=self.model,
                tools=[...],
                messages=[...]
            )
            # Process tool_use, etc.
```

**After (CrewAI):**
```python
Agent(
    role="Skyscanner Flight Search Specialist",
    goal="Find the cheapest flights on Skyscanner",
    backstory="You are an expert at finding budget flights...",
    tools=[search_skyscanner],
    model="claude-3-5-sonnet-20241022",
    memory=True,
    verbose=True
)
```

#### Orchestration

**Before (ReAct):**
```python
class AgentOrchestrator:
    def __init__(self):
        self.agents = {
            "skyscanner": FlightSearchAgent("skyscanner", ...),
            "kayak": FlightSearchAgent("kayak", ...),
            # ...
        }
    
    def search_all_providers(self, origin, destination, departure_date):
        results = []
        for agent in self.agents.values():
            result = agent.search(origin, destination, departure_date)
            results.extend(result["flights"])
        return {"flights": results, ...}
```

**After (CrewAI):**
```python
class FlightAggregatorCrew:
    def __init__(self, model="claude-3-5-sonnet-20241022"):
        self.agents = create_agents(model=model)
    
    def search_flights(self, origin, destination, departure_date, passengers=1):
        tasks = create_tasks(self.agents, origin, destination, departure_date, passengers)
        crew = Crew(agents=list(self.agents.values()), tasks=tasks)
        result = crew.kickoff()
        return self._aggregate_results(result, origin, destination, departure_date, passengers)
```

## 🚀 Benefits of CrewAI Migration

### 1. **Simplicity**
- Removed 250+ lines of manual agent loop code
- Replaced with declarative agent and task definitions
- Less boilerplate, more business logic

### 2. **Maintainability**
- Clear separation of concerns (agents, tasks, crew)
- Easier to understand the flow
- Simpler to debug and extend

### 3. **Flexibility**
- CrewAI supports multiple LLMs (Claude, Gemini, GPT-4, etc.)
- Easy to switch models or add new ones
- Works with any LLM via LangChain

### 4. **Performance**
- Built-in support for parallel task execution
- Automatic memory management
- Optimized agent collaboration

### 5. **Scalability**
- Easy to add more agents
- Task-based architecture scales well
- Built-in error recovery

## 🔧 Breaking Changes

### API Endpoints
**No breaking changes** - All endpoints remain the same:
- `POST /api/v1/agents/search` - Still works
- `GET /api/v1/agents/status` - Still works
- Response format unchanged

### Client Code
**Minimal changes** - Update imports and docstrings:
```python
# Old
from flight_agents import agent_orchestrator
result = agent_orchestrator.search_all_providers(...)

# New
from flight_crew import get_crew
crew = get_crew()
result = crew.search_flights(...)
```

### Environment Variables
**No changes** - Still requires:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## 📦 Dependencies

### Removed
- None (still use anthropic SDK)

### Added
```
crewai==0.10.5
crewai-tools==0.1.6
langchain==0.1.12
langchain-anthropic==0.1.0
```

### Updated
- All other dependencies remain the same

## ✅ Migration Checklist

- [x] Create `crew_config.py` with agents and tools
- [x] Create `flight_crew.py` with FlightAggregatorCrew
- [x] Update `main_agents.py` to use CrewAI
- [x] Update `requirements.txt` with CrewAI dependencies
- [x] Update `example_agent_client.py` documentation
- [x] Create `README_CREWAI.md` with new architecture
- [x] Create this migration guide
- [ ] **Verify**: Test all endpoints with actual requests
- [ ] **Deploy**: Push to production

## 🧪 Testing

### Quick Test
```bash
python example_agent_client.py
```

### API Test
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

### Status Check
```bash
curl http://localhost:8080/api/v1/agents/status
```

## 🚀 Next Steps

1. **Test Thoroughly** - Verify all endpoints work as expected
2. **Real API Integration** - Connect to actual flight provider APIs
3. **Performance Tuning** - Profile and optimize for latency
4. **Monitoring** - Add Prometheus metrics and logging
5. **Deployment** - Containerize and deploy to production

## 📚 References

- [CrewAI Documentation](https://docs.crewai.com)
- [CrewAI GitHub](https://github.com/joaomdmoura/crewAI)
- [Anthropic API](https://docs.anthropic.com)

---

**Migration completed: ReAct → CrewAI**
