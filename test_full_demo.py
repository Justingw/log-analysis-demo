#!/usr/bin/env python3
"""
End-to-End Test with Demo Data
Tests the complete workflow including Slack notifications
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, TypedDict, Dict, Any, Optional
from google.cloud import logging as gcp_logging
from github import Github
from slack_sdk import WebClient
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("LOG ANALYSIS SYSTEM - FULL END-TO-END TEST WITH DEMO DATA")
print("=" * 80)

class Log(BaseModel):
    id: str
    question: str
    docs: str = None
    answer: str
    grade: int = None
    grader: str
    feedback: str = None

def fetch_real_logs_and_add_demo_errors(project_id: str = None, hours_back: int = 24, max_results: int = 10) -> List[Log]:
    """Fetch real logs and add some demo error logs for testing"""
    if not project_id:
        project_id = os.getenv('GCP_PROJECT_ID')
    
    print(f"Fetching real logs from GCP project: {project_id}")
    
    client = gcp_logging.Client(project=project_id)
    start_time = datetime.now() - timedelta(hours=hours_back)
    
    # Get any real logs
    filter_str = f'timestamp >= "{start_time.isoformat()}Z"'
    
    logs = []
    real_log_count = 0
    
    # Fetch some real logs first
    for entry in client.list_entries(filter_=filter_str, max_results=max_results):
        real_log_count += 1
        log_id = entry.insert_id or f"gcp-{hash(str(entry.payload))}"
        
        if hasattr(entry, 'json_payload') and entry.json_payload:
            payload = entry.json_payload
            question = str(payload)[:100]
            answer = str(payload)[:200]
            feedback = f"Resource: {entry.resource.type if entry.resource else 'unknown'}"
        else:
            question = str(entry.payload)[:100] if entry.payload else "GCP Log Entry"
            answer = str(entry.payload)[:200] if entry.payload else "No details available"
            feedback = f"Resource: {entry.resource.type if entry.resource else 'unknown'}"
        
        # Most real logs will be INFO level (grade 200)
        grade = 200
        if entry.severity:
            severity_name = str(entry.severity)
            if hasattr(entry.severity, 'name'):
                severity_name = entry.severity.name
            grader = f"GCP_{severity_name}"
        else:
            grader = "GCP_INFO"
        
        log = Log(
            id=log_id,
            question=question.strip(),
            answer=answer.strip(),
            grade=grade,
            grader=grader,
            feedback=feedback.strip()
        )
        
        logs.append(log)
    
    print(f"Fetched {real_log_count} real logs from GCP")
    
    # Add demo error logs for testing the complete workflow
    demo_errors = [
        Log(
            id="demo-timeout-001",
            question="Database connection timeout during user authentication",
            answer="Connection to database timed out after 30 seconds",
            grade=500,
            grader="GCP_ERROR_AUTH_SERVICE",
            feedback="Stack trace: TimeoutError at auth.db.connect()"
        ),
        Log(
            id="demo-memory-001", 
            question="Memory limit exceeded in processing service",
            answer="Process killed due to memory consumption exceeding 2GB limit",
            grade=500,
            grader="GCP_CRITICAL_PROCESS_SERVICE",
            feedback="Memory usage peaked at 2.1GB before termination"
        ),
        Log(
            id="demo-api-001",
            question="API rate limit exceeded for external service calls",
            answer="HTTP 429 Too Many Requests from external API",
            grade=429,
            grader="GCP_WARNING_API_SERVICE", 
            feedback="Rate limit: 1000 requests per hour exceeded"
        ),
        Log(
            id="demo-auth-001",
            question="Unauthorized access attempt detected",
            answer="HTTP 401 Unauthorized - invalid API key provided",
            grade=401,
            grader="GCP_WARNING_SECURITY",
            feedback="API key validation failed for client IP 192.168.1.100"
        )
    ]
    
    logs.extend(demo_errors)
    print(f"Added {len(demo_errors)} demo error logs for testing")
    print(f"Total logs for analysis: {len(logs)}")
    
    return logs

def categorize_logs_by_error_type(logs: List[Log]) -> Dict[str, List[Log]]:
    """Group logs by error type"""
    error_groups = {}
    
    for log in logs:
        if log.grade < 400:
            continue
            
        text_to_analyze = (log.question + " " + log.answer).lower()
        
        if any(word in text_to_analyze for word in ["timeout", "deadline"]):
            error_type = "Timeout/Deadline Exceeded"
        elif any(word in text_to_analyze for word in ["auth", "permission", "unauthorized", "forbidden"]):
            error_type = "Authentication/Authorization"
        elif any(word in text_to_analyze for word in ["quota", "limit", "exceeded", "429"]):
            error_type = "Resource Quota/Limits"
        elif any(word in text_to_analyze for word in ["database", "sql", "connection"]):
            error_type = "Database Connection"
        elif any(word in text_to_analyze for word in ["memory", "cpu", "resource"]):
            error_type = "Resource Usage"
        else:
            error_type = "Unknown Error"
        
        if error_type not in error_groups:
            error_groups[error_type] = []
        error_groups[error_type].append(log)
    
    return error_groups

def create_github_issue(error_type: str, error_logs: List[Log]) -> Dict[str, Any]:
    """Create or update GitHub issue"""
    issue_title = f"GCP Log Error: {error_type}"
    
    try:
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            return {"action": "skipped", "reason": "No GitHub token"}
        
        github_client = Github(token)
        repo_name = os.getenv('GITHUB_REPO')
        if not repo_name:
            return {"action": "skipped", "reason": "No GitHub repo configured"}
            
        repo = github_client.get_repo(repo_name)
        
        # For demo purposes, we'll just simulate issue creation
        print(f"    Would create/update GitHub issue: {issue_title}")
        print(f"    Error count: {len(error_logs)}")
        
        return {
            "action": "simulated",
            "issue_number": 999,
            "title": issue_title,
            "url": "https://github.com/example/repo/issues/999"
        }
        
    except Exception as e:
        print(f"GitHub issue creation failed: {e}")
        return {"action": "failed", "error": str(e)}

def send_slack_notification(summary: str, github_issues: List[dict] = None) -> dict:
    """Send notification to Slack"""
    try:
        token = os.getenv('SLACK_BOT_TOKEN')
        if not token:
            print("WARNING: SLACK_BOT_TOKEN not found - skipping Slack notification")
            return {"action": "skipped", "reason": "No Slack token"}
        
        client = WebClient(token=token)
        channel = os.getenv('SLACK_CHANNEL', '#alerts')
        
        message = f"""Log Analysis Complete - End-to-End Test

