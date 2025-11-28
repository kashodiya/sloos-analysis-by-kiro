# 🏠 Local Development Setup

## Running SLOOS Analyzer Locally (Windows/Mac/Linux)

If you want to test the application locally before deploying to EC2, you need to configure AWS credentials.

### Option 1: AWS CLI Configuration (Recommended)

1. **Install AWS CLI**
   
   Windows:
   ```powershell
   msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
   ```
   
   Mac:
   ```bash
   brew install awscli
   ```
   
   Linux:
   ```bash
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

2. **Configure AWS Credentials**
   ```bash
   aws configure
   ```
   
   Enter:
   - AWS Access Key ID: [Your access key]
   - AWS Secret Access Key: [Your secret key]
   - Default region: us-east-1
   - Default output format: json

3. **Verify Configuration**
   ```bash
   aws sts get-caller-identity
   ```

### Option 2: Environment Variables

Set these environment variables:

**Windows (PowerShell):**
```powershell
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:AWS_DEFAULT_REGION="us-east-1"
```

**Mac/Linux (Bash):**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Option 3: AWS Credentials File

Create `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
```

Create `~/.aws/config`:

```ini
[default]
region = us-east-1
output = json
```

### Required IAM Permissions

Your AWS user/role needs these permissions:

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

### Getting AWS Access Keys

1. Log in to AWS Console
2. Go to IAM → Users → Your User
3. Security credentials tab
4. Create access key
5. Choose "Local code" as use case
6. Download and save the credentials securely

⚠️ **Security Warning**: Never commit AWS credentials to git!

### Running the Application

Once credentials are configured:

```bash
# Install dependencies
uv sync

# Run the application
uv run python app.py
```

Access at: http://localhost:7251

### Troubleshooting

**Error: "Unable to locate credentials"**
- Verify AWS CLI is configured: `aws configure list`
- Check credentials file exists: `cat ~/.aws/credentials`
- Try setting environment variables directly

**Error: "Access Denied" or "Not Authorized"**
- Verify your IAM user has Bedrock permissions
- Check the model ID is correct for your region
- Ensure you're using us-east-1 region

**Error: "Model not found"**
- The Claude Sonnet 4.5 model may not be available in your account
- Request access in AWS Console → Bedrock → Model access
- Wait for approval (usually instant for Claude models)

### Cost Considerations for Local Testing

- **Bedrock Pricing**: ~$0.003 per 1K input tokens, ~$0.015 per 1K output tokens
- **Typical Analysis**: $0.01-0.05 per request
- **Testing Budget**: $5-10 should be sufficient for extensive testing

### Production Deployment

For production, always use EC2 with IAM role instead of access keys:
- More secure (no credentials in code or config)
- Automatic credential rotation
- Better audit trail
- See DEPLOYMENT.md for details

---

**Note**: This local setup is for development and testing only. For production use, deploy to EC2 with IAM role as described in DEPLOYMENT.md.
