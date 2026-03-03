# Data Schema Documentation

This document outlines the expected data structure for all inputs to the Flexible Hybrid Reporting application.

## Overview

The application integrates data from multiple sources:
1. **Snowflake** - Employee roster, swipes, PTO
2. **Google Sheets** - Manual swipe entries (WeWork)
3. **Workday** - Leave of Absence data (manual export)

## Snowflake Tables

### 1. VIEW_WORKDAY_KITCHEN_SINK_PI

**Description**: Active employee roster with organizational hierarchy

**Location**: `US_PEOPLE_INSIGHTS.LAYER_ANALYTICS.VIEW_WORKDAY_KITCHEN_SINK_PI`

**Required Columns**:

| Column Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| EMPLOYEE_ID | VARCHAR | Unique employee identifier | 3722446 |
| POSITION_ID | VARCHAR | Position identifier | P189884 |
| FIRST_NAME | VARCHAR | Employee first name | John |
| LAST_NAME | VARCHAR | Employee last name | Doe |
| WORK_EMAIL | VARCHAR | Employee email address | john.doe@hellofresh.com |
| WORK_LOCATION | VARCHAR | Primary work location | NYC Headquarters |
| DEPARTMENT | VARCHAR | Department name | Enterprise Data |
| SUPERVISORY_ORG_1 | VARCHAR | Level 1 supervisory org | Assaf Ronen |
| SUPERVISORY_ORG_2 | VARCHAR | Level 2 supervisory org | Dan Seidel |
| SUPERVISORY_ORG_3 | VARCHAR | Level 3 supervisory org | Ben Waugh |
| SUPERVISORY_ORG_4 | VARCHAR | Level 4 supervisory org | Rachel Jennings |
| SUPERVISORY_ORG_5 | VARCHAR | Level 5 supervisory org | John Reeves |
| MANAGER_NAME | VARCHAR | Direct manager name | Jane Smith |
| MANAGER_EMAIL | VARCHAR | Direct manager email | jane.smith@hellofresh.com |
| SKIP_LEVEL_MANAGER_NAME | VARCHAR | Skip level manager name | Bob Johnson |
| SKIP_LEVEL_MANAGER_EMAIL | VARCHAR | Skip level manager email | bob.johnson@hellofresh.com |
| HIRE_DATE | DATE | Employee hire date | 2023-01-15 |
| TERMINATION_DATE | DATE | Termination date (NULL if active) | NULL |
| ACTIVE_STATUS | VARCHAR | Employment status | Active |

**Filters Applied**:
- `ACTIVE_STATUS = 'Active'`
- `TERMINATION_DATE IS NULL`

---

### 2. VIEW_LENEL_S2_EVENTS_180_DAYS_v2

**Description**: Badge swipe events from Lenel access control system

**Location**: `US_PEOPLE_INSIGHTS.LAYER_ANALYTICS.VIEW_LENEL_S2_EVENTS_180_DAYS_v2`

**Required Columns**:

| Column Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| EMPLOYEE_ID | VARCHAR | Employee identifier | 3722446 |
| EVENT_TIME | TIMESTAMP | Date and time of badge swipe | 2026-03-03 08:15:23 |
| LOCATION | VARCHAR | Badge reader location | NYC HQ - Floor 3 |
| EVENT_TYPE | VARCHAR | Type of event (entry/exit) | Entry |

**Usage**:
- Group by EMPLOYEE_ID and DATE(EVENT_TIME)
- Count distinct dates per employee
- Filter by date range for reporting period

**Sample Query**:

```sql
SELECT 
    EMPLOYEE_ID,
    COUNT(DISTINCT DATE(EVENT_TIME)) as SWIPE_COUNT
FROM US_PEOPLE_INSIGHTS.LAYER_ANALYTICS.VIEW_LENEL_S2_EVENTS_180_DAYS_v2
WHERE DATE(EVENT_TIME) BETWEEN '2026-03-02' AND '2026-04-05'
GROUP BY EMPLOYEE_ID
```

---

### 3. VIEW_ADP_TIME_OFF_APPROVED

**Description**: Approved PTO requests from ADP

**Location**: `US_PEOPLE_INSIGHTS.LAYER_ANALYTICS.VIEW_ADP_TIME_OFF_APPROVED`

**Required Columns**:

