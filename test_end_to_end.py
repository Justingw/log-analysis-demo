#!/usr/bin/env python3
"""
End-to-End Test Script for Log Analysis System
Fetches logs from GCP, analyzes them, creates GitHub issues, and sends Slack notifications
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, TypedDict, Dict, Any, Optional
from google.cloud import logging as gcp_logging
from github import Github
from slack_sdk import WebClient
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

try:
    from langgraph.graph import Send
except ImportError:
    Send = None

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("LOG ANALYSIS SYSTEM - END-TO-END TEST")
print("=" * 80)

# Log structure definition
class Log(BaseModel):
    id: str
    question: str
    docs: str = None
    answer: str
    grade: int = None
    grader: str
    feedback: str = None

# GCP Log Fetcher
def fetch_gcp_logs(project_id: str = None, hours_back: int = 6, max_results: int = 20) -> List[Log]:
    """Fetch logs from GCP Cloud Logging"""
    if not project_id:
        project_id = os.getenv('GCP_PROJECT_ID')
    
    if not project_id:
        raise ValueError("GCP_PROJECT_ID not found in environment variables")
    
    print(f"Fetching logs from GCP project: {project_id}")
    
    client = gcp_logging.Client(project=project_id)
    start_time = datetime.now() - timedelta(hours=hours_back)
    
    # Enhanced filter for meaningful logs
    filter_str = f'''
    timestamp >= "{start_time.isoformat()}Z"
    AND (
        severity >= "WARNING"
        OR jsonPayload.level >= "warn" 
        OR textPayload:"error"
        OR textPayload:"failed"
        OR textPayload:"timeout"
        OR textPayload:"exception"
    )
    '''
    
    logs = []
    for entry in client.list_entries(filter_=filter_str, max_results=max_results):
        log_id = entry.insert_id or f"gcp-{hash(str(entry.payload))}"
        
        # Extract meaningful information
        if hasattr(entry, 'json_payload') and entry.json_payload:
            payload = entry.json_payload
            question = (
                payload.get('message', '') or
                payload.get('msg', '') or  
                payload.get('error', '') or
                str(payload)[:100]
            )
            answer = str(payload.get('error', payload))[:200]
            feedback = str(payload.get('stack_trace', ''))[:300]
        else:
            question = str(entry.payload)[:100] if entry.payload else "GCP Log Entry"
            answer = str(entry.payload)[:200] if entry.payload else "No details available"
            feedback = f"Resource: {entry.resource.type if entry.resource else 'unknown'}"
        
        # Determine grade based on severity
        grade = 400
        grader = "GCP_UNKNOWN"
        
        if entry.severity:
            severity_name = str(entry.severity) if entry.severity else "UNKNOWN"
            if hasattr(entry.severity, 'name'):
                severity_name = entry.severity.name
            
            severity_str = severity_name.upper()
            if severity_str in ['CRITICAL', 'ALERT', 'EMERGENCY', 'ERROR']:
                grade = 500
            elif severity_str in ['WARNING']:
                grade = 400
            else:
                grade = 200
            
            grader = f"GCP_{severity_name}"
            if entry.resource and hasattr(entry.resource, 'type') and entry.resource.type:
                grader += f"_{entry.resource.type.upper().replace('.', '_')}"
        
        log = Log(
            id=log_id,
            question=question.strip(),
            answer=answer.strip(),
            grade=grade,
            grader=grader,
            feedback=feedback.strip()
        )
        
        logs.append(log)
    
    print(f"Fetched {len(logs)} log entries from GCP")
    return logs

# Error categorization
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
        elif any(word in text_to_analyze for word in ["quota", "limit", "exceeded"]):
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

# GitHub Integration
def create_github_issue(error_type: str, error_logs: List[Log]) -> Dict[str, Any]:
    """Create or update GitHub issue"""
    issue_title = f"GCP Log Error: {error_type}"
    issue_body = f"""
## Error Summary
**Error Type**: {error_type}  
**Total Occurrences**: {len(error_logs)}  
**First Detected**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Source**: GCP Log Analysis System

## Error Details
"""
    
    for i, log in enumerate(error_logs[:3]):
        issue_body += f"""
### Occurrence {i+1}
- **Log ID**: {log.id}
- **Context**: {log.question}
- **Error**: {log.feedback}
- **Severity**: {log.grade}
"""
    
    if len(error_logs) > 3:
        issue_body += f"\n... and {len(error_logs) - 3} more occurrences"
    
    issue_body += """

## Recommended Actions
- [ ] Investigate the root cause of this error
- [ ] Review recent deployments or configuration changes  
- [ ] Check system resources and dependencies
- [ ] Update monitoring and alerting if needed

