# AgentRed JavaScript/TypeScript SDK

Official JavaScript/TypeScript SDK for the AgentRed AI Red Teaming Platform. Provides type-safe access to all AgentRed API endpoints for automated security testing of AI systems.

## Installation

```bash
npm install agentred
# or
yarn add agentred
```

## Quick Start

```typescript
import { AgentRedClient } from 'agentred';

const client = new AgentRedClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.agentred.io',
});

// Create a target
const target = await client.targets.create({
  name: 'My LLM Application',
  adapter_type: 'openai',
  config: {
    api_key: 'sk-...',
    model: 'gpt-4'
  }
});

// Start a security scan
const scan = await client.scans.create({
  target_id: target.id,
  attack_categories: ['prompt-injection', 'jailbreak'],
  max_attacks: 50
});

// Wait for completion
const completed = await client.scans.waitForCompletion(scan.id);

// Get results
const results = await client.scans.getResults(scan.id);
results.forEach(result => {
  console.log(`${result.attack_name}: ${result.severity}`);
});

// Generate report
const report = await client.reports.generate(scan.id, 'executive');
```

## Authentication

Initialize the client with your API key:

```typescript
const client = new AgentRedClient({
  apiKey: process.env.AGENTRED_API_KEY
});
```

## API Reference

### Targets

Manage test targets (LLM applications, APIs, chatbots).

```typescript
// List all targets
const targets = await client.targets.list();

// Create a new target
const target = await client.targets.create({
  name: 'GPT-4 API',
  adapter_type: 'openai',
  config: {
    api_key: 'sk-...',
    model: 'gpt-4'
  }
});

// Get target details
const target = await client.targets.get('target-id');

// Update target configuration
await client.targets.update('target-id', {
  config: { model: 'gpt-4-turbo' }
});

// Test connection to target
const test = await client.targets.testConnection('target-id');

// Delete target
await client.targets.delete('target-id');
```

### Scans

Execute security scans against targets.

```typescript
// Create a new scan
const scan = await client.scans.create({
  target_id: 'target-id',
  attack_categories: ['prompt-injection'],
  max_attacks: 100,
  stop_on_critical: true
});

// List scans
const page = await client.scans.list({
  page: 1,
  per_page: 20,
  status: 'completed'
});

// Get scan details
const scan = await client.scans.get('scan-id');

// Get attack results
const results = await client.scans.getResults('scan-id');

// Wait for scan completion (polls every 5 seconds)
const completed = await client.scans.waitForCompletion('scan-id');

// Cancel running scan
await client.scans.cancel('scan-id');
```

### Reports

Generate and download security reports.

```typescript
// List available reports
const reports = await client.reports.list();

// Generate a new report
const report = await client.reports.generate('scan-id', 'executive');
// Types: 'executive', 'technical', 'detailed'

// Get report details
const report = await client.reports.get('report-id');

// Download report as PDF/JSON
const buffer = await client.reports.download('report-id');
fs.writeFileSync('report.pdf', buffer);
```

### Compliance

Assess compliance against security frameworks.

```typescript
// List available compliance frameworks
const frameworks = await client.compliance.listFrameworks();
// ['NIST', 'ISO27001', 'CIS', 'OWASP']

// Run compliance assessment
const assessment = await client.compliance.assess('scan-id', 'NIST');

// Get assessment details
const assessment = await client.compliance.getAssessment('assessment-id');

// Get compliance summary for scan
const summary = await client.compliance.getSummary('scan-id');
```

### Attacks

Query available attacks and statistics.

```typescript
// List all attacks
const attacks = await client.attacks.list();

// Filter by category
const injectionAttacks = await client.attacks.list('prompt-injection');

// Get attack categories
const categories = await client.attacks.getCategories();

// Get attack statistics
const stats = await client.attacks.getStats();
```

### Health Check

```typescript
// Check API connectivity
const isHealthy = await client.ping();
```

## Error Handling

```typescript
import { AgentRedClient, AgentRedAuthError, AgentRedRateLimitError, AgentRedError } from 'agentred';

try {
  const scan = await client.scans.create({...});
} catch (error) {
  if (error instanceof AgentRedAuthError) {
    console.error('Authentication failed', error.message);
  } else if (error instanceof AgentRedRateLimitError) {
    console.error('Rate limited, retry after delay');
  } else if (error instanceof AgentRedError) {
    console.error(`API Error (${error.statusCode}):`, error.message);
  }
}
```

## Configuration

### Timeout

Set custom request timeout (milliseconds):

```typescript
const client = new AgentRedClient({
  apiKey: 'your-key',
  timeout: 120000 // 2 minutes
});
```

### Custom Base URL

For self-hosted deployments:

```typescript
const client = new AgentRedClient({
  apiKey: 'your-key',
  baseUrl: 'https://agentred.internal.company.com'
});
```

## Examples

### Basic Security Scan

```typescript
async function runSecurityScan() {
  const client = new AgentRedClient({ apiKey: process.env.AGENTRED_API_KEY });

  // Create target
  const target = await client.targets.create({
    name: 'Production ChatBot',
    adapter_type: 'openai',
    config: {
      api_key: process.env.OPENAI_API_KEY,
      model: 'gpt-4'
    }
  });

  // Run scan
  const scan = await client.scans.create({
    target_id: target.id,
    attack_categories: ['prompt-injection', 'jailbreak', 'data-exfiltration'],
    max_attacks: 200,
    stop_on_critical: true
  });

  // Wait and get results
  await client.scans.waitForCompletion(scan.id);
  const results = await client.scans.getResults(scan.id);

  console.log(`Total Attacks: ${results.length}`);
  console.log(`Successful: ${results.filter(r => r.success).length}`);
  console.log(`Critical: ${results.filter(r => r.severity === 'critical').length}`);
}
```

### Compliance Reporting

```typescript
async function generateComplianceReport() {
  const client = new AgentRedClient({ apiKey: process.env.AGENTRED_API_KEY });

  // Get existing scan
  const scan = await client.scans.get('scan-id');

  // Assess against frameworks
  const nistAssessment = await client.compliance.assess(scan.id, 'NIST');
  const iso27001Assessment = await client.compliance.assess(scan.id, 'ISO27001');

  console.log(`NIST Score: ${nistAssessment.percentage}%`);
  console.log(`ISO 27001 Score: ${iso27001Assessment.percentage}%`);

  // List compliance gaps
  console.log('Gaps found:');
  nistAssessment.gaps.forEach(gap => console.log(`  - ${gap}`));
}
```

## Development

### Build TypeScript

```bash
npm run build
```

### Run Tests

```bash
npm test
```

### Lint

```bash
npm run lint
```

## License

MIT

## Support

- Documentation: https://docs.agentred.io
- GitHub Issues: https://github.com/agentred/agentred-node/issues
- Email: support@agentred.io
