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

### Step 2: Create IAM Roles (Manual Process)

Create the following IAM roles manually in AWS IAM Console:

1. **CustomerRetentionBedrockServiceRole**
   - Trust policy: `bedrock.amazonaws.com`
   - Permissions: Bedrock service permissions

2. **CustomerRetentionLambdaExecutionRole**
   - Trust policy: `lambda.amazonaws.com`
   - Permissions: Lambda execution + Athena + S3 permissions

### Step 3: Create Cognito User Pool (Manual Process)

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

## 🧹 Cleanup Instructions

### Step 1: Delete Lambda Functions (SAM)
```bash
# Delete each Lambda stack
cd lambda/web_search && sam delete
cd lambda/churn_data_query && sam delete
cd lambda/retention_offer && sam delete
```

### Step 2: Delete Bedrock Resources (Manual)
1. **Knowledge Base**: Delete from Bedrock Console
2. **SSM Parameters**: Delete from Systems Manager Console
   ```bash
   # Delete Bedrock SSM parameters
   aws ssm delete-parameter --name "/app/retention/agentcore/knowledge_base_id"
   aws ssm delete-parameter --name "/app/retention/agentcore/data_source_id"
   aws ssm delete-parameter --name "/app/retention/agentcore/memory_id"
   ```

### Step 3: Delete Cognito Resources (Manual)
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

### Step 4: Delete IAM Roles (Manual)
1. **CustomerRetentionBedrockServiceRole**
2. **CustomerRetentionLambdaExecutionRole**

### Step 5: Delete S3 Bucket
```bash
# Empty and delete bucket
aws s3 rm s3://412602263780-us-east-1-retention-kb-bucket --recursive
aws s3 rb s3://412602263780-us-east-1-retention-kb-bucket
```

## 📊 Resource Summary

| Resource Type | Name | Management Method | Cleanup Method |
|---------------|------|-------------------|----------------|
| S3 Bucket | `412602263780-us-east-1-retention-kb-bucket` | Manual | Manual |
| IAM Role | `CustomerRetentionBedrockServiceRole` | Manual | Manual |
| IAM Role | `CustomerRetentionLambdaExecutionRole` | Manual | Manual |
| Knowledge Base | `knowledge_base_data` | Manual | Manual |
| Memory | `CustomerRetentionMemory` | Python Scripts | Python Scripts |
| Cognito User Pool | `CustomerRetentionGatewayPool` | Manual | Manual |
| Cognito User Pool | `CustomerRetentionMCPServerPool` | Manual | Manual |
| Cognito App Client | `CustomerRetentionMachineClient` | Manual | Manual |
| Cognito App Client | `CustomerRetentionWebClient` | Manual | Manual |
| Cognito App Client | `CustomerRetentionMCPServerClient` | Manual | Manual |
| Lambda | `dev-customer-retention-web-search` | SAM | `sam delete` |
| Lambda | `dev-customer-retention-churn-data-query` | SAM | `sam delete` |
| Lambda | `dev-customer-retention-retention-offer` | SAM | `sam delete` |
| SSM Parameters | `/app/retention/agentcore/*` | Manual | Manual |
| SSM Parameters | `/customer-retention-agent/cognito/*` | Manual | Manual |

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
```
