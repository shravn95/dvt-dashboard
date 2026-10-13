# Dataset Discovery Summary

**Dataset:** CollegeMsg (SNAP), a temporal network of private messages on an online student social platform.

## 1. Records and Attributes

- **59,835 records**, each one a directed message
- **3 raw attributes:** `source` (sender ID), `target` (receiver ID), `timestamp` (Unix time)
- **1,899 unique users:** 1,350 senders and 1,862 receivers
- **20,296 unique sender→receiver pairs**

## 2. Variable Types

| Type         | Variables                                                                            |
| ------------ | ------------------------------------------------------------------------------------ |
| Categorical  | `source`, `target` (user IDs), weekday (derived)                                     |
| Numerical    | `timestamp`, hour of day, messages sent, messages received, total activity (derived) |
| Temporal     | `timestamp` → date, hour, weekday                                                    |
| Geographical | Not available                                                                        |

## 3. Temporal Coverage

- 15 Apr 2004 to 26 Oct 2004 (**193 days**), with activity on all 193 days
- Timestamps already sorted (0 out-of-order rows)

## 4. Data Quality

- **Missing values:** none
- **Duplicates:** 37 duplicate rows (~0.06%), removed, leaving 59,798 records
- **Self-messages:** 0

## 5. Distribution and Outliers

- Heavily right-skewed activity: median 4 messages sent vs. mean 31.5 (max 1,091)
- **159 outlier senders** (11.8% of senders) by the IQR rule (upper fence = 100.5)
- Top senders: users 9, 323, 12, 103, 105
- 549 users never sent a message; 37 never received one

## 6. Potential Relationships and Patterns

- A small group of highly active users drives much of the traffic (heavy-tailed degree distribution)
- Daily volume averages 310 messages, with a spike of **2,678 on 27 May 2004**
- Peak hour: 7 (UTC); peak weekday: Thursday
- **63.6%** of sender→receiver pairs are reciprocated
