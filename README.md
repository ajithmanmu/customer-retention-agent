# Customer Retention Agent

A comprehensive AI-powered customer retention system built with AWS Bedrock AgentCore, featuring real-time churn analysis, personalized retention offers, and conversational AI capabilities.

## 🎯 Project Overview

The Customer Retention Agent is designed to help telecom companies identify at-risk customers and provide personalized retention strategies through an intelligent conversational interface. The system combines multiple AWS services to deliver a complete customer retention solution.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   AgentCore      │    │   AWS Services  │
│   (Next.js)     │◄──►│   Runtime        │◄──►│                 │
│                 │    │                  │    │ • Lambda        │
│ • Cognito Auth  │    │ • JWT Auth       │    │ • Gateway       │
│ • Chat UI       │    │ • Memory         │    │ • Memory        │
│ • JWT Tokens    │    │ • Tool Calling   │    │ • Knowledge Base│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Key Features

### 🤖 **Intelligent Conversational AI**
- **Memory Integration**: Remembers customer preferences and conversation history
- **Context Awareness**: Maintains customer context across sessions
- **Natural Language Processing**: Understands customer intent and sentiment

### 📊 **Real-Time Churn Analysis**
- **Customer Risk Assessment**: Analyzes customer behavior patterns
- **Churn Prediction**: Identifies high-risk customers proactively
- **Data-Driven Insights**: Uses historical data for accurate predictions

### 🎁 **Personalized Retention Offers**
- **Dynamic Offer Generation**: Creates offers based on customer risk level
- **Discount Codes**: Generates unique discount codes for retention
- **Service Upgrades**: Recommends relevant service improvements

### 🔍 **Knowledge Base Integration**
- **Policy Information**: Access to company policies and procedures
- **Troubleshooting Guides**: Step-by-step problem resolution
- **Real-Time Search**: Current information retrieval capabilities

## 🛠️ Technology Stack

### **Frontend**
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **AWS SDK**: Cognito authentication and AgentCore integration

### **Backend**
- **AWS Bedrock AgentCore**: AI agent runtime platform
- **AWS Lambda**: Serverless functions for business logic
- **AWS Cognito**: User authentication and JWT token management
- **AWS Systems Manager**: Configuration and secrets management

### **Data & Analytics**
- **Amazon Athena**: SQL-based data querying
- **Amazon S3**: Data storage and knowledge base documents
- **Bedrock Knowledge Base**: Document processing and retrieval

### **AI & Machine Learning**
- **Claude 3.7 Sonnet**: Large language model for conversation
- **Amazon Titan**: Text embeddings for knowledge base
- **Strands Framework**: Agent development and tool integration

## 📁 Project Structure

```
customer-retention-agent/
├── agent/                          # AgentCore agent implementation
│   ├── main.py                     # Main agent logic and runtime entrypoint
│   ├── memory_hooks.py             # Memory integration hooks
│   ├── test_invoke_local.py        # Local testing suite
│   └── scripts/                    # Deployment and setup scripts
├── lambda/                         # AWS Lambda functions
│   ├── web_search/                 # Web search functionality
│   ├── churn_data_query/           # Customer churn analysis
│   └── retention_offer/            # Personalized offer generation
├── frontend/                       # Next.js web application
│   ├── src/                        # Source code
│   ├── components/                 # React components
│   └── lib/                        # Utility libraries
├── DEPLOYMENT.md                   # Complete deployment guide
├── TESTING.md                      # Testing strategies and approaches
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Node.js 18+ and Python 3.9+
- SAM CLI for Lambda deployment
- AgentCore Starter Toolkit

### 1. Deploy Infrastructure
Follow the comprehensive deployment guide:
```bash
# See DEPLOYMENT.md for complete instructions
```

### 2. Set Up Frontend
```bash
cd frontend
npm install
cp env.example .env.local
# Update .env.local with your AWS configuration
npm run dev
```

### 3. Test the System
```bash
cd agent
python test_invoke_local.py
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Complete infrastructure deployment guide |
| **[TESTING.md](TESTING.md)** | Testing strategies and validation approaches |
| **[frontend/README.md](frontend/README.md)** | Frontend development and setup |
| **[lambda/*/README.md](lambda/)** | Individual Lambda function documentation |

## 🔧 Configuration

### Environment Variables
The system requires configuration for:
- **AWS Credentials**: IAM roles and permissions
- **Cognito User Pool**: Authentication configuration
- **AgentCore Runtime**: Agent deployment settings
- **Lambda Functions**: Business logic configuration

### Security Features
- **JWT Authentication**: Secure token-based authentication
- **IAM Roles**: Least-privilege access control
- **SSM Parameter Store**: Secure configuration management
- **Environment Isolation**: Separate dev/prod configurations

## 🧪 Testing

The project includes comprehensive testing at multiple levels:

### **Local Development Testing**
- Interactive agent testing with `python main.py`
- Runtime simulation with `agentcore invoke --local`
- Automated test suite with `python test_invoke_local.py`

### **Integration Testing**
- Lambda function testing with SAM
- Gateway integration validation
- Memory persistence testing

### **Production Testing**
- End-to-end workflow validation
- Performance and scalability testing
- Security and authentication testing

## 🚀 Deployment Options

### **Development Environment**
- Local agent with real AWS services
- Frontend development server
- Individual Lambda function testing

### **Production Environment**
- AgentCore Runtime deployment
- Vercel frontend deployment
- Scalable AWS infrastructure

## 🔒 Security Considerations

- **Authentication**: Cognito User Pool with JWT tokens
- **Authorization**: IAM roles with least-privilege access
- **Data Protection**: Encrypted data at rest and in transit
- **Secrets Management**: SSM Parameter Store for sensitive data
- **Network Security**: VPC and security group configurations

## 📊 Monitoring & Observability

- **CloudWatch Logs**: Comprehensive logging across all services
- **CloudWatch Metrics**: Performance and usage monitoring
- **X-Ray Tracing**: Distributed tracing for debugging
- **Custom Metrics**: Business-specific KPIs and analytics

## 🤝 Contributing

1. **Development Setup**: Follow the deployment guide
2. **Testing**: Run the test suite before making changes
3. **Documentation**: Update relevant documentation
4. **Security**: Ensure no sensitive information is committed

## 📄 License

This project is for demonstration and educational purposes. Please ensure compliance with AWS service terms and your organization's policies.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting sections in the documentation
2. Review the testing guide for validation steps
3. Consult AWS documentation for service-specific issues

---

**Built with ❤️ using AWS Bedrock AgentCore and modern web technologies**
