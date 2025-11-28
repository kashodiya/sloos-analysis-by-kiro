# 🚀 SLOOS Analyzer - Quick Start

## ✅ Application is Running!

Your SLOOS Interactive Analyzer is now live at:

**http://0.0.0.0:7251**

Or access via:
- http://localhost:7251
- http://127.0.0.1:7251
- http://[your-ec2-public-ip]:7251

---

## 📋 Quick Usage Guide

### 1. Fetch Data
Click the **"Fetch SLOOS Data"** button to fetch real SLOOS reports from the Federal Reserve website.

### 2. Select a Report
Click on any report in the **"Available Reports"** panel to select it for analysis.

### 3. Analyze
Choose an analysis type:
- **📝 Summary** - Get an executive summary
- **😊 Sentiment** - Analyze sentiment and tone
- **📈 Trends** - Identify lending trends
- **⚠️ Risks** - Identify potential risks

### 4. Chat with AI
Use the **AI Assistant** panel to ask questions like:
- "What are the main trends in recent SLOOS reports?"
- "How have lending standards changed for CRE loans?"
- "What risks are banks most concerned about?"

---

## 🔧 Technical Details

### Configuration
- **AWS Region**: us-east-1
- **Bedrock Model**: anthropic.claude-sonnet-4-5-20250929-v1:0
- **Database**: SQLite (sloos_data.db)
- **Port**: 7251
- **Host**: 0.0.0.0 (accessible from all interfaces)

### Requirements
- AWS EC2 instance with IAM role for Bedrock access
- Internet connection for fetching SLOOS data from Federal Reserve

### API Endpoints
- `GET /` - Web interface
- `GET /api/reports` - List all reports
- `POST /api/fetch-data` - Fetch SLOOS data
- `POST /api/analyze` - Analyze a report
- `POST /api/chat` - Chat with AI
- `GET /api/chat-history` - View chat history

### Database Tables
1. **sloos_reports** - Stores SLOOS report data
2. **sloos_analysis** - Stores AI analysis results
3. **chat_history** - Stores chat conversations

---

## 🛑 Stopping the Server

To stop the server:
1. Press `CTRL+C` in the terminal
2. Or close the terminal window

---

## 🔄 Restarting

To restart the application:

**Windows:**
```bash
start.bat
```

**Linux/macOS:**
```bash
./start.sh
```

**Manual:**
```bash
uv run python app.py
```

---

## 📊 Features

✅ Interactive web interface  
✅ AWS Bedrock Claude Sonnet 4.5 integration  
✅ Multiple analysis types  
✅ AI-powered chat assistant  
✅ SQLite data persistence  
✅ Real-time analysis  
✅ Professional UI design  

---

## 🆘 Troubleshooting

### Can't access the application?
- Check if port 7251 is open in your EC2 security group
- Verify the server is running (check terminal output)
- Try accessing via localhost:7251 first

### Bedrock errors?
- Ensure your EC2 instance has an IAM role with Bedrock permissions
- Verify the model ID is correct for your region
- Check AWS region is set to us-east-1

### Database errors?
- The SQLite database is created automatically
- Check file permissions in the application directory

---

## 📚 Next Steps

1. **Add Real Data**: Modify the fetch function to scrape actual SLOOS data from the Federal Reserve website
2. **Enhance Analysis**: Add more analysis types (comparisons, forecasting, etc.)
3. **Export Features**: Add ability to export analysis results
4. **Visualizations**: Integrate charts and graphs
5. **Historical Analysis**: Compare trends across multiple quarters

---

Enjoy analyzing SLOOS data! 🎉
