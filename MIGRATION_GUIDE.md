# Migration Guide: Manual Process to Automated App

This guide helps you transition from the current manual Google Sheets process to the new automated Streamlit application.

## 📋 Overview

**Current State** (Manual):
- Monthly copy/paste between multiple Google Sheets
- Manual KNIME pipeline execution with multiple steps
- 4-6 hours per month of manual work
- Error-prone calculations
- Complex sheet maintenance

**Future State** (Automated):
- One-click monthly updates
- Automated data pipeline from Snowflake
- Real-time calculations
- Role-based dashboards
- < 30 minutes per month

## 🗓️ Migration Timeline

### Phase 1: Setup & Testing (Week 1-2)

**Week 1: Initial Setup**
- [ ] Install application (see SETUP_GUIDE.md)
- [ ] Configure Snowflake connection
- [ ] Set up Google Sheets integration (WeWork)
- [ ] Create user accounts for pilot group
- [ ] Load configuration (months, HRBPs, roles)

**Week 2: Data Validation**
- [ ] Run pipeline for most recent month
- [ ] Compare output with current manual Google Sheet
- [ ] Validate calculations match
- [ ] Fix any discrepancies
- [ ] Test all user roles

### Phase 2: Pilot Program (Week 3-4)

**Week 3: Internal Testing**
- [ ] GOAT team uses app for daily work
- [ ] 2-3 HRBPs pilot the system
- [ ] Gather feedback on UI/UX
- [ ] Identify bugs and issues
- [ ] Make necessary adjustments

**Week 4: Expanded Pilot**
- [ ] Add 5-6 more HRBPs
- [ ] Include 3-4 managers
- [ ] Test export functionality
- [ ] Validate role-based access
- [ ] Conduct training sessions

### Phase 3: Full Rollout (Week 5-6)

**Week 5: Go-Live Preparation**
- [ ] Finalize all user accounts
- [ ] Conduct organization-wide training
- [ ] Prepare communication plan
- [ ] Set up support channel
- [ ] Create video tutorials

**Week 6: Launch**
- [ ] Announce to organization
- [ ] Switch from manual to automated
- [ ] Monitor usage and issues
- [ ] Provide hands-on support
- [ ] Maintain manual process as backup

### Phase 4: Optimization (Week 7-8)

**Ongoing**
- [ ] Collect user feedback
- [ ] Fix reported issues
- [ ] Add requested features
- [ ] Retire manual process
- [ ] Document lessons learned

## 🔄 Process Comparison

### Current Manual Process

| Step | Time | Complexity |
|------|------|------------|
| Prep All Org Sheet | 30 min | High |
| Run KNIME Pipeline | 45 min | High |
| Copy/Paste Data | 60 min | Medium |
| Update ELT Sheets | 90 min | High |
| Update Disciplinary Action | 30 min | Medium |
| Validate & Distribute | 45 min | Medium |
| **TOTAL** | **4-5 hours** | **High** |

### New Automated Process

| Step | Time | Complexity |
|------|------|------------|
| Run Monthly Update | 5 min | Low |
| Upload LOA Data | 3 min | Low |
| Review Dashboard | 5 min | Low |
| Grant Exceptions | 5 min | Low |
| Export Reports | 5 min | Low |
| Distribute | 5 min | Low |
| **TOTAL** | **< 30 min** | **Low** |

## 📊 Data Mapping

### From Manual Google Sheets to App

| Current Location | New Location | Notes |
|------------------|--------------|-------|
| All Org Tracker Sheet | Dashboard → All Org View | Automated calculation |
| ELT Department Sheets | Department View | Filtered automatically |
| Disciplinary Action Sheet | Admin Panel + Export | Coming in Phase 2 |
| WD_Roster Tab | Snowflake Kitchen Sink | Direct query |
| Swipes Tab | Snowflake Lenel + GSheets | Automated aggregation |
| PTO Tab | Snowflake ADP | Direct query |
| Days_Off Tab | Admin → LOA Processing | Automated calculation |
| Exceptions Tab | Admin → Manage Exceptions | Database-backed |

### Historical Data Migration

**Option 1: Import Historical Sheets (Recommended for < 6 months)**

Create a script to import existing Google Sheets data:

```python
# import_historical.py
import pandas as pd
import gspread
from utils import get_snowflake_connector

# Read historical sheets
sheets = [
    "Flexible_Hybrid_Jan2026_ALLORG",
    "Flexible_Hybrid_Feb2026_ALLORG",
    "Flexible_Hybrid_Mar2026_ALLORG"
]

# Process and load into app database
for sheet in sheets:
    df = read_sheet(sheet)
    # Transform and load
    ...
```

**Option 2: Keep Historical Sheets (Recommended for > 6 months)**

- Keep existing sheets as-is for historical reference
- Start fresh with new app from current month forward
- Archive old sheets after 12 months in app

**Option 3: Hybrid Approach**

- Import last 3 months for trend analysis
- Archive older months in Snowflake
- Use app going forward

## 🔀 Transition Strategy

### Parallel Run Period (Recommended)

For the first 2-3 months, run both systems in parallel:

**Month 1: Parallel + Validation**
- Run manual process as usual
- Run automated app
- Compare outputs
- Identify discrepancies
- Trust manual, verify automated

**Month 2: Automated + Manual Backup**
- Use automated app as primary
- Run manual process as backup
- Spot-check critical numbers
- Build confidence in automation

**Month 3: Automated Only**
- Fully trust automated system
- Manual process available but not used
- Retire manual process

