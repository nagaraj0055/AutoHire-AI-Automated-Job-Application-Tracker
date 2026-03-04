# 🚀 AutoHire AI — Automated Job Application Tracker

A complete full-stack system that **automatically scrapes job postings** from LinkedIn, Indeed & Naukri, stores them in a MySQL database, displays them in a stunning dashboard, and sends **daily email alerts** with new opportunities.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.15-43B02A?logo=selenium)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [Setup Guide](#-setup-guide)
- [Running the Project](#-running-the-project)
- [API Documentation](#-api-documentation)
- [Example Output](#-example-output)
- [Architecture](#-architecture)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Auto Scraping** | Scrapes LinkedIn, Indeed & Naukri for jobs |
| 💾 **Smart Storage** | MySQL database with duplicate detection |
| 📊 **Live Dashboard** | Glassmorphism dark-themed web UI with filters |
| 📧 **Email Alerts** | Daily HTML email notifications with apply links |
| ⏰ **Scheduler** | APScheduler runs scraping every 12 hours |
| 🔌 **REST API** | Full CRUD API for job management |
| 🎨 **Premium UI** | Animated stats, particle effects, responsive design |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.9+, Flask 3.0 |
| **Automation** | Selenium WebDriver, WebDriver Manager |
| **Database** | MySQL 8.0 |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Scheduler** | APScheduler (BackgroundScheduler) |
| **Email** | smtplib (Gmail SMTP) |

---

## 📂 Project Structure

```
AutoHire AI/
│
├── app.py                 # Main Flask application (routes, API, startup)
├── scraper.py             # Selenium scrapers (LinkedIn, Indeed, Naukri)
├── database.py            # MySQL database manager (CRUD, stats, logging)
├── email_service.py       # Email notification service (HTML emails)
├── scheduler.py           # APScheduler for automated tasks
├── config.py              # Centralized configuration management
├── requirements.txt       # Python dependencies
├── schema.sql             # Database schema + sample data
├── .env.example           # Environment variables template
├── README.md              # This file
│
├── templates/
│   └── dashboard.html     # Jinja2 dashboard template
│
└── static/
    ├── style.css           # Premium dark theme styles
    └── script.js           # Client-side interactivity
```

---

## 🗄 Database Schema

### `job_listings` — Main table for storing scraped jobs

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT (PK, AUTO) | Unique job ID |
| `job_title` | VARCHAR(255) | Job position title |
| `company_name` | VARCHAR(255) | Hiring company |
| `location` | VARCHAR(255) | Job location |
| `job_link` | VARCHAR(512) | Unique job URL |
| `date_posted` | VARCHAR(100) | When job was posted |
| `source` | VARCHAR(50) | Platform: linkedin/indeed/naukri |
| `scraped_at` | TIMESTAMP | When we scraped it |
| `is_emailed` | BOOLEAN | Included in email alert? |
| `is_active` | BOOLEAN | Soft delete flag |

### `scrape_logs` — Tracks scraping sessions

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT (PK, AUTO) | Log ID |
| `source` | VARCHAR(50) | Platform scraped |
| `jobs_found` | INT | Total jobs found |
| `jobs_added` | INT | New jobs added |
| `status` | ENUM | success/failed/partial |
| `error_message` | TEXT | Error details if any |

### `email_logs` — Tracks email notifications

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT (PK, AUTO) | Log ID |
| `recipient` | VARCHAR(255) | Email recipient |
| `jobs_count` | INT | Jobs included |
| `status` | ENUM | sent/failed |

---

## 🚀 Setup Guide

### Prerequisites

- **Python 3.9+** installed
- **MySQL 8.0+** installed and running
- **Google Chrome** browser installed
- **Gmail account** with App Password (for email alerts)

### Step 1: Clone & Navigate

```bash
cd "AutoHire AI"
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup Environment Variables

```bash
# Copy the template
copy .env.example .env

# Edit .env with your credentials
```

**Required `.env` values:**

| Variable | Example | Description |
|----------|---------|-------------|
| `DB_PASSWORD` | `mypassword` | Your MySQL password |
| `EMAIL_USER` | `you@gmail.com` | Gmail address |
| `EMAIL_PASSWORD` | `abcd efgh ijkl mnop` | Gmail App Password |
| `EMAIL_RECIPIENT` | `you@gmail.com` | Alert recipient email |

> **💡 Gmail App Password:** Go to Google Account → Security → 2-Step Verification → App passwords → Generate one for "Mail"

### Step 5: Setup Database

**Option A — Automatic (recommended):**
The app auto-creates the database and tables on first run.

**Option B — Manual:**
```bash
mysql -u root -p < schema.sql
```

### Step 6: Run the Application

```bash
python app.py
```

Visit **http://localhost:5000** to see the dashboard! 🎉

---

## ▶️ Running the Project

### Start the Full Application
```bash
python app.py
```
This starts:
- ✅ Flask web server on port 5000
- ✅ Background scheduler (scraping every 12h, emails at 9 AM)
- ✅ Auto-creates database if needed

### Run Scraper Standalone
```bash
python scraper.py
```

### Send Email Alert Manually
```bash
python email_service.py
```

### Run Scheduler Standalone
```bash
python scheduler.py
```

---

## 🔌 API Documentation

### Base URL: `http://localhost:5000/api`

### Get All Jobs
```
GET /api/jobs
GET /api/jobs?company=Google&role=Engineer&location=Bangalore&source=linkedin
```

**Response:**
```json
{
    "status": "success",
    "count": 8,
    "data": [
        {
            "id": 1,
            "job_title": "Software Engineer",
            "company_name": "Google",
            "location": "Bangalore, India",
            "job_link": "https://careers.google.com/jobs/1",
            "date_posted": "2 days ago",
            "source": "linkedin",
            "scraped_at": "2026-03-04 14:30:00",
            "is_emailed": false,
            "is_active": true
        }
    ]
}
```

### Get Single Job
```
GET /api/jobs/1
```

### Add Job
```bash
POST /api/jobs
Content-Type: application/json

{
    "job_title": "ML Engineer",
    "company_name": "DeepMind",
    "location": "London, UK",
    "job_link": "https://deepmind.com/careers/123",
    "source": "manual"
}
```

### Delete Job
```
DELETE /api/jobs/1
```

### Get Statistics
```
GET /api/stats
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "total_jobs": 42,
        "jobs_today": 8,
        "unique_companies": 15,
        "by_source": {
            "linkedin": 18,
            "indeed": 12,
            "naukri": 10,
            "manual": 2
        }
    }
}
```

### Trigger Scraping
```bash
POST /api/scrape
Content-Type: application/json

{
    "platform": "all"        // or "linkedin", "indeed", "naukri"
}
```

### Trigger Email Alert
```
POST /api/email
```

### Scheduler Status
```
GET /api/scheduler/status
```

---

## 📸 Example Output

### Dashboard
- Modern glassmorphism dark theme
- 4 animated statistics cards (Total Jobs, Added Today, Companies, Sources)
- Filterable job table with company avatars and source badges
- One-click "Apply" links and manual job entry modal

### Email Alert
- Professional HTML email with gradient header
- Tabular job listings with "Apply" buttons
- Source-colored badges per platform
- Automated daily at 9 AM

### Scraper Console Output
```
============================================================
  AutoHire AI - Starting Full Scraping Pipeline
============================================================

==================================================
[SCRAPER] Starting LINKEDIN scraper
[SCRAPER] Role: Software Engineer | Location: India
==================================================
[SCRAPER] Chrome WebDriver initialized successfully
[LinkedIn] Navigating to: https://www.linkedin.com/jobs/search/...
[LinkedIn] Found 25 job cards
[DB] Inserted 18 new jobs out of 25 scraped
[SCRAPER] LINKEDIN: Found 25 jobs, added 18 new

============================================================
  Scraping Complete! Total jobs found: 65
============================================================
```

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     AutoHire AI                         │
├──────────┬────────────┬──────────────┬──────────────────┤
│          │            │              │                  │
│  Flask   │  Selenium  │  APScheduler │  Email Service   │
│  Server  │  Scrapers  │  (Cron Jobs) │  (SMTP/Gmail)    │
│          │            │              │                  │
│  Routes  │  LinkedIn  │  Scrape Job  │  HTML Templates  │
│  API     │  Indeed    │  (12 hours)  │  Send via SMTP   │
│  Templates│ Naukri    │  Email Job   │  Track Status    │
│          │            │  (Daily 9AM) │                  │
├──────────┴────────────┴──────────────┴──────────────────┤
│                  Database Manager                       │
│              (MySQL + CRUD + Logging)                   │
├─────────────────────────────────────────────────────────┤
│                    MySQL Database                       │
│    job_listings  |  scrape_logs  |  email_logs          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 OOP Design Patterns Used

| Pattern | Implementation |
|---------|---------------|
| **Abstract Base Class** | `BaseScraper` defines scraping interface |
| **Template Method** | `run()` method in BaseScraper orchestrates pipeline |
| **Strategy Pattern** | Platform-specific scrapers are interchangeable |
| **Facade Pattern** | `JobScraperManager` simplifies multi-scraper orchestration |
| **Singleton-like** | `Config` class centralizes all settings |

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ by <strong>AutoHire AI</strong>
</p>
