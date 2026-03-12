# AgentRed: AI Red Teaming Platform

AgentRed is a comprehensive AI security platform designed to identify vulnerabilities in Large Language Models and AI systems through adversarial testing. With **456+ attack vectors** across multiple categories, AgentRed helps organizations evaluate and harden their AI applications before deployment.

## Key Features

- **Comprehensive Attack Library**: 456+ adversarial attack patterns covering:
  - Prompt Injection & Jailbreaks
  - Model Extraction & Evasion
  - Data Poisoning & Backdoors
  - Bias & Fairness Issues
  - Safety Violation Attempts
  - Role-Playing Attacks
  - Information Disclosure
  - Compliance Violations

- **Multi-LLM Support**: Test Claude, GPT-4, Gemini, Llama, and custom endpoints
- **Risk Scoring & ASR**: Attack Success Rate (ASR) and automated risk scoring
- **Compliance Frameworks**: EU AI Act, NIST AI RMF, SOC 2, ISO 27001
- **Beautiful Reports**: Executive, Technical, and EU AI Act compliance reports (PDF)
- **CI/CD Integration**: Seamless integration into your deployment pipelines
- **Full Pro Access**: All users have complete platform access during beta

## Tech Stack

- **Backend**: FastAPI (Python 3.12), SQLAlchemy + PostgreSQL with pgvector
- **Async Jobs**: Celery + Redis for distributed attack execution
- **Frontend**: Next.js 14 with React + TypeScript
- **Monitoring**: Flower for Celery task monitoring
- **Containerization**: Docker & Docker Compose
- **Deployment**: Railway (backend), Vercel (frontend)

## Quick Start (5 minutes)

### Prerequisites

- Docker & Docker Compose (or Python 3.12+, Node.js 20+)
- API keys for AI models (Anthropic, OpenAI, etc.)

### Option 1: Docker Compose (Recommended)

```bash
git clone https://github.com/yourusername/agentred.git
cd agentred

# Copy environment template
cp .env.example .env

# Add your API keys
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
export OPENAI_API_KEY="sk-xxxxx"

# Start all services
docker-compose up -d

# Wait for services to be healthy
docker-compose ps

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# Flower (Celery): http://localhost:5555
```

### Option 2: Local Development

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
cp ../.env.example ../.env

# Update .env with your API keys
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

## CLI Usage Examples

### Installation

```bash
# From source
pip install ./cli

# Verify installation
agentred --version
```

### Authentication

```bash
# Configure API credentials
agentred auth login
# Prompted for API key: ar_xxxxxxxxxxxxxxxx

# Verify authentication
agentred auth whoami

# Remove credentials
agentred auth logout
```

### Running Scans

```bash
# Quick scan with default settings
agentred scan run --target my-gpt-wrapper

# Standard scan with specific categories
agentred scan run \
  --target my-api \
  --mode standard \
  --categories "prompt_injection,jailbreak,data_extraction"

# Deep scan with severity threshold for CI/CD
agentred scan run \
  --target production-model \
  --mode deep \
  --fail-on-severity critical \
  --output json

# Async scan (returns immediately)
agentred scan run \
  --target my-target \
  --async
```

### Monitoring Scans

```bash
# List all scans
agentred scan list

# Filter by status
agentred scan list --status completed --limit 10

# Check specific scan status
agentred scan status scan-uuid-1234

# Get detailed results
agentred scan results scan-uuid-1234 --format table

# Filter by severity
agentred scan results scan-uuid-1234 --severity critical
```

### Generating Reports

```bash
# Executive summary
agentred report generate scan-uuid-1234 --type executive

# Technical deep-dive
agentred report generate scan-uuid-1234 --type technical

# EU AI Act compliance
agentred report generate scan-uuid-1234 --type eu_ai_act

# Remediation guide
agentred report generate scan-uuid-1234 --type remediation
```

### Target Management

```bash
# List all targets
agentred target list

# Register new LLM target
agentred target add \
  --name "Production GPT" \
  --type openai \
  --endpoint "https://api.example.com/v1/chat/completions" \
  --api-key "sk-xxxxx"

# Test connection to target
agentred target add \
  --name "Claude API" \
  --type anthropic \
  --endpoint "https://api.anthropic.com/v1" \
  --api-key "sk-ant-xxxxx"
```

### Compliance

```bash
# Run compliance assessment
agentred compliance assess scan-uuid-1234 \
  --frameworks "eu_ai_act,nist_ai_rmf,soc2"

# View overall compliance posture
agentred compliance posture
```

### Configuration

```bash
# View current configuration
agentred config show

# Set custom API URL
agentred config set api-url https://custom.agentred.io

# Set via environment
export AGENTRED_API_KEY="ar_xxxxxxxxxxxxxxxx"
export AGENTRED_API_URL="https://api.agentred.io"
agentred scan list
```

## Python SDK Usage Examples

### Installation

```bash
pip install ./sdk
```

### Basic Usage

```python
from agentred import AgentRedClient

client = AgentRedClient(api_key="ar_xxxxxxxxxxxxxxxx")

# Create a target
target = client.targets.create(
    name="My GPT Wrapper",
    endpoint_url="https://api.example.com/chat",
    model_type="openai",
    auth_config={"api_key": "sk-xxxxx"}
)
print(f"Target created: {target['id']}")

# Run a scan and wait for completion
scan = client.scans.run(
    target_id=target['id'],
    mode="standard",
    categories=["prompt_injection", "jailbreak"]
)
print(f"Scan completed: {scan['id']}, Risk Score: {scan['risk_score']}")
```

