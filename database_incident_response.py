#!/usr/bin/env python3
"""
Database Incident Response Module
Enhanced response system for CloudSQL and database connectivity alerts
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel

class DatabaseIncident(BaseModel):
    """Structured representation of a database incident"""
    incident_type: str
    database_instance: str
    error_count: int
    severity: str  # CRITICAL, WARNING, INFO
    first_seen: datetime
    last_seen: datetime
    affected_operations: List[str]
    root_cause_analysis: str
    recommended_actions: List[str]
    escalation_required: bool

class DatabaseIncidentAnalyzer:
    """Analyzes database logs and creates structured incident reports"""
    
    def __init__(self):
        self.cloudsql_patterns = {
            'connection_timeout': [
                r'connection.*timeout',
                r'deadline.*exceeded',
                r'connect.*timed out'
            ],
            'auth_failure': [
                r'authentication.*failed',
                r'password.*incorrect',
                r'access.*denied',
                r'permission.*denied'
            ],
            'connection_limit': [
                r'too many.*connections',
                r'connection.*limit.*exceeded',
                r'max.*connections.*reached'
            ],
            'resource_exhaustion': [
                r'out of memory',
                r'disk.*full',
                r'storage.*exceeded',
                r'cpu.*limit'
            ],
            'sql_errors': [
                r'syntax error',
                r'relation.*does not exist',
                r'constraint.*violation',
                r'deadlock.*detected'
            ]
        }
    
    def analyze_database_logs(self, logs: List[Any]) -> List[DatabaseIncident]:
        """Analyze database logs and create structured incidents"""
        incidents = []
        
        # Group logs by database instance and error type
        grouped_logs = self._group_logs_by_instance_and_error(logs)
        
        for key, log_group in grouped_logs.items():
            instance, error_type = key
            incident = self._create_incident_from_logs(instance, error_type, log_group)
            incidents.append(incident)
        
        return incidents
    
    def _group_logs_by_instance_and_error(self, logs: List[Any]) -> Dict[Tuple[str, str], List[Any]]:
        """Group logs by database instance and error type"""
        grouped = {}
        
        for log in logs:
            if not self._is_database_error(log):
                continue
                
            instance = self._extract_database_instance(log)
            error_type = self._classify_database_error(log)
            
            key = (instance, error_type)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(log)
        
        return grouped
    
    def _is_database_error(self, log: Any) -> bool:
        """Check if log is a database-related error"""
        if not hasattr(log, 'grade') or log.grade < 400:
            return False
        
        text = f"{getattr(log, 'question', '')} {getattr(log, 'answer', '')} {getattr(log, 'feedback', '')}".lower()
        
        database_keywords = ['database', 'sql', 'cloudsql', 'postgres', 'mysql', 'connection']
        return any(keyword in text for keyword in database_keywords)
    
    def _extract_database_instance(self, log: Any) -> str:
        """Extract database instance name from log"""
        text = f"{getattr(log, 'question', '')} {getattr(log, 'answer', '')} {getattr(log, 'feedback', '')}"
        
        # Look for CloudSQL instance patterns
        patterns = [
            r'Database:\s*([^:)]+)',
            r'cloudsql_database.*?([a-z0-9-]+:[a-z0-9-]+)',
            r'instance[:\s]+([a-z0-9-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "unknown-instance"
    
    def _classify_database_error(self, log: Any) -> str:
        """Classify the type of database error"""
        text = f"{getattr(log, 'question', '')} {getattr(log, 'answer', '')} {getattr(log, 'feedback', '')}".lower()
        
        for error_type, patterns in self.cloudsql_patterns.items():
            if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
                return error_type
        
        return "general_database_error"
    
    def _create_incident_from_logs(self, instance: str, error_type: str, logs: List[Any]) -> DatabaseIncident:
        """Create a structured incident from grouped logs"""
        error_count = len(logs)
        severity = self._determine_severity(error_count, error_type)
        
        # Extract timestamps (simulate since we don't have real timestamps)
        now = datetime.now()
        first_seen = now
        last_seen = now
        
        # Analyze affected operations
        affected_operations = self._extract_affected_operations(logs)
        
        # Generate root cause analysis and recommendations
        root_cause, recommendations, escalation = self._generate_response_plan(error_type, error_count, instance)
        
        return DatabaseIncident(
            incident_type=error_type,
            database_instance=instance,
            error_count=error_count,
            severity=severity,
            first_seen=first_seen,
            last_seen=last_seen,
            affected_operations=affected_operations,
            root_cause_analysis=root_cause,
            recommended_actions=recommendations,
            escalation_required=escalation
        )
    
    def _determine_severity(self, error_count: int, error_type: str) -> str:
        """Determine incident severity based on error count and type"""
        if error_count >= 100:
            return "CRITICAL"
        elif error_count >= 10:
            return "WARNING" 
        elif error_type in ['connection_limit', 'resource_exhaustion']:
            return "WARNING"
        else:
            return "INFO"
    
    def _extract_affected_operations(self, logs: List[Any]) -> List[str]:
        """Extract affected database operations from logs"""
        operations = set()
        
        for log in logs:
            text = f"{getattr(log, 'question', '')} {getattr(log, 'answer', '')}".lower()
            
            if 'select' in text or 'query' in text:
                operations.add('SELECT queries')
            if 'insert' in text or 'create' in text:
                operations.add('INSERT operations')
            if 'update' in text or 'modify' in text:
                operations.add('UPDATE operations')
            if 'delete' in text or 'drop' in text:
                operations.add('DELETE operations')
            if 'connect' in text or 'auth' in text:
                operations.add('Connection establishment')
        
        return list(operations) if operations else ['General database operations']
    
    def _generate_response_plan(self, error_type: str, error_count: int, instance: str) -> Tuple[str, List[str], bool]:
        """Generate root cause analysis and response recommendations"""
        
        response_plans = {
            'connection_timeout': {
                'root_cause': 'Database connection timeouts indicate network latency, connection pool exhaustion, or database overload.',
                'actions': [
                    'Check CloudSQL instance CPU and memory utilization',
                    'Review connection pool configuration and sizing',
                    'Analyze network connectivity between client and database',
                    'Consider increasing connection timeout values',
                    'Scale up CloudSQL instance if resources are constrained'
                ],
                'escalate_threshold': 50
            },
            'auth_failure': {
                'root_cause': 'Authentication failures suggest credential issues, user permission problems, or security policy violations.',
                'actions': [
                    'Verify database user credentials and permissions',
                    'Check for recent password or user changes',
                    'Review CloudSQL IAM policies and database users',
                    'Audit application connection string configuration',
                    'Monitor for potential security threats or brute force attempts'
                ],
                'escalate_threshold': 20
            },
            'connection_limit': {
                'root_cause': 'Connection limit exceeded indicates too many concurrent connections or connection leaks.',
                'actions': [
                    'Review application connection pooling configuration',
                    'Identify and fix connection leaks in application code',
                    'Consider increasing CloudSQL max connections limit',
                    'Implement connection retry logic with exponential backoff',
                    'Monitor application instances for connection usage patterns'
                ],
                'escalate_threshold': 10
            },
            'resource_exhaustion': {
                'root_cause': 'Resource exhaustion indicates CloudSQL instance is under-provisioned for current workload.',
                'actions': [
                    'Scale up CloudSQL instance (CPU, memory, or storage)',
                    'Optimize database queries and indexes',
                    'Review and archive old data if storage is full',
                    'Consider read replicas for read-heavy workloads',
                    'Implement application-level caching to reduce database load'
                ],
                'escalate_threshold': 5
            },
            'sql_errors': {
                'root_cause': 'SQL errors indicate application code issues, schema problems, or data integrity violations.',
                'actions': [
                    'Review recent application deployments for SQL changes',
                    'Analyze failed queries for syntax or schema issues',
                    'Check database schema consistency and constraints',
                    'Review application error logs for additional context',
                    'Consider rolling back recent schema or application changes'
                ],
                'escalate_threshold': 25
            }
        }
        
        plan = response_plans.get(error_type, {
            'root_cause': 'General database error requiring investigation.',
            'actions': [
                'Review CloudSQL instance logs in GCP Console',
                'Check application logs for additional context',
                'Monitor database performance metrics',
                'Contact database administrator if issues persist'
            ],
            'escalate_threshold': 30
        })
        
        escalation_required = error_count >= plan['escalate_threshold']
        
        return plan['root_cause'], plan['actions'], escalation_required

def create_database_incident_issue(incident: DatabaseIncident, timestamp: str) -> Dict[str, Any]:
    """Create a detailed GitHub issue for database incidents"""
    
    severity_emoji = {
        'CRITICAL': '🚨',
        'WARNING': '⚠️',
        'INFO': 'ℹ️'
    }
    
    issue_title = f"{severity_emoji.get(incident.severity, '🔍')} CloudSQL Database Alert - {incident.incident_type.replace('_', ' ').title()} ({timestamp})"
    
    issue_body = f"""# {severity_emoji.get(incident.severity)} Database Incident Alert