| Column Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| EMPLOYEE_ID | VARCHAR | Employee identifier | 3722446 |
| TIME_OFF_DATE | DATE | Date of time off | 2026-03-15 |
| TIME_OFF_TYPE | VARCHAR | Type of time off | Vacation |
| TIME_OFF_STATUS | VARCHAR | Request status | Approved |
| HOURS | FLOAT | Hours of PTO | 8.0 |

**Filters Applied**:
- `TIME_OFF_STATUS = 'Approved'`
- `TIME_OFF_DATE BETWEEN <start_date> AND <end_date>`

**Usage**:
- Count distinct TIME_OFF_DATE per employee
- Only count full-day PTOs (8+ hours)

**Sample Query**:

```sql
SELECT 
    EMPLOYEE_ID,
    COUNT(DISTINCT TIME_OFF_DATE) as PTO_DAYS
FROM US_PEOPLE_INSIGHTS.LAYER_ANALYTICS.VIEW_ADP_TIME_OFF_APPROVED
WHERE TIME_OFF_DATE BETWEEN '2026-03-02' AND '2026-04-05'
    AND TIME_OFF_STATUS = 'Approved'
    AND HOURS >= 8
GROUP BY EMPLOYEE_ID
```

---

### 4. INT0136_WORKER_SCHEDULE_CHANGES

**Description**: Employee schedule types from Workday

**Location**: `US_PEOPLE_INSIGHTS.WORKDAY.INT0136_WORKER_SCHEDULE_CHANGES`

**Required Columns**:

| Column Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| EMPLOYEE_ID | VARCHAR | Employee identifier | 3722446 |
| SCHEDULE_NAME | VARCHAR | Schedule type name | Mon - Fri, 8 Hour Days (Default) |
| EFFECTIVE_DATE | DATE | Date schedule became effective | 2023-01-15 |

**Usage**:
- Get most recent schedule per employee
- Determines expected office average (2.5 for 8-hour, 2.0 for 10-hour)

**Schedule Types**:
- "Mon - Fri, 8 Hour Days (Default)" → 2.5 days/week expected
- "FLEX - Schedule Varies - 10 Hours" → 2.0 days/week expected

---

## Google Sheets Integration

### Chicago WeWork Swipe Tracker

**Description**: Manual swipe entries for Chicago WeWork location

**Sheet Name**: "Chicago WeWork Swipe Tracker_Current"

**Required Columns**:

| Column Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| DATE | DATE | Date of swipe | 2026-03-15 |
| EMPLOYEE_ID | VARCHAR | Employee identifier | 3722446 |
| FIRST_NAME | VARCHAR | Employee first name | John |
| LAST_NAME | VARCHAR | Employee last name | Doe |
| SWIPE_COUNT | INTEGER | Number of swipes (should be 1 per day) | 1 |

**Format**:
- Header row in row 1
- Data starts in row 2
- Date format: YYYY-MM-DD or MM/DD/YYYY

---

## Workday Manual Exports

### Workers on Leave Report

**Report Name**: "US HF - Workers on Leave"

**Export Format**: Excel (.xlsx) or CSV

**Required Columns**:

| Column Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| EMPLOYEE_ID | VARCHAR | Employee identifier | 3722446 |
| FIRST_NAME | VARCHAR | Employee first name | John |
| LAST_NAME | VARCHAR | Employee last name | Doe |
| LOA_TYPE | VARCHAR | Type of leave | Medical Leave |
| LOA_START_DATE | DATE | Leave start date | 2026-03-01 |
| LOA_END_DATE | DATE | Leave end date | 2026-03-31 |
| LOA_STATUS | VARCHAR | Status of leave | Active |

**Processing**:
The application calculates weekdays (Mon-Fri) on leave during the reporting period.

**Example Calculation**:
- LOA: March 1 - March 31 (31 days)
- Reporting Period: March 2 - April 5
- Overlap: March 2 - March 31 (30 days)
- Weekdays in overlap: 21 days

---

## Application Output Schema

### Processed Monthly Data

The application generates a comprehensive dataset with the following schema:

