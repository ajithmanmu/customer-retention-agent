#!/usr/bin/env python3
"""
Customer Retention Agent - Basic Local Prototype

This is the basic agent prototype following the tutorial pattern.
We'll start with a local agent that has an internal tool (Product Catalog),
then progressively add Memory, Gateway, and Runtime components.
"""

import os
import sys
import boto3
from strands import Agent
from strands.models import BedrockModel
from strands.tools import tool

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Configuration
REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
ACCOUNT_ID = boto3.client('sts').get_caller_identity()['Account']

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

def create_basic_agent():
    """
    Create the basic Customer Retention Agent with internal tools only.
    This is the starting point - we'll add Memory, Gateway, and Runtime later.
    """
    try:
        # Initialize the Bedrock model
        model = BedrockModel(
            model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            temperature=0.3,  # Balanced between creativity and consistency
            region_name=REGION
        )
        
        # Create agent with internal tools only (for now)
        tools = [get_product_catalog]
        
        agent = Agent(
            model=model,
            tools=tools,
            system_prompt=SYSTEM_PROMPT
        )
        
        logger.info("✅ Basic Customer Retention Agent created successfully!")
        logger.info(f"Available tools: {[tool.__name__ for tool in tools]}")
        
        return agent
        
    except Exception as e:
        logger.error(f"Error creating basic agent: {str(e)}")
        raise

# Test function will be added later

if __name__ == "__main__":
    """
    Main entry point for the basic agent.
    
    Usage:
    python main.py                    # Create basic agent for manual testing
    """
    
    # Create basic agent
    agent = create_basic_agent()
    print("\n🎯 Basic Customer Retention Agent Ready!")
    print("Next steps:")
    print("1. Add Memory component (conversation persistence)")
    print("2. Add Gateway component (external tools)")
    print("3. Deploy to Runtime (production)")
    print("\n" + "="*60)
    print("🤖 AGENT INTERACTIVE MODE")
    print("="*60)
    print("Type your questions below. Type 'quit' or 'exit' to stop.")
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
