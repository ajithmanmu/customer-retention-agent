# Customer Retention Agent - Deployment Guide

This guide provides step-by-step instructions for deploying the Customer Retention Agent infrastructure.

## 📋 Prerequisites

- AWS CLI configured with appropriate permissions
- SAM CLI installed
- Python 3.9+ installed
- AWS Account with Bedrock access

## 🚀 Deployment Steps

### Step 1: Create S3 Bucket and Bedrock Knowledge Base (Manual Process)

1. **Create S3 Bucket for Knowledge Base:**
   - Create an S3 bucket for knowledge base documents
   - Note the bucket name for later configuration

2. **Create Bedrock Knowledge Base:**
   - Go to Amazon Bedrock Console
   - Navigate to Knowledge Base
   - Create new Knowledge Base:
     - **Name**: `knowledge_base_data`
     - **Vector Store**: S3 Vectors (Preview)
     - **Embedding Model**: Amazon Titan Text Embeddings v2
     - **Data Source**: Your S3 bucket
   - Note the Knowledge Base ID and Data Source ID
   - Store in SSM Parameter Store:
     ```bash
     aws ssm put-parameter \
       --name "/app/retention/agentcore/knowledge_base_id" \
       --value "YOUR_KNOWLEDGE_BASE_ID" \
       --type "String"
     
     aws ssm put-parameter \
       --name "/app/retention/agentcore/data_source_id" \
       --value "YOUR_DATA_SOURCE_ID" \
       --type "String"
     ```

3. **Upload Knowledge Base Documents:**
   - Upload telecom troubleshooting and policy documents to your S3 bucket
   - Verify the documents are uploaded successfully

4. **Sync Knowledge Base:**
   - Go to Amazon Bedrock Console → Knowledge Base → `knowledge_base_data`
   - Click "Sync" to process new documents
   - Wait for "Sync completed" status (5-15 minutes)
   - Verify documents are indexed and searchable

### Step 2: Deploy Lambda Functions (SAM)

**Script Locations**: 
- `lambda/web_search/` (with `template.yaml`)
- `lambda/churn_data_query/` (with `template.yaml`) 
- `lambda/retention_offer/` (with `template.yaml`)

**Commands**:
```bash
# Deploy Web Search Lambda
cd lambda/web_search
sam build
sam deploy --guided

# Deploy Churn Data Query Lambda
cd ../churn_data_query
sam build
sam deploy --guided

# Deploy Retention Offer Lambda
cd ../retention_offer
sam build
sam deploy --guided
```

**What these deployments do**:
- Creates 3 Lambda functions with proper IAM roles and API Gateway endpoints
- Uses existing `CustomerRetentionLambdaExecutionRole` for consistent permissions
- Deploys with SAM for easy local testing and deployment

### Step 3: Create IAM Roles (Manual Process)

Create the following IAM roles manually in AWS IAM Console:

1. **CustomerRetentionBedrockServiceRole**
   - Trust policy: `bedrock.amazonaws.com`
   - Permissions: Bedrock service permissions

2. **CustomerRetentionLambdaExecutionRole**
   - Trust policy: `lambda.amazonaws.com`
   - Permissions: Lambda execution + Athena + S3 permissions

### Step 4: Create Cognito User Pool (Manual Process)

Create a single Cognito User Pool for authentication:

1. **User Pool Configuration**:
   - **Name**: `CustomerRetentionGatewayPool` (or auto-generated name like `us-east-1_U4maVaYc5`)
   - **Sign-in method**: Username-based authentication
   - **Password policy**: Default settings
   - **MFA**: Disabled (for simplicity)
   - **Self-registration**: Disabled (for high security)

2. **App Clients Created**:
   - **Machine-to-Machine Client**: `CustomerRetentionGatewayM2MClient`
     - **Purpose**: Agent authentication with Gateway
     - **Grant Type**: Client credentials
     - **Client ID**: `<generated-client-id>`
     - **Client Secret**: Generated automatically
     - **Scopes**: Default M2M resource server scopes
   
   - **Web Client**: `CustomerRetentionGatewayWebClient`
     - **Purpose**: End user authentication via web application
     - **Grant Types**: Authorization code, Implicit
     - **Client ID**: `<generated-client-id>`
     - **Client Secret**: Generated automatically
     - **Scopes**: `email`, `openid`, `phone`
     - **⚠️ IMPORTANT**: Enable `USER_PASSWORD_AUTH` flow for this client
     - **⚠️ JWT Authentication**: This client is used for JWT authentication with AgentCore Runtime

