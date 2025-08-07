# Multi-Agent Log Analysis Demo

🚀 **Enhanced Multi-Agent Log Analysis System**

This repository demonstrates an intelligent log analysis system that:

## 🎯 Features

- **📥 GCP Integration**: Fetches real logs from Google Cloud Platform
- **🚨 Failure Analysis**: Automatically detects and categorizes errors
- **🐙 GitHub Issues**: Creates issues automatically for detected problems
- **📱 Slack Notifications**: Sends comprehensive reports with GitHub links
- **🤖 Multi-Agent Architecture**: Uses LangGraph sub-graphs for parallel processing

## 🔄 Workflow

```
GCP Logs → Clean → [Failure Analysis + Question Summary] → GitHub Issues + Slack
```

## 🛠️ Tech Stack

- **LangGraph**: Multi-agent orchestration
- **Google Cloud Logging**: Log source
- **GitHub API**: Issue management
- **Slack API**: Notifications
- **Python**: Implementation

## 🎬 Demo

Run the Jupyter notebook to see the system in action with simulated GCP logs and automated GitHub issue creation.

---
*Built with ❤️ for production incident management*
