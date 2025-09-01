#!/usr/bin/env python3
"""
Enhanced Log Analysis System with Database Incident Response
Improved version that specifically handles CloudSQL database alerts
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pydantic import BaseModel

# Import the database incident response module
from database_incident_response import DatabaseIncidentAnalyzer, create_database_incident_issue

from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("ENHANCED LOG ANALYSIS SYSTEM - DATABASE INCIDENT RESPONSE")
print("=" * 80)

class Log(BaseModel):
    id: str
    question: str
    docs: str = None
    answer: str
    grade: int = None
    grader: str
    feedback: str = None

def create_demo_cloudsql_logs() -> List[Log]:
    """Create demo CloudSQL logs that match the GitHub issue #14 pattern"""
    
    demo_logs = [
        # Critical CloudSQL connection errors similar to issue #14
        Log(
            id="cloudsql-error-001",
            question="CloudSQL Database Connection Failure",
            answer="Database: august-impact-457008-d6:thinkoptic-sql - Connection timeout after 30 seconds",
            grade=500,
            grader="GCP_ERROR_CLOUDSQL",
            feedback="2025-09-01 09:22:26.764 UTC [10600]: [19-1] db=thinkoptic,user=postgres,host=196.192.186.58 ERROR: connection timeout"
        ),
        Log(
            id="cloudsql-error-002", 
            question="CloudSQL Database Connection Failure",
            answer="Database: august-impact-457008-d6:thinkoptic-sql - Connection refused by server",
            grade=500,
            grader="GCP_ERROR_CLOUDSQL",
            feedback="2025-09-01 09:22:26.758 UTC [10600]: [17-1] db=thinkoptic,user=postgres,host=196.192.186.58 ERROR: connection refused"
        ),
        Log(
            id="cloudsql-error-003",
            question="CloudSQL Database Connection Failure", 
            answer="Database: august-impact-457008-d6:thinkoptic-sql - Too many connections",
            grade=500,
            grader="GCP_ERROR_CLOUDSQL",
            feedback="2025-09-01 09:22:00.957 UTC [10600]: [15-1] db=thinkoptic,user=postgres,host=196.192.186.58 ERROR: too many connections"
        ),
        # Multiple similar errors to simulate the 136 errors from issue #14
        *[Log(
            id=f"cloudsql-batch-error-{i:03d}",
            question="CloudSQL Database Connection Issues",
            answer=f"Database: august-impact-457008-d6:thinkoptic-sql - Connection timeout during heavy load",
            grade=500,
            grader="GCP_ERROR_CLOUDSQL",
            feedback=f"2025-09-01 09:19:29.679 UTC [10600]: [11-{i}] db=thinkoptic,user=postgres,host=196.192.186.58 ERROR: connection timeout after 30 seconds"
        ) for i in range(4, 140)],  # Simulate the actual 136+ errors from issue #14
        
        # Add some other database-related errors
        Log(
            id="cloudsql-auth-001",
            question="CloudSQL Authentication Failure",
            answer="Database: august-impact-457008-d6:thinkoptic-sql - Authentication failed for user postgres",
            grade=401,
            grader="GCP_WARNING_CLOUDSQL",
            feedback="Authentication failed: password incorrect"
        ),
        Log(
            id="cloudsql-resource-001",
            question="CloudSQL Resource Exhaustion",
            answer="Database: august-impact-457008-d6:thinkoptic-sql - Out of memory error",
            grade=503,
            grader="GCP_CRITICAL_CLOUDSQL", 
            feedback="Resource exhausted: insufficient memory for operation"
        )
    ]
    
    print(f"Created {len(demo_logs)} demo CloudSQL logs matching issue #14 pattern")
    return demo_logs