3. **Test User Creation**:
   - **Username**: `testuser`
   - **Email**: `test@example.com`
   - **Password**: Set during creation
   - **Email verification**: Enabled

4. **Authentication Flow Validation**:
   - **M2M Client**: Tested with curl command to get access token
   - **Web Client**: Tested login flow through Cognito hosted UI
   - **Authorization URL**: `https://<user-pool-domain>.auth.us-east-1.amazoncognito.com/login`
   - **Login Success**: User successfully authenticated and received authorization code
   - **Callback URL**: `https://<callback-domain>/?code=<authorization_code>`

5. **Key Endpoints and URLs**:
   - **User Pool ID**: `<user-pool-id>`
   - **Discovery URL**: `https://cognito-idp.us-east-1.amazonaws.com/<user-pool-id>/.well-known/openid-configuration`
   - **Token Endpoint**: `https://<user-pool-domain>.auth.us-east-1.amazoncognito.com/oauth2/token`
   - **Login Endpoint**: `https://<user-pool-domain>.auth.us-east-1.amazoncognito.com/login`

6. **Store configuration in SSM Parameter Store**:
   Create the following SSM parameters with your actual values:
   ```bash
   aws ssm put-parameter --name "/customer-retention-agent/cognito/user-pool-id" --value "YOUR_USER_POOL_ID" --type "String"
   aws ssm put-parameter --name "/customer-retention-agent/cognito/m2m-client-id" --value "YOUR_M2M_CLIENT_ID" --type "String"
   aws ssm put-parameter --name "/customer-retention-agent/cognito/m2m-client-secret" --value "YOUR_M2M_CLIENT_SECRET" --type "String"
   aws ssm put-parameter --name "/customer-retention-agent/cognito/discovery-url" --value "YOUR_DISCOVERY_URL" --type "String"
   aws ssm put-parameter --name "/customer-retention-agent/cognito/auth-scope" --value "YOUR_AUTH_SCOPE" --type "String"
   ```

### Step 5: Create AgentCore Gateway (Python Script)

**Script Location**: `agent/scripts/create_gateway.py`

**Command**:
```bash
cd agent/scripts
python create_gateway.py
```

**What this script does**:
1. **Create Gateway IAM Role**:
   - **Name**: `CustomerRetentionGatewayRole`
   - **Trust Policy**: `bedrock-agentcore.amazonaws.com`
   - **Permissions**: `lambda:InvokeFunction` for our 3 Lambda functions

2. **Create AgentCore Gateway**:
   - **Name**: `customer-retention-gateway`
   - **Protocol**: MCP (Model Context Protocol)
   - **Authentication**: Custom JWT with Cognito M2M client
   - **Gateway URL**: `https://customer-retention-gateway-{id}.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp`

3. **Store Gateway configuration in SSM Parameter Store**:
   - Automatically stores Gateway ID and URL in SSM parameters
   - Parameters: `/customer-retention-agent/gateway/id` and `/customer-retention-agent/gateway/url`

### Step 6: Attach Lambda Functions to Gateway (Python Script)

**Script Location**: `agent/scripts/attach_lambda_targets.py`

**Command**:
```bash
cd agent/scripts
python attach_lambda_targets.py
```

**What this script does**:
1. **Create Gateway Targets**:
   - **WebSearchTarget**: Attaches `web_search` Lambda with search tool schema
   - **ChurnDataQueryTarget**: Attaches `churn_data_query` Lambda with query tool schema
   - **RetentionOfferTarget**: Attaches `retention_offer` Lambda with offer generation schema

2. **Store Target configuration in SSM Parameter Store**:
   - Automatically stores target IDs in SSM parameters
   - Parameters: `/customer-retention-agent/gateway/targets/websearchtarget`, `/customer-retention-agent/gateway/targets/churndataquerytarget`, `/customer-retention-agent/gateway/targets/retentionoffertarget`

### Step 7: Create and Attach Memory (Python Script)

**Script Location**: `agent/scripts/create_memory.py`

**Command**:
```bash
cd agent/scripts
python create_memory.py
```

**What this script does**:
- Creates AgentCore Memory for conversation persistence
- Tests memory functionality with sample operations
- Stores memory ID and ARN in SSM Parameter Store
- Parameters: `/customer-retention-agent/memory/id` and `/customer-retention-agent/memory/arn`

### Step 8: Test the Complete Agent (Local)

**Script Location**: `agent/main.py`

**Command**:
```bash
cd agent
python main.py
```

**What this does**:
- Creates the complete Customer Retention Agent with memory integration
- Connects to Gateway and loads external tools (Web Search, Churn Data Query, Retention Offer)
- Provides interactive chat interface for testing
- Combines internal tools (Product Catalog) with external tools via Gateway
- Persists conversation history across sessions
- Provides customer context awareness
- Remembers customer preferences and past interactions

