## **🚀 Customer Retention Agent - Updated Step-by-Step Guide**

### **Phase 1: Foundation Setup**

#### **Step 1: Create S3 Bucket**
- **Name**: `{your-account-id}-{region}-retention-kb-bucket`
- **Purpose**: Store knowledge base documents
- **Settings**: Block all public access

#### **Step 2: Create IAM Roles**
- **BedrockServiceRole**: For Knowledge Base (S3 access + Titan v2 model access)
- **LambdaExecutionRole**: For Lambda functions (Athena + Secrets Manager access)

#### **Step 3: Create Knowledge Base (Empty)**
- **Type**: Vector
- **Embedding Model**: `amazon.titan-embed-text-v2:0`
- **Storage**: S3 Vectors
- **Data Source**: Your S3 bucket

#### **Step 4: Create SSM Parameters**
- `/{account-id}-{region}/kb/knowledge-base-id` → Your KB ID
- `/{account-id}-{region}/kb/data-source-id` → Your DS ID

### **Phase 2: Memory Setup**

#### **Step 5: Create AgentCore Memory**
- **Name**: `CustomerRetentionMemory`
- **Strategies**: 
  - `USER_PREFERENCE`: `retention/customer/{actorId}/preferences`
  - `SEMANTIC`: `retention/customer/{actorId}/semantic`
- **Event Expiry**: 90 days

#### **Step 6: Create SSM Parameter**
- `/app/retention/agentcore/memory_id` → Your Memory ID

### **Phase 3: External Tools Setup**

#### **Step 7: Create Lambda Functions**
- **Lambda 1**: Web Search (DDGS layer)
- **Lambda 2**: Churn Data Query (Athena access)
- **Lambda 3**: Retention Offer (Pre-approved offers)

#### **Step 8: Create API Spec JSON**
- Define the 3 external tools schema

### **Phase 4: Gateway Setup**

#### **Step 9: Create Cognito User Pool (Gateway Auth)**
- **Name**: `CustomerRetentionGatewayPool`
- **Machine Client**: `RetentionMachineClient` (with secret)

#### **Step 10: Create AgentCore Gateway**
- **Name**: `customer-retention-gateway`
- **Auth**: Custom JWT (Cognito)
- **Target**: Your 3 Lambda functions

#### **Step 11: Create SSM Parameters**
- Gateway configuration parameters

### **Phase 5: Runtime Setup**

#### **Step 12: Create Cognito User Pool (Runtime Auth)**
- **Name**: `CustomerRetentionRuntimePool`
- **Web Client**: `RetentionWebClient` (no secret)

#### **Step 13: Create Runtime IAM Role**
- **Name**: `CustomerRetentionRuntimeRole`
- **Trust**: `bedrock-agentcore.amazonaws.com`

#### **Step 14: Deploy to AgentCore Runtime**
- **Entrypoint**: Your agent code with internal offer decision matrix
- **Auth**: Custom JWT (Runtime Cognito)

#### **Step 15: Create SSM Parameters**
- Runtime configuration parameters

### **Phase 6: Web App Setup**

#### **Step 16: Create Web Application**
- **Framework**: Streamlit (or your choice)
- **Auth**: Runtime Cognito
- **Endpoint**: AgentCore Runtime

### **Phase 7: Content & Testing**

#### **Step 17: Populate Knowledge Base**
- Upload customer support docs, retention playbooks, FAQ to S3
- Sync Knowledge Base to ingest documents

#### **Step 18: Create Pre-approved Offers**
- **Stripe Dashboard**: Create 3-5 retention coupons
- **Offer Tiers**: 10% off, 20% off, feature upgrades, support credits

#### **Step 19: Test End-to-End**
- Test customer scenarios: Low/medium/high churn risk
- Verify offer logic and web app functionality

## **📁 File Structure**

```
customer-retention-agent/
├── agent/
│   ├── main.py
│   ├── tools/
│   │   └── offer_decision_matrix.py
│   └── requirements.txt
├── lambda/
│   ├── web_search/
│   ├── churn_data_query/
│   ├── retention_offer/
│   └── api_spec.json
├── webapp/
│   ├── main.py
│   ├── chat.py
│   └── requirements.txt
└── docs/
    └── knowledge_base/
```

# Customer Retention Agent Project

## Architecture
- 3 External Tools: Web Search, Churn Data Query, Retention Offer
- 1 Internal Tool: Offer Decision Matrix
- 2 Cognito User Pools: Gateway auth + Runtime auth
- AgentCore Memory + Gateway + Runtime

## Key Decisions
- Manual AWS console setup (no Terraform)
- Pre-approved Stripe coupons (no dynamic creation)
- Skip DynamoDB (use Memory + Athena)
- 19-step setup process
---