### Big Bang Cutover (Faster but Riskier)

If confident after testing:

1. **Final Manual Run**: Complete last manual month
2. **Switch**: Next month uses only automated app
3. **Backup Plan**: Have manual process documented just in case
4. **Extra Support**: GOAT team on standby for issues

## 👥 Training Plan

### For HRBPs & Admins

**Session 1: Overview & Dashboard (30 min)**
- Application tour
- Understanding metrics
- Navigating pages
- Role-based access

**Session 2: Monthly Process (45 min)**
- Running monthly updates
- LOA processing
- Exception management
- Export and distribution

**Session 3: Troubleshooting (30 min)**
- Common issues
- Data validation
- Getting help
- Escalation process

### For Managers

**Session 1: Team View (20 min)**
- Accessing the app
- Viewing team data
- Understanding compliance
- Exporting reports

**Session 2: Q&A (10 min)**
- Answer questions
- Share best practices
- Provide support resources

### For Employees

**Communication Email** (No training needed)
- App announcement
- How to access
- What to expect
- Where to get help

## 📋 Validation Checklist

Before fully retiring manual process:

### Data Accuracy
- [ ] Employee counts match
- [ ] Swipe counts match (±1-2 due to timing)
- [ ] PTO days match exactly
- [ ] LOA days match exactly
- [ ] Adjusted weekly averages match (±0.01)
- [ ] Compliance status matches

### Functionality
- [ ] All users can log in
- [ ] Role-based access works correctly
- [ ] Monthly update completes successfully
- [ ] LOA processing works
- [ ] Exception management works
- [ ] Exports generate correctly
- [ ] All pages load without errors

### Performance
- [ ] Dashboard loads in < 5 seconds
- [ ] Monthly update completes in < 5 minutes
- [ ] Exports generate in < 10 seconds
- [ ] No timeouts or crashes

### User Acceptance
- [ ] HRBPs approve accuracy
- [ ] Managers can access team data
- [ ] Leadership gets required reports
- [ ] Users find interface intuitive
- [ ] Support requests manageable

## 🚨 Rollback Plan

If critical issues arise:

**Immediate Actions:**
1. Announce issue via Slack/email
2. Direct users back to manual process
3. Pause new app development
4. Investigate root cause

**Issue Categories:**

**Minor Issues** (Continue with app):
- UI bugs
- Minor calculation differences
- Performance issues
- Non-critical errors

**Major Issues** (Pause and fix):
- Incorrect calculations affecting decisions
- Data access problems
- Security concerns
- Persistent crashes

**Critical Issues** (Rollback):
- Data loss or corruption
- Major security breach
- Complete system failure
- Incorrect disciplinary actions taken

**Rollback Steps:**
1. Switch users back to manual Google Sheets
2. Document all issues encountered
3. Fix issues in test environment
4. Re-test extensively
5. Plan new rollout date

## 📞 Support During Transition

### Support Channels

**Priority 1: Critical Issues** (Blocking work)
- Email: goat-team@hellofresh.com (Subject: URGENT)
- Slack: DM @goat-team
- Response time: < 1 hour during business hours

**Priority 2: Important Issues** (Workaround available)
- Slack: #flexible-hybrid-support
- Email: goat-team@hellofresh.com
- Response time: < 4 hours

**Priority 3: Questions & Feature Requests**
- Slack: #flexible-hybrid-support
- Email: goat-team@hellofresh.com
- Response time: < 1 business day

### Office Hours

During transition period (first 4 weeks):
- **Tuesday & Thursday**: 2:00 PM - 3:00 PM ET
- **Open Q&A and hands-on help**
- **Zoom link in Slack channel**

## 📊 Success Metrics

Track these metrics during transition:

| Metric | Target | Current |
|--------|--------|---------|
| Time to complete monthly update | < 30 min | — |
| User satisfaction score | > 4/5 | — |
| Data accuracy | 99.9% | — |
| Critical bugs | 0 | — |
| User adoption rate | > 95% | — |
| Support tickets per month | < 10 | — |

## ✅ Post-Migration Cleanup

After successful transition:

**Month 3:**
- [ ] Archive manual Google Sheets
- [ ] Update documentation to remove manual steps
- [ ] Remove KNIME pipeline (after backup)
- [ ] Celebrate success! 🎉

**Month 6:**
- [ ] Review historical data retention
- [ ] Delete temporary/test data
- [ ] Optimize performance based on usage
- [ ] Plan Phase 2 features

## 🎯 Phase 2 Enhancements

After successful migration:

1. **Disciplinary Action Automation**
   - Automated email generation
   - Workflow integration
   - Tracking and escalation

2. **Real-time Dashboards**
   - Daily updates instead of monthly
   - Live swipe tracking
   - Predictive alerts

3. **Advanced Analytics**
   - Trend analysis
   - Predictive compliance
   - Department benchmarking

4. **Mobile Access**
   - Mobile-responsive design
   - Native app (future)

---

## 💡 Tips for Success

1. **Start Small**: Pilot with trusted users first
2. **Communicate Often**: Over-communicate during transition
3. **Be Patient**: Allow time for users to adapt
4. **Listen**: Gather and act on feedback quickly
5. **Document**: Record issues and solutions
6. **Support**: Provide excellent support during transition
7. **Celebrate**: Recognize the team's effort

## 📞 Questions?

Contact the GOAT team:
- 📧 goat-team@hellofresh.com
- 💬 #flexible-hybrid-support on Slack

---

**Remember**: The goal is to make everyone's life easier. Take the time to do it right!