## 🚀 Production Deployment (AgentCore Runtime)

### Step 9: Deploy to AgentCore Runtime

**Prerequisites:**
- Complete all previous steps
- AgentCore Starter Toolkit installed: `pip install bedrock-agentcore-starter-toolkit`

**Deployment Commands:**
```bash
cd agent

# Configure the agent for runtime deployment
agentcore configure -e main.py

# Deploy to AgentCore Runtime
agentcore launch
```

**Configuration Options Selected:**
- **Agent Name**: `main`
- **Execution Role**: Auto-create
- **ECR Repository**: Auto-create
- **Authorization**: IAM (default)
- **Memory**: Short-term + Long-term memory enabled
- **Platform**: ARM64 (CodeBuild deployment)

**⚠️ IMPORTANT: JWT Authentication Configuration**
- **Inbound Authentication**: The AgentCore Runtime is configured to use **JWT (JSON Web Tokens)** for inbound authentication
- **Discovery URL**: `https://cognito-idp.us-east-1.amazonaws.com/YOUR_USER_POOL_ID/.well-known/openid-configuration`
- **Allowed Clients**: Your Web Frontend Client ID
- **Authentication Flow**: Frontend users authenticate via Cognito and send JWT tokens to the AgentCore Runtime
- **Security**: Only users with valid JWT tokens from the configured Cognito User Pool can invoke the agent

### Step 10: Fix SSM Permissions (CRITICAL)

**Problem**: The auto-created execution role lacks SSM Parameter Store permissions.

**Solution**: Add the following inline policy to the execution role `AmazonBedrockAgentCoreSDKRuntime-us-east-1-{random}`:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "SSMParameterAccess",
            "Effect": "Allow",
            "Action": [
                "ssm:GetParameter",
                "ssm:GetParameters"
            ],
            "Resource": [
                "arn:aws:ssm:us-east-1:YOUR_ACCOUNT_ID:parameter/customer-retention-agent/*"
            ]
        }
    ]
}
```

**Steps:**
1. Go to IAM Console → Roles → `AmazonBedrockAgentCoreSDKRuntime-us-east-1-{random}`
2. Click "Add permissions" → "Create inline policy"
3. Paste the JSON above
4. Name it: `CustomerRetentionSSMPolicy`
5. Save

### Step 11: Test Production Agent

**Test Commands:**
```bash
# Basic functionality test
agentcore invoke '{"prompt": "Hello"}'

# Product catalog test
agentcore invoke '{"prompt": "What telecom plans do you offer?"}'

# Churn analysis test
agentcore invoke '{"prompt": "Check the churn risk for customer ID YOUR_CUSTOMER_ID"}'

