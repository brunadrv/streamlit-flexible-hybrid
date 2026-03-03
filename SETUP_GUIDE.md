# Flexible Hybrid Reporting - Setup Guide

This guide will walk you through setting up the Flexible Hybrid Reporting application from scratch.

## 📋 Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.10 or higher installed
- [ ] Access to Snowflake with required permissions
- [ ] Google Cloud Project with Sheets API enabled (for WeWork swipes)
- [ ] Access to Workday for LOA exports
- [ ] Text editor or IDE (VS Code, PyCharm, etc.)
- [ ] Git installed (optional, but recommended)

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
cd flexible_hybrid_app
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
SNOWFLAKE_ACCOUNT=mycompany
SNOWFLAKE_USER=myusername
SNOWFLAKE_PASSWORD=mypassword
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=US_PEOPLE_INSIGHTS
SNOWFLAKE_SCHEMA=LAYER_ANALYTICS
SNOWFLAKE_ROLE=ANALYST
```

### 3. Create User Account

Generate password hash:

```python
import bcrypt
password = "your_password"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(hashed)
```

Add to `config.yaml`:

```yaml
credentials:
  usernames:
    your_username:
      email: your.email@hellofresh.com
      name: Your Name
      password: <paste_hashed_password_here>
      role: admin
```

### 4. Run the App

```bash
streamlit run app.py
```

Visit `http://localhost:8501` and log in!

## 📚 Detailed Setup Instructions

### Step 1: Python Environment Setup

#### Windows:

```powershell
# Check Python version
python --version

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Mac/Linux:

```bash
# Check Python version
python3 --version

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Snowflake Configuration

#### 2.1 Get Snowflake Credentials

1. Log into Snowflake web interface
2. Note your account identifier (from URL: `https://<account>.snowflakecomputing.com`)
3. Verify you have access to:
   - `US_PEOPLE_INSIGHTS.LAYER_ANALYTICS.VIEW_WORKDAY_KITCHEN_SINK_PI`
   - `US_PEOPLE_INSIGHTS.LAYER_ANALYTICS.VIEW_LENEL_S2_EVENTS_180_DAYS_v2`
   - `US_PEOPLE_INSIGHTS.LAYER_ANALYTICS.VIEW_ADP_TIME_OFF_APPROVED`

#### 2.2 Test Snowflake Connection

Create a test script `test_snowflake.py`:

```python
import snowflake.connector
from dotenv import load_dotenv
import os

load_dotenv()

conn = snowflake.connector.connect(
    account=os.getenv('SNOWFLAKE_ACCOUNT'),
    user=os.getenv('SNOWFLAKE_USER'),
    password=os.getenv('SNOWFLAKE_PASSWORD'),
    warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
    database=os.getenv('SNOWFLAKE_DATABASE'),
    schema=os.getenv('SNOWFLAKE_SCHEMA')
)

cursor = conn.cursor()
cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE()")
result = cursor.fetchone()
print(f"Connected as: {result[0]} with role: {result[1]}")

conn.close()
print("✅ Snowflake connection successful!")
```

Run:

```bash
python test_snowflake.py
```

### Step 3: Google Sheets Setup (for WeWork Swipes)

#### 3.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project: "Flexible Hybrid App"
3. Enable Google Sheets API:
   - APIs & Services → Library
   - Search for "Google Sheets API"
   - Click Enable

#### 3.2 Create Service Account

1. APIs & Services → Credentials
2. Create Credentials → Service Account
3. Name: "flexible-hybrid-service"
4. Role: Editor
5. Create Key → JSON
6. Download JSON file to project directory

#### 3.3 Share Google Sheet

1. Open your WeWork swipe tracker sheet
2. Click "Share"
3. Add service account email (from JSON file)
4. Grant "Editor" access

#### 3.4 Update Configuration

In `.env`:

```env
GOOGLE_SHEETS_CREDENTIALS_FILE=./credentials.json
```

### Step 4: User Management

#### 4.1 Generate Password Hashes

Create `generate_password.py`:

```python
import bcrypt
import sys

if len(sys.argv) < 2:
    print("Usage: python generate_password.py <password>")
    sys.exit(1)

password = sys.argv[1]
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(f"\nHashed password:\n{hashed}\n")
print("Copy this hash to config.yaml")
```

Generate hashes:

```bash
python generate_password.py "MySecurePassword123"
```

#### 4.2 Add Users to config.yaml

```yaml
credentials:
  usernames:
    # Admin user
    admin:
      email: admin@hellofresh.com
      name: Admin User
      password: $2b$12$your_hashed_password_here
      role: admin
    
    # HRBP user
    jane.smith:
      email: jane.smith@hellofresh.com
      name: Jane Smith
      password: $2b$12$another_hashed_password
      role: hrbp
    
    # Manager user
    john.manager:
      email: john.manager@hellofresh.com
      name: John Manager
      password: $2b$12$manager_hashed_password
      role: manager
```

