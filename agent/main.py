#!/usr/bin/env python3
"""
Customer Retention Agent - Complete Local Agent

This agent integrates:
- Internal tools (Product Catalog)
- External tools via Gateway (Web Search, Churn Data Query, Retention Offer)
- Memory for conversation persistence
"""

import os
import sys
import boto3
import json
import requests
import uuid
from strands import Agent
from strands.models import BedrockModel
from strands.tools import tool
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from memory_hooks import CustomerRetentionMemoryHooks

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Configuration
REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
ACCOUNT_ID = boto3.client('sts').get_caller_identity()['Account']

# SSM Client for retrieving configuration
SSM_CLIENT = boto3.client('ssm', region_name=REGION)

# Memory Client for AgentCore Memory (now handled in memory_hooks.py)

def get_ssm_parameter(name: str) -> str:
    """Retrieve a parameter from SSM Parameter Store."""
    try:
        response = SSM_CLIENT.get_parameter(Name=name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        logger.error(f"Error retrieving SSM parameter '{name}': {e}")
        raise

def get_cognito_token() -> str:
    """Get access token from Cognito for Gateway authentication."""
    try:
        # Get Cognito configuration from SSM
        client_id = get_ssm_parameter("/customer-retention-agent/cognito/m2m-client-id")
        client_secret = get_ssm_parameter("/customer-retention-agent/cognito/m2m-client-secret")
        scope = get_ssm_parameter("/customer-retention-agent/cognito/auth-scope")
        
        # Use the correct token URL format from the discovery document
        token_url = "https://us-east-1u4mavayc5.auth.us-east-1.amazoncognito.com/oauth2/token"
        
        # Request token from Cognito
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope
        }
        
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        
        return token_data["access_token"]
        
    except Exception as e:
        logger.error(f"Error getting Cognito token: {e}")
        raise

@tool
def get_product_catalog() -> str:
    """
    Get information about available telecom plans and services.
    
    Returns:
        str: Information about available plans, pricing, and features
    """
    try:
        # Internal tool - Product Catalog information
        product_info = {
            "plans": [
                {
                    "name": "Basic Plan",
                    "price": "$29.99/month",
                    "features": ["Unlimited calls", "1GB data", "Basic support"],
                    "target_customers": "Low usage customers"
                },
                {
                    "name": "Premium Plan", 
                    "price": "$59.99/month",
                    "features": ["Unlimited calls", "10GB data", "Premium support", "International calls"],
                    "target_customers": "High usage customers"
                },
                {
                    "name": "Family Plan",
                    "price": "$89.99/month", 
                    "features": ["4 lines", "Unlimited data", "Family controls", "Premium support"],
                    "target_customers": "Family customers"
                }
            ],
            "add_ons": [
                {
                    "name": "International Roaming",
                    "price": "$15/month",
                    "description": "Unlimited international calls and data"
                },
                {
                    "name": "Device Protection",
                    "price": "$8/month", 
                    "description": "Device insurance and replacement"
                }
            ],
            "retention_offers": [
                {
                    "type": "discount",
                    "description": "20% off for 6 months",
                    "eligibility": "High churn risk customers"
                },
                {
                    "type": "upgrade",
                    "description": "Free plan upgrade for 3 months",
                    "eligibility": "Medium churn risk customers"
                }
            ]
        }
        
        return f"""
📋 **Telecom Product Catalog**

**Available Plans:**
{chr(10).join([f"• {plan['name']}: {plan['price']} - {', '.join(plan['features'])}" for plan in product_info['plans']])}

**Add-on Services:**
{chr(10).join([f"• {addon['name']}: {addon['price']} - {addon['description']}" for addon in product_info['add_ons']])}

**Retention Offers:**
{chr(10).join([f"• {offer['type'].title()}: {offer['description']} (for {offer['eligibility']})" for offer in product_info['retention_offers']])}
        """
        
    except Exception as e:
        logger.error(f"Error getting product catalog: {str(e)}")
        return f"Error retrieving product catalog: {str(e)}"