# Retention offer test
agentcore invoke '{"prompt": "Create a personalized offer for customer YOUR_CUSTOMER_ID"}'
```

**Expected Results:**
- ✅ Agent responds with professional customer service tone
- ✅ Product catalog displays all plans and pricing
- ✅ Churn data query returns customer risk scores
- ✅ Retention offers are personalized and data-driven
- ✅ Memory integration maintains customer context

## 🧹 Cleanup Instructions

Delete these resources in the following order:

### 1. AgentCore Runtime Resources
- **Agent Runtime**: Delete from Bedrock AgentCore Console → Runtime
- **ECR Repository**: Delete `bedrock-agentcore-main` from ECR Console
- **Execution Role**: Delete `AmazonBedrockAgentCoreSDKRuntime-us-east-1-{random}` from IAM Console

### 2. Lambda Functions
- **Web Search Lambda**: Delete using `sam delete` from `lambda/web_search/`
- **Churn Data Query Lambda**: Delete using `sam delete` from `lambda/churn_data_query/`
- **Retention Offer Lambda**: Delete using `sam delete` from `lambda/retention_offer/`

### 3. AgentCore Gateway Resources
- **Gateway Targets**: Delete from Bedrock AgentCore Console
- **Gateway**: Delete from Bedrock AgentCore Console
- **Gateway IAM Role**: Delete `CustomerRetentionGatewayRole` from IAM Console

### 4. Bedrock Resources
- **Knowledge Base**: Delete from Bedrock Console
- **Memory**: Delete from Bedrock AgentCore Console
- **SSM Parameters**: Delete the following from Systems Manager Console:
  - `/app/retention/agentcore/knowledge_base_id`
  - `/app/retention/agentcore/data_source_id`
  - `/customer-retention-agent/gateway/id`
  - `/customer-retention-agent/gateway/url`
  - `/customer-retention-agent/gateway/targets/websearchtarget`
  - `/customer-retention-agent/gateway/targets/churndataquerytarget`
  - `/customer-retention-agent/gateway/targets/retentionoffertarget`
  - `/customer-retention-agent/memory/id`
  - `/customer-retention-agent/memory/arn`

### 5. Cognito Resources
- **User Pool**: Delete from Cognito Console (app clients are automatically deleted)
- **SSM Parameters**: Delete the following from Systems Manager Console:
  - `/customer-retention-agent/cognito/user-pool-id`
  - `/customer-retention-agent/cognito/m2m-client-id`
  - `/customer-retention-agent/cognito/m2m-client-secret`
  - `/customer-retention-agent/cognito/discovery-url`
  - `/customer-retention-agent/cognito/auth-scope`

### 6. IAM Roles
- **CustomerRetentionBedrockServiceRole**
- **CustomerRetentionLambdaExecutionRole**

### 7. S3 Bucket
- **Knowledge Base Bucket**: Empty and delete your S3 bucket

## 📊 Resource Summary

| Resource Type | Name | Step | Management Method | Cleanup Method |
|---------------|------|------|-------------------|----------------|
| S3 Bucket | Your knowledge base bucket | 1 | Manual | Manual |
| Knowledge Base Documents | Telecom troubleshooting and policy documents | 1 | Manual | Manual |
| IAM Role | `CustomerRetentionBedrockServiceRole` | 3 | Manual | Manual |
| IAM Role | `CustomerRetentionLambdaExecutionRole` | 3 | Manual | Manual |
| Knowledge Base | `knowledge_base_data` | 1 | Manual | Manual |
| Lambda | `dev-customer-retention-web-search` | 2 | SAM (`lambda/web_search/`) | `sam delete` |
| Lambda | `dev-customer-retention-churn-data-query` | 2 | SAM (`lambda/churn_data_query/`) | `sam delete` |
| Lambda | `dev-customer-retention-retention-offer` | 2 | SAM (`lambda/retention_offer/`) | `sam delete` |
| Cognito User Pool | `CustomerRetentionGatewayPool` | 4 | Manual | Manual |
| Cognito App Client | `CustomerRetentionGatewayM2MClient` | 4 | Manual | Manual |
| Cognito App Client | `CustomerRetentionGatewayWebClient` | 4 | Manual | Manual |
| AgentCore Gateway | `customer-retention-gateway` | 5 | Python Script (`agent/scripts/create_gateway.py`) | Manual |
| Gateway IAM Role | `CustomerRetentionGatewayRole` | 5 | Python Script (`agent/scripts/create_gateway.py`) | Manual |
| Gateway Targets | `WebSearchTarget`, `ChurnDataQueryTarget`, `RetentionOfferTarget` | 6 | Python Script (`agent/scripts/attach_lambda_targets.py`) | Manual |
| Memory | `customer-retention-memory` | 7 | Python Script (`agent/scripts/create_memory.py`) | Manual |
| Agent | Complete Customer Retention Agent with Memory | 8 | Python Script (`agent/main.py`) | N/A (Local) |
| Memory Hooks | Memory Integration Logic | 8 | Integrated in `agent/memory_hooks.py` | N/A (Local) |
| SSM Parameters | `/app/retention/agentcore/*` | 1 | Manual | Manual |
| SSM Parameters | `/customer-retention-agent/cognito/*` | 4 | Manual | Manual |
| SSM Parameters | `/customer-retention-agent/gateway/*` | 5,6 | Python Scripts | Manual |
| SSM Parameters | `/customer-retention-agent/memory/*` | 7 | Python Script | Manual |
| AgentCore Runtime | Your runtime name | 9-11 | CLI (`agentcore`) | Manual |
| ECR Repository | `bedrock-agentcore-main` | 9-11 | Auto-created | Manual |
| Runtime Execution Role | `AmazonBedrockAgentCoreSDKRuntime-us-east-1-{random}` | 9-11 | Auto-created | Manual |

## 🔧 Troubleshooting

### Common Issues:
1. **Lambda deployment fails**: Check IAM permissions
2. **Knowledge Base creation fails**: Verify S3 bucket permissions
3. **Memory creation fails**: Check AgentCore access
4. **SSM parameter access fails**: Verify parameter names and permissions
5. **AgentCore Runtime deployment fails**: Check execution role permissions
6. **JWT authentication fails**: Verify Cognito User Pool configuration and USER_PASSWORD_AUTH flow
7. **Gateway connection fails**: Check Gateway IAM role and Lambda function permissions
