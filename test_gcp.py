#!/usr/bin/env python3
"""
GCP Integration Test Script
Tests if Google Cloud Platform credentials and logging access are working correctly.
"""

import os
from dotenv import load_dotenv
from google.cloud import logging as gcp_logging
from google.auth.exceptions import GoogleAuthError
from google.cloud.exceptions import NotFound, Forbidden

def test_gcp_connection():
    """Test GCP logging connection and permissions"""
    load_dotenv()
    
    # Check environment variables
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = os.getenv('GCP_PROJECT_ID')
    
    print("🔍 Checking GCP environment variables...")
    if not project_id:
        print("❌ GCP_PROJECT_ID not found in .env file")
        return False
    
    print(f"✅ Project ID: {project_id}")
    
    if credentials_path and credentials_path != "path/to/service-account.json":
        if os.path.exists(credentials_path):
            print(f"✅ Credentials file found: {credentials_path}")
        else:
            print(f"❌ Credentials file not found: {credentials_path}")
            return False
    else:
        print("💡 Using default credentials (gcloud auth or metadata server)")
    
    try:
        # Test basic client creation
        print(f"🔍 Testing connection to GCP project: {project_id}")
        client = gcp_logging.Client(project=project_id)
        
        # Test if we can list log entries (basic read permission)
        print("🔍 Testing Cloud Logging permissions...")
        entries = list(client.list_entries(max_results=1))
        print(f"✅ Successfully connected to Cloud Logging")
        print(f"✅ Found {len(entries)} sample log entry")
        
        # Test different log severities available
        print("🔍 Checking available log severities...")
        filter_severities = [
            'severity >= "INFO"',
            'severity >= "WARNING"', 
            'severity >= "ERROR"'
        ]
        
        severity_counts = {}
        for filter_str in filter_severities:
            try:
                entries = list(client.list_entries(filter_=filter_str, max_results=5))
                severity = filter_str.split('"')[1]
                severity_counts[severity] = len(entries)
                print(f"   - {severity}: {len(entries)} recent entries")
            except Exception as e:
                print(f"   - {severity}: Error - {e}")
        
        # Test if we can access different log types
        print("🔍 Testing access to different log sources...")
        common_log_names = [
            "projects/{}/logs/stdout".format(project_id),
            "projects/{}/logs/stderr".format(project_id),
            "projects/{}/logs/cloudrun.googleapis.com%2Frequests".format(project_id),
            "projects/{}/logs/run.googleapis.com%2Frequests".format(project_id)
        ]
        
        for log_name in common_log_names[:2]:  # Test first 2 to avoid too much output
            try:
                entries = list(client.list_entries(
                    filter_=f'logName="{log_name}"', 
                    max_results=1
                ))
                if entries:
                    print(f"   ✅ Access to {log_name.split('/')[-1]}")
                else:
                    print(f"   📝 {log_name.split('/')[-1]} (no recent entries)")
            except Exception:
                continue
        
        return True
        
    except GoogleAuthError as e:
        print(f"❌ Authentication Error: {e}")
        print("💡 This usually means:")
        print("   - Invalid service account key")
        print("   - Expired credentials") 
        print("   - Need to run 'gcloud auth application-default login'")
        return False
    
    except Forbidden as e:
        print(f"❌ Permission Error: {e}")
        print("💡 This usually means:")
        print("   - Missing Cloud Logging Viewer role")
        print("   - Project access denied")
        return False
        
    except NotFound as e:
        print(f"❌ Project Not Found: {e}")
        print("💡 Check if the project ID is correct")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def list_gcp_projects():
    """Helper to list available GCP projects"""
    try:
        from google.cloud import resource_manager
        client = resource_manager.Client()
        projects = list(client.list_projects())
        
        print("\n📋 Available GCP projects:")
        for project in projects[:10]:  # Show first 10
            print(f"   - {project.project_id} ({project.name})")
        
        if len(projects) > 10:
            print(f"   ... and {len(projects) - 10} more projects")
            
    except Exception as e:
        print(f"❌ Could not list projects: {e}")

if __name__ == "__main__":
    print("🚀 GCP Integration Test")
    print("=" * 40)
    
    success = test_gcp_connection()
    
    if not success:
        print("\n📋 GCP Setup Options:")
        print("\n🔧 Option 1: Use Service Account (Recommended for production)")
        print("   1. Create a service account in your GCP project")
        print("   2. Download the JSON key file")
        print("   3. Set GOOGLE_APPLICATION_CREDENTIALS to the file path")
        print("   4. Assign 'Logging Viewer' role to the service account")
        
        print("\n🔧 Option 2: Use Your Personal Credentials (Good for development)")
        print("   1. Run: gcloud auth application-default login")
        print("   2. Set GCP_PROJECT_ID to your project ID")
        print("   3. Remove GOOGLE_APPLICATION_CREDENTIALS from .env")
        
        try:
            list_gcp_projects()
        except:
            print("\n💡 Run 'gcloud projects list' to see your projects")
    
    else:
        print("\n🎉 GCP integration is ready!")
        print("✅ Your log analysis system can now fetch real GCP logs")
        print("📊 Ready to analyze Cloud Run, App Engine, and Compute Engine logs")
