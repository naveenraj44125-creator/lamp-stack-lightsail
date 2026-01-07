#!/usr/bin/env node

/**
 * Test GitHub OIDC IAM role creation
 */

import { IAMClient, CreateRoleCommand, AttachRolePolicyCommand, CreatePolicyCommand, GetRoleCommand, UpdateAssumeRolePolicyCommand } from '@aws-sdk/client-iam';
import { STSClient, GetCallerIdentityCommand } from '@aws-sdk/client-sts';

const ROLE_NAME = 'github-actions-mcp-test';
const GITHUB_REPO = 'naveenraj44125-creator/mcp-test-app'; // Replace with actual repo

async function createGitHubOidcRole() {
  console.log('🔐 Creating GitHub OIDC IAM Role\n');
  console.log('=' .repeat(60));

  // Get AWS account ID
  const stsClient = new STSClient({ region: 'us-east-1' });
  const identity = await stsClient.send(new GetCallerIdentityCommand({}));
  const accountId = identity.Account;
  console.log(`\n📋 AWS Account: ${accountId}`);

  const iamClient = new IAMClient({ region: 'us-east-1' });

  // Trust policy for GitHub OIDC
  const trustPolicy = {
    Version: "2012-10-17",
    Statement: [{
      Effect: "Allow",
      Principal: {
        Federated: `arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com`
      },
      Action: "sts:AssumeRoleWithWebIdentity",
      Condition: {
        StringEquals: {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        StringLike: {
          "token.actions.githubusercontent.com:sub": [
            `repo:${GITHUB_REPO}:ref:refs/heads/main`,
            `repo:${GITHUB_REPO}:ref:refs/heads/master`,
            `repo:${GITHUB_REPO}:pull_request`
          ]
        }
      }
    }]
  };

  // Create or update role
  console.log(`\n🔨 Creating IAM role: ${ROLE_NAME}`);
  let roleArn;
  
  try {
    const createResponse = await iamClient.send(new CreateRoleCommand({
      RoleName: ROLE_NAME,
      AssumeRolePolicyDocument: JSON.stringify(trustPolicy),
      Description: `GitHub Actions OIDC role for ${GITHUB_REPO}`
    }));
    roleArn = createResponse.Role.Arn;
    console.log(`   ✅ Role created: ${roleArn}`);
  } catch (e) {
    if (e.name === 'EntityAlreadyExistsException') {
      console.log('   ℹ️ Role already exists, updating trust policy...');
      await iamClient.send(new UpdateAssumeRolePolicyCommand({
        RoleName: ROLE_NAME,
        PolicyDocument: JSON.stringify(trustPolicy)
      }));
      const getResponse = await iamClient.send(new GetRoleCommand({ RoleName: ROLE_NAME }));
      roleArn = getResponse.Role.Arn;
      console.log(`   ✅ Role updated: ${roleArn}`);
    } else {
      throw e;
    }
  }

  // Attach Lightsail policy
  console.log('\n📎 Attaching Lightsail policy...');
  const lightsailPolicyName = `${ROLE_NAME}-LightsailAccess`;
  
  try {
    await iamClient.send(new CreatePolicyCommand({
      PolicyName: lightsailPolicyName,
      PolicyDocument: JSON.stringify({
        Version: "2012-10-17",
        Statement: [{
          Effect: "Allow",
          Action: "lightsail:*",
          Resource: "*"
        }]
      }),
      Description: "Full access to AWS Lightsail"
    }));
    console.log(`   ✅ Policy created: ${lightsailPolicyName}`);
  } catch (e) {
    if (e.name === 'EntityAlreadyExistsException') {
      console.log(`   ℹ️ Policy already exists`);
    } else {
      console.log(`   ⚠️ Policy creation: ${e.message}`);
    }
  }

  try {
    await iamClient.send(new AttachRolePolicyCommand({
      RoleName: ROLE_NAME,
      PolicyArn: `arn:aws:iam::${accountId}:policy/${lightsailPolicyName}`
    }));
    console.log('   ✅ Policy attached to role');
  } catch (e) {
    console.log(`   ⚠️ Policy attachment: ${e.message}`);
  }

  // Summary
  console.log('\n' + '=' .repeat(60));
  console.log('📊 GITHUB OIDC SETUP COMPLETE\n');
  console.log(`   Role ARN: ${roleArn}`);
  console.log(`   GitHub Repo: ${GITHUB_REPO}`);
  console.log('\n   GitHub Secrets to configure:');
  console.log(`   - AWS_ROLE_ARN: ${roleArn}`);
  console.log('   - AWS_REGION: us-east-1');
  console.log('   - LIGHTSAIL_INSTANCE_NAME: mcp-test-instance');
  console.log('\n' + '=' .repeat(60));
}

createGitHubOidcRole().catch(e => {
  console.error('Failed:', e);
  process.exit(1);
});
