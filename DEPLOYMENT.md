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
   ```bash
   # Create S3 bucket for knowledge base documents
   aws s3 mb s3://412602263780-us-east-1-retention-kb-bucket --region us-east-1
   
   # Verify bucket creation
   aws s3 ls s3://412602263780-us-east-1-retention-kb-bucket
   ```

2. **Create Bedrock Knowledge Base:**
   - Go to Amazon Bedrock Console
   - Navigate to Knowledge Base
   - Create new Knowledge Base:
     - **Name**: `knowledge_base_data`
     - **Vector Store**: S3 Vectors (Preview)
     - **Embedding Model**: Amazon Titan Text Embeddings v2
     - **Data Source**: S3 bucket `412602263780-us-east-1-retention-kb-bucket`
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

### Step 7: Test the Complete Agent (Local)

**Script Location**: `agent/main.py`

**Command**:
```bash
cd agent
python main.py
```

**What this does**:
- Creates the complete Customer Retention Agent with all tools integrated
- Connects to Gateway and loads external tools (Web Search, Churn Data Query, Retention Offer)
- Provides interactive chat interface for testing
- Combines internal tools (Product Catalog) with external tools via Gateway

**Test Commands to Try**:
- "What tools do you have available?"
- "Show me your product catalog"
- "Search for customer retention strategies 2024"
- "Check churn data for customer 7590-VHVEF"
- "Generate a retention offer for a high-risk customer"

## 🧹 Cleanup Instructions

### Step 1: Delete Lambda Functions (SAM)
```bash
# Delete each Lambda stack
cd lambda/web_search && sam delete
cd lambda/churn_data_query && sam delete
cd lambda/retention_offer && sam delete
```

### Step 2: Delete AgentCore Gateway (Manual)
```bash
# Note: We don't have a delete script, so this needs to be done manually
# 1. Delete Gateway targets from Bedrock AgentCore Console
# 2. Delete Gateway from Bedrock AgentCore Console
# 3. Delete Gateway IAM role from IAM Console
```

### Step 3: Delete Bedrock Resources (Manual)
1. **Knowledge Base**: Delete from Bedrock Console
2. **Memory**: Delete from Bedrock AgentCore Console
3. **SSM Parameters**: Delete from Systems Manager Console
   ```bash
   # Delete Bedrock SSM parameters
   aws ssm delete-parameter --name "/app/retention/agentcore/knowledge_base_id"
   aws ssm delete-parameter --name "/app/retention/agentcore/data_source_id"
   aws ssm delete-parameter --name "/app/retention/agentcore/memory_id"
   
   # Delete Gateway SSM parameters
   aws ssm delete-parameter --name "/customer-retention-agent/gateway/id"
   aws ssm delete-parameter --name "/customer-retention-agent/gateway/url"
   aws ssm delete-parameter --name "/customer-retention-agent/gateway/targets/websearchtarget"
   aws ssm delete-parameter --name "/customer-retention-agent/gateway/targets/churndataquerytarget"
   aws ssm delete-parameter --name "/customer-retention-agent/gateway/targets/retentionoffertarget"
   ```

### Step 4: Delete Cognito Resources (Manual)
1. **User Pool**: Delete from Cognito Console
2. **App Clients**: Automatically deleted with User Pool
3. **SSM Parameters**: Delete Cognito-related parameters
   ```bash
   # Delete Cognito SSM parameters
   aws ssm delete-parameter --name "/customer-retention-agent/cognito/user-pool-id"
   aws ssm delete-parameter --name "/customer-retention-agent/cognito/m2m-client-id"
   aws ssm delete-parameter --name "/customer-retention-agent/cognito/m2m-client-secret"
   aws ssm delete-parameter --name "/customer-retention-agent/cognito/discovery-url"
   aws ssm delete-parameter --name "/customer-retention-agent/cognito/auth-scope"
   ```

### Step 5: Delete IAM Roles (Manual)
1. **CustomerRetentionBedrockServiceRole**
2. **CustomerRetentionLambdaExecutionRole**
3. **CustomerRetentionGatewayRole**

### Step 6: Delete S3 Bucket
```bash
# Empty and delete bucket
aws s3 rm s3://412602263780-us-east-1-retention-kb-bucket --recursive
aws s3 rb s3://412602263780-us-east-1-retention-kb-bucket
```

## 📊 Resource Summary

| Resource Type | Name | Step | Management Method | Cleanup Method |
|---------------|------|------|-------------------|----------------|
| S3 Bucket | `412602263780-us-east-1-retention-kb-bucket` | 1 | Manual | Manual |
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
| Agent | Complete Customer Retention Agent | 7 | Python Script (`agent/main.py`) | N/A (Local) |
| SSM Parameters | `/app/retention/agentcore/*` | 1 | Manual | Manual |
| SSM Parameters | `/customer-retention-agent/cognito/*` | 4 | Manual | Manual |
| SSM Parameters | `/customer-retention-agent/gateway/*` | 5,6 | Python Scripts | Manual |

## 🔧 Troubleshooting

### Common Issues:
1. **Lambda deployment fails**: Check IAM permissions
2. **Knowledge Base creation fails**: Verify S3 bucket permissions
3. **Memory creation fails**: Check AgentCore access
4. **SSM parameter access fails**: Verify parameter names and permissions

### Useful Commands:
```bash
# Check CloudFormation stacks
aws cloudformation list-stacks --query 'StackSummaries[?contains(StackName, `customer-retention`)].StackName'

# Check Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `customer-retention`)].FunctionName'

# Check SSM parameters
aws ssm get-parameters-by-path --path "/app/retention/agentcore"
aws ssm get-parameters-by-path --path "/customer-retention-agent/cognito"
aws ssm get-parameters-by-path --path "/customer-retention-agent/gateway"

# Check AgentCore Gateway
aws bedrock-agentcore-control list-gateways --query 'gateways[?contains(name, `customer-retention`)].{Name:name,ID:gatewayId,Status:status}'
```