**Alert Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## 📊 Incident Summary
- **Severity**: {incident.severity}
- **Database Instance**: `{incident.database_instance}`
- **Incident Type**: {incident.incident_type.replace('_', ' ').title()}
- **Error Count**: {incident.error_count} occurrences
- **Escalation Required**: {'Yes' if incident.escalation_required else 'No'}

## 🔍 Affected Operations
{chr(10).join(f'- {op}' for op in incident.affected_operations)}

## 🎯 Root Cause Analysis
{incident.root_cause_analysis}

## 🛠️ Recommended Actions
{chr(10).join(f'- [ ] {action}' for action in incident.recommended_actions)}

## 🚨 Escalation Guidelines
{'**IMMEDIATE ESCALATION REQUIRED** - Contact on-call DBA/SRE team' if incident.escalation_required else 'Monitor and resolve through standard procedures'}

## 📋 Investigation Checklist
- [ ] Check CloudSQL instance metrics in GCP Console
- [ ] Review application logs for correlation
- [ ] Verify recent deployments or configuration changes
- [ ] Monitor ongoing error patterns
- [ ] Document resolution steps

## 🔗 Related Resources
- [CloudSQL Instance Console](https://console.cloud.google.com/sql/instances)
- [Application Logs](https://console.cloud.google.com/logs)
- [Database Monitoring Dashboard](https://console.cloud.google.com/monitoring)

## 📈 Monitoring
Continue monitoring this incident until:
- Error rate returns to baseline
- Root cause is identified and resolved
- Preventive measures are implemented

---
*This issue was automatically created by the Enhanced GCP Log Analysis system*
*Database Incident Response Module v1.0*
"""
    
    return {
        'title': issue_title,
        'body': issue_body,
        'labels': [
            'automated',
            'database-incident',
            'cloudsql',
            incident.severity.lower(),
            incident.incident_type
        ]
    }