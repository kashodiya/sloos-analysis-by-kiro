"""SLOOS Interactive Data Analysis Application"""
import json
import re
from datetime import datetime
from typing import Optional

import boto3
import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, text

# Configuration
AWS_REGION = "us-east-1"
BEDROCK_MODEL = "us.anthropic.claude-sonnet-4-20250514-v1:0"
DATABASE_URL = "sqlite:///./sloos_data.db"
SLOOS_DATA_URL = "https://www.federalreserve.gov/data/sloos.htm"

# Initialize FastAPI
app = FastAPI(title="SLOOS Analyzer", description="Interactive SLOOS Data Analysis")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Database engine
engine = create_engine(DATABASE_URL, echo=False)

# AWS Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)


def init_database():
    """Initialize SQLite database with required tables"""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sloos_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT NOT NULL,
                report_url TEXT,
                report_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sloos_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER,
                analysis_type TEXT,
                analysis_result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES sloos_reports(id)
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT,
                assistant_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()


def call_bedrock(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Call AWS Bedrock Claude model"""
    messages = [{"role": "user", "content": prompt}]
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": messages,
    }
    
    if system_prompt:
        body["system"] = system_prompt
    
    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL,
        body=json.dumps(body)
    )
    
    response_body = json.loads(response["body"].read())
    return response_body["content"][0]["text"]


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_database()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/reports")
async def get_reports():
    """Get all SLOOS reports from database"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM sloos_reports ORDER BY report_date DESC"))
        reports = [dict(row._mapping) for row in result]
    return JSONResponse(content={"reports": reports})


