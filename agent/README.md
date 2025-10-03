# Customer Retention Agent

This directory contains the Customer Retention Agent implementation following the tutorial pattern.

## 🏗️ Architecture

The agent is built progressively in stages:

1. **Basic Agent** (`main.py`) - Local prototype with internal tools
2. **Memory Component** (`scripts/attach_memory.py`) - Conversation persistence
3. **Gateway Component** (`scripts/attach_gateway.py`) - External tools integration
4. **Runtime Deployment** (`scripts/deploy_runtime.py`) - Production deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- AWS credentials configured
- Bedrock access with Claude 3.7 Sonnet
- Docker or Finch installed and running

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Test basic agent locally
python main.py
```

### 🚀 Deploy to Production

You have two deployment options:

#### Option 1: Simple CLI Deployment (Recommended for Basic Use)

```bash
# 1. Install all dependencies (including starter toolkit)
pip install -r requirements.txt

# 2. Configure the deployment (auto-creates IAM roles, ECR repository)
agentcore configure -e main.py
```

**Configuration Options Selected:**
- ✅ **Execution Role**: Auto-create (recommended)
- ✅ **ECR Repository**: Auto-create (recommended)
- ✅ **Dependencies**: Use detected `requirements.txt`
- ✅ **Authorization**: IAM (default)
- ✅ **Request Headers**: Default configuration
- ✅ **Memory**: Short-term + Long-term memory enabled
- ⚠️ **Platform**: Note the ARM64 requirement warning (handled automatically)

```bash
# 3. Deploy to AWS (builds container and deploys)
agentcore launch

# 4. Test your deployed agent
agentcore invoke '{"prompt": "What is the customer churn risk for customer 123?"}'
```

#### Option 2: Custom Deployment Script (Recommended for Production)

For production deployments with custom IAM permissions and comprehensive testing:

```bash
# 1. Deploy with custom execution role and proper permissions
python deploy_runtime.py

# 2. Run comprehensive tests
python test_runtime.py

# 3. Clean up when done
python cleanup_runtime.py
```

**Custom Deployment Features:**
- ✅ **Custom IAM Role**: Proper permissions for SSM, Bedrock, and Memory
- ✅ **ECR Repository**: Automated container registry setup
- ✅ **Comprehensive Testing**: Automated test suite
- ✅ **Cleanup Script**: Complete resource cleanup
- ✅ **Deployment Tracking**: Saves deployment information

## 📁 File Structure

```
agent/
├── main.py                 # Complete agent with memory, gateway, and runtime support
├── requirements.txt        # Python dependencies
├── memory_hooks.py         # Memory integration hooks
├── deploy_runtime.py       # Custom deployment script with proper IAM permissions
├── cleanup_runtime.py      # Complete cleanup script
├── test_runtime.py         # Comprehensive test suite
├── README.md              # This file
└── scripts/               # Progressive enhancement scripts
    ├── create_memory.py   # Create and attach memory
    ├── create_gateway.py  # Create AgentCore Gateway
    └── attach_lambda_targets.py  # Attach Lambda functions to Gateway
```

## 🛠️ Development Flow

### Stage 1: Basic Agent ✅
- ✅ Internal tool: Product Catalog
- ✅ Local testing and development
- ✅ Basic conversation capabilities

### Stage 2: Memory ✅
- ✅ Conversation persistence with AgentCore Memory
- ✅ Customer context across sessions
- ✅ Personalized interactions

### Stage 3: Gateway ✅
- ✅ External tools: Web Search, Churn Data Query, Retention Offer
- ✅ Secure authentication via Cognito
- ✅ Centralized tool management

### Stage 4: Runtime ✅
- ✅ Production deployment via CLI commands
- ✅ Scalability and monitoring
- ✅ Real-world usage

## 🧪 Testing

```bash
# Test basic agent functionality
python main.py --test

# Interactive testing
python main.py
```

## 📋 Available Tools

### Internal Tools (Current)
- **Product Catalog**: Information about telecom plans, pricing, and features

### External Tools (Coming Soon)
- **Web Search**: Current information about retention strategies
- **Churn Data Query**: Customer data analysis and risk scoring
- **Retention Offer**: Personalized offers and discounts

## 🔧 Configuration

The agent uses the following AWS resources:
- **Region**: us-east-1 (configurable via AWS_DEFAULT_REGION)
- **Model**: Claude 3.7 Sonnet
- **Memory**: AgentCore Memory (to be added)
- **Gateway**: AgentCore Gateway (to be added)

## 📝 Next Steps

1. **Add Memory Component**: Enable conversation persistence
2. **Add Gateway Component**: Integrate external tools
3. **Deploy to Runtime**: Production deployment
4. **Build Frontend**: Customer-facing interface
