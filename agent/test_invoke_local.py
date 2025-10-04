#!/usr/bin/env python3
"""
Local test script for Customer Retention Agent
Tests the invoke function directly with various scenarios
"""

import os
import sys
import json
import base64
from main import invoke

def decode_jwt_payload(token):
    """Decode JWT payload to see what's inside"""
    try:
        # Split the token
        parts = token.split('.')
        if len(parts) != 3:
            print(f"❌ Invalid JWT format: expected 3 parts, got {len(parts)}")
            return None
        
        # Decode the payload (middle part)
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"❌ Error decoding JWT: {e}")
        return None

def get_test_jwt_token():
    """Get a test JWT token for local testing"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        import hashlib
        import hmac

        # Test credentials
        username = "test-user"
        password = "<test-pw>"
        
        # Cognito App Client details
        user_pool_id = os.environ.get("NEXT_PUBLIC_USER_POOL_ID", "YOUR_USER_POOL_ID")
        client_id = os.environ.get("NEXT_PUBLIC_USER_POOL_WEB_CLIENT_ID", "YOUR_CLIENT_ID")
        client_secret = os.environ.get("NEXT_PUBLIC_USER_POOL_WEB_CLIENT_SECRET", "<secret>")
        region = os.environ.get("NEXT_PUBLIC_AWS_REGION", "us-east-1")

        cognito_client = boto3.client('cognito-idp', region_name=region)

        # Calculate SECRET_HASH
        message = username + client_id
        dig = hmac.new(client_secret.encode('utf-8'), msg=message.encode('utf-8'), digestmod=hashlib.sha256).digest()
        secret_hash = base64.b64encode(dig).decode('utf-8')

        response = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
                'SECRET_HASH': secret_hash,
            },
            ClientId=client_id
        )
        
        auth_result = response['AuthenticationResult']
        access_token = auth_result['AccessToken']
        
        print(f"✅ Authentication successful!")
        print(f"Access token: {access_token[:50]}...")
        
        # Decode JWT payload to see what's inside
        token_payload = decode_jwt_payload(access_token)
        if token_payload:
            print(f"🔍 JWT Payload: {json.dumps(token_payload, indent=2)}")
        else:
            print("❌ Failed to decode JWT payload")
        
        return access_token
        
    except ClientError as e:
        print(f"❌ Authentication failed: {e}")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred during authentication: {e}")
        return None

def test_agent_scenario(scenario_name, prompt, customer_id=None, user_id=None):
    """Test a specific scenario with the agent"""
    print(f"\n🧪 Testing Scenario: {scenario_name}")
    print("-" * 50)
    print(f"Prompt: {prompt}")
    if customer_id:
        print(f"Customer ID: {customer_id}")
    if user_id:
        print(f"User ID: {user_id}")
    
    try:
        # Create payload
        payload = {"prompt": prompt}
        if customer_id:
            payload["customerId"] = customer_id
        
        # Create context with JWT token if available
        context = None
        if user_id:
            # For local testing, we'll simulate the context
            context = {
                "headers": {
                    "Authorization": f"Bearer {user_id}"  # Using user_id as token for testing
                }
            }
        
        # Call the invoke function
        response = invoke(payload, user_id=user_id, context=context)
        
        print(f"✅ Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 Local Agent Testing Suite")
    print("=" * 60)
    
    # Get JWT token for testing
    jwt_token = get_test_jwt_token()
    if not jwt_token:
        print("❌ Failed to get JWT token. Exiting.")
        return
    
    print("\n" + "=" * 60)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Basic Greeting",
            "prompt": "Hello, I need help with my account",
            "customer_id": "test-user"
        },
        {
            "name": "Customer ID Recognition",
            "prompt": "What did I tell you about my customer ID in our previous conversation?",
            "customer_id": "test-user"
        },
        {
            "name": "Discount Code Request",
            "prompt": "I want a discount code for my account",
            "customer_id": "test-user"
        },
        {
            "name": "Product Catalog Query",
            "prompt": "What plans do you have available?",
            "customer_id": "test-user"
        }
    ]
    
    # Run all test scenarios
    success_count = 0
    total_tests = len(test_scenarios)
    
    for scenario in test_scenarios:
        success = test_agent_scenario(
            scenario["name"],
            scenario["prompt"],
            scenario.get("customer_id"),
            jwt_token
        )
        if success:
            success_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Agent is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    print("\n" + "=" * 60)
    print("🏁 Local agent testing completed!")

if __name__ == "__main__":
    main()