# System prompt for the Customer Retention Agent
SYSTEM_PROMPT = """
You are a Customer Retention Agent for a telecom company. Your primary goal is to help retain customers who are at risk of churning.

**Your Role:**
- Analyze customer churn risk and behavior patterns
- Provide personalized retention strategies and offers
- Help customers find better plans that suit their needs
- Offer discounts and incentives to prevent churn

**Available Tools:**
- Product Catalog: Information about available plans, pricing, and features
- Web Search: Find current information about customer retention strategies
- Churn Data Query: Analyze customer data and churn risk scores
- Retention Offer: Generate personalized retention offers and discounts

**Guidelines:**
1. Always be helpful, empathetic, and solution-oriented
2. Focus on understanding customer needs and pain points
3. Offer relevant solutions based on customer data and behavior
4. Use data-driven insights to make retention recommendations
5. Be proactive in identifying at-risk customers

**Response Style:**
- Professional but friendly tone
- Data-driven recommendations
- Clear explanations of offers and benefits
- Proactive suggestions for improving customer experience
"""

def create_complete_agent():
    """
    Create the complete Customer Retention Agent with internal tools, Gateway, and Memory.
    """
    try:
        # Initialize the Bedrock model
        model = BedrockModel(
            model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            temperature=0.3,  # Balanced between creativity and consistency
            region_name=REGION
        )
        
        # Get Gateway configuration
        gateway_url = get_ssm_parameter("/customer-retention-agent/gateway/url")
        
        # Get Cognito token for Gateway authentication
        access_token = get_cognito_token()
        
        # Create MCP client for Gateway
        mcp_client = MCPClient(
            lambda: streamablehttp_client(
                gateway_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
        )
        
        # Start MCP client to get external tools
        mcp_client.start()
        external_tools = mcp_client.list_tools_sync()
        
        # Combine internal and external tools
        all_tools = [get_product_catalog] + external_tools
        
        # Initialize Memory Hooks
        memory_id = get_ssm_parameter("/customer-retention-agent/memory/id")
        # For testing, we can use a fixed customer ID or generate one
        customer_id = "test-customer-001" 
        session_id = str(uuid.uuid4())
        memory_hooks = CustomerRetentionMemoryHooks(memory_id, customer_id, session_id, REGION)
        logger.info(f"✅ Initialized Memory Hooks for customer: {customer_id}, session: {session_id}")
        
        # Create agent with all tools and memory hooks
        agent = Agent(
            model=model,
            tools=all_tools,
            hooks=[memory_hooks],  # Attach memory hooks
            system_prompt=SYSTEM_PROMPT
        )
        
        logger.info("✅ Complete Customer Retention Agent created successfully!")
        logger.info(f"Internal tools: {[get_product_catalog.__name__]}")
        logger.info(f"External tools: {[tool.tool_name for tool in external_tools]}")
        logger.info(f"Total tools: {len(all_tools)}")
        logger.info(f"Memory integration: Active (customer: {customer_id})")
        
        return agent, mcp_client
        
    except Exception as e:
        logger.error(f"Error creating complete agent: {str(e)}")
        raise

# Test function will be added later

if __name__ == "__main__":
    """
    Main entry point for the complete agent.
    
    Usage:
    python main.py                    # Create complete agent with Gateway integration
    """
    
    try:
        # Create complete agent with Gateway integration
        agent, mcp_client = create_complete_agent()
        
        print("\n🎯 Complete Customer Retention Agent Ready!")
        print("✅ Internal tools: Product Catalog")
        print("✅ External tools: Web Search, Churn Data Query, Retention Offer")
        print("✅ Gateway integration: Active")
        print("✅ Memory integration: Active (persistent conversations)")
        print("\n" + "="*60)
        print("🤖 AGENT INTERACTIVE MODE")
        print("="*60)
        print("Type your questions below. Type 'quit' or 'exit' to stop.")
        print("The agent will remember your conversations and preferences!")
        print("="*60)
        
        # Interactive loop
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye! Agent session ended.")
                    break
                    
                if not user_input:
                    continue
                    
                print("\n🤖 Agent: ", end="", flush=True)
                response = agent(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Agent session ended.")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again or type 'quit' to exit.")
                
    except Exception as e:
        print(f"\n❌ Failed to create agent: {str(e)}")
        print("Please check your AWS configuration and SSM parameters.")
        sys.exit(1)
    finally:
        # Clean up MCP client
        try:
            if 'mcp_client' in locals():
                mcp_client.close()
        except:
            pass
