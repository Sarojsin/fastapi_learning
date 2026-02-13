# Day 6 - Setup Guide

## Table of Contents
1. [Install PostgreSQL](#1-install-postgresql)
2. [Create Database](#2-create-database)
3. [Install pgAdmin (Optional)](#3-install-pgadmin-optional)
4. [Install Python Dependencies](#4-install-python-dependencies)
5. [Configure Database Connection](#5-configure-database-connection)
6. [Run the Application](#6-run-the-application)
7. [Test the API](#7-test-the-api)

---

## 1. Install PostgreSQL

### Windows
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer (postgres-**-windows-x64.exe)
3. Follow the installation wizard:
   - **Installation Directory**: Keep default
   - **Password**: Set a strong password (remember it!)
   - **Port**: Keep default (5432)
   - **Locale**: Keep default
4. Click "Next" until installation completes
5. Uncheck "Stack Builder" and click "Finish"

### macOS
```bash
# Using Homebrew
brew install postgresql

# Start PostgreSQL service
brew services start postgresql

# Verify installation
psql --version
```

### Linux (Ubuntu/Debian)
```bash
# Update packages
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

---

## 2. Create Database

### Option A: Using pgAdmin (GUI)
1. Open pgAdmin in your browser: http://localhost:5050
2. Login with your pgAdmin password
3. Right-click "Databases" → "Create" → "Database..."
4. Enter:
   - **Database name**: `school`
   - **Owner**: `postgres`
5. Click "Save"

### Option B: Using psql (Command Line)

**Windows:**
1. Open "SQL Shell (psql)" from Start Menu
2. Press Enter to accept defaults (localhost, port 5432, database postgres)
3. Enter the password you set during installation
4. Run:
   ```sql
   CREATE DATABASE school;
   ```

**macOS/Linux:**
```bash
# Switch to postgres user
sudo -i -u postgres

# Open psql
psql

# Create database
CREATE DATABASE school;

# Exit
\q
```
### Option c: Using VSCode Terminal (Recommended)

You can create the database directly from VSCode terminal using the `createdb` command:

```bash
# Make sure PostgreSQL is running and in your PATH
# Create database
createdb day6_db -U postgres

# Enter your PostgreSQL password when prompted
```

**Alternative using psql directly in terminal:**

```bash
# Create database using psql command
psql -U postgres -c "CREATE DATABASE day6_db;"

# Verify database was created
psql -U postgres -l
```

**Note:** If `psql` is not recognized, you need to add PostgreSQL to your system PATH:
1. Find your PostgreSQL installation directory (usually `C:\Program Files\PostgreSQL\<version>\bin`)
2. Add this path to your system Environment Variables
3. Restart VSCode terminal

## 3. Install pgAdmin (Optional)

pgAdmin is a web-based administration tool for PostgreSQL.

### Windows/macOS/Linux
1. Download from: https://www.pgadmin.org/download/
2. Run the installer
3. Open browser and go to: http://localhost:5050
4. Set a master password
5. Add your PostgreSQL server:
   - Right-click "Servers" → "Create" → "Server..."
   - **Name**: Local PostgreSQL
   - **Host**: localhost
   - **Port**: 5432
   - **Username**: postgres
   - **Password**: Your PostgreSQL password

---

## 4. Install Python Dependencies

### Create Virtual Environment (Recommended)
```bash
# Navigate to your project directory
cd e:/backend\ concepts/fastapi_30days/basic1

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r day6/requirements.txt
```

### Install Dependencies Manually
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic
```

---

## 5. Configure Database Connection

Edit [`database.py`](database.py) and update the connection string:

```python
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/school"
```

**Replace:**
- `postgres`: Your PostgreSQL username
- `password`: Your PostgreSQL password
- `school`: Your database name

**Format:**
```
postgresql://username:password@host:port/database_name
```

---

## 6. Run the Application

### Using Uvicorn (Recommended)
```bash
cd e:/backend\ concepts/fastapi_30days/basic1

# Activate virtual environment
.venv\Scripts\activate

# Run the application
uvicorn day6.main:app --reload --host 0.0.0.0 --port 8000
```

### Using Python Directly
```bash
cd e:/backend\ concepts/fastapi_30days/basic1
.venv\Scripts\activate
python -m day6.main
```

### Verify Server is Running
- Open browser: http://localhost:8000
- You should see: `{"message":"Welcome to Day 6 - Database Basics + PostgreSQL"}`

### View API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 7. Test the API

### Using Swagger UI (Recommended)
1. Open http://localhost:8000/docs
2. Expand "POST /api/students"
3. Click "Try it out"
4. Enter student data:
   ```json
   {
     "name": "John Doe",
     "email": "john@example.com",
     "age": 20
   }
   ```
5. Click "Execute"
6. Copy the response (includes student ID)

### Using cURL
```bash
# Create a student
curl -X 'POST' \
  'http://localhost:8000/api/students' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 20
}'

# Get all students
curl -X 'GET' 'http://localhost:8000/api/students'

# Get student by ID
curl -X 'GET' 'http://localhost:8000/api/students/1'

# Update student
curl -X 'PUT' \
  'http://localhost:8000/api/students/1' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "John Updated",
  "age": 21
}'

# Delete student
curl -X 'DELETE' 'http://localhost:8000/api/students/1'
```

### Using Python (Requests)
```python
import requests

BASE_URL = "http://localhost:8000/api"

# Create student
response = requests.post(f"{BASE_URL}/students", json={
    "name": "John Doe",
    "email": "john@example.com",
    "age": 20
})
print(response.json())

# Get all students
response = requests.get(f"{BASE_URL}/students")
print(response.json())
```

---

## Troubleshooting

### 🚨 "database 'day6_db' does not exist" Error

**Error Message:**
```
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed: FATAL:  database "day6_db" does not exist
```

**What this means:**
Your application is trying to connect to a database named `day6_db` but it hasn't been created in PostgreSQL yet.

**Solution:**

1. **Open SQL Shell (psql):**
   - Search for "SQL Shell (psql)" in Windows Start Menu
   - Press Enter to accept all defaults (localhost, 5432, postgres)
   - Enter your PostgreSQL password

2. **Create the database:**
   ```sql
   CREATE DATABASE day6_db;
   ```

3. **Exit psql:**
   ```sql
   \q
   ```

4. **Run the app again:**
   ```bash
   uvicorn day6.main:app --reload
   ```

**Alternative - Using pgAdmin:**
1. Open http://localhost:5050 in your browser
2. Login with your pgAdmin password
3. Expand "Servers" → "PostgreSQL"
4. Right-click "Databases" → "Create" → "Database..."
5. Enter:
   - **Database name**: `day6_db`
   - **Owner**: `postgres`
6. Click "Save"

---

### "Connection refused" Error
- PostgreSQL service not running
- Wrong host/port in connection string
- Firewall blocking connection

### "password authentication failed" Error
- Wrong username or password
- Check pg_hba.conf for authentication settings

### "database 'school' does not exist"
- Create the database first (Step 2)
- Check database name in connection string

### "ModuleNotFoundError: No module named 'sqlalchemy'"
- Install dependencies (Step 4)
- Activate virtual environment

### Port 8000 already in use
- Stop other processes using port 8000
- Or run on different port: `--port 8001`

---

## Quick Reference Commands

```bash
# Start PostgreSQL
# Windows: Service manager or pgAdmin
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Create database
psql -U postgres -c "CREATE DATABASE school;"

# List databases
psql -U postgres -l

# Connect to database
psql -U postgres -d school

# Run FastAPI
uvicorn day6.main:app --reload

# Access API docs
# http://localhost:8000/docs
```

---

## What's Next?

After setup, explore:
1. Read [`README.md`](README.md) for database concepts
2. Try all API endpoints in Swagger UI
3. Practice SQL commands in pgAdmin
4. Modify the code to add new features