def analyze_database_incidents_and_create_issues(logs: List[Log]) -> List[Dict[str, Any]]:
    """Analyze logs for database incidents and create appropriate GitHub issues"""
    
    analyzer = DatabaseIncidentAnalyzer()
    incidents = analyzer.analyze_database_logs(logs)
    
    created_issues = []
    
    print(f"\nDatabase Incident Analysis Results:")
    print("=" * 50)
    
    for incident in incidents:
        print(f"\n🔍 Incident: {incident.incident_type.replace('_', ' ').title()}")
        print(f"   Database: {incident.database_instance}")
        print(f"   Severity: {incident.severity}")
        print(f"   Error Count: {incident.error_count}")
        print(f"   Escalation Required: {'Yes' if incident.escalation_required else 'No'}")
        
        # Create GitHub issue for this incident
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        issue_data = create_database_incident_issue(incident, timestamp)
        
        print(f"   📋 Would create GitHub issue: {issue_data['title']}")
        print(f"   🏷️  Labels: {', '.join(issue_data['labels'])}")
        
        # Simulate issue creation
        created_issues.append({
            'action': 'created',
            'incident': incident,
            'issue_data': issue_data,
            'issue_number': len(created_issues) + 100,  # Simulate issue numbers
            'url': f"https://github.com/Justingw/log-analysis-demo/issues/{len(created_issues) + 100}"
        })
    
    return created_issues

def generate_incident_summary_report(issues: List[Dict[str, Any]]) -> str:
    """Generate a summary report of all database incidents"""
    
    total_incidents = len(issues)
    critical_incidents = sum(1 for issue in issues if issue['incident'].severity == 'CRITICAL')
    warning_incidents = sum(1 for issue in issues if issue['incident'].severity == 'WARNING')
    escalation_required = sum(1 for issue in issues if issue['incident'].escalation_required)
    
    total_errors = sum(issue['incident'].error_count for issue in issues)
    
    report = f"""
🚨 DATABASE INCIDENT RESPONSE SUMMARY
{'=' * 50}

📊 INCIDENT OVERVIEW:
   • Total Incidents: {total_incidents}
   • Critical Incidents: {critical_incidents}
   • Warning Incidents: {warning_incidents}
   • Escalation Required: {escalation_required}
   • Total Errors Processed: {total_errors}

🏥 INCIDENTS CREATED:"""
    
    for i, issue in enumerate(issues, 1):
        incident = issue['incident']
        severity_emoji = {'CRITICAL': '🚨', 'WARNING': '⚠️', 'INFO': 'ℹ️'}.get(incident.severity, '🔍')
        
        report += f"""
   {i}. {severity_emoji} {incident.incident_type.replace('_', ' ').title()}
      Database: {incident.database_instance}
      Errors: {incident.error_count} | Severity: {incident.severity}
      Escalation: {'Required' if incident.escalation_required else 'Not Required'}
      Issue: #{issue['issue_number']}"""
    
    report += f"""

🎯 NEXT STEPS:
   • Review all {critical_incidents} critical incidents immediately
   • Escalate {escalation_required} incidents to on-call team
   • Monitor database health and error patterns
   • Implement recommended preventive measures

📈 MONITORING:
   • Continue monitoring CloudSQL instance metrics
   • Track error rate trends and recovery
   • Document resolution steps for knowledge base

Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
    
    return report

def run_enhanced_database_analysis():
    """Run the enhanced database incident analysis"""
    
    print("STEP 1: Creating Demo CloudSQL Logs")
    print("-" * 40)
    logs = create_demo_cloudsql_logs()
    
    print(f"✅ Created {len(logs)} CloudSQL logs for analysis")
    print(f"   - Simulating the 136 errors from GitHub issue #14")
    print(f"   - Database instance: august-impact-457008-d6:thinkoptic-sql")
    print(f"   - Error types: Connection timeouts, authentication failures, resource issues")
    
    print("\nSTEP 2: Enhanced Database Incident Analysis")
    print("-" * 40)
    
    issues = analyze_database_incidents_and_create_issues(logs)
    
    print(f"\n✅ Analysis complete: {len(issues)} incidents identified")
    
    print("\nSTEP 3: Incident Summary Report")
    print("-" * 40)
    
    summary_report = generate_incident_summary_report(issues)
    print(summary_report)
    
    print("\nSTEP 4: GitHub Issue Preview")
    print("-" * 40)
    
    if issues:
        # Show a preview of one of the created issues
        sample_issue = issues[0]
        print("📋 Sample GitHub Issue Preview:")
        print("=" * 50)
        print(f"Title: {sample_issue['issue_data']['title']}")
        print("\nBody Preview (first 500 chars):")
        print(sample_issue['issue_data']['body'][:500] + "...")
        print(f"\nLabels: {', '.join(sample_issue['issue_data']['labels'])}")
    
    print("\n" + "=" * 80)
    print("ENHANCED DATABASE INCIDENT RESPONSE COMPLETE")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = run_enhanced_database_analysis()
    sys.exit(0 if success else 1)