@app.post("/api/fetch-data")
async def fetch_sloos_data():
    """Fetch latest SLOOS data from Federal Reserve"""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(SLOOS_DATA_URL)
            response.raise_for_status()
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        reports_found = 0
        new_reports = 0
        
        # Find all links to SLOOS reports
        # Pattern: /data/sloos/sloos-YYYYMM.htm
        report_links = soup.find_all('a', href=re.compile(r'/data/sloos/sloos-\d{6}\.htm'))
        
        with engine.connect() as conn:
            for link in report_links:
                href = link.get('href')
                if not href.startswith('http'):
                    href = f"https://www.federalreserve.gov{href}"
                
                # Extract date from URL (e.g., sloos-202410.htm -> 2024-10)
                date_match = re.search(r'sloos-(\d{4})(\d{2})\.htm', href)
                if not date_match:
                    continue
                
                year, month = date_match.groups()
                report_date = f"{year}-{month}"
                
                # Check if report already exists
                existing = conn.execute(
                    text("SELECT COUNT(*) as count FROM sloos_reports WHERE report_url = :url"),
                    {"url": href}
                ).fetchone()
                
                if existing[0] > 0:
                    reports_found += 1
                    continue
                
                # Fetch the actual report content
                try:
                    async with httpx.AsyncClient(timeout=30.0) as report_client:
                        report_response = await report_client.get(href)
                        report_response.raise_for_status()
                        
                    report_soup = BeautifulSoup(report_response.text, 'html.parser')
                    
                    # Extract main content (remove scripts, styles, navigation)
                    for element in report_soup(['script', 'style', 'nav', 'header', 'footer']):
                        element.decompose()
                    
                    # Get text content
                    content = report_soup.get_text(separator='\n', strip=True)
                    
                    # Clean up excessive whitespace
                    content = re.sub(r'\n\s*\n', '\n\n', content)
                    content = content[:50000]  # Limit content size
                    
                    # Insert into database
                    conn.execute(text("""
                        INSERT INTO sloos_reports (report_date, report_url, report_content)
                        VALUES (:date, :url, :content)
                    """), {"date": report_date, "url": href, "content": content})
                    
                    new_reports += 1
                    reports_found += 1
                    
                except Exception as e:
                    print(f"Error fetching report {href}: {e}")
                    continue
            
            conn.commit()
        
        return JSONResponse(content={
            "status": "success",
            "message": f"Found {reports_found} reports ({new_reports} new)",
            "reports_found": reports_found,
            "new_reports": new_reports
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_report(request: Request):
    """Analyze SLOOS report using Bedrock"""
    data = await request.json()
    report_id = data.get("report_id")
    analysis_type = data.get("analysis_type", "summary")
    
    if not report_id:
        raise HTTPException(status_code=400, detail="report_id is required")
    
    # Get report from database
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM sloos_reports WHERE id = :id"),
            {"id": report_id}
        ).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report = dict(result._mapping)
    
    # Create analysis prompt based on type
    prompts = {
        "summary": f"Provide a concise executive summary of this SLOOS report:\n\n{report['report_content']}",
        "sentiment": f"Analyze the sentiment (positive, neutral, negative) of this SLOOS report and explain the key factors:\n\n{report['report_content']}",
        "trends": f"Identify key lending trends and changes in credit conditions from this SLOOS report:\n\n{report['report_content']}",
        "risks": f"Identify potential risks and concerns mentioned in this SLOOS report:\n\n{report['report_content']}"
    }
    
    prompt = prompts.get(analysis_type, prompts["summary"])
    system_prompt = "You are an expert financial analyst specializing in Federal Reserve data and credit market analysis."
    
    # Call Bedrock
    try:
        analysis_result = call_bedrock(prompt, system_prompt)
    except Exception as e:
        error_msg = str(e)
        if "NoCredentialsError" in error_msg or "credentials" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail="AWS credentials not configured. This application requires AWS Bedrock access. Please deploy to EC2 with IAM role or configure AWS credentials locally."
            )
        raise HTTPException(status_code=500, detail=f"Error calling Bedrock: {error_msg}")
    
    # Store analysis
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO sloos_analysis (report_id, analysis_type, analysis_result)
            VALUES (:report_id, :analysis_type, :analysis_result)
        """), {
            "report_id": report_id,
            "analysis_type": analysis_type,
            "analysis_result": analysis_result
        })
        conn.commit()
    
    return JSONResponse(content={
        "status": "success",
        "analysis": analysis_result,
        "report_date": report["report_date"]
    })


@app.post("/api/chat")
async def chat(request: Request):
    """Chat with AI about SLOOS data"""
    data = await request.json()
    user_message = data.get("message", "")
    
    if not user_message:
        raise HTTPException(status_code=400, detail="message is required")
    
    # Get recent reports for context
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT report_date, report_content FROM sloos_reports ORDER BY report_date DESC LIMIT 5")
        )
        reports = [dict(row._mapping) for row in result]
    
    # Build context
    context = "Recent SLOOS Reports:\n\n"
    for report in reports:
        context += f"[{report['report_date']}]: {report['report_content']}\n\n"
    
    prompt = f"{context}\n\nUser Question: {user_message}\n\nProvide a detailed, data-driven answer based on the SLOOS reports above."
    system_prompt = "You are an expert financial analyst specializing in Federal Reserve SLOOS data. Provide clear, actionable insights based on the data."
    
    # Call Bedrock
    try:
        assistant_response = call_bedrock(prompt, system_prompt)
    except Exception as e:
        error_msg = str(e)
        if "NoCredentialsError" in error_msg or "credentials" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail="AWS credentials not configured. This application requires AWS Bedrock access. Please deploy to EC2 with IAM role or configure AWS credentials locally."
            )
        raise HTTPException(status_code=500, detail=f"Error calling Bedrock: {error_msg}")
    
    # Store chat history
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO chat_history (user_message, assistant_response)
            VALUES (:user_message, :assistant_response)
        """), {
            "user_message": user_message,
            "assistant_response": assistant_response
        })
        conn.commit()
    
    return JSONResponse(content={
        "status": "success",
        "response": assistant_response
    })


@app.get("/api/chat-history")
async def get_chat_history():
    """Get chat history"""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM chat_history ORDER BY created_at DESC LIMIT 20")
        )
        history = [dict(row._mapping) for row in result]
    return JSONResponse(content={"history": history})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7251)