### Step 5: Configure Flexible Hybrid Schedule

Edit `config.yaml` to add months:

```yaml
flex_schedule:
  months:
    "2026-01":
      start_date: "2026-01-05"
      end_date: "2026-02-01"
      weeks: 4
      days_possible: 20
    
    "2026-02":
      start_date: "2026-02-02"
      end_date: "2026-03-01"
      weeks: 4
      days_possible: 20
    
    "2026-03":
      start_date: "2026-03-02"
      end_date: "2026-04-05"
      weeks: 5
      days_possible: 25
```

### Step 6: Configure HRBP Assignments

In `config.yaml`:

```yaml
hrbp_assignments:
  stephanie.hains@hellofresh.com:
    - People
    - HR Operations
  
  stephanie.melilli@hellofresh.com:
    - Operations
    - Distribution Centers
  
  pablo.velez@hellofresh.com:
    - Meal Kits
    - Manufacturing
```

### Step 7: Test the Application

#### 7.1 Start in Demo Mode

```bash
streamlit run app.py
```

#### 7.2 Test Login

1. Navigate to `http://localhost:8501`
2. Log in with credentials from `config.yaml`
3. Verify you see the home page

#### 7.3 Test Demo Data

1. Go to Dashboard
2. Check "Use Demo Data"
3. Verify charts and metrics display correctly

#### 7.4 Test Real Data (if ready)

1. Uncheck "Use Demo Data"
2. Select a month
3. Click "Run Monthly Update" in Admin Panel
4. Verify data loads from Snowflake

## 🔧 Troubleshooting Setup

### Issue: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:

```bash
# Ensure virtual environment is activated
# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Snowflake Authentication Failed

**Error**: `Authentication failed`

**Solution**:

1. Check credentials in `.env`
2. Verify Snowflake account identifier
3. Try logging into Snowflake web interface with same credentials
4. Check if MFA is enabled (not supported in connector)

### Issue: Google Sheets Permission Denied

**Error**: `Permission denied when accessing Google Sheet`

**Solution**:

1. Verify service account email has access to sheet
2. Check credentials file path in `.env`
3. Ensure Google Sheets API is enabled in Cloud Console
4. Try sharing sheet with "Anyone with link" temporarily for testing

### Issue: Config YAML Parse Error

**Error**: `yaml.scanner.ScannerError`

**Solution**:

1. Check YAML indentation (use spaces, not tabs)
2. Verify no special characters in strings
3. Use a YAML validator online
4. Ensure password hashes are properly quoted if they contain special chars

## 🚀 Production Deployment

### Streamlit Cloud Deployment

#### 1. Prepare Repository

```bash
# Initialize git if not already
git init

# Add files
git add .

# Commit
git commit -m "Initial commit: Flexible Hybrid App"

# Push to GitHub
git remote add origin <your-repo-url>
git push -u origin main
```

#### 2. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect GitHub repository
4. Select repository and branch
5. Set main file path: `app.py`

#### 3. Configure Secrets

In Streamlit Cloud dashboard:

Settings → Secrets

Add:

```toml
[snowflake]
account = "your_account"
user = "your_user"
password = "your_password"
warehouse = "your_warehouse"
database = "US_PEOPLE_INSIGHTS"
schema = "LAYER_ANALYTICS"
role = "your_role"
```

#### 4. Deploy

Click "Deploy" and wait for application to start.

### Internal Server Deployment

See README.md for Docker and systemd deployment options.

## 📞 Getting Help

If you encounter issues during setup:

1. **Check Documentation**: Review README.md and in-app documentation
2. **Search Logs**: Look for error messages in terminal
3. **Test Components**: Test Snowflake and Google Sheets connections separately
4. **Contact Support**:
   - Email: goat-team@hellofresh.com
   - Slack: #flexible-hybrid-support

## ✅ Setup Verification Checklist

Before going live, verify:

- [ ] Application starts without errors
- [ ] Can log in with test account
- [ ] Snowflake connection works
- [ ] Demo data displays correctly
- [ ] Real data loads from Snowflake
- [ ] Google Sheets integration works (if applicable)
- [ ] All pages accessible based on role
- [ ] Export functionality works
- [ ] LOA processing works
- [ ] Monthly update pipeline runs successfully

## 🎉 Next Steps

Once setup is complete:

1. **Add Users**: Create accounts for all HRBPs and managers
2. **Load Historical Data**: Run monthly updates for past months
3. **Test with Real Users**: Have a few users test the system
4. **Train Users**: Conduct training sessions for HRBPs
5. **Go Live**: Announce to organization
6. **Monitor**: Watch for issues in first few weeks

---

**Setup Complete!** You're ready to start using the Flexible Hybrid Reporting application.
