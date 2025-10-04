# Customer Retention Agent - Testing Guide

This guide covers all testing approaches for the Customer Retention Agent, from local development to production validation.

## 🧪 Testing Approaches Overview

| Method | Purpose | Environment | Best For |
|--------|---------|-------------|----------|
| **`python main.py`** | Interactive local testing | Local development | Development, debugging, manual testing |
| **`agentcore invoke --local`** | Runtime simulation | Local with real AWS services | Testing runtime behavior locally |
| **`python test_invoke_local.py`** | Automated test suite | Local with real AWS services | Automated testing, CI/CD validation |

## 🚀 Testing Methods

### Method 1: Interactive Local Testing (`python main.py`)

**Purpose**: Interactive development and debugging with full agent capabilities.

**Command**:
```bash
cd agent
python main.py
```

**What it does**:
- Creates the complete Customer Retention Agent with all tools
- Connects to Gateway and loads external tools (Web Search, Churn Data Query, Retention Offer)
- Integrates memory for conversation persistence
- Provides interactive chat interface
- Uses real AWS services (Lambda, Gateway, Memory, Knowledge Base)

**Best for**:
- Development and debugging
- Manual testing of agent behavior
- Testing memory persistence across conversations
- Validating tool integration
- Testing customer context and preferences

**Example Session**:
```
🧪 Customer Retention Agent - Interactive Mode
==============================================

Agent: Hello! I'm your Customer Retention Agent. How can I help you today?

You: Hello, I need help with my account
Agent: Hello! I'd be happy to help you with your account. To provide you with the most relevant assistance, could you please provide your customer ID?

You: My customer ID is 3916-NRPAP
Agent: Thank you! I have your customer ID (3916-NRPAP) noted. Let me check your account details and see what personalized offers might be available for you.

You: What did I tell you about my customer ID?
Agent: You mentioned that your customer ID is 3916-NRPAP. I can see that you might be considering cancelling your telecom service with us...
```

### Method 2: Runtime Simulation (`agentcore invoke --local`)

**Purpose**: Test the agent in runtime mode locally, simulating production behavior.

**Command**:
```bash
cd agent
agentcore invoke --local '{"prompt": "Hello, I need help with my account"}'
```

**What it does**:
- Runs the agent in AgentCore Runtime mode locally
- Uses the same entrypoint as production deployment
- Tests JWT authentication flow
- Validates runtime configuration
- Simulates production request/response cycle

**Best for**:
- Testing runtime behavior before production deployment
- Validating JWT authentication
- Testing the `invoke` function directly
- Ensuring production readiness

**Example Commands**:
```bash
# Basic functionality test
agentcore invoke --local '{"prompt": "Hello"}'

# Product catalog test
agentcore invoke --local '{"prompt": "What telecom plans do you offer?"}'

# Memory test
agentcore invoke --local '{"prompt": "My customer ID is 3916-NRPAP"}'
agentcore invoke --local '{"prompt": "What did I tell you about my customer ID?"}'

# Tool integration test
agentcore invoke --local '{"prompt": "I want a discount code for my account"}'
```

### Method 3: Automated Test Suite (`python test_invoke_local.py`)

**Purpose**: Comprehensive automated testing with multiple scenarios.

**Command**:
```bash
cd agent
python test_invoke_local.py
```

**What it does**:
- Runs multiple test scenarios automatically
- Tests JWT token authentication
- Validates customer ID mapping
- Tests memory persistence
- Provides pass/fail results
- Generates test reports

**Test Scenarios**:
1. **Basic Greeting**: Tests general agent functionality
2. **Customer ID Recognition**: Tests memory persistence
3. **Discount Code Request**: Tests tool calling workflow
4. **Product Catalog Query**: Tests internal tools

**Example Output**:
```
🧪 Local Agent Testing Suite
============================================================
✅ Authentication successful!
Access token: eyJraWQiOiJ...
🔍 JWT Payload: {
  "sub": "d4e884b8-70a1-7024-9457-deb37a8c77cb",
  "aud": "13rgm18m8g39c2dn7ik8gg6in9",
  ...
}

============================================================

🧪 Testing Scenario: Basic Greeting
--------------------------------------------------
Prompt: Hello, I need help with my account
Customer ID: test-user
✅ Response: Hello! I'd be happy to help you with your account...

🧪 Testing Scenario: Customer ID Recognition
--------------------------------------------------
Prompt: What did I tell you about my customer ID in our previous conversation?
Customer ID: test-user
✅ Response: Based on the context provided, you mentioned that your customer ID is 3916-NRPAP...

============================================================
🎯 Test Results: 4/4 tests passed
🎉 All tests passed! Agent is working correctly.
============================================================
🏁 Local agent testing completed!
```