---
*Auto-generated by Multi-Agent Log Analysis System*
    """
    
    try:
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print("WARNING: GITHUB_TOKEN not found - skipping GitHub issue creation")
            return {"action": "skipped", "reason": "No GitHub token"}
        
        github_client = Github(token)
        repo_name = os.getenv('GITHUB_REPO')
        if not repo_name:
            print("WARNING: GITHUB_REPO not found - skipping GitHub issue creation")
            return {"action": "skipped", "reason": "No GitHub repo configured"}
            
        repo = github_client.get_repo(repo_name)
        
        # Check for existing issues
        existing_issues = repo.get_issues(state="open", labels=["auto-generated"])
        for issue in existing_issues:
            if error_type.lower() in issue.title.lower():
                comment = f"New occurrences detected: {len(error_logs)} errors at {datetime.now()}"
                issue.create_comment(comment)
                return {
                    "action": "updated", 
                    "issue_number": issue.number,
                    "title": issue.title,
                    "url": issue.html_url
                }
        
        # Create new issue
        labels = ["auto-generated", "log-error", "bug"]
        if len(error_logs) >= 5:
            labels.append("priority-high")
        
        new_issue = repo.create_issue(title=issue_title, body=issue_body, labels=labels)
        
        return {
            "action": "created",
            "issue_number": new_issue.number, 
            "title": new_issue.title,
            "url": new_issue.html_url
        }
        
    except Exception as e:
        print(f"GitHub issue creation failed: {e}")
        return {"action": "failed", "error": str(e)}

# Slack Integration
def send_slack_notification(summary: str, github_issues: List[dict] = None) -> dict:
    """Send notification to Slack"""
    try:
        token = os.getenv('SLACK_BOT_TOKEN')
        if not token:
            print("WARNING: SLACK_BOT_TOKEN not found - skipping Slack notification")
            return {"action": "skipped", "reason": "No Slack token"}
        
        client = WebClient(token=token)
        channel = os.getenv('SLACK_CHANNEL', '#alerts')
        
        message = f"""
*Log Analysis Complete*

{summary}

*GitHub Issues:*
"""
        
        if github_issues:
            for issue in github_issues:
                if issue['action'] in ['created', 'updated']:
                    action_text = "Created" if issue['action'] == 'created' else "Updated"
                    message += f"- {action_text} #{issue['issue_number']}: {issue['title']}\n  {issue['url']}\n"
        else:
            message += "- No issues created (no critical errors detected)\n"
        
        message += f"\n*Analysis completed at:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
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

# Main execution function
def run_end_to_end_test():
    """Run complete end-to-end test"""
    
    print("\nSTEP 1: Environment Check")
    print("-" * 40)
    
    required_vars = ['GCP_PROJECT_ID']
    optional_vars = ['GITHUB_TOKEN', 'GITHUB_REPO', 'SLACK_BOT_TOKEN', 'SLACK_CHANNEL']
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"  {var}: configured")
    
    if missing_required:
        print(f"ERROR: Missing required environment variables: {missing_required}")
        return False
    
    for var in optional_vars:
        status = "configured" if os.getenv(var) else "not configured"
        print(f"  {var}: {status}")
    
    print("\nSTEP 2: Fetching Logs from GCP")
    print("-" * 40)
    
    try:
        logs = fetch_gcp_logs(hours_back=6, max_results=20)
        
        if not logs:
            print("No logs found in the specified time period")
            return True
        
        print(f"Retrieved {len(logs)} logs")
        for i, log in enumerate(logs[:3]):
            status = "ERROR" if log.grade >= 500 else "WARNING" if log.grade >= 400 else "OK"
            print(f"  {i+1}. {status} [{log.grader}] {log.question[:50]}...")
        
    except Exception as e:
        print(f"ERROR: Failed to fetch logs: {e}")
        return False
    
    print("\nSTEP 3: Analyzing Logs and Creating GitHub Issues")
    print("-" * 40)
    
    # Categorize errors
    error_groups = categorize_logs_by_error_type(logs)
    
    if not error_groups:
        print("No errors found in logs")
        github_issues = []
    else:
        print(f"Found {len(error_groups)} error categories:")
        for error_type, error_logs in error_groups.items():
            print(f"  - {error_type}: {len(error_logs)} occurrences")
        
        # Create GitHub issues
        github_issues = []
        for error_type, error_logs in error_groups.items():
            print(f"  Creating issue for {error_type}...")
            issue_result = create_github_issue(error_type, error_logs)
            github_issues.append(issue_result)
            
            if issue_result['action'] in ['created', 'updated']:
                print(f"    {issue_result['action'].title()} issue #{issue_result['issue_number']}")
            else:
                print(f"    {issue_result['action'].title()}: {issue_result.get('reason', 'Unknown')}")
    
    print("\nSTEP 4: Sending Slack Notification")
    print("-" * 40)
    
    # Generate summary
    total_logs = len(logs)
    error_logs = [log for log in logs if log.grade >= 400]
    critical_logs = [log for log in logs if log.grade >= 500]
    
    summary = f"Analyzed {total_logs} logs: {len(error_logs)} errors ({len(critical_logs)} critical, {len(error_logs) - len(critical_logs)} warnings)"
    
    slack_result = send_slack_notification(summary, github_issues)
    
    if slack_result['action'] == 'sent':
        print(f"  Notification sent to {slack_result['channel']}")
    else:
        print(f"  {slack_result['action'].title()}: {slack_result.get('reason', 'Unknown')}")
    
    print("\nSTEP 5: Test Results Summary")
    print("-" * 40)
    print(f"Total logs processed: {total_logs}")
    print(f"Errors found: {len(error_logs)}")
    print(f"GitHub issues: {len([i for i in github_issues if i['action'] in ['created', 'updated']])}")
    print(f"Slack notification: {slack_result['action']}")
    
    print("\n" + "=" * 80)
    print("END-TO-END TEST COMPLETE")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = run_end_to_end_test()
    sys.exit(0 if success else 1)
