#!/usr/bin/env python3
"""
Test the invoke function locally with real user_id
Simulates what AgentCore Runtime would do
"""

import os
import sys
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_invoke_with_user_id():
    """Test the invoke function with different user_id values"""
    
    print("🧪 Testing invoke function with real user_id")
    print("=" * 50)
    
    try:
        from main import invoke
        
        # Test case with the actual Cognito user ID
        test_cases = [
            {
                "name": "Test with Cognito user ID",
                "payload": {"prompt": "I need discount codes for my account"},
                "user_id": "d4e884b8-70a1-7024-9457-deb37a8c77cb"  # Your actual Cognito user ID
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔍 Test {i}: {test_case['name']}")
            print(f"User ID: {test_case['user_id']}")
            print(f"Prompt: {test_case['payload']['prompt']}")
            
            try:
                response = invoke(test_case['payload'], user_id=test_case['user_id'])
                print(f"✅ Response: {response[:150]}...")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n🎉 Invoke function tests completed!")
        
    except Exception as e:
        print(f"❌ Error importing invoke function: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Testing invoke function locally")
    print("=" * 50)
    
    test_invoke_with_user_id()
    
    print("\n🏁 Invoke function testing completed!")
