#!/usr/bin/env python3
"""
Simple test script for local AgentCore agent
Directly calls Cognito and invokes the local agent endpoint
"""

import requests
import json
import sys
import os
from botocore.exceptions import ClientError

def get_jwt_token_direct():
    """Get JWT token directly from Cognito"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # Cognito configuration
        user_pool_id = "us-east-1_U4maVaYc5"
        client_id = "13rgm18m8g39c2dn7ik8gg6in9"
        client_secret = "2k8q6ffeqr0n72njcuufhnenr3mc4nmc9t4ioj101r9jktav3n1"
        region = "us-east-1"
        
        # Test credentials
        username = "test-user"
        password = "lfWOmTOhKG4!9f"
        
        print(f"🔐 Authenticating user: {username}")
        
        # Create Cognito client
        cognito_client = boto3.client('cognito-idp', region_name=region)
        
        # Calculate SECRET_HASH
        import hmac
        import hashlib
        import base64
        
        message = username + client_id
        secret_hash = base64.b64encode(
            hmac.new(
                client_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode()
        
        # Authenticate
        response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
                'SECRET_HASH': secret_hash
            }
        )
        
        auth_result = response['AuthenticationResult']
        access_token = auth_result['AccessToken']
        
        print(f"✅ Authentication successful!")
        print(f"Access token: {access_token[:50]}...")
        
        return access_token
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None

def test_local_agent(prompt, access_token):
    """Test the local AgentCore agent"""
    try:
        url = "http://localhost:8080/invocations"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        payload = {
            "prompt": prompt
        }
        
        print(f"🚀 Sending request to local agent...")
        print(f"URL: {url}")
        print(f"Prompt: {prompt}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response received:")
            print(f"Status: {response.status_code}")
            print(f"Response: {result}")
            return result
        else:
            print(f"❌ Request failed:")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def main():
    """Main test function"""
    print("🧪 Testing Local AgentCore Agent (Simple Version)")
    print("=" * 60)
    
    # Get JWT token
    access_token = get_jwt_token_direct()
    if not access_token:
        print("❌ Failed to get JWT token. Exiting.")
        return
    
    print("\n" + "=" * 60)
    
    # Single test case to focus on JWT token issue
    # Don't mention customer ID in prompt - let JWT token handle the mapping
    test_prompt = "Hello, I need help with my account"
    
    print(f"\n🔍 Single Test: {test_prompt}")
    print("-" * 40)
    
    result = test_local_agent(test_prompt, access_token)
    
    if result:
        print(f"✅ Test completed successfully")
    else:
        print(f"❌ Test failed")
    
    print("\n" + "=" * 60)
    print("🎉 Local agent testing completed!")

if __name__ == "__main__":
    main()
