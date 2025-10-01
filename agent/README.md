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

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Test basic agent
python main.py --test
```

## 📁 File Structure

```
agent/
├── main.py                 # Basic agent with internal tools
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── scripts/               # Progressive enhancement scripts
    ├── attach_memory.py   # Add conversation memory
    ├── attach_gateway.py  # Add external tools via Gateway
    └── deploy_runtime.py  # Deploy to production
```

## 🛠️ Development Flow

### Stage 1: Basic Agent
- ✅ Internal tool: Product Catalog
- ✅ Local testing and development
- ✅ Basic conversation capabilities

### Stage 2: Memory (Next)
- 🔄 Conversation persistence
- 🔄 Customer context across sessions
- 🔄 Personalized interactions

### Stage 3: Gateway (Next)
- 🔄 External tools: Web Search, Churn Data Query, Retention Offer
- 🔄 Secure authentication via Cognito
- 🔄 Centralized tool management

### Stage 4: Runtime (Next)
- 🔄 Production deployment
- 🔄 Scalability and monitoring
- 🔄 Real-world usage

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
