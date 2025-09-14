# 🏠 Zimmo Airflow Scraper

### Because Data Collection Should (Not) Feel Like Burning in Red (Taylor's Version)

![red](https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExeWwzanJpemYyN2o3aWVldDNiNmI4bjBxcXJzY214bHN4bWFzMnducyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xUPN3cuPESDoHHBuog/giphy.gif)

_for those who get the reference ;)_

---

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-3.0+-red.svg)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=flat&logo=postgresql&logoColor=white)
![Status](https://img.shields.io/badge/status-burning%20red-ff0000.svg)

## 🎵 The Story Behind This Project

This is an **extension** of my original [Zimmo scraping project](https://github.com/jgchoti/challenge-collecting-data), now orchestrated with Apache Airflow. As a **first-timer with Airflow**, I've learned that:

- Setting up workflows can be challenging, much like solving a complex puzzle with no clear solution.
- Debugging Docker containers often requires understanding unfamiliar systems and interactions.
- But when everything runs smoothly, it delivers clean, structured data efficiently and reliably.

## 🌟 What This Project Does

**Zimmo Airflow Scraper** extracts Belgian real estate data from zimmo.be using:

- 🕷️ **Web Scraping**: CloudScraper to bypass protections
- 🐘 **PostgreSQL**: For data storage
- 🌊 **Apache Airflow**: Workflow orchestration
- 🐳 **Docker**: Containerized deployment

![airflow](/assets/airflow.png)

### Features

- **Multi-range price scraping** – Collects data across all property price ranges
- **Automatic retry logic** – Ensures reliable scraping even when network or server issues occur
- **Database conflict handling** – Uses smart upserts to prevent data loss and maintain integrity
- **Error fallback system** – Generates placeholder or sample data when scraping fails

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM and 2 CPUs available for Docker
- 10GB+ disk space

### 1. Clone and Setup

```bash
git clone https://github.com/jgchoti/immoeliza-airflow.git
cd immoeliza-airflow
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.template .env
```

### 3. Essential Configuration

Edit `.env` file with these essential settings:

```bash
# User ID (CRITICAL - prevents permission issues)
AIRFLOW_UID=1000  # Replace with output of: id -u

# Security (REQUIRED)
# Generate with: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
AIRFLOW_FERNET_KEY=your_generated_fernet_key_here

# Credentials (Change in production!)
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow
POSTGRES_PASSWORD=airflow
PGADMIN_DEFAULT_PASSWORD=root

# Performance settings
AIRFLOW_PARALLELISM=8
AIRFLOW_MAX_ACTIVE_TASKS_PER_DAG=4

# Port configuration
AIRFLOW_WEBSERVER_PORT=8080
POSTGRES_PORT=5432
PGLADMIN_PORT=5050

# Additional Python packages
_PIP_ADDITIONAL_REQUIREMENTS=pandas==1.5.0,requests==2.28.0,cloudscraper,beautifulsoup4,psycopg2-binary
```

### 4. Generate Required Keys

```bash
# Set your user ID
echo "AIRFLOW_UID=$(id -u)" >> .env

# Generate Fernet key
python3 -c "from cryptography.fernet import Fernet; print('AIRFLOW_FERNET_KEY=' + Fernet.generate_key().decode())" >> .env
```

### 5. Start Airflow

```bash
# Start all services
docker-compose up -d

# Or start with pgAdmin
docker-compose --profile tools up -d
```

### 6. Initialize Database Schema

```bash
# Wait for services to be healthy (2-3 minutes), then run:
docker exec -i $(docker-compose ps -q postgres) psql -U airflow -d airflow < sql/zimmo_schema.sql
```

## 🌐 Access Points

- **Airflow Web UI**: http://localhost:8080
  - Username: `airflow` | Password: `airflow`
- **pgAdmin** (if started with tools profile): http://localhost:5050
  - Email: `admin@admin.com` | Password: `root`

### Database Connection Details

For connecting to PostgreSQL from external tools or scripts:

- **Host**: `localhost` (external) / `postgres` (internal)
- **Port**: `5432`
- **Database**: `airflow`
- **Username**: `airflow`
- **Password**: `airflow`

## 📁 Project Structure

```
immoeliza-airflow/
├── 🎭 dags/                    # Airflow workflows
├── 🔧 plugins/                 # Custom scrapers & utilities
├── 📜 sql/                     # Database schema files
├── 📊 logs/                    # All the debugging adventures
├── 📝 scripts/                 # ML training & dashboard generation
├── 📋 .env.template            # Environment variables template
├── 🐳 docker-compose.yml       # Container orchestration
└── 📖 README.md               # This file
```

## 🔄 Data Pipeline Flow

```
start_pipeline → check_dependencies → scrape_apartments → scrape_houses → deduplicate_data
                                                                              ↓
                            end_pipeline ← final_summary ← train_regression_model
                                                        ↖ generate_dashboard_data
```

## 🛠️ Common Operations

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f airflow-scheduler
```

### Execute Airflow Commands

```bash
# Access Airflow CLI
docker-compose exec airflow-scheduler bash

# List DAGs
docker-compose exec airflow-scheduler airflow dags list
```

### Troubleshooting

```bash
# Check service status
docker-compose ps

# Reset everything (⚠️ removes all data)
docker-compose down -v
docker-compose up -d
```

## 📝 Future Enhancements

- 📱 **Enhanced Streamlit dashboard**: More interactive features and real-time updates
- 🤖 **Advanced ML models**: Deep learning for better price predictions
- 📧 **Alert system**: Get notified when scraping hits those green success notes
- 🔄 **Incremental updates**: Smart scraping of only new/changed listings
- ⚡ **Parallel scraping**: Ability to run both house and apartment scrapers in parallel (currently limited by local machine resources)

## 🙏 Acknowledgments

- **Taylor Swift** - For the emotional inspiration behind this README
- **Apache Airflow Community** - For making workflow orchestration feel less impossible
- **zimmo.be** - For having data worth scraping (and for not blocking me... yet)
- **My Future Self** – The data engineer version of me who will finally understand this first-ever Airflow project better
- **Airflow Errors** – For teaching patience, persistence, and the true meaning of "retry"

---

## 📊 Demo Dashboard

[Visit Demo Dashboard](https://immo-be.streamlit.app/)
![dashboard](/assets/immo-dashboard.png)

---
