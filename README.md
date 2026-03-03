# Flexible Hybrid Reporting Application

A comprehensive Streamlit application for automating HelloFresh's Flexible Hybrid policy compliance tracking and reporting.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🎯 Overview

The Flexible Hybrid Reporting Application automates the monthly compliance tracking process for HelloFresh's Flexible Hybrid policy, which requires Non-Essential employees to be in the office for an average of 2.5 days per week.

**Previous Process:**
- Manual monthly updates taking 4-6 hours
- Multiple data sources requiring manual copy/paste
- Error-prone calculations
- Complex Google Sheets maintenance

**New Process:**
- Automated data pipeline from Snowflake
- Real-time compliance calculations
- Role-based access control
- One-click monthly updates
- Automated report generation

## ✨ Features

### Core Features

- **📊 Real-time Dashboards**: Interactive compliance dashboards with key metrics and visualizations
- **👥 Role-Based Access Control**: Segmented views for Admins, HRBPs, Managers, and Employees
- **🔄 Automated Data Pipeline**: Direct integration with Snowflake, Google Sheets, and Workday
- **📈 Compliance Tracking**: Automated calculation of adjusted weekly averages
- **⚙️ Exception Management**: HRBP interface for managing exceptions and classifications
- **📤 Export Capabilities**: Multiple format exports (CSV, Excel, Google Sheets)
- **📋 LOA Processing**: Automated Leave of Absence data processing
- **🔐 Authentication**: Secure login with role-based permissions

### User Roles

1. **Admin/HRBP**:
   - View all organizational data
   - Manage exceptions and classifications
   - Run monthly updates
   - Access all reports

2. **Manager**:
   - View direct reports only
   - Export team reports
   - Monitor team compliance

3. **Employee**:
   - View personal compliance status
   - Track progress over time

## 🏗️ Architecture

### Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Snowflake  │────▶│   Pipeline   │────▶│  Streamlit  │
│   (Roster,  │     │  Processing  │     │     App     │
│   Swipes,   │     │    Engine    │     │             │
│    PTO)     │     └──────────────┘     └─────────────┘
└─────────────┘            ▲                     │
                           │                     │
┌─────────────┐            │                     ▼
│   GSheets   │────────────┘              ┌─────────────┐
│  (WeWork    │                           │    Users    │
│   Swipes)   │                           │  (HRBP,     │
└─────────────┘                           │  Managers,  │
                                          │  Employees) │
┌─────────────┐                           └─────────────┘
│   Workday   │
│    (LOA)    │
└─────────────┘
```

### Technology Stack

- **Frontend**: Streamlit 1.31+
- **Data Warehouse**: Snowflake
- **Authentication**: streamlit-authenticator
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Plotly
- **Integrations**: Google Sheets API, Snowflake Connector
- **Configuration**: YAML, Python-dotenv

### Project Structure

```
flexible_hybrid_app/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── config.yaml                 # Application configuration
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
│
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── snowflake_connector.py # Snowflake data access
│   ├── data_processor.py      # Compliance calculations
│   ├── auth.py                # Authentication & RBAC
│   ├── gsheets_connector.py   # Google Sheets integration
│   └── loa_processor.py       # LOA data processing
│
├── pages/                      # Streamlit pages
│   ├── 1_📊_Dashboard.py
│   ├── 2_🏢_All_Org_View.py
│   ├── 3_🏛️_Department_View.py
│   ├── 4_👥_Team_View.py
│   ├── 5_⚙️_Admin.py
│   ├── 6_📤_Export.py
│   └── 7_📚_Documentation.py
│
├── data/                       # Data directory (gitignored)
├── logs/                       # Logs directory
└── README.md                  # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- Snowflake account with access to required tables
- Google Sheets API credentials (for WeWork swipes)
- Access to Workday for LOA exports

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd flexible_hybrid_app
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
notepad .env  # Windows
nano .env     # Mac/Linux
```

### Step 5: Configure Application

Edit `config.yaml` to set up:

- User accounts and roles
- HRBP department assignments
- Flexible Hybrid schedule configuration
- Company holidays

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account_name
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=US_PEOPLE_INSIGHTS
SNOWFLAKE_SCHEMA=LAYER_ANALYTICS
SNOWFLAKE_ROLE=your_role

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE=path/to/credentials.json

# Application Configuration
APP_TITLE=Flexible Hybrid Reporting
APP_ENV=development
```

### User Configuration (config.yaml)

#### Adding Users

```yaml
credentials:
  usernames:
    john.doe:
      email: john.doe@hellofresh.com
      name: John Doe
      password: $2b$12$... # Use bcrypt to hash passwords
      role: admin
```

To generate password hash:

```python
import bcrypt
password = "your_password"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(hashed)
```

#### HRBP Department Assignments

```yaml
hrbp_assignments:
  stephanie.hains@hellofresh.com:
    - People
  stephanie.melilli@hellofresh.com:
    - Operations
```

#### Flexible Hybrid Schedule

```yaml
flex_schedule:
  months:
    "2026-01":
      start_date: "2026-01-05"
      end_date: "2026-02-01"
      weeks: 4
      days_possible: 20
```

### Google Sheets Setup

1. Create a Google Cloud Project
2. Enable Google Sheets API
3. Create Service Account credentials
4. Download credentials JSON file
5. Share target Google Sheets with service account email
6. Update `.env` with credentials file path

