# Reconciliation System Setup Guide

This guide will walk you through setting up and running the reconciliation data import system, which processes Geneva and Custodian Bank CSV files and loads them into a PostgreSQL database.

## Prerequisites

Before starting, ensure you have the following installed on your system:

- **Python 3.8+**: Required to run the import scripts
- **Docker & Docker Compose**: Required to run the database services
- **Git**: For cloning the repository (optional)

## Step-by-Step Installation Guide

### 1. Install Python (if not already installed)

#### Windows:
1. Download the latest Python installer from [python.org](https://www.python.org/downloads/windows/)
2. Run the installer
3. Make sure to check ✅ "Add Python to PATH" during installation
4. Verify installation by opening Command Prompt and typing: `python --version`

#### macOS:
1. Download the latest Python installer from [python.org](https://www.python.org/downloads/mac-osx/)
2. Run the installer and follow the prompts
3. Verify installation by opening Terminal and typing: `python3 --version`

#### Linux:
1. Most Linux distributions come with Python pre-installed
2. If not, use your package manager:
   ```
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   
   # Fedora
   sudo dnf install python3 python3-pip python3-venv
   ```
3. Verify with: `python3 --version`

### 2. Install Docker & Docker Compose

#### Windows:
1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Run the installer and follow the prompts
3. Docker Compose comes bundled with Docker Desktop

#### macOS:
1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Run the installer and follow the prompts
3. Docker Compose comes bundled with Docker Desktop

#### Linux:
1. Follow the [official Docker installation guide](https://docs.docker.com/engine/install/)
2. Install Docker Compose following the [compose installation guide](https://docs.docker.com/compose/install/)

### 3. Set Up the Project

1. Create a new folder for your project:
   ```
   mkdir reconciliation-system
   cd reconciliation-system
   ```

2. Download or copy all project files into this folder:
   - `custodian_bank-03-06.sql` - Database schema for custodian bank table
   - `geneva-03-06.sql` - Database schema for geneva table
   - `excel_to_postgres.py` - Import script
   - `docker-compose.yml` - Docker services configuration
   - `requirements.txt` - Python dependencies
   - CSV files:
     - `GVA Cash ledger.csv` - Geneva data
     - `BAnk Cash.csv` - Custodian Bank data

### 4. Create and Set Up Python Virtual Environment

1. Open a terminal/command prompt in your project folder
2. Create a virtual environment:

   **Windows**:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

   **macOS/Linux**:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the System

### 1. Start the Database Services

1. Open a terminal/command prompt in your project folder
2. Start Docker services:
   ```
   docker-compose up -d
   ```
   This will start:
   - PostgreSQL database on port 5433
   - Adminer (database management tool) on port 8080
   - MinIO object storage on ports 9000 (API) and 9001 (Web console)

3. Wait a few moments for the services to initialize

### 2. Initialize the Database Schema

1. With Docker services running, connect to PostgreSQL and create the tables:
   ```
   docker exec -i reco-postgres psql -U reco_user -d reco_db < geneva-03-06.sql
   docker exec -i reco-postgres psql -U reco_user -d reco_db < custodian_bank-03-06.sql
   ```

### 3. Run the Import Script

1. Make sure your virtual environment is active
2. Run the Python script:

   **Windows**:
   ```
   python excel_to_postgres.py
   ```

   **macOS/Linux**:
   ```
   python3 excel_to_postgres.py
   ```

3. The script will:
   - Connect to the PostgreSQL database
   - Read and process the CSV files
   - Import the data into the appropriate tables
   - Display progress and results

## Accessing the Database

### PostgreSQL via Adminer

1. Open a web browser and go to:
   ```
   http://localhost:8080
   ```

2. Log in with these credentials:
   - System: PostgreSQL
   - Server: postgres (the service name in docker-compose)
   - Username: reco_user
   - Password: reco_pass
   - Database: reco_db

3. You can now browse, query, and manage the database tables

### MinIO Object Storage

1. Open a web browser and go to:
   ```
   http://localhost:9001
   ```

2. Log in with these credentials:
   - Username: minioadmin
   - Password: minioadmin

## Troubleshooting

### Docker Issues

1. **Services won't start**:
   - Check if Docker is running
   - Ensure no other services are using the specified ports
   - Run `docker-compose down` and then `docker-compose up -d` again

2. **Cannot connect to database**:
   - Ensure PostgreSQL service is running: `docker ps | grep postgres`
   - Check if you can connect directly: 
     ```
     docker exec -it reco-postgres psql -U reco_user -d reco_db
     ```

### Python Issues

1. **Package installation errors**:
   - Make sure your virtual environment is activated
   - Try upgrading pip: `pip install --upgrade pip`
   - Install `psycopg2-binary` if `psycopg2` fails: `pip install psycopg2-binary`

2. **CSV import errors**:
   - Check CSV file encoding and format
   - Verify the file paths in the script
   - Ensure the column names match between CSV files and the script mappings

## Shutting Down

1. Stop the Docker services when done:
   ```
   docker-compose down
   ```

2. To completely remove all data and start fresh:
   ```
   docker-compose down -v
   ```

## Database Schema Overview

The system uses two main tables:

1. **geneva**: Contains Geneva cash ledger data
2. **custodian_bank**: Contains bank cash data

These tables are used for data reconciliation between the two systems.