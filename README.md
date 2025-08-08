# 🔍 Multi-Agent GCP Log Analysis & Incident Management System

> **End-to-End Automated Incident Detection, Analysis, and Response Pipeline**

This repository showcases a production-ready, intelligent log analysis system that automatically monitors GCP logs, detects critical issues, and orchestrates incident response workflows using multi-agent architecture.

## ✨ Key Features

### 🤖 **Intelligent Multi-Agent Processing**
- **Parallel Sub-Graphs**: Simultaneous failure analysis and pattern detection
- **LangGraph Orchestration**: Advanced workflow management with state sharing
- **LangSmith Tracing**: Complete observability and debugging capabilities

### 📥 **Real-Time GCP Integration**
- **Cloud Logging API**: Fetches live logs from your GCP project
- **Smart Filtering**: Configurable time ranges and severity levels
- **Robust Fallback**: Sample data generation for testing and demos

### 🚨 **Advanced Error Detection**
- **Severity Classification**: Automatic ERROR/WARNING/INFO categorization  
- **Resource Analysis**: Identifies affected GCP services and instances
- **Pattern Recognition**: Detects recurring issues and trends

### 🐛 **Automated Issue Management**
- **Smart GitHub Integration**: Creates detailed issues only for critical errors
- **Rich Issue Content**: Includes error details, affected resources, and action items
- **Professional Labeling**: Auto-tags with `🚨 critical`, `automated`, `gcp-logs`, `incident`
- **No Spam Logic**: Prevents duplicate or unnecessary issue creation

### 📤 **Enhanced Team Communication**
- **Rich Slack Notifications**: Professional formatting with status indicators
- **GitHub Issue Links**: Direct integration between Slack messages and GitHub issues
- **Action Items**: Clear next steps for incident response teams
- **Fallback Support**: Graceful degradation for reliable delivery

## 🔄 Complete Workflow

```mermaid
graph LR
    A[GCP Logs] --> B[Log Cleaning]
    B --> C[Parallel Analysis]
    C --> D[Failure Analysis Sub-Graph]
    C --> E[Pattern Analysis Sub-Graph] 
    D --> F[Critical Error Detection]
    E --> F
    F --> G[GitHub Issue Creation]
    F --> H[Slack Notification]
    G --> H
    H --> I[Team Response]
```

### **Step-by-Step Process:**
1. **📥 Log Ingestion**: Fetches real logs from your GCP project (configurable time range)
2. **🧹 Data Cleaning**: Normalizes and structures log entries for analysis
3. **🔀 Parallel Analysis**: Runs failure detection and pattern analysis simultaneously
4. **🐛 Issue Creation**: Automatically creates GitHub issues for ERROR-level logs
5. **📱 Team Notification**: Sends comprehensive Slack reports with GitHub issue links
6. **📊 Observability**: Full tracing available in LangSmith for debugging and optimization

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Orchestration** | LangGraph | Multi-agent workflow management |
| **Observability** | LangSmith | Tracing and debugging |
| **Log Source** | Google Cloud Logging API | Real-time log ingestion |
| **Issue Tracking** | GitHub API | Automated incident management |
| **Communication** | Slack API | Team notifications and alerts |
| **Environment** | Python 3.11+ | Core implementation |
| **Notebook** | Jupyter | Interactive development and demos |

## 🚀 Quick Start

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Authenticate with GCP
gcloud auth application-default login
```

### Environment Setup
Create a `.env` file with your API keys:
```bash
# LangSmith (for tracing)
LANGCHAIN_API_KEY="your_langsmith_key"
LANGCHAIN_TRACING_V2=true

# GCP Configuration
GCP_PROJECT_ID="your-gcp-project-id"

# GitHub Integration  
GITHUB_TOKEN="your_github_token"
GITHUB_REPO="owner/repo-name"

# Slack Integration
SLACK_BOT_TOKEN="xoxb-your-slack-bot-token"
SLACK_DEFAULT_CHANNEL="general"
```

### Running the System
1. **Open the Notebook**: `jupyter notebook sub-graph.ipynb`
2. **Execute Cells Sequentially**: Follow the step-by-step workflow
3. **Monitor Results**: Check Slack for notifications and GitHub for any created issues
4. **View Traces**: Access LangSmith for detailed execution insights

## 📊 Sample Output

### **GitHub Issue Creation**
When critical errors are detected:
```
✅ GitHub issue created successfully!
   📋 Issue #5
   🔗 URL: https://github.com/owner/repo/issues/5
   📝 Title: 🚨 GCP Log Analysis Alert - Errors Detected (2025-08-08 06:13)
```

### **Slack Notification**  
Rich formatted messages include:
- � Analysis summary with log counts
- ⚠️ Failure analysis with error details  
- 📈 Resource usage patterns and insights
- 🚨 Status indicators (CRITICAL/WARNING/HEALTHY)
- 🐛 Direct links to created GitHub issues
- 🏥 Clear action items for incident response

## 🎯 Use Cases

- **Production Monitoring**: Continuous monitoring of GCP services
- **Incident Response**: Automated detection and escalation of critical issues
- **DevOps Integration**: Seamless workflow with existing GitHub/Slack tools
- **SRE Workflows**: Pattern analysis for proactive system improvements
- **Compliance Logging**: Structured analysis and documentation of system events

## 🔧 Customization

The system is highly configurable:
- **Log Sources**: Easily adaptable to other cloud providers or log systems
- **Analysis Logic**: Customize failure detection and pattern recognition
- **Integration Endpoints**: Modify GitHub/Slack integration for your workflow
- **Alert Thresholds**: Configure when issues should be created or notifications sent

## 📚 Architecture Deep Dive

### **Sub-Graph Design**
- **Failure Analysis Sub-Graph**: Identifies and categorizes errors with resource context
- **Pattern Analysis Sub-Graph**: Analyzes trends, resource usage, and behavioral patterns
- **Parent Graph**: Orchestrates parallel execution and result aggregation

### **State Management**
- **Shared State**: Efficient data sharing between parallel sub-graphs
- **Type Safety**: Strongly typed state definitions with TypedDict
- **Result Aggregation**: Intelligent merging of parallel analysis results

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)  
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain Team** for the excellent LangGraph framework
- **Google Cloud** for comprehensive logging APIs
- **GitHub & Slack** for powerful integration capabilities

---

**🚀 Ready to deploy intelligent log analysis in your production environment?**  
*This system provides enterprise-grade incident management from detection to resolution tracking.*
