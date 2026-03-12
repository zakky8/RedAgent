# AgentRed Monitor SDK

Real-time security monitoring SDK for AI agents. Non-blocking, privacy-first monitoring with zero impact on agent latency.

## Features

- **Zero Latency Impact**: Background asyncio tasks run completely non-blocking
- **Privacy-First**: Inputs hashed before cloud transmission, raw data never leaves your machine
- **Kill Switch**: Automatic emergency termination on critical injection detection
- **Easy Integration**: Drop-in wrapper for any LangChain or custom agent
- **Alert Channels**: Slack, email, and logging integrations
- **Local Mode**: Run monitoring without cloud connectivity for testing

## Installation

```bash
pip install agentred-monitor
```

## Quick Start

### Basic Usage

```python
from agentred_monitor import AgentRedMonitor
from langchain.agents import AgentExecutor

# Wrap your agent
agent = AgentExecutor.from_agent_and_tools(...)

monitored = AgentRedMonitor(
    agent=agent,
    api_key="ar_xxxxxxxxxxxx",
    agent_name="production-bot",
    kill_switch_enabled=True,
)

# Use exactly like the original agent
result = await monitored.ainvoke({"input": "user query"})
```

### With Alert Channels

```python
monitored = AgentRedMonitor(
    agent=agent,
    api_key="ar_xxxxxxxxxxxx",
    agent_name="production-bot",
    kill_switch_enabled=True,
    alert_channels=["slack", "email", "log"],
)
```

### Local Testing Mode

```python
monitored = AgentRedMonitor(
    agent=agent,
    api_key="ar_xxxxxxxxxxxx",
    agent_name="test-agent",
    local_mode=True,  # No cloud reporting
)
```

## API Methods

### ainvoke(input, **kwargs)

Async invoke the monitored agent.

```python
result = await monitored.ainvoke({"input": "What is 2+2?"})
```

### run(input_text, **kwargs)

Synchronous run wrapper.

```python
result = monitored.run("What is 2+2?")
```

### invoke(input, **kwargs)

Synchronous invoke wrapper.

```python
result = monitored.invoke({"input": "What is 2+2?"})
```

### get_stats()

Get current monitoring statistics.

```python
stats = monitored.get_stats()
# {
#     "total_requests": 42,
#     "anomalies": 2,
#     "blocked": 0,
#     "killed": False,
#     "agent_name": "production-bot"
# }
```

### manual_kill(reason="")

Manually kill the agent.

```python
monitored.manual_kill("Suspicious activity detected")
```

### manual_resurrect(reason="")

Resurrect a killed agent.

```python
monitored.manual_resurrect("Issue resolved")
```

### is_alive()

Check if agent is still active.

```python
if monitored.is_alive():
    result = await monitored.ainvoke({"input": "..."})
```

## Configuration Options

```python
AgentRedMonitor(
    agent=agent,                           # Required: The AI agent to monitor
    api_key="ar_xxxxxxxxxxxx",             # Required: AgentRed API key
    agent_name="my-agent",                 # Optional: Human-readable name
    api_url="https://api.agentred.io",     # Optional: API endpoint
    kill_switch_enabled=True,              # Optional: Enable auto kill switch
    alert_channels=["slack", "email"],     # Optional: Alert destinations
    local_mode=False,                      # Optional: Disable cloud reporting
)
```

## How It Works

1. **Request Monitoring**: When the agent receives input, the timestamp is recorded
2. **Non-Blocking Analysis**: Background asyncio task analyzes for injection patterns
3. **Hash Privacy**: Input and output are hashed using SHA256 before transmission
4. **Anomaly Detection**: Injection score calculated (0-1) for suspicious patterns
5. **Cloud Reporting**: Hashed events sent to AgentRed API (if not in local mode)
6. **Kill Switch**: If score exceeds threshold (0.95), agent is automatically terminated

## Injection Detection Patterns

The monitor detects common prompt injection patterns:

- "ignore previous instructions"
- "jailbreak"
- "dan mode"
- "system override"
- "forget your instructions"
- And many more...

Detection is probabilistic: multiple patterns increase the confidence score.

## Performance Impact

- **Zero latency on main request**: Analysis runs in background
- **Memory**: ~10 MB overhead per monitor instance
- **CPU**: Minimal (hash computation only)
- **Network**: Async HTTP with 5s timeout (non-blocking)

## Privacy Guarantees

- Raw inputs **never** transmitted to cloud
- All inputs hashed with SHA256 before sending
- Only hashes, scores, and metadata sent to AgentRed
- Local mode option available for air-gapped environments

## Compatibility

- Python 3.10+
- LangChain agents
- Custom agents with `ainvoke()`, `run()`, or `invoke()` methods
- Async and sync execution patterns

## Error Handling

The monitor is designed to be non-intrusive:

- If cloud API is unreachable, monitoring silently degrades
- Background analysis errors never propagate to user code
- Kill switch errors logged but don't crash agent
- All exceptions are caught and logged

## Advanced Usage

### Custom Injection Patterns

```python
class CustomMonitor(AgentRedMonitor):
    def _detect_injection(self, text: str) -> float:
        # Implement custom detection logic
        score = super()._detect_injection(text)
        # Add custom checks
        return score
```

### Integration with External Systems

```python
async def on_anomaly(event):
    # Custom handler for anomalies
    await send_to_security_team(event)

monitored._analyze_background = on_anomaly
```

## Troubleshooting

### Agent doesn't respond

Check if the agent has been killed:

```python
if not monitored.is_alive():
    monitored.manual_resurrect("Restarting after maintenance")
```

### Missing monitoring events

Verify API key and network connectivity:

```python
monitored.local_mode = False  # Enable cloud reporting
```

### High injection scores on legitimate input

Adjust detection patterns or increase threshold before kill switch triggers.

## Support

- Documentation: https://docs.agentred.io/monitor
- Issues: https://github.com/agentred/monitor/issues
- Email: support@agentred.io

## License

Apache 2.0 - See LICENSE for details

## Changelog

### 0.1.0 (Initial Release)

- Core monitoring functionality
- Non-blocking background analysis
- Kill switch mechanism
- Multiple alert channels
- Privacy-first hashing