## 📖 Usage

### Starting the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Monthly Workflow

#### For Admins/HRBPs:

1. **First Week of New Month**:
   - Navigate to Admin Panel → Monthly Data Update
   - Select the previous month
   - Click "Run Monthly Update Pipeline"
   - Monitor progress and review summary

2. **Process LOA Data**:
   - Export "Workers on Leave" from Workday
   - Go to Admin Panel → LOA Processing
   - Upload the export file
   - Download processed LOA data

3. **Review Compliance**:
   - Check Dashboard for overall metrics
   - Review All Org View for detailed data
   - Identify non-compliant employees

4. **Manage Exceptions**:
   - Grant exceptions as needed
   - Update classifications
   - Document reasons

5. **Export Reports**:
   - Generate monthly reports
   - Distribute to leadership and managers
   - Update Disciplinary Action tracker

#### For Managers:

1. Visit "My Team" page
2. Review team compliance status
3. Reach out to at-risk or non-compliant team members
4. Export team report for records

#### For Employees:

1. View Dashboard for personal compliance status
2. Track swipes and adjusted weekly average
3. Contact manager/HRBP with questions

## 🚢 Deployment

### Option 1: Streamlit Cloud (Recommended)

1. Push code to GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Add secrets in Streamlit Cloud settings:

```toml
# .streamlit/secrets.toml
[snowflake]
account = "your_account"
user = "your_user"
password = "your_password"
warehouse = "your_warehouse"
database = "US_PEOPLE_INSIGHTS"
schema = "LAYER_ANALYTICS"
role = "your_role"
```

### Option 2: Internal Server

#### Using Docker:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t flexible-hybrid-app .
docker run -p 8501:8501 --env-file .env flexible-hybrid-app
```

#### Using systemd (Linux):

Create `/etc/systemd/system/flexible-hybrid.service`:

```ini
[Unit]
Description=Flexible Hybrid Reporting App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/flexible_hybrid_app
Environment="PATH=/opt/flexible_hybrid_app/venv/bin"
ExecStart=/opt/flexible_hybrid_app/venv/bin/streamlit run app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable flexible-hybrid
sudo systemctl start flexible-hybrid
```

### Option 3: Azure App Service

1. Create Azure App Service (Python 3.10)
2. Configure deployment from GitHub
3. Add application settings (environment variables)
4. Deploy

## 🔧 Troubleshooting

### Common Issues

#### Snowflake Connection Failed

**Symptoms**: "Failed to connect to Snowflake" error

**Solutions**:
- Verify credentials in `.env` file
- Check VPN connection if required
- Confirm Snowflake account is active
- Verify warehouse is running
- Check role permissions

#### Authentication Issues

**Symptoms**: Cannot log in or "Invalid credentials"

**Solutions**:
- Verify username in `config.yaml`
- Regenerate password hash using bcrypt
- Clear browser cookies
- Check `config.yaml` formatting

#### Data Not Loading

**Symptoms**: Empty dashboards or "No data available"

**Solutions**:
- Run monthly update pipeline first
- Check month configuration in `config.yaml`
- Verify Snowflake tables exist and are accessible
- Review logs for errors

#### Google Sheets Integration Failed

**Symptoms**: "Failed to read Google Sheet"

**Solutions**:
- Verify credentials file path in `.env`
- Check service account has access to sheet
- Ensure Google Sheets API is enabled
- Verify sheet URL/ID is correct

### Debug Mode

Enable debug logging:

```bash
streamlit run app.py --logger.level=debug
```

### Getting Help

- 📧 Email: goat-team@hellofresh.com
- 💬 Slack: #flexible-hybrid-support
- 📖 Check Documentation page in app
- 🎫 Submit ticket: [Support Portal]

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and test thoroughly
4. Commit with clear messages: `git commit -m "Add feature X"`
5. Push to your fork: `git push origin feature/your-feature`
6. Create a Pull Request

### Code Standards

- Follow PEP 8 style guide
- Add docstrings to all functions
- Include type hints
- Write unit tests for new features
- Update documentation

### Testing

Run tests before submitting:

```bash
pytest tests/
```

## 📄 License

Internal HelloFresh Application - Proprietary

## 👥 Authors

- **GOAT Team** - Initial development
- **People Analytics** - Requirements and testing

## 📝 Changelog

### Version 1.0.0 (March 2026)

- Initial release
- Automated monthly pipeline
- Role-based dashboards
- Exception management
- LOA processing
- Export functionality
- Complete documentation

## 🗺️ Roadmap

### Phase 2 Features (Q2 2026)

- [ ] Disciplinary Action automation
- [ ] Email notifications
- [ ] Real-time dashboard updates
- [ ] Mobile app version
- [ ] Predictive analytics
- [ ] Integration with HRIS workflow

### Phase 3 Features (Q3 2026)

- [ ] Manager self-service exception requests
- [ ] Automated report distribution
- [ ] Historical trend analysis
- [ ] Custom alert thresholds
- [ ] API for external integrations

## 📞 Support

For support, please contact:

- **Technical Issues**: goat-team@hellofresh.com
- **Policy Questions**: Your HRBP
- **Data Issues**: people-analytics@hellofresh.com

---

**Built with ❤️ by the GOAT Team**
