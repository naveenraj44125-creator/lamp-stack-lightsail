#!/usr/bin/env node

/**
 * Deploy Demo App - Creates Lightsail instance, GitHub repo, and deploys via GitHub Actions
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { LightsailClient, CreateInstancesCommand, GetInstanceCommand } from '@aws-sdk/client-lightsail';
import { IAMClient, CreateRoleCommand, AttachRolePolicyCommand, CreatePolicyCommand, GetRoleCommand, UpdateAssumeRolePolicyCommand } from '@aws-sdk/client-iam';
import { STSClient, GetCallerIdentityCommand } from '@aws-sdk/client-sts';
import { fromEnv } from '@aws-sdk/credential-providers';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CONFIG = {
  appName: 'demo-app',
  repoName: 'mcp-demo-app',
  githubUsername: 'naveenraj44125-creator',
  awsRegion: 'us-east-1',
  demoAppPath: path.join(__dirname, '..', 'demo-app')
};

const run = (cmd, opts = {}) => {
  console.log(`$ ${cmd}`);
  try {
    return execSync(cmd, { encoding: 'utf8', stdio: opts.silent ? 'pipe' : 'inherit', ...opts });
  } catch (e) {
    if (opts.ignoreError) return null;
    throw e;
  }
};

async function getAwsAccountId() {
  const client = new STSClient({ region: CONFIG.awsRegion, credentials: fromEnv() });
  return (await client.send(new GetCallerIdentityCommand({}))).Account;
}

async function createInstance(name) {
  const client = new LightsailClient({ region: CONFIG.awsRegion, credentials: fromEnv() });
  try {
    const existing = await client.send(new GetInstanceCommand({ instanceName: name }));
    if (existing.instance) return console.log(`✅ Instance ${name} exists`) || existing.instance;
  } catch (e) {}
  
  await client.send(new CreateInstancesCommand({
    instanceNames: [name], blueprintId: 'ubuntu_22_04', bundleId: 'nano_3_0',
    availabilityZone: `${CONFIG.awsRegion}a`
  }));
  console.log(`✅ Instance ${name} creating...`);
}

async function waitForInstance(name) {
  const client = new LightsailClient({ region: CONFIG.awsRegion, credentials: fromEnv() });
  for (let i = 0; i < 30; i++) {
    try {
      const r = await client.send(new GetInstanceCommand({ instanceName: name }));
      if (r.instance?.state?.name === 'running' && r.instance?.publicIpAddress) return r.instance;
    } catch (e) {}
    console.log('⏳ Waiting for instance...');
    await new Promise(r => setTimeout(r, 10000));
  }
  throw new Error('Timeout waiting for instance');
}

async function createIamRole(roleName, repo, accountId) {
  const client = new IAMClient({ region: CONFIG.awsRegion, credentials: fromEnv() });
  const trustPolicy = {
    Version: "2012-10-17",
    Statement: [{
      Effect: "Allow",
      Principal: { Federated: `arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com` },
      Action: "sts:AssumeRoleWithWebIdentity",
      Condition: {
        StringEquals: { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
        StringLike: { "token.actions.githubusercontent.com:sub": [`repo:${repo}:*`] }
      }
    }]
  };
  
  let roleArn;
  try {
    roleArn = (await client.send(new CreateRoleCommand({
      RoleName: roleName, AssumeRolePolicyDocument: JSON.stringify(trustPolicy)
    }))).Role.Arn;
  } catch (e) {
    if (e.name === 'EntityAlreadyExistsException') {
      await client.send(new UpdateAssumeRolePolicyCommand({ RoleName: roleName, PolicyDocument: JSON.stringify(trustPolicy) }));
      roleArn = (await client.send(new GetRoleCommand({ RoleName: roleName }))).Role.Arn;
    } else throw e;
  }
  
  const policyName = `${roleName}-Lightsail`;
  try {
    await client.send(new CreatePolicyCommand({
      PolicyName: policyName,
      PolicyDocument: JSON.stringify({ Version: "2012-10-17", Statement: [{ Effect: "Allow", Action: "lightsail:*", Resource: "*" }] })
    }));
  } catch (e) {}
  try {
    await client.send(new AttachRolePolicyCommand({ RoleName: roleName, PolicyArn: `arn:aws:iam::${accountId}:policy/${policyName}` }));
  } catch (e) {}
  
  return roleArn;
}

const workflow = (instanceName) => `name: Deploy
on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: \${{ secrets.AWS_ROLE_ARN }}
          aws-region: \${{ secrets.AWS_REGION }}
      - id: ip
        run: echo "ip=$(aws lightsail get-instance --instance-name ${instanceName} --query 'instance.publicIpAddress' --output text)" >> $GITHUB_OUTPUT
      - name: Deploy via SSH
        run: |
          # Get SSH key
          aws lightsail download-default-key-pair --query 'privateKey' --output text > key.pem
          chmod 600 key.pem
          
          # Setup SSH
          mkdir -p ~/.ssh
          ssh-keyscan -H \${{ steps.ip.outputs.ip }} >> ~/.ssh/known_hosts 2>/dev/null
          
          # Create app directory
          ssh -i key.pem -o StrictHostKeyChecking=no ubuntu@\${{ steps.ip.outputs.ip }} "mkdir -p ~/app"
          
          # Copy files
          scp -i key.pem -r package.json src ubuntu@\${{ steps.ip.outputs.ip }}:~/app/
          
          # Install and run
          ssh -i key.pem ubuntu@\${{ steps.ip.outputs.ip }} << 'ENDSSH'
            cd ~/app
            
            # Install Node.js if needed
            if ! command -v node &> /dev/null; then
              curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
              sudo apt-get install -y nodejs
            fi
            
            # Install PM2
            sudo npm install -g pm2 2>/dev/null || true
            
            # Install deps and start
            npm install --production
            pm2 delete demo 2>/dev/null || true
            pm2 start src/server.js --name demo
            pm2 save
          ENDSSH
          
          rm -f key.pem
      - name: Verify
        run: |
          sleep 5
          curl -f http://\${{ steps.ip.outputs.ip }}:3000/health
          echo ""
          echo "✅ App deployed to http://\${{ steps.ip.outputs.ip }}:3000"
`;

async function main() {
  console.log('🚀 MCP Demo App Deployment\n');
  
  const instanceName = `nodejs-${CONFIG.appName}`;
  const roleName = `gh-${instanceName}`;
  const repo = `${CONFIG.githubUsername}/${CONFIG.repoName}`;

  // 1. Create GitHub repo
  console.log('📦 Creating GitHub repo...');
  run(`gh repo delete ${repo} --yes`, { ignoreError: true, silent: true });
  run(`gh repo create ${CONFIG.repoName} --public -d "MCP Demo App"`);

  // 2. AWS setup
  console.log('\n☁️ Setting up AWS...');
  const accountId = await getAwsAccountId();
  await createInstance(instanceName);
  const roleArn = await createIamRole(roleName, repo, accountId);
  console.log(`✅ Role: ${roleArn}`);

  // 3. GitHub secrets
  console.log('\n🔑 Setting secrets...');
  run(`gh secret set AWS_ROLE_ARN --repo ${repo} -b "${roleArn}"`, { silent: true });
  run(`gh secret set AWS_REGION --repo ${repo} -b "${CONFIG.awsRegion}"`, { silent: true });

  // 4. Push code
  console.log('\n📤 Pushing code...');
  const tmp = '/tmp/mcp-demo';
  run(`rm -rf ${tmp}`, { ignoreError: true, silent: true });
  fs.cpSync(CONFIG.demoAppPath, tmp, { recursive: true });
  fs.mkdirSync(`${tmp}/.github/workflows`, { recursive: true });
  fs.writeFileSync(`${tmp}/.github/workflows/deploy.yml`, workflow(instanceName));
  fs.writeFileSync(`${tmp}/.gitignore`, 'node_modules/\n');
  
  run('git init && git add . && git commit -m "Deploy"', { cwd: tmp, silent: true });
  run(`git branch -M main && git remote add origin https://github.com/${repo}.git && git push -uf origin main`, { cwd: tmp });

  // 5. Wait for instance
  console.log('\n⏳ Waiting for instance...');
  const instance = await waitForInstance(instanceName);
  
  // 6. Wait for workflow
  console.log('\n🔄 Waiting for GitHub Actions...');
  for (let i = 0; i < 24; i++) {
    await new Promise(r => setTimeout(r, 10000));
    const result = run(`gh run list --repo ${repo} -L1 --json conclusion -q '.[0].conclusion'`, { silent: true })?.trim();
    if (result === 'success') { console.log('✅ Workflow passed!'); break; }
    if (result === 'failure') { console.log('❌ Workflow failed'); break; }
    console.log('⏳ Workflow running...');
  }

  // 7. Verify
  console.log('\n🌐 Verifying...');
  await new Promise(r => setTimeout(r, 5000));
  const health = run(`curl -s http://${instance.publicIpAddress}:3000/health`, { silent: true });
  console.log(`Health: ${health}`);

  console.log(`
${'='.repeat(50)}
✅ DONE!
${'='.repeat(50)}
🌐 Open: http://${instance.publicIpAddress}:3000
📦 Repo: https://github.com/${repo}
`);
}

main().catch(console.error);
