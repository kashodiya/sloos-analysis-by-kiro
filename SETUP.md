# 🚀 SLOOS Interactive Analyzer - Setup Guide

## Overview

This application provides an interactive interface for analyzing Senior Loan Officer Opinion Survey (SLOOS) data using AWS Bedrock's Claude Sonnet 4.5 model.

## Features

- 📥 **Real Data Fetching**: Fetch actual SLOOS reports from Federal Reserve website
- 🔍 **AI Analysis**: Multiple analysis types using AWS Bedrock Claude (Summary, Sentiment, Trends, Risks)
- 💬 **Interactive Chat**: Ask questions about SLOOS data using natural language
- 💾 **SQLite Storage**: Local database for reports and analysis history
- 🎨 **Professional UI**: Modern, responsive web interface

## Prerequisites

- Python 3.11+
- UV package manager
- AWS EC2 instance with IAM role for Bedrock access
- Internet connection for fetching SLOOS data

## Installation

### 1. Install UV (if not already installed)

```bash
# On Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install Dependencies

```bash
uv sync
```

This will:
- Create a virtual environment
- Install all required packages from pyproject.toml

## Running the Application

### On Linux/macOS:
```bash
chmod +x start.sh
./start.sh
```

### On Windows:
```bash
start.bat
```

### Manual Start:
```bash
uv run python app.py
```

The application will start on **http://0.0.0.0:7251**

## Configuration

The application is pre-configured with:
- **AWS Region**: us-east-1
- **Bedrock Model**: anthropic.claude-sonnet-4-5-20250929-v1:0
- **Port**: 7251
- **Database**: SQLite (sloos_data.db)

No AWS credentials needed - uses EC2 IAM role.

## Usage

1. **Fetch Data**: Click "Fetch SLOOS Data" to download real reports from Federal Reserve
2. **Select Report**: Click on any report in the list
3. **Analyze**: Choose an analysis type (Summary, Sentiment, Trends, or Risks) - powered by AWS Bedrock
4. **Chat**: Ask questions about the data in the AI Assistant panel

## API Endpoints

- `GET /` - Main web interface
- `GET /api/reports` - List all reports
- `POST /api/fetch-data` - Fetch new SLOOS data
- `POST /api/analyze` - Analyze a specific report
- `POST /api/chat` - Chat with AI about SLOOS data
- `GET /api/chat-history` - Get chat history

## Database Schema

### sloos_reports
- id, report_date, report_url, report_content, created_at

### sloos_analysis
- id, report_id, analysis_type, analysis_result, created_at

### chat_history
- id, user_message, assistant_response, created_at

## Troubleshooting

### Bedrock Access Issues
Ensure your EC2 instance has an IAM role with:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0"
    }
  ]
}
```

### Port Already in Use
Change the port in `app.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=YOUR_PORT)
```

## Development

To add new features:
1. Modify `app.py` for backend logic
2. Update `templates/index.html` for UI changes
3. Run `uv sync` if adding new dependencies to `pyproject.toml`

## License

MIT License - Feel free to modify and use as needed.
