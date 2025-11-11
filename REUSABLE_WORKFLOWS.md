# Reusable Workflows & Actions Guide

This repository provides reusable GitHub Actions workflows and composite actions that can be used across multiple repositories for deploying applications to AWS Lightsail.

## 📋 Table of Contents

- [Reusable Workflow](#reusable-workflow)
- [Composite Action](#composite-action)
- [Setup Requirements](#setup-requirements)
- [Examples](#examples)
- [Configuration](#configuration)

---

## 🔄 Reusable Workflow

### Usage in Other Repositories

To use the reusable workflow in another repository, create a workflow file (e.g., `.github/workflows/deploy.yml`):

```yaml
name: Deploy Application

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    uses: YOUR-USERNAME/YOUR-REPO/.github/workflows/deploy-generic-reusable.yml@main
    with:
      config_file: 'deployment-generic.config.yml'
      # Optional: override config values
      # aws_region: 'us-east-1'
      # instance_name: 'my-instance'
      skip_tests: false
      environment: 'production'  # Optional: use GitHub environments
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `config_file` | No | `deployment-generic.config.yml` | Path to deployment config |
| `aws_region` | No | (from config) | AWS region override |
| `instance_name` | No | (from config) | Instance name override |
| `skip_tests` | No | `false` | Skip test execution |
| `environment` | No | - | GitHub environment name |

### Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `AWS_ACCESS_KEY_ID` | Yes | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS secret key |

### Outputs

| Output | Description |
|--------|-------------|
| `deployment_url` | URL of deployed application |
| `deployment_status` | Status: `success` or `failed` |

### Example with Outputs

```yaml
jobs:
  deploy:
    uses: YOUR-USERNAME/YOUR-REPO/.github/workflows/deploy-generic-reusable.yml@main
    with:
      config_file: 'deployment-generic.config.yml'
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  
  notify:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - name: Send notification
        run: |
          echo "Deployed to: ${{ needs.deploy.outputs.deployment_url }}"
          echo "Status: ${{ needs.deploy.outputs.deployment_status }}"
```

---

## 🎯 Composite Action

### Usage in Other Repositories

To use the composite action, reference it in your workflow:

```yaml
name: Deploy with Action

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Checkout deployment scripts
        uses: actions/checkout@v4
        with:
          repository: YOUR-USERNAME/YOUR-REPO
          path: .deployment-scripts
      
      - name: Copy deployment files
        run: |
          cp -r .deployment-scripts/workflows ./
          cp .deployment-scripts/deployment-generic.config.yml ./
      
      - name: Deploy to Lightsail
        uses: YOUR-USERNAME/YOUR-REPO/.github/actions/deploy-lightsail@main
        with:
          config-file: 'deployment-generic.config.yml'
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          skip-tests: false
          verify-deployment: true
      
      - name: Show deployment URL
        run: echo "Deployed to ${{ steps.deploy.outputs.deployment-url }}"
```

### Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `config-file` | No | `deployment-generic.config.yml` | Config file path |
| `aws-access-key-id` | Yes | - | AWS access key |
| `aws-secret-access-key` | Yes | - | AWS secret key |
| `aws-region` | No | (from config) | AWS region override |
| `instance-name` | No | (from config) | Instance name override |
| `skip-tests` | No | `false` | Skip tests |
| `verify-deployment` | No | `true` | Verify after deploy |

### Outputs

| Output | Description |
|--------|-------------|
| `deployment-url` | Application URL |
| `deployment-status` | Deployment status |
| `static-ip` | Instance static IP |

---

## 🔧 Setup Requirements

### In the Calling Repository

1. **Create config file** (`deployment-generic.config.yml`):

```yaml
aws:
  region: us-east-1

lightsail:
  instance_name: my-app-instance
  static_ip: 1.2.3.4

application:
  name: my-app
  type: web
  version: 1.0.0
  package_files:
    - index.php
    - config/
  package_fallback: true

dependencies:
  php:
    enabled: true
    version: "8.1"
  mysql:
    enabled: true
    version: "8.0"

github_actions:
  triggers:
    push_branches:
      - main
  jobs:
    test:
      enabled: true
```

2. **Add GitHub Secrets**:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

3. **For Composite Action**: Copy the `workflows/` directory from this repo to your repo

---

## 📚 Examples

### Example 1: Simple Deployment

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    uses: YOUR-USERNAME/YOUR-REPO/.github/workflows/deploy-generic-reusable.yml@main
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### Example 2: Multi-Environment Deployment

```yaml
name: Deploy to Environments

on:
  push:
    branches: [main, staging]

jobs:
  deploy-staging:
    if: github.ref == 'refs/heads/staging'
    uses: YOUR-USERNAME/YOUR-REPO/.github/workflows/deploy-generic-reusable.yml@main
    with:
      config_file: 'deployment-staging.config.yml'
      environment: 'staging'
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.STAGING_AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.STAGING_AWS_SECRET_ACCESS_KEY }}
  
  deploy-production:
    if: github.ref == 'refs/heads/main'
    uses: YOUR-USERNAME/YOUR-REPO/.github/workflows/deploy-generic-reusable.yml@main
    with:
      config_file: 'deployment-production.config.yml'
      environment: 'production'
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.PROD_AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.PROD_AWS_SECRET_ACCESS_KEY }}
```

### Example 3: Manual Deployment with Inputs

```yaml
name: Manual Deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        type: choice
        options:
          - staging
          - production
      skip_tests:
        description: 'Skip tests'
        type: boolean
        default: false

jobs:
  deploy:
    uses: YOUR-USERNAME/YOUR-REPO/.github/workflows/deploy-generic-reusable.yml@main
    with:
      config_file: 'deployment-${{ inputs.environment }}.config.yml'
      skip_tests: ${{ inputs.skip_tests }}
      environment: ${{ inputs.environment }}
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### Example 4: Using Specific Version/Tag

```yaml
jobs:
  deploy:
    # Use specific version tag
    uses: YOUR-USERNAME/YOUR-REPO/.github/workflows/deploy-generic-reusable.yml@v1.0.0
    # Or use specific commit
    # uses: YOUR-USERNAME/YOUR-REPO/.github/workflows/deploy-generic-reusable.yml@abc123
    # Or use branch
    # uses: YOUR-USERNAME/YOUR-REPO/.github/workflows/deploy-generic-reusable.yml@main
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

---

## 🔐 Configuration

### GitHub Environments (Optional)

For better security and approval workflows, use GitHub Environments:

1. Go to repository Settings → Environments
2. Create environment (e.g., "production")
3. Add protection rules:
   - Required reviewers
   - Wait timer
   - Deployment branches
4. Add environment secrets

Then use in workflow:

```yaml
jobs:
  deploy:
    uses: YOUR-USERNAME/YOUR-REPO/.github/workflows/deploy-generic-reusable.yml@main
    with:
      environment: 'production'  # Uses environment protection rules
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

---

## 🏷️ Versioning

### Creating Releases

To version your reusable workflows:

```bash
# Tag a release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Update major version tag
git tag -fa v1 -m "Update v1 to v1.0.0"
git push origin v1 --force
```

Users can then reference:
- `@v1` - Latest v1.x.x (recommended)
- `@v1.0.0` - Specific version
- `@main` - Latest (not recommended for production)

---

## 🐛 Troubleshooting

### Common Issues

1. **"Workflow not found"**
   - Ensure the workflow file exists in the source repo
   - Check the path and branch/tag reference
   - Verify the source repo is public or you have access

2. **"Required secrets not provided"**
   - Add AWS credentials to repository secrets
   - Check secret names match exactly

3. **"Config file not found"**
   - Ensure `deployment-generic.config.yml` exists in calling repo
   - Or specify custom path with `config_file` input

4. **"Python scripts not found"**
   - For composite action: Copy `workflows/` directory to your repo
   - For reusable workflow: Scripts are in the source repo

---

## 📝 Notes

- **Reusable Workflow**: Best for complete CI/CD pipelines, runs in separate job context
- **Composite Action**: Best for reusable steps within a job, shares job context
- Both approaches support the same deployment configuration
- Workflows can be versioned with tags for stability
- Use GitHub Environments for production deployments with approval gates

---

## 🤝 Contributing

To improve these reusable workflows:

1. Fork the repository
2. Make changes
3. Test with your own repositories
4. Submit a pull request

---

## 📄 License

[Your License Here]