| Column Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| FLEX_HYBRID_MONTH | VARCHAR | Reporting month | 2026-03 |
| EMPLOYEE_ID | VARCHAR | Employee identifier | 3722446 |
| POSITION_ID | VARCHAR | Position identifier | P189884 |
| FIRST_NAME | VARCHAR | Employee first name | John |
| LAST_NAME | VARCHAR | Employee last name | Doe |
| WORK_EMAIL | VARCHAR | Employee email | john.doe@hellofresh.com |
| WORK_LOCATION | VARCHAR | Work location | NYC Headquarters |
| DEPARTMENT | VARCHAR | Department | Enterprise Data |
| SUPERVISORY_ORG_1 | VARCHAR | Sup org level 1 | Assaf Ronen |
| SUPERVISORY_ORG_2 | VARCHAR | Sup org level 2 | Dan Seidel |
| SUPERVISORY_ORG_3 | VARCHAR | Sup org level 3 | Ben Waugh |
| SUPERVISORY_ORG_4 | VARCHAR | Sup org level 4 | Rachel Jennings |
| SUPERVISORY_ORG_5 | VARCHAR | Sup org level 5 | John Reeves |
| MANAGER_NAME | VARCHAR | Manager name | Jane Smith |
| MANAGER_EMAIL | VARCHAR | Manager email | jane.smith@hellofresh.com |
| SCHEDULE_NAME | VARCHAR | Schedule type | Mon - Fri, 8 Hour Days (Default) |
| SWIPES_LENEL | INTEGER | Lenel swipe count | 15 |
| SWIPES_MANUAL | INTEGER | Manual swipe count (WeWork) | 0 |
| SWIPES_TOTAL | INTEGER | Total swipes | 15 |
| PTO_DAYS | INTEGER | PTO days taken | 2 |
| LOA_DAYS | INTEGER | LOA weekdays | 0 |
| IS_ON_LEAVE | BOOLEAN | Currently on leave | FALSE |
| COMPANY_HOLIDAYS | INTEGER | Company holidays in period | 0 |
| DAYS_POSSIBLE | INTEGER | Working days available | 23 |
| EXCEPTIONS | INTEGER | Exception days granted | 0 |
| HAS_EXCEPTION | BOOLEAN | Has active exception | FALSE |
| IS_ESSENTIAL | BOOLEAN | Essential classification | FALSE |
| ADJUSTED_WEEKLY_AVG | FLOAT | Calculated average | 3.26 |
| COMPLIANCE_STATUS | VARCHAR | Compliance status | Compliant |
| LAST_UPDATED | TIMESTAMP | Last update timestamp | 2026-03-03 14:30:00 |

---

## Calculation Formulas

### Adjusted Weekly Average

```
Adjusted Weekly Average = ((Swipes Total + Exceptions) / Days Possible) × 5
```

### Days Possible

```
Days Possible = Base Days - PTO Days - LOA Days
```

Where:
- **Base Days**: Working days in reporting period (from config)
- **PTO Days**: Count of PTO days taken
- **LOA Days**: Count of weekdays on leave

### Compliance Status Logic

```python
if IS_ON_LEAVE:
    return "On Leave"
elif IS_ESSENTIAL:
    return "Essential (Exempt)"
elif HAS_EXCEPTION:
    return "Exception Granted"
elif ADJUSTED_WEEKLY_AVG >= 2.5:
    return "Compliant"
elif ADJUSTED_WEEKLY_AVG >= 2.0:
    return "At Risk"
else:
    return "Non-Compliant"
```

---

## Data Quality Requirements

### Required Validations

1. **Employee ID**: Must be valid and exist in roster
2. **Dates**: Must fall within reporting period
3. **Swipe Counts**: Must be >= 0
4. **PTO Days**: Must be >= 0 and <= Days Possible
5. **LOA Days**: Must be >= 0 and <= Days Possible
6. **Adjusted Weekly Avg**: Should be between 0 and 5

### Data Freshness

- **Lenel Swipes**: Updated hourly (Snowflake)
- **PTO Data**: Updated daily (Snowflake)
- **Kitchen Sink**: Updated weekly (Snowflake)
- **WeWork Swipes**: Updated weekly (Manual)
- **LOA Data**: Updated monthly (Manual)

---

## Testing Data

For testing purposes, sample data files are available in `/data/samples/`:

- `sample_roster.csv`
- `sample_swipes.csv`
- `sample_pto.csv`
- `sample_loa.csv`

Use these to test the application without connecting to production databases.
