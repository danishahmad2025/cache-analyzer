# 🏥 Medicare Claims — Cache Performance Analyzer

A data engineering project I built to understand **how caching works** and **how much faster Redis is compared to PostgreSQL** when running real queries on a large dataset.

I used real US Medicare hospital claims data (146,000+ rows) to run the benchmark (test + compare) .
---

##  Why I Built This

When I started learning data engineering, I kept hearing the word **cache** but never really understood what it did or why it mattered. So I decided to build something that would show me the difference — visually, with real numbers, on real data.

This project answered my own questions:
- What actually happens when data is cached?
- How much faster is it — really?
- What does a cache hit and a cache miss look like in practice?

---

## What I Learned Building This

- What a **cache** is and how it works step by step
- How to connect Python to a real **PostgreSQL** database
- How to use **Redis** as a caching layer on top of a database
- How to load and clean a large real-world **CSV dataset** using Pandas
- How to write real **SQL queries** that answer business-style questions
- How to **benchmark** two systems (measure their speed and compare)
- How to build a **multi-panel chart** in Matplotlib to visualize results
- How to structure a Python project with multiple files properly
- How to use **virtual environments** and **Git** for version control

---

## 📊 The Dataset

**Name:** Medicare Inpatient Hospitals by Provider and Service  
**Source:** [data.cms.gov](https://data.cms.gov) — US Government open data, free and public  
**Size:** ~38MB, 146,427 rows after cleaning

This is real US hospital billing data. It shows which medical procedures were performed at hospitals across every US state, how many patients were treated, what the hospitals charged, and what Medicare actually paid.

I chose this dataset because it is large enough to make the cache vs database speed difference very visible, it is messy and realistic (has missing values that need cleaning), and it contains the kind of data that real healthcare data engineering roles work with.

### Columns I used:

| Column | What it means |
|---|---|
| `Rndrng_Prvdr_State_Abrvtn` | US state where the hospital is |
| `DRG_Desc` | Name of the medical procedure |
| `Tot_Dschrgs` | Number of patients discharged |
| `Avg_Submtd_Cvrd_Chrg` | What the hospital billed on average |
| `Avg_Mdcr_Pymt_Amt` | What Medicare actually paid on average |

---

## 🗂️ Project Structure

```
cache_project/
│
├── config.py           → Connection settings for PostgreSQL and Redis
├── db_setup.py         → Loads and cleans the CSV, saves into PostgreSQL
├── cache.py            → Redis logic: get, set, and clear cache
├── queries.py          → SQL queries I run against the database
├── benchmark.py        → Runs queries with and without cache, records time
├── visualize.py        → Builds the comparison chart
├── main.py             → Runs everything in order
│
├── medicare_claims.csv → The real dataset (downloaded from CMS.gov)
└── results.png         → The output chart (generated after running main.py)
```

---

## 📁 What Each File Does

### `config.py` — Settings
Stores the PostgreSQL and Redis connection details in one place. Every other file reads from here. This way if anything changes, I only need to update one file.

---

### `db_setup.py` — Data Loader
This was my first real experience loading a large dataset into a production-grade database. It does three things:

1. Reads the raw CSV using Pandas
2. Cleans it — drops rows with missing billing values, fixes data types
3. Bulk-loads all 146,427 cleaned rows into PostgreSQL using the `COPY` command (the fastest way to insert large amounts of data)

---

### `cache.py` — Redis Layer
Three simple functions that handle everything cache-related:

| Function | What it does |
|---|---|
| `get_from_cache(key)` | Check if an answer already exists in Redis |
| `set_in_cache(key, value, ttl)` | Save an answer into Redis with an expiry time |
| `flush_cache()` | Wipe Redis clean for a fresh benchmark |

I also had to handle a real bug here — PostgreSQL returns `Decimal` type numbers which JSON cannot serialize. I built a custom `DecimalEncoder` to convert them to floats before storing in Redis.

---

### `queries.py` — The SQL Questions
I wrote two queries that represent real analytical questions on healthcare data:

**Query 1 — Top procedures by state**
> Which medical procedures are most commonly billed in a given US state, and what is the average amount billed vs paid?

**Query 2 — Billing gap by state**
> How large is the gap between what hospitals charge and what Medicare actually pays, for a given state?

These are slow aggregation queries — they scan thousands of rows, group them, and average them. This is exactly the kind of query where caching gives the biggest benefit.

---

### `benchmark.py` — The Speed Test
This is the core of the project. I run the same queries in two ways:

**Without cache:** Every query goes directly to PostgreSQL. No shortcuts.

**With cache:** Before hitting the database, check Redis first.
- If the answer is there → return it instantly (cache hit ✅)
- If not → go to the database, get the answer, save it in Redis (cache miss ⚠️)

I tested 10 US states × 5 repetitions each = 50 queries per method. The first query for each state is always a miss. Queries 2 through 5 for the same state are hits.

---

### `visualize.py` — The Chart
I built a 4-panel chart saved as `results.png`:

| Panel | What it shows |
|---|---|
| **Line chart** | Every query's response time. Blue = database, green = cache. Orange shading = cache miss, green shading = cache hit |
| **Bar chart** | Average response time comparison side by side |
| **Speedup gauge** | How many times faster the cache was (e.g. 120x faster) |
| **Pie chart** | Percentage of queries that were cache hits vs misses |

---

### `main.py` — Entry Point
Ties everything together. Running `python main.py` triggers all steps in order:

```
1. Load CSV into PostgreSQL
2. Clear Redis (clean start)
3. Run the benchmark
4. Draw and save the chart
```

---

## ⚙️ How to Run It

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/cache-analyzer.git
cd cache-analyzer
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL
```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE medicare_cache_db;
CREATE USER medicare_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE medicare_cache_db TO medicare_user;
\q

sudo -u postgres psql -d medicare_cache_db
GRANT ALL ON SCHEMA public TO medicare_user;
\q
```

### 5. Download the dataset
Go to [data.cms.gov](https://data.cms.gov), search **"Medicare Inpatient Hospitals by Provider and Service"**, export as CSV, rename to `medicare_claims.csv`, and place it in the project folder.

### 6. Update config.py
Set your PostgreSQL password in `config.py`.

### 7. Start Redis
```bash
sudo service redis-server start
redis-cli ping    # should reply: PONG
```

### 8. Run
```bash
python main.py
```

---

## 📈 Sample Output

```
=== Medicare Claims Cache Analyzer ===
Dataset: US Medicare Inpatient Hospital Claims

Table and index created.
Reading Medicare CSV file...
Cleaned data: 146,427 rows ready to insert.
Inserted 146,427 rows into PostgreSQL.
Cache flushed.
Running benchmark on 10 US states x 5 repetitions each...

Chart saved as results.png
Cache hit rate : 80%
Avg DB time    : 45.23 ms
Avg cache time : 0.31 ms
Speedup        : 145.9x faster
```

---

## 🔑 Concepts This Project Covers

### Cache
A temporary storage layer that saves the result of a slow operation so the next request can get it instantly without repeating the work.

### Cache Hit
The answer was already in Redis — returned in under 1ms. No database involved.

### Cache Miss
The answer was not in Redis yet — had to go to PostgreSQL, get the result, then save it in Redis for next time.

### TTL (Time To Live)
Every cached result has a timer. After 300 seconds (5 minutes), it auto-deletes. The next request causes a miss and fetches fresh data. This prevents outdated answers from living in cache forever.

### Cache-Aside Pattern
The pattern I implemented: check cache first → if miss, query database → store result in cache → return result. This is the most common caching pattern in real data systems.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.14 | Main language |
| PostgreSQL | Permanent database storage |
| Redis | In-memory cache layer |
| Pandas | CSV reading and cleaning |
| psycopg2 | Python → PostgreSQL connection |
| redis-py | Python → Redis connection |
| Matplotlib | Chart generation |

---

## 📋 Dependencies

```
pandas
psycopg2-binary
redis
matplotlib
faker
```

Install with:
```bash
pip install -r requirements.txt
```

---

## 👤 About

**Danish Ekbal Ahmad**  
Learning data engineering | Kathmandu, Nepal  
This is one of my portfolio projects built while learning how real data pipelines and caching systems work.

## 📄 License

This project is open source. The Medicare dataset is public domain, provided by the US Centers for Medicare & Medicaid Services (CMS).