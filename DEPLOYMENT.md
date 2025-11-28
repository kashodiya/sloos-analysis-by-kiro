# 🚀 SLOOS Analyzer - Deployment Guide

## Production Deployment on AWS EC2

This application is designed to run on AWS EC2 with proper IAM role configuration.

### Prerequisites

1. **EC2 Instance**
   - Any instance type (t3.medium or larger recommended)
   - Amazon Linux 2023 or Ubuntu 22.04 LTS
   - Security group allowing inbound traffic on port 7251

2. **IAM Role Configuration**
   
   Attach an IAM role to your EC2 instance with the following policy:

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

3. **Python & UV**
   - Python 3.11+
   - UV package manager

### Installation Steps

1. **Connect to EC2**
   ```bash
   ssh -i your-key.pem ec2-user@your-instance-ip
   ```

2. **Install UV**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.cargo/env
   ```

3. **Clone/Upload Application**
   ```bash
   # Upload your application files or clone from git
   cd /home/ec2-user
   mkdir sloos-analyzer
   cd sloos-analyzer
   # Copy all application files here
   ```

4. **Install Dependencies**
   ```bash
   uv sync
   ```

5. **Run Application**
   ```bash
   # For testing
   uv run python app.py

   # For production (with systemd service)
   sudo nano /etc/systemd/system/sloos-analyzer.service
   ```

### Systemd Service Configuration

Create `/etc/systemd/system/sloos-analyzer.service`:

```ini
[Unit]
Description=SLOOS Interactive Analyzer
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/sloos-analyzer
ExecStart=/home/ec2-user/.cargo/bin/uv run python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sloos-analyzer
sudo systemctl start sloos-analyzer
sudo systemctl status sloos-analyzer
```

### Accessing the Application

- **Local**: http://localhost:7251
- **Remote**: http://your-ec2-public-ip:7251

Make sure port 7251 is open in your security group:
- Type: Custom TCP
- Port: 7251
- Source: Your IP or 0.0.0.0/0 (for public access)

### Data Flow

1. **Fetch Data**: Application scrapes SLOOS reports from federalreserve.gov
2. **Store**: Reports saved to local SQLite database
3. **Analyze**: User selects report and analysis type
4. **AI Processing**: Request sent to AWS Bedrock Claude Sonnet 4.5
5. **Display**: Results shown in web interface and saved to database

### Monitoring

View application logs:
```bash
sudo journalctl -u sloos-analyzer -f
```

Check database:
```bash
sqlite3 sloos_data.db
.tables
SELECT COUNT(*) FROM sloos_reports;
.quit
```

### Troubleshooting

**Issue**: "Unable to locate credentials"
- **Solution**: Verify IAM role is attached to EC2 instance
- Check: `aws sts get-caller-identity`

**Issue**: "Connection refused" when accessing web interface
- **Solution**: Check security group allows port 7251
- Verify service is running: `sudo systemctl status sloos-analyzer`

**Issue**: "Error fetching SLOOS data"
- **Solution**: Verify EC2 has internet access
- Check: `curl https://www.federalreserve.gov/data/sloos.htm`

**Issue**: Bedrock model not found
- **Solution**: Verify model is available in us-east-1 region
- Check IAM permissions include the correct model ARN

### Security Best Practices

1. **Restrict Access**: Use security groups to limit who can access port 7251
2. **HTTPS**: Consider adding nginx reverse proxy with SSL certificate
3. **Authentication**: Add authentication layer for production use
4. **Database Backups**: Regularly backup sloos_data.db
5. **Updates**: Keep dependencies updated with `uv sync`

### Performance Optimization

- **Database**: SQLite is sufficient for single-user or small team use
- **Scaling**: For high traffic, consider:
  - PostgreSQL instead of SQLite
  - Load balancer with multiple instances
  - Redis for caching analysis results
  - S3 for storing report content

### Cost Considerations

- **EC2**: ~$30-50/month for t3.medium
- **Bedrock**: Pay per token (input + output)
  - Approximate: $0.003 per 1K input tokens, $0.015 per 1K output tokens
  - Typical analysis: ~$0.01-0.05 per request
- **Data Transfer**: Minimal (SLOOS reports are text-based)

### Maintenance

- **Weekly**: Check logs for errors
- **Monthly**: Review and clean old analysis data if needed
- **Quarterly**: Update dependencies and review AWS costs

---

For questions or issues, check the application logs and AWS CloudWatch.
