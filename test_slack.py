#!/usr/bin/env python3
"""
Slack Integration Test Script
Tests if Slack Bot credentials and permissions are working correctly.
"""

import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime

def test_slack_connection():
    """Test Slack Bot connection and permissions"""
    load_dotenv()
    
    # Check if token exists
    bot_token = os.getenv('SLACK_BOT_TOKEN')
    
    if not bot_token:
        print("SLACK_BOT_TOKEN not found in .env file")
        print("Please add your Slack Bot Token to .env")
        return False
    
    if bot_token == "xoxb-your-bot-token":
        print("Please replace the placeholder Slack token with your actual bot token")
        return False
    
    try:
        # Test API connection
        print("Testing Slack API connection...")
        client = WebClient(token=bot_token)
        
        # Test bot authentication
        auth_response = client.auth_test()
        print(f"Connected as bot: {auth_response['user']}")
        print(f"  - Team: {auth_response['team']}")
        print(f"  - Bot ID: {auth_response['user_id']}")
        
        # Test if we can list channels (basic read permission)
        print("Testing channel access...")
        channels_response = client.conversations_list(types="public_channel,private_channel", limit=5)
        channels = channels_response['channels']
        print(f"Can access {len(channels)} channels")
        
        # Find a test channel (look for general or random)
        test_channel = None
        for channel in channels:
            if channel['name'] in ['general', 'random', 'test']:
                test_channel = channel
                break
        
        if not test_channel and channels:
            test_channel = channels[0]  # Use first available channel
        
        if test_channel:
            print(f"   - Will use channel: #{test_channel['name']}")
            
            # Test if we can post messages (write permission)
            print("Testing message posting...")
            test_message = f"Log Analysis System Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            try:
                message_response = client.chat_postMessage(
                    channel=test_channel['id'],
                    text=test_message,
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "* Slack Integration Test*\n\nYour log analysis system can now send notifications to Slack! 🎉"
                            }
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "plain_text",
                                    "text": "This is a test message from your log analysis setup"
                                }
                            ]
                        }
                    ]
                )
                print(f"Successfully posted test message")
                print(f"  - Message ID: {message_response['ts']}")
                
            except SlackApiError as e:
                if e.response['error'] == 'not_in_channel':
                    print(f"Bot is not in #{test_channel['name']} channel")
                    print(f"Please invite the bot to the channel with: /invite @your-bot-name")
                else:
                    print(f"Cannot post messages: {e.response['error']}")
                    return False
        else:
            print(" No accessible channels found")
            
        return True
        
    except SlackApiError as e:
        print(f"Slack API Error: {e.response['error']}")
        
        if e.response['error'] == 'invalid_auth':
            print("This usually means the bot token is invalid or expired")
        elif e.response['error'] == 'account_inactive':
            print("The bot account may be deactivated")
        
        return False
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def list_available_channels():
    """Helper to list available Slack channels"""
    load_dotenv()
    bot_token = os.getenv('SLACK_BOT_TOKEN')
    
    if not bot_token:
        return
    
    try:
        client = WebClient(token=bot_token)
        channels_response = client.conversations_list(
            types="public_channel,private_channel", 
            limit=20
        )
        
        print("\n Available channels:")
        for channel in channels_response['channels']:
            visibility = "Private" if channel['is_private'] else "Public"
            member_count = channel.get('num_members', 'Unknown')
            print(f"   - #{channel['name']} ({visibility}, {member_count} members)")
            
    except Exception as e:
        print(f" Could not list channels: {e}")

if __name__ == "__main__":
    print("Slack Integration Test")
    print("=" * 40)
    
    success = test_slack_connection()
    
    if not success:
        print("\n Slack Bot Setup Instructions:")
        print("\n Step 1: Create a Slack App")
        print("   1. Go to https://api.slack.com/apps")
        print("   2. Click 'Create New App' > 'From scratch'")
        print("   3. Name it 'Log Analysis Bot' and select your workspace")
        
        print("\n Step 2: Configure Bot Permissions")
        print("   1. Go to 'OAuth & Permissions'")
        print("   2. Add these Bot Token Scopes:")
        print("      - chat:write (Send messages)")
        print("      - channels:read (View public channels)")
        print("      - groups:read (View private channels)")
        print("      - im:write (Send direct messages)")
        
        print("\n Step 3: Install the App")
        print("   1. Click 'Install to Workspace'")
        print("   2. Copy the 'Bot User OAuth Token' (starts with xoxb-)")
        print("   3. Add it to your .env file as SLACK_BOT_TOKEN")
        
        print("\n Step 4: Invite Bot to Channels")
        print("   1. In Slack, go to the channel you want notifications")
        print("   2. Type: /invite @log-analysis-bot")
    
    else:
        print("\n Slack integration is ready!")
        print("Your log analysis system can now send rich notifications to Slack")
        
        # List available channels for reference
        list_available_channels()
