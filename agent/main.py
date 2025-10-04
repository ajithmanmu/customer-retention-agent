#!/usr/bin/env python3
"""
Customer Retention Agent - Runtime Only Version

This is a clean, production-ready agent for AgentCore Runtime deployment.
No interactive mode, no complex logic - just the runtime entrypoint.
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
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Configuration
REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
ACCOUNT_ID = boto3.client('sts').get_caller_identity()['Account']

# SSM Client for retrieving configuration
SSM_CLIENT = boto3.client('ssm', region_name=REGION)

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
- Retention Offer: Generate personalized retention offers and discount codes

**IMPORTANT: When customers ask for discount codes or retention offers, you MUST:**
**1. First call the churn_data_query tool to get customer data and churn risk**
**2. Then call the retention_offer tool with customer_id and the complete churn_data from the response**

**Guidelines:**
1. Always be helpful, empathetic, and solution-oriented
2. Focus on understanding customer needs and pain points
3. Offer relevant solutions based on customer data and behavior
4. Use data-driven insights to make retention recommendations
5. Be proactive in identifying at-risk customers
6. When customers request discount codes, first call churn_data_query, then call retention_offer with customer_id and the complete churn_data response
7. Remember customer information from the conversation context
8. Use the customer ID provided in the conversation for all tool calls

**Response Style:**
- Professional but friendly tone
- Data-driven recommendations
- Clear explanations of offers and benefits
- Proactive suggestions for improving customer experience
- Always provide actual discount codes when requested
"""

def create_agent(customer_id=None):
    """
    Create the Customer Retention Agent with internal tools, Gateway, and Memory.
    
    Args:
        customer_id (str): The customer ID to use for memory context
    """
    try:
        # Initialize the Bedrock model
        model = BedrockModel(
            model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            temperature=0.3,
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
        session_id = str(uuid.uuid4())
        
        # Use provided customer_id or fall back to session-based ID
        if not customer_id:
            customer_id = f"session-{session_id[:8]}"
            
        memory_hooks = CustomerRetentionMemoryHooks(memory_id, customer_id, session_id, REGION)
        
        # Create agent with all tools and memory hooks
        agent = Agent(
            model=model,
            tools=all_tools,
            hooks=[memory_hooks],
            system_prompt=SYSTEM_PROMPT
        )
        
        logger.info("✅ Customer Retention Agent created successfully!")
        logger.info(f"Internal tools: {[get_product_catalog.__name__]}")
        logger.info(f"External tools: {[tool.tool_name for tool in external_tools]}")
        logger.info(f"Total tools: {len(all_tools)}")
        logger.info(f"Memory integration: Active (customer: {customer_id})")
        logger.info(f"Session ID: {session_id}")
        
        return agent, mcp_client
        
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise

# Initialize the AgentCore Runtime App
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload, user_id=None):
    """
    AgentCore Runtime entrypoint function
    
    Args:
        payload (dict): The request payload containing:
            - prompt (str): The user's input message
        user_id (str): The authenticated user ID from JWT token
            
    Returns:
        str: The agent's response text
    """
    user_input = payload.get("prompt", "")
    
    if not user_input:
        return "Error: No prompt provided in the request payload."
    
    try:
        # Create the agent for this request with the authenticated user_id
        agent, mcp_client = create_agent(customer_id=user_id)
        
        # Log the customer ID being used
        logger.info(f"Processing request for customer: {user_id or 'anonymous'}")
        
        # Invoke the agent with the user input
        response = agent(user_input)
        
        # Clean up the MCP client
        try:
            mcp_client.close()
        except:
            pass
            
        return response.message["content"][0]["text"]
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return f"Error processing request: {str(e)}"

# This file is ONLY for runtime deployment - no interactive mode
if __name__ == "__main__":
    # Always run in runtime mode
    app.run()
