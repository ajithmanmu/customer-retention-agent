#!/usr/bin/env python3
"""
Generate Cognito Authorization URL for testing
"""

import urllib.parse
import webbrowser
import sys

def generate_cognito_auth_url():
    """
    Generate the Cognito authorization URL for testing
    """
    
    # Configuration - UPDATE THESE VALUES
    USER_POOL_DOMAIN = "us-east-1u4mavayc5.auth.us-east-1.amazoncognito.com"  # Correct domain from your console
    WEB_CLIENT_ID = "YOUR_WEB_CLIENT_ID_HERE"  # Replace with your actual Web Client ID
    REDIRECT_URI = "https://d84l1y8p4kdic.cloudfront.net"  # Use the working redirect URI from console
    
    # OAuth 2.0 parameters
    params = {
        "response_type": "code",
        "client_id": WEB_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "email openid phone",  # Match the working URL format
        "state": "test-state-123"  # Optional: for security
    }
    
    # Build the authorization URL
    base_url = f"https://{USER_POOL_DOMAIN}/login"  # Use /login path like the working URL
    query_string = urllib.parse.urlencode(params)
    auth_url = f"{base_url}?{query_string}"
    
    return auth_url, params

def main():
    """
    Main function to generate and display the auth URL
    """
    print("🔐 Cognito Authorization URL Generator")
    print("=" * 50)
    
    # Get user input
    web_client_id = input("Enter your Web Client ID: ").strip()
    
    if not web_client_id or web_client_id == "YOUR_WEB_CLIENT_ID_HERE":
        print("❌ Please provide a valid Web Client ID")
        return
    
    # Generate the URL
    auth_url, params = generate_cognito_auth_url()
    
    # Update with actual client ID
    auth_url = auth_url.replace("YOUR_WEB_CLIENT_ID_HERE", web_client_id)
    
    print(f"\n📋 Configuration:")
    print(f"User Pool Domain: us-east-1u4mavayc5.auth.us-east-1.amazoncognito.com")
    print(f"Web Client ID: {web_client_id}")
    print(f"Redirect URI: http://localhost:8080/callback")
    print(f"Scopes: openid email profile")
    
    print(f"\n🔗 Authorization URL:")
    print(f"{auth_url}")
    
    print(f"\n📝 What happens next:")
    print(f"1. Click the URL above or copy it to your browser")
    print(f"2. You'll see the Cognito login page")
    print(f"3. Enter your test user credentials")
    print(f"4. After login, you'll be redirected to: http://localhost:8080/callback")
    print(f"5. The URL will contain an authorization code")
    
    # Ask if user wants to open in browser
    open_browser = input(f"\n🌐 Open in browser? (y/n): ").strip().lower()
    if open_browser in ['y', 'yes']:
        try:
            webbrowser.open(auth_url)
            print("✅ Opened in browser!")
        except Exception as e:
            print(f"❌ Could not open browser: {e}")
            print("Please copy the URL above and paste it in your browser")
    
    print(f"\n💡 Note: The redirect will fail (localhost:8080 doesn't exist)")
    print(f"   But you'll see the Cognito login page and can test the flow!")

if __name__ == "__main__":
    main()
