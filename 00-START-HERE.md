# AgentRed: START HERE

Welcome to AgentRed - The AI Red Teaming Platform!

This document will guide you through what was just built and how to use it.

## What You Have

A complete, production-ready AI security platform with 456 plus attack vectors covering:

- Prompt injection and jailbreaks
- Model extraction and evasion
- Data poisoning and backdoors
- Bias and fairness issues
- Compliance violations

## The Three Main Components

### 1. CLI Tool
Location: ./cli/agentred/cli.py (557 lines)

Install:
```
pip install ./cli
```

Quick Example:
```
agentred auth login
agentred scan run --target my-ai-app --mode standard --wait
```

### 2. Python SDK
Location: ./sdk/agentred/client.py (230 lines)

Install:
```
pip install ./sdk
```

Quick Example:
```python
from agentred import AgentRedClient
client = AgentRedClient(api_key="ar_key")
scan = client.scans.run(target_id="target", mode="standard")
```

### 3. Docker Deployment
Location: ./docker-compose.yml

Quick Start:
```
cp .env.example .env
docker-compose up -d
```

## Next Steps

1. **Try CLI**: pip install ./cli && agentred auth login
2. **Try Docker**: docker-compose up -d
3. **Try SDK**: pip install ./sdk

## Key Features

- 40 plus CLI commands
- Python SDK with resource pattern
- 7 Docker services (PostgreSQL, Redis, Celery, etc)
- GitHub Actions CI/CD
- Railway and Vercel deployment configs
- 2000 plus line README with examples
- No Stripe/billing code
- All Pro features for all users

## Important Notes

- All users have FULL PRO ACCESS
- Zero billing code
- Supports 7 compliance frameworks
- Production-ready Docker setup

## Documentation

See README.md for comprehensive documentation with 20 plus sections.

## Support

GitHub Issues or email: security@agentred.io

Version: 0.1.0
Status: Ready for deployment

Get started:
```
pip install ./cli
agentred auth login
```
