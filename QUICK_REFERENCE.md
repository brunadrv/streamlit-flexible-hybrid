# Flexible Hybrid Reporting - Quick Reference

## 🚀 Quick Commands

### Start Application
```bash
streamlit run app.py
```

### Generate Password Hash
```python
import bcrypt
bcrypt.hashpw('password'.encode(), bcrypt.gensalt()).decode()
```

### Test Snowflake Connection
```python
from utils import get_snowflake_connector
sf = get_snowflake_connector()
sf.connect()
```

## 📊 Key Formulas

### Adjusted Weekly Average
```
((Swipes + Exceptions) / Days Possible) × 5
```

### Days Possible
```
Base Days - PTO Days - LOA Days
```

### Compliance Status
- **Compliant**: ≥ 2.5
- **At Risk**: 2.0 - 2.49
- **Non-Compliant**: < 2.0

## 🔐 User Roles & Permissions

| Role | View All Org | Manage Exceptions | View Own Team | Export Data |
|------|--------------|-------------------|---------------|-------------|
| Admin | ✅ | ✅ | ✅ | ✅ |
| HRBP | Department Only | ✅ | ✅ | ✅ |
| Manager | ❌ | ❌ | ✅ | Team Only |
| Employee | ❌ | ❌ | ❌ | Own Data |

## 📅 Monthly Workflow Checklist

### Week 1 of New Month (After Reporting Period Ends)

- [ ] **Admin Panel** → Monthly Data Update
- [ ] Select previous month
- [ ] Click "Run Monthly Update Pipeline"
- [ ] Monitor progress and verify completion

### LOA Processing

- [ ] Export "Workers on Leave" from Workday
- [ ] **Admin Panel** → LOA Processing tab
- [ ] Upload export file
- [ ] Download processed LOA data

### Review & Exceptions

- [ ] Review Dashboard for compliance metrics
- [ ] Check All Org View for detailed data
- [ ] Grant exceptions as needed via Admin Panel
- [ ] Update classifications if required

### Reporting & Distribution

- [ ] **Export** → Monthly Compliance Report
- [ ] Generate department reports for HRBPs
- [ ] Update Disciplinary Action tracker (if needed)
- [ ] Distribute reports to leadership and managers

## 🔧 Common Tasks

### Add New User

1. Generate password hash (see command above)
2. Edit `config.yaml`:
   ```yaml
   credentials:
     usernames:
       new_user:
         email: user@hellofresh.com
         name: User Name
         password: <hashed_password>
         role: <role>
   ```
3. Restart application

### Assign Department to HRBP

Edit `config.yaml`:
```yaml
hrbp_assignments:
  hrbp.email@hellofresh.com:
    - Department Name 1
    - Department Name 2
```

### Add New Reporting Month

Edit `config.yaml`:
```yaml
flex_schedule:
  months:
    "2026-04":
      start_date: "2026-04-06"
      end_date: "2026-05-03"
      weeks: 4
      days_possible: 20
```

### Grant Exception

1. **Admin Panel** → Manage Exceptions
2. Enter Employee ID
3. Specify exception days
4. Provide reason
5. Select exception type
6. Click "Add Exception"

## 📁 File Structure

```
flexible_hybrid_app/
├── app.py                 # Main entry point
├── config.yaml            # Configuration
├── .env                   # Environment variables (local)
├── utils/                 # Core modules
│   ├── snowflake_connector.py
│   ├── data_processor.py
│   ├── auth.py
│   ├── gsheets_connector.py
│   └── loa_processor.py
└── pages/                 # Streamlit pages
    ├── 1_📊_Dashboard.py
    ├── 2_🏢_All_Org_View.py
    ├── 3_🏛️_Department_View.py
    ├── 4_👥_Team_View.py
    ├── 5_⚙️_Admin.py
    ├── 6_📤_Export.py
    └── 7_📚_Documentation.py
```

## 🐛 Troubleshooting Quick Fixes

### "No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### "Failed to connect to Snowflake"
- Check `.env` credentials
- Verify VPN connection
- Test credentials in Snowflake web interface

### "Permission denied"
- Verify user role in `config.yaml`
- Check required permissions for page
- Log out and log back in

### "No data available"
- Run monthly update pipeline first
- Check month configuration exists
- Verify Snowflake tables accessible

### Application won't start
```bash
# Check for Python errors
streamlit run app.py --logger.level=debug

# Verify Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📊 Data Sources

| Source | Type | Update Frequency | Connection Method |
|--------|------|------------------|-------------------|
| Kitchen Sink | Snowflake | Weekly | Automated |
| Lenel Swipes | Snowflake | Hourly | Automated |
| PTO Data | Snowflake | Daily | Automated |
| WeWork Swipes | Google Sheets | Weekly | Automated |
| LOA Data | Workday | Monthly | Manual Export |
| Schedules | Snowflake | As needed | Automated |

## 🎯 Key Metrics Definitions

- **Total Employees**: All employees in roster
- **Eligible Employees**: Non-essential, no exceptions, not on leave
- **Compliance Rate**: % of eligible employees ≥ 2.5 average
- **At Risk**: Employees between 2.0 and 2.5 average
- **Non-Compliant**: Employees < 2.0 average

## 📞 Support Contacts

- **Technical Issues**: goat-team@hellofresh.com
- **Policy Questions**: Your HRBP
- **Data Issues**: people-analytics@hellofresh.com
- **Slack Channel**: #flexible-hybrid-support

## 🔗 Useful Links

- [Flexible Hybrid Policy](https://docs.google.com)
- [HRBP Directory](https://docs.google.com)
- [Workday Access](https://hellofresh.workday.com)
- [Snowflake Web UI](https://hellofresh.snowflakecomputing.com)

## 📝 Quick Notes

- Default compliance threshold: **2.5 days/week**
- 10-hour schedule threshold: **2.0 days/week**
- Company holidays are pre-deducted from base days
- PTO and LOA reduce days possible
- Exceptions add to numerator, not days possible
- Essential employees are exempt (expected 5x/week)

---

**Last Updated**: March 2026 | **Version**: 1.0.0
