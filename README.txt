# 🛰️ Gossip-Based Disaster Recovery Simulation

This project simulates a **gossip-inspired decision mechanism** for dynamically redirecting data inserts across multiple PostgreSQL databases.

The goal is to mimic a realistic **disaster recovery scenario** with lightweight, decentralized load balancing and failover behavior.

## System Components

- 🛠️ 1 production database: `gsp_prod`  
- 💾 3 disaster recovery nodes: `gsp_1`, `gsp_2`, `gsp_3`  
- 🗣️ Gossip agent: monitors node load and routes inserts  
- 🧪 Data simulator: sends fake sensor data to the active database

## ⚙️ Requirements

- PostgreSQL 12 or higher (pre-installed in GitHub Codespaces)
- Python 3.7 or higher
- Python packages:
  ```bash
  pip install psycopg2

## 📦 Setup (First-time only)

### 1. Start PostgreSQL

If PostgreSQL is not already running, start the service:

  ```bash
  sudo service postgresql start
  ```

  
### 2. Create Required Databases

Enter the PostgreSQL shell:


```bash
sudo -u postgres psql

CREATE DATABASE gsp_prod;
CREATE DATABASE gsp_1;
CREATE DATABASE gsp_2;
CREATE DATABASE gsp_3;
```
Each database should include:

```bash
CREATE TABLE sensor_data (
    sensor_id INT,
    value FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE node_state (
    node_id TEXT PRIMARY KEY,
    load_percent FLOAT,
    last_updated TIMESTAMP
);

```

### 3. Insert initial node_state for each DB

For gsp_prod:
```
INSERT INTO node_state VALUES ('prod', 0, CURRENT_TIMESTAMP);
```
For gsp_1, gsp_2, gsp_3:
```
INSERT INTO node_state VALUES ('dr1', 0, CURRENT_TIMESTAMP);  -- gsp_1
INSERT INTO node_state VALUES ('dr2', 0, CURRENT_TIMESTAMP);  -- gsp_2
INSERT INTO node_state VALUES ('dr3', 0, CURRENT_TIMESTAMP);  -- gsp_3
```

## ▶️ How to Run the Project

### 1. Set the Initial Insert Target

```bash
echo "gsp_prod" > active_target.txt
```

### 2. Run the Gossip Agent
Start the gossip agent in one terminal. It monitors all databases and updates active_target.txt if the current target becomes overloaded (>80%).

```
python gossip_agent.py
```
Checks node states every second and redirects future inserts if needed.

### 3. Run the Data Simulator
In another terminal, start simulating sensor data inserts:

```
python simulate_data.py
```
Sends fake sensor data every 2 seconds to the database listed in active_target.txt.

### 🔁 Optional: Reset for New Run
To clear all sensor data from all databases:

```
python clear_data.py
```