### Async Scanning

```python
# Start scan without waiting
scan = client.scans.create(
    target_id="target-uuid",
    mode="deep",
    categories=["all"]
)
scan_id = scan['id']

# Poll for completion
import time
while True:
    status = client.scans.get(scan_id)
    if status['status'] in ('completed', 'failed'):
        break
    print(f"Status: {status['status']}")
    time.sleep(10)

# Get results
results = client.scans.results(scan_id, severity="critical")
for attack in results:
    print(f"{attack['attack_name']}: {attack['severity']}")
```

### Report Generation

```python
# Generate executive report
report = client.reports.generate(
    scan_id=scan_id,
    report_type="executive"
)
print(f"Report: {report['file_url']}")

# List all reports
reports = client.reports.list()
for r in reports:
    print(f"{r['id']}: {r['report_type']}")
```

### Compliance Assessment

```python
# Assess compliance
assessment = client.compliance.assess(
    scan_id=scan_id,
    frameworks=["eu_ai_act", "nist_ai_rmf", "soc2"]
)

print(f"EU AI Act Compliance: {assessment['eu_ai_act']['score']}%")
print(f"NIST AI RMF: {assessment['nist_ai_rmf']['score']}%")

# Organization-wide posture
posture = client.compliance.posture()
print(f"Overall Risk: {posture['risk_level']}")
```

### Error Handling

```python
import httpx

try:
    scan = client.scans.get("invalid-id")
except httpx.HTTPStatusError as e:
    if e.response.status_code == 404:
        print("Scan not found")
    else:
        print(f"API Error: {e.response.status_code}")
except Exception as e:
    print(f"Error: {e}")
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Test LLM Safety
on: [push]

jobs:
  agentred-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run AgentRed Scan
        env:
          AGENTRED_API_KEY: ${{ secrets.AGENTRED_API_KEY }}
        run: |
          pip install agentred
          agentred scan run \
            --target production-llm \
            --mode deep \
            --fail-on-severity high \
            --wait
```

### Pre-deployment Check

```bash
#!/bin/bash
set -e

echo "Running AgentRed security scan..."
agentred scan run \
  --target "$LLM_ENDPOINT" \
  --mode standard \
  --fail-on-severity critical

echo "Scan passed. Proceeding with deployment."
```

## Architecture

### Backend Services (Docker Compose)

1. **postgres**: PostgreSQL 16 with pgvector extension
2. **redis**: Redis for caching and Celery task queue
3. **backend**: FastAPI server (port 8000)
4. **worker**: Celery worker for distributed attack execution
5. **beat**: Celery Beat scheduler for periodic tasks
6. **flower**: Celery monitoring UI (port 5555)
7. **frontend**: Next.js application (port 3000)

### Database Schema

- **Users**: Authentication and organization management
- **Targets**: LLM endpoints and credentials
- **Scans**: Security audit records
- **Attacks**: Individual attack results
- **Reports**: Generated compliance and security reports
- **Compliance Assessments**: Framework evaluation results

## Environment Variables

```
DATABASE_URL           # PostgreSQL connection string
REDIS_URL             # Redis connection string
SECRET_KEY            # JWT signing key (32+ chars)
ANTHROPIC_API_KEY     # For Claude-based attacks
OPENAI_API_KEY        # For GPT-4 comparison testing
OLLAMA_BASE_URL       # Optional local LLM endpoint
ENVIRONMENT           # "development" or "production"
LOG_LEVEL             # DEBUG, INFO, WARNING, ERROR
NEXT_PUBLIC_API_URL   # Frontend API endpoint
```

## Deployment

### Railway

```bash
# Deploy backend to Railway
railway init
railway up

# Set environment variables
railway variables add ANTHROPIC_API_KEY=sk-ant-xxxxx
railway variables add OPENAI_API_KEY=sk-xxxxx
```

### Vercel (Frontend)

```bash
# Deploy frontend
vercel deploy

# Configure environment
vercel env add NEXT_PUBLIC_API_URL
```

### Self-Hosted (VPS)

```bash
docker-compose -f docker-compose.yml up -d

# Enable auto-restart
docker-compose restart --no-deps backend worker beat
```

## Monitoring & Logs

### View Logs

```bash
# Backend logs
docker-compose logs -f backend

# Worker logs
docker-compose logs -f worker

# All services
docker-compose logs -f
```

### Flower Monitoring

Visit http://localhost:5555 to monitor:
- Active tasks
- Worker health
- Task execution history
- Real-time statistics

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-attack`)
3. Make your changes
4. Run tests: `pytest backend/tests/`
5. Submit a pull request

### Development Workflow

```bash
# Set up dev environment
docker-compose up -d
docker-compose logs -f backend

# Make changes
# Tests run automatically on push

# Check code quality
ruff check backend/
mypy backend/
```

## Support & Community

- GitHub Issues: Report bugs and request features
- Discussions: Connect with other security researchers
- Email: security@agentred.io

## License

MIT License - See LICENSE.md for details

## Security Notice

AgentRed is designed for authorized security testing only. Always obtain proper authorization before testing AI systems you don't own or operate.

---

Built with by the AgentRed team. During beta, all users have full Pro access to all features.