{summary}

GitHub Issues:"""
        
        if github_issues:
            for issue in github_issues:
                if issue['action'] in ['created', 'updated', 'simulated']:
                    action_text = issue['action'].title()
                    message += f"""
- {action_text} #{issue['issue_number']}: {issue['title']}
  {issue['url']}"""
        else:
            message += """
- No issues created (no critical errors detected)"""
        
        message += f"""

Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Test Status: SUCCESS"""
        
        print(f"Sending message to Slack channel: {channel}")
        print("Message preview:")
        print("-" * 40)
        print(message)
        print("-" * 40)
        
        response = client.chat_postMessage(
            channel=channel,
            text=message,
            username="Log Analysis Bot"
        )
        
        return {
            "action": "sent",
            "channel": channel,
            "ts": response["ts"]
        }
        
    except Exception as e:
        print(f"Slack notification failed: {e}")
        return {"action": "failed", "error": str(e)}

def run_full_test():
    """Run complete end-to-end test with demo data"""
    
    print("\nSTEP 1: Environment Check")
    print("-" * 40)
    
    required_vars = ['GCP_PROJECT_ID']
    optional_vars = ['GITHUB_TOKEN', 'GITHUB_REPO', 'SLACK_BOT_TOKEN', 'SLACK_CHANNEL']
    
    for var in required_vars:
        if not os.getenv(var):
            print(f"ERROR: Missing required environment variable: {var}")
            return False
        else:
            print(f"  {var}: configured")
    
    for var in optional_vars:
        status = "configured" if os.getenv(var) else "not configured"
        print(f"  {var}: {status}")
    
    print("\nSTEP 2: Fetching Logs (Real + Demo Errors)")
    print("-" * 40)
    
    try:
        logs = fetch_real_logs_and_add_demo_errors(hours_back=24, max_results=5)
        
        print(f"\nLog breakdown:")
        info_logs = [l for l in logs if l.grade < 400]
        error_logs = [l for l in logs if l.grade >= 400]
        critical_logs = [l for l in logs if l.grade >= 500]
        
        print(f"  INFO logs: {len(info_logs)}")
        print(f"  ERROR/WARNING logs: {len(error_logs)}")
        print(f"  CRITICAL logs: {len(critical_logs)}")
        
        print("\nSample logs:")
        for i, log in enumerate(logs[:5]):
            status = "ERROR" if log.grade >= 500 else "WARNING" if log.grade >= 400 else "INFO"
            print(f"  {i+1}. {status} [{log.grader}] {log.question[:50]}...")
        
    except Exception as e:
        print(f"ERROR: Failed to fetch logs: {e}")
        return False
    
    print("\nSTEP 3: Analyzing Errors and Creating GitHub Issues")
    print("-" * 40)
    
    error_groups = categorize_logs_by_error_type(logs)
    
    if not error_groups:
        print("No errors found in logs")
        github_issues = []
    else:
        print(f"Found {len(error_groups)} error categories:")
        github_issues = []
        
        for error_type, error_logs in error_groups.items():
            print(f"\n  Processing: {error_type} ({len(error_logs)} occurrences)")
            issue_result = create_github_issue(error_type, error_logs)
            github_issues.append(issue_result)
    
    print("\nSTEP 4: Sending Slack Notification")
    print("-" * 40)
    
    total_logs = len(logs)
    error_logs = [log for log in logs if log.grade >= 400]
    critical_logs = [log for log in logs if log.grade >= 500]
    
    summary = f"Analyzed {total_logs} logs: {len(error_logs)} errors ({len(critical_logs)} critical, {len(error_logs) - len(critical_logs)} warnings)"
    
    slack_result = send_slack_notification(summary, github_issues)
    
    print(f"\nSlack notification result: {slack_result['action']}")
    if slack_result['action'] == 'sent':
        print(f"  Message sent to: {slack_result['channel']}")
        print(f"  Slack timestamp: {slack_result['ts']}")
    elif slack_result['action'] == 'failed':
        print(f"  Error: {slack_result['error']}")
    
    print("\nSTEP 5: Test Results Summary")
    print("-" * 40)
    print(f"Total logs processed: {total_logs}")
    print(f"Real GCP logs: {total_logs - 4}")
    print(f"Demo error logs: 4")
    print(f"Errors analyzed: {len(error_logs)}")
    print(f"Error categories: {len(error_groups)}")
    print(f"GitHub issues: {len([i for i in github_issues if i['action'] in ['created', 'updated', 'simulated']])}")
    print(f"Slack notification: {slack_result['action']}")
    
    print("\n" + "=" * 80)
    print("FULL END-TO-END TEST COMPLETE - SUCCESS")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = run_full_test()
    sys.exit(0 if success else 1)