## 🔧 Testing Prerequisites

### Environment Setup
1. **AWS Credentials**: Configured with appropriate permissions
2. **Environment Variables**: Set in `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_USER_POOL_ID=YOUR_USER_POOL_ID
   NEXT_PUBLIC_USER_POOL_WEB_CLIENT_ID=YOUR_CLIENT_ID
   NEXT_PUBLIC_USER_POOL_WEB_CLIENT_SECRET=YOUR_CLIENT_SECRET
   NEXT_PUBLIC_AWS_REGION=us-east-1
   ```

### Required AWS Resources
- ✅ Cognito User Pool with test user
- ✅ AgentCore Gateway with Lambda targets
- ✅ AgentCore Memory
- ✅ Lambda functions deployed
- ✅ Knowledge Base (optional for basic testing)

## 🎯 Testing Scenarios

### Core Functionality Tests
1. **Agent Initialization**: Verify agent starts and loads all tools
2. **Memory Integration**: Test conversation persistence
3. **Tool Integration**: Validate Gateway and Lambda connections
4. **Customer Context**: Test user ID to customer ID mapping

### Business Logic Tests
1. **Product Catalog**: Verify plan information retrieval
2. **Churn Analysis**: Test customer risk assessment
3. **Retention Offers**: Validate discount code generation
4. **Web Search**: Test external information retrieval

### Authentication Tests
1. **JWT Token**: Validate token generation and parsing
2. **User Mapping**: Test Cognito user ID to customer ID mapping
3. **Session Management**: Verify session persistence

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Check Cognito User Pool configuration
   - Verify USER_PASSWORD_AUTH flow is enabled
   - Validate client secret configuration

2. **Memory Not Working**:
   - Check AgentCore Memory configuration
   - Verify SSM parameters for memory ID
   - Test memory hooks integration

3. **Tool Integration Failures**:
   - Verify Gateway configuration
   - Check Lambda function deployments
   - Validate IAM permissions

4. **JWT Token Issues**:
   - Check token expiration
   - Verify token format and structure
   - Test token decoding

### Debug Commands
```bash
# Check environment variables
echo $NEXT_PUBLIC_USER_POOL_ID
echo $NEXT_PUBLIC_USER_POOL_WEB_CLIENT_ID

# Test Cognito authentication
aws cognito-idp initiate-auth --auth-flow USER_PASSWORD_AUTH --client-id YOUR_CLIENT_ID --auth-parameters USERNAME=test-user,PASSWORD=your-password

# Check SSM parameters
aws ssm get-parameters-by-path --path "/customer-retention-agent"
```

## 📊 Test Results Interpretation

### Success Indicators
- ✅ All test scenarios pass
- ✅ Memory persistence works across conversations
- ✅ Tool calls return expected results
- ✅ Customer ID mapping functions correctly
- ✅ JWT authentication succeeds

### Failure Indicators
- ❌ Authentication errors
- ❌ Memory not persisting
- ❌ Tool calls failing
- ❌ Customer ID not mapping
- ❌ JWT token issues

## 🔄 Testing Workflow

### Development Testing
1. **Start with**: `python main.py` for interactive development
2. **Validate with**: `agentcore invoke --local` for runtime testing
3. **Automate with**: `python test_invoke_local.py` for comprehensive validation

### Pre-Production Testing
1. **Run automated test suite**: `python test_invoke_local.py`
2. **Test runtime behavior**: `agentcore invoke --local`
3. **Validate all scenarios pass**
4. **Deploy to production**: `agentcore launch`

### Post-Deployment Testing
1. **Test production endpoint** with real JWT tokens
2. **Validate memory persistence** in production
3. **Test tool integration** with production services
4. **Monitor performance** and error rates

## 📝 Test Documentation

### Recording Test Results
- Document any test failures with error messages
- Note environment-specific issues
- Track performance metrics
- Update test scenarios as needed

### Test Maintenance
- Update test scenarios when adding new features
- Validate test data remains current
- Review and update authentication credentials
- Maintain test environment parity with production

---

**Note**: This testing guide covers local and development testing. For production testing, refer to the production deployment section in `DEPLOYMENT.md`.
