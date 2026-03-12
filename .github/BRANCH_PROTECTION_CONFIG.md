# Branch Protection Configuration

This file documents the branch protection rules for the `main` branch.

## To Configure Branch Protection Rules

1. Go to **Settings** → **Branches** → **Branch protection rules**
2. Click **Add rule**
3. Apply these settings for `main` branch:

### Rule Name
Pattern: `main`

### Protect Matching Branches
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: **2**
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from code owners
  
- ✅ **Require status checks to pass before merging**
  - Status checks that must pass:
    - `Tests & Quality / test`
    - `Tests & Quality / lint`
    - `Docker Build & Push / build`
  - ✅ Require branches to be up to date before merging
  
- ✅ **Require all conversations on code to be resolved before merging**

- ✅ **Include administrators**
  - ✅ Enforce all the above rules for administrators

- ✅ **Restrict who can push to matching branches**
  - Allow push access to: (select maintainers only)

## Automated Actions

The following GitHub Actions are configured:

### 1. Tests & Quality (`tests.yml`)
- Runs on every push and PR
- Tests Python code with pytest
- Linting with flake8, black, isort
- Security scanning with bandit
- Dependency check with safety
- Code coverage reporting

### 2. Docker Build (`docker-build.yml`)
- Builds Docker image on every push
- Pushes to Docker Hub on main branch push
- Uses GitHub Actions cache for faster builds

### 3. Deploy (`deploy.yml`)
- Triggers on version tags (v*)
- Deploys to Railway (backend)
- Deploys to Vercel (frontend)
- Requires secrets: RAILWAY_API_TOKEN, VERCEL_TOKEN

## Setup Instructions

### Step 1: Create Secrets
Go to **Settings** → **Secrets and variables** → **Actions**

Add these secrets:
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub access token
- `RAILWAY_API_TOKEN` - Railway.app API token (optional)
- `VERCEL_TOKEN` - Vercel deployment token (optional)

### Step 2: Configure Branch Protection
Use the GUI settings above or run via GitHub API:

```bash
# Using GitHub CLI
gh api repos/zakky8/RedAgent/branches/main/protection \
  --input - << 'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Tests & Quality / test",
      "Tests & Quality / lint",
      "Docker Build & Push / build"
    ]
  },
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1
  },
  "enforce_admins": true,
  "restrictions": null
}
JSON
```

### Step 3: Enable CODEOWNERS
Create `.github/CODEOWNERS` file:
```
# Owner of all Python code
/backend/app/ @zakky8

# Owner of frontend
/frontend/ @zakky8
```

## Expected Workflow

1. Create feature branch from `main`
2. Make changes and push
3. Create Pull Request
4. GitHub Actions run automatically:
   - Tests pass ✓
   - Linting passes ✓
   - Docker build succeeds ✓
5. Get 1-2 peer reviews
6. Merge to main
7. On tag, auto-deploy to production

## Troubleshooting

**Tests failing?**
- Check workflow logs: Actions tab → workflow run → logs
- Run tests locally: `cd backend && pytest tests/`

**Docker build failing?**
- Check Docker secrets are set
- Run locally: `docker build -t agentred:test backend/`

**Deployment failing?**
- Ensure RAILWAY_API_TOKEN and VERCEL_TOKEN are set
- Check deployment logs in Railway/Vercel dashboards
