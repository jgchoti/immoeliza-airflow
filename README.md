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
![First Timer](https://img.shields.io/badge/airflow-first%20timer-orange.svg)

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

### Features

- Multi-range price scraping – Collects data across all property price ranges.
- Automatic retry logic – Ensures reliable scraping even when network or server issues occur.
- Database conflict handling – Uses smart upserts to prevent data loss and maintain integrity.
- Error fallback system – Generates placeholder or sample data when scraping fails.

## 🚀 Quick Start

```bash

git clone https://github.com/jgchoti/immoeliza-airflow.git
cd immoeliza-airflow

# Start the Airflow
docker-compose up -d

# Access Airflow UI: http://localhost:8080
# Username: airflow | Password: airflow
```

**Initialize the Database Schema:**

```bash
docker exec -i immoeliza-airflow-postgres-1 psql -U airflow -d airflow < sql/zimmo_schema.sql
```

**Access pgAdmin:**

URL: `http://localhost:5050`
Login: `admin@admin.com / root`

**Server Connection Details:**

Host: `postgres`
Port:`5432`
Database: `airflow`
Username / Password: `airflow / airflow`

**Database Connection Info (for Airflow & Scripts)**

Host: `postgres`
Port: `5432`
Database: `airflow`
Username / Password: `airflow / airflow`

## 📁 Project Structure

```
immoeliza-airflow/
├── 🎭 dags/                    # Airflow workflows
├── 🔧 plugins/                 # Custom scrapers & utilities
├── 📜 sql/                     # Database schema files
├── 📊 logs/                    # All the debugging adventures
├── 📝 scripts/                 # ML training & dashboard generation
└── 🐳 docker-compose.yml       # Container orchestration
```

### Data Pipeline Flow:

```
start_pipeline → check_dependencies → scrape_apartments → scrape_houses → deduplicate_data
                                                                              ↓
                            end_pipeline ← final_summary ← train_regression_model
                                                        ↖ generate_dashboard_data
```

## 🐛 Troubleshooting Common Issues

### Connection timeouts

- Increase retry attempts
- Add exponential backoff
- Check Docker network settings

## 📈 Performance Metrics

When everything works perfectly:

- **Properties per minute**: ~50-100 (depending on zimmo.be mood)
- **Success rate**: 85-95% (those SSL errors though...)
- **Data accuracy**: 99.9% (thanks to robust cleaning)

## 📝 Future Enhancements

- 📱 **Enhanced Streamlit dashboard**: More interactive features and real-time updates
- 🤖 **Advanced ML models**: Deep learning for better price predictions
- 📧 **Alert system**: Get notified when scraping hits those green success notes
- 🔄 **Incremental updates**: Smart scraping of only new/changed listings
- ⚡ **Parallel scraping** – Ability to run both house and apartment scrapers in parallel(currently limited by local machine resources).

## 🙏 Acknowledgments

- **Taylor Swift** - For the emotional inspiration behind this README
- **Apache Airflow Community** - For making workflow orchestration feel less impossible
- **zimmo.be** - For having data worth scraping (and for not blocking me... yet)
- **My Future Self** – The data engineer version of me who will finally understand this first-ever Airflow project better
- **Airflow Errors** – For teaching patience, persistence, and the true meaning of “retry.”

---

## 📊 Demo Dashboard

[Visit Demo Dashboard]()
