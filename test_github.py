#!/usr/bin/env python3
"""
GitHub Integration Test Script
Tests if GitHub API credentials are working correctly.
"""

import os
from dotenv import load_dotenv
from github import Github
from github.GithubException import GithubException

def test_github_connection():
    """Test GitHub API connection and permissions"""
    load_dotenv()
    
    # Check if token exists
    token = os.getenv('GITHUB_TOKEN')
    repo_name = os.getenv('GITHUB_REPO')
    
    if not token:
        print("❌ GITHUB_TOKEN not found in .env file")
        print("📝 Please add your GitHub Personal Access Token to .env")
        return False
    
    if not repo_name:
        print("❌ GITHUB_REPO not found in .env file")
        return False
    
    try:
        # Test API connection
        print("🔍 Testing GitHub API connection...")
        github_client = Github(token)
        user = github_client.get_user()
        print(f"✅ Connected as: {user.login}")
        
        # Test repository access
        print(f"🔍 Testing repository access: {repo_name}")
        repo = github_client.get_repo(repo_name)
        print(f"✅ Repository found: {repo.full_name}")
        print(f"   - Description: {repo.description}")
        print(f"   - Private: {repo.private}")
        
        # Test permissions
        print("🔍 Testing repository permissions...")
        permissions = repo.get_collaborator_permission(user.login)
        print(f"✅ Permission level: {permissions}")
        
        # Check if we can list issues
        issues = list(repo.get_issues(state="all"))
        print(f"✅ Can access issues: {len(issues)} total issues found")
        
        return True
        
    except GithubException as e:
        print(f"❌ GitHub API Error: {e}")
        if e.status == 401:
            print("💡 This usually means the token is invalid or expired")
        elif e.status == 404:
            print("💡 Repository not found or no access permissions")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 GitHub Integration Test")
    print("=" * 40)
    
    success = test_github_connection()
    
    if success:
        print("\n🎉 GitHub integration is ready!")
        print("✅ You can now create issues automatically from your log analysis system")
    else:
        print("\n❌ GitHub integration needs attention")
        print("📋 Next steps:")
        print("   1. Create a GitHub Personal Access Token")
        print("   2. Add it to your .env file as GITHUB_TOKEN")
        print("   3. Make sure the token has 'repo' and 'issues' permissions")
