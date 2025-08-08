#!/usr/bin/env python3
"""
Quick Slack Connection Test
Simple script to test if Slack token works and can send messages.
"""

import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime

def test_slack_quick():
    """Quick test of Slack connection"""
    
    # Load environment variables
    load_dotenv()
    
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN not found in .env file")
        return False
    
    print(f"🔧 Testing Slack token: {slack_token[:12]}...")
    
    # Test 1: Auth test (fastest way to verify token)
    print("1️⃣ Testing authentication...")
    try:
        auth_response = requests.post(
            "https://slack.com/api/auth.test",
            headers={"Authorization": f"Bearer {slack_token}"},
            timeout=10
        )
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            if auth_data.get("ok"):
                print(f"✅ Auth OK - Bot: {auth_data.get('user', 'unknown')}")
                print(f"   Team: {auth_data.get('team', 'unknown')}")
            else:
                print(f"❌ Auth failed: {auth_data.get('error', 'unknown')}")
                return False
        else:
            print(f"❌ HTTP Error: {auth_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        return False
    
    # Test 2: Send a simple test message
    print("2️⃣ Testing message sending...")
    test_message = f"🤖 Quick test from log analysis system - {datetime.now().strftime('%H:%M:%S')}"
    
    payload = {
        "channel": "general",
        "text": test_message,
        "username": "TestBot"
    }
    
    try:
        message_response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {slack_token}",
                "Content-Type": "application/json"
            },
            data=json.dumps(payload),
            timeout=10
        )
        
        if message_response.status_code == 200:
            msg_data = message_response.json()
            if msg_data.get("ok"):
                print(f"✅ Message sent successfully!")
                print(f"   Channel: #{msg_data.get('channel', 'unknown')}")
                print(f"   Timestamp: {msg_data.get('ts', 'unknown')}")
                return True
            else:
                error = msg_data.get('error', 'unknown')
                print(f"❌ Message failed: {error}")
                
                # Provide specific help
                if error == 'channel_not_found':
                    print("💡 Channel 'general' not found or bot can't access it")
                elif error == 'not_in_channel':
                    print("💡 Bot not in #general channel - invite it first")
                elif error == 'invalid_auth':
                    print("💡 Token invalid or expired")
                    
                return False
        else:
            print(f"❌ HTTP Error: {message_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Message test failed: {e}")
        return False

def main():
    print("🚀 Quick Slack Connection Test")
    print("=" * 35)
    
    success = test_slack_quick()
    
    if success:
        print("\n🎉 Slack connection working perfectly!")
        print("✅ Your notebook should be able to send reports to Slack")
    else:
        print("\n⚠️ Slack connection issues detected")
        print("🔧 Troubleshooting steps:")
        print("   1. Check SLACK_BOT_TOKEN in .env")
        print("   2. In Slack: /invite @your-bot-name to #general")
        print("   3. Verify bot has 'chat:write' permission")
        print("   4. Make sure bot token starts with 'xoxb-'")

if __name__ == "__main__":
    main()
