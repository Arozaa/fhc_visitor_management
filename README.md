# FHC Visitor Management System

A custom Frappe application built for the **Federal Housing Corporation (FHC)**
to manage visitor access, badge assignment, host coordination, and security
compliance across FHC premises.

---

## Table of Contents

1. [Project Purpose](#project-purpose)
2. [Prerequisites](#prerequisites)
3. [Part A — Environment Setup](#part-a--environment-setup)
4. [Part B — App Installation](#part-b--app-installation)
5. [DocType Structure](#doctype-structure)
6. [Roles & Permissions](#roles--permissions)
7. [Workflow](#workflow)
8. [Reports](#reports)
9. [Testing](#testing)
10. [Sample Data](#sample-data)
11. [Key Features](#key-features)

---

## Project Purpose

FHC receives a large number of daily visitors across its offices.  The Visitor
Management System (VMS) provides:

- A structured **pre-registration and approval** process for planned visits.
- Real-time **check-in / check-out** tracking with badge management.
- **Security controls** including blacklist enforcement and role-scoped access.
- **Audit-ready reporting** on visit frequency, duration, and department traffic.

---

## Prerequisites

| Dependency | Minimum Version |
|---|---|
| Ubuntu / Debian | 20.04 LTS or later |
| Python | 3.10+ |
| Node.js | 18 LTS |
| MariaDB | 10.6+ |
| Redis | 6.x |
| wkhtmltopdf | 0.12.6 (with patched Qt) |
| Frappe Bench | 5.x |
| Frappe Framework | 15.x |
| ERPNext | 15.x |

---

## Part A — Environment Setup

### 1. System Prerequisites

```bash
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip python3-venv \
    git mariadb-server mariadb-client redis-server \
    libmysqlclient-dev libssl-dev libffi-dev \
    wkhtmltopdf curl
```

### 2. Node.js (via nvm)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
npm install -g yarn
```

### 3. MariaDB Configuration

```bash
sudo mysql_secure_installation
```

Edit `/etc/mysql/mariadb.conf.d/50-server.cnf` and add under `[mysqld]`:

```ini
character-set-server  = utf8mb4
collation-server      = utf8mb4_unicode_ci
```

```bash
sudo systemctl restart mariadb
```

### 4. Install Frappe Bench

```bash
pip3 install frappe-bench
bench --version          # should print 5.x
```

### 5. Initialise a Bench

```bash
bench init frappe-bench --frappe-branch version-15
cd frappe-bench
```

### 6. Create a Site

```bash
bench new-site fhc.localhost \
    --db-name fhc_db \
    --admin-password <choose-a-password>
bench use fhc.localhost
```

### 7. Install ERPNext

```bash
bench get-app erpnext --branch version-15
bench --site fhc.localhost install-app erpnext
```

### 8. Start the Development Server

```bash
bench start
```

Open `http://fhc.localhost:8000` in your browser and log in as **Administrator**.

---

## Part B — App Installation

### Clone the Repository

```bash
# From inside the frappe-bench directory:
bench get-app https://github.com/Arozaa/fhc_visitor_management
bench --site fhc.localhost install-app fhc_visitor_management
bench migrate
bench build
bench restart
```

### Verify Installation

1. Log in as Administrator.
2. Open the **Visitor Management** workspace from the desk.
3. Confirm the following DocTypes are present:
   - Visit, Visitor, Visitor Badge, Host Department, Visit Item (child table)

---

## DocType Structure

```
Visitor  ◄──────────────────  Visit  ──────────►  Host Department
                                 │
                                 ├──►  Visit Item (child table — items brought in)
                                 │
                                 └──►  Visitor Badge
```

| DocType | Purpose | Naming |
|---|---|---|
| **Visitor** | Stores visitor identity and status | `VM-VIS-YYYY-#####` |
| **Visit** | Core visit record (submittable) | `VM-VISIT-YYYY-#####` |
| **Visit Item** | Child table — items a visitor brings in | — |
| **Visitor Badge** | Badge inventory and assignment | `VM-BADGE-YYYY-#####` |
| **Host Department** | FHC departments available to host visitors | By name |

---

## Roles & Permissions

| Role | Capabilities |
|---|---|
| **Receptionist** | Register visitors, create and submit visit requests, view own records |
| **Security Officer** | View all visits, perform check-in / check-out, manage badges |
| **VM Admin Manager** | Full access — approve/reject visits, manage all records, run reports |

### Create Test Users

```
Desk → Users → New User
  - Receptionist Test:  role = Receptionist
  - Security Test:      role = Security Officer
  - Manager Test:       role = VM Admin Manager
```

---

## Workflow

```
[Draft]
   │  Submit for Approval  (Receptionist)
   ▼
[Pending Approval]
   │  Approve              (VM Admin Manager)
   │  Reject ──────────────────────────────► [Cancelled]
   ▼
[Approved]
   │  Check In             (Security Officer)
   │  Cancel ──────────────────────────────► [Cancelled]
   ▼
[Checked In]
   │  Check Out            (Security Officer)
   ▼
[Checked Out]
```

---

## Reports

| Report | Type | Access |
|---|---|---|
| **Daily Visit Summary** | Script Report | Receptionist, Security Officer, VM Admin Manager |
| **Visitor Frequency** | Script Report | Security Officer, VM Admin Manager |

Both reports support date-range and category filters, include summary cards,
and render a bar chart.

---

## Testing

```bash
bench run-tests --app fhc_visitor_management --doctype Visit
bench run-tests --app fhc_visitor_management --doctype Visitor
```

### Manual Test Checklist

| # | Test Case | Expected Result |
|---|---|---|
| 1 | Register a new visitor with valid details | Visitor saved, ID `VM-VIS-...` assigned |
| 2 | Register a visitor with a duplicate ID number | ValidationError thrown |
| 3 | Blacklist a visitor without providing a reason | ValidationError thrown |
| 4 | Create a visit for a blacklisted visitor | ValidationError thrown |
| 5 | Set expected departure before expected arrival | ValidationError thrown |
| 6 | Submit visit for approval as Receptionist | Status changes to `Pending Approval` |
| 7 | Approve visit as VM Admin Manager | Status changes to `Approved` |
| 8 | Check in visitor as Security Officer | Status changes to `Checked In`, badge marked Issued |
| 9 | Check out visitor as Security Officer | Status changes to `Checked Out`, duration calculated |
| 10 | Run Daily Visit Summary report | Rows, chart, and summary cards rendered |
| 11 | Log in as Receptionist — cannot see other users' visits | Only own records visible |
| 12 | Print Visitor Pass | Formatted pass PDF generated |

---

## Sample Data

After installing the app, run the following from the bench console to load
seed data for demonstration:

```bash
bench --site fhc.localhost execute \
    fhc_visitor_management.visitor_management.setup.create_sample_data
```

This creates:
- 5 Host Departments
- 10 Visitor records
- 5 Visitor Badges
- 8 Visit records in various workflow states

---

## Key Features

- **Blacklist enforcement** — blacklisted visitors are blocked at form level with a clear error message.
- **Auto-suggest departure** — entering an expected arrival auto-fills departure 2 hours later.
- **Live duration calculation** — duration is computed client-side and server-side.
- **Badge lifecycle management** — badges are automatically marked Issued on check-in and Available on check-out or cancellation.
- **Scheduled auto-checkout** — visits open for more than 12 hours are automatically checked out overnight.
- **Scoped data access** — Receptionists only see their own visit records.
- **Desk notifications** — visit counts shown on the desk for `Pending Approval` and `Checked In` states.
- **Print Visitor Pass** — professional branded pass printable from any approved visit.

---

*Federal Housing Corporation — Information Technology / ERP Development*
*Candidate Submission — ERPNext / Frappe Developer Practical Exam*
