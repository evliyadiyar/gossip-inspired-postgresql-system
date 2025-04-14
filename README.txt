📌 Project Summary
This simulation demonstrates how a gossip-inspired decision mechanism can dynamically redirect incoming data inserts across multiple PostgreSQL databases, mimicking a realistic disaster recovery scenario.
The system consists of:

1 production database (gsp_prod)

3 disaster recovery nodes (gsp_1, gsp_2, gsp_3)

A gossip agent that monitors the system and controls data routing

A data simulator that inserts fake sensor data

⚙️ Requirements
PostgreSQL 12+ (already pre-installed in GitHub Codespaces)

Python 3.7+

psycopg2: install with:

bash
Copy
Edit
pip install psycopg2
📦 Setup (First-time only)
1. Start PostgreSQL (if not already running)
bash
Copy
Edit
sudo service postgresql start
2. Create required databases
sql
Copy
Edit
-- From any terminal:
sudo -u postgres psql

-- Then in PostgreSQL shell:
CREATE DATABASE gsp_prod;
CREATE DATABASE gsp_1;
CREATE DATABASE gsp_2;
CREATE DATABASE gsp_3;
\q
3. Apply schema to all databases (run once for each)
Each DB should contain:

A table: sensor_data(sensor_id INT, value FLOAT, created_at TIMESTAMP)

A table: node_state(node_id TEXT PRIMARY KEY, load_percent FLOAT, last_updated TIMESTAMP)

Use this inside each DB (change DB name in the connection):

bash
Copy
Edit
psql -U postgres -d gsp_prod -h localhost
-- or gsp_1, gsp_2, gsp_3
sql
Copy
Edit
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

-- Insert initial node ID
INSERT INTO node_state VALUES ('prod', 0, CURRENT_TIMESTAMP);  -- for gsp_prod
-- Use 'dr1', 'dr2', 'dr3' for others respectively
Repeat this setup for each database (with matching node_id values).

▶️ How to Run the Project
1. Set initial insert target
bash
Copy
Edit
echo "gsp_prod" > active_target.txt
2. Run the gossip agent (monitor and decision logic)
Keep this running in one terminal tab

bash
Copy
Edit
python gossip_agent.py
This script checks all databases every second, evaluates current loads, and updates active_target.txt if the current write target exceeds 80% load.

3. Run the data simulator
In a separate terminal tab

bash
Copy
Edit
python simulate_data.py
This script inserts random sensor data into the current active database, as defined in active_target.txt, every 2 seconds.
Each DB can hold up to 10 rows (100% load), simulating capacity constraints.

🔁 Optional: Reset for New Run
If you want to reset the simulation:

bash
Copy
Edit
python clear_data.py
This will clear sensor_data from all databases.

💡 Notes
Insert direction will not change unless the current target exceeds 80% load

Targets are only redirected to nodes under 20% load

No data is moved or migrated — this is a write redirection mechanism only

Gossip agent behaves reactively — no centralized control beyond monitoring

🧪 Sample Output
bash
Copy
Edit
[2025-04-13 23:12:01] Checking node states...
PROD Load: 90.0%
DR1 Load: 10.0%
DR2 Load: 0.0%
 → Current target DR1 is stable (10.0%). No change.

[2025-04-13 23:12:12] Checking node states...
DR1 Load: 80.0%
 → Current target DR1 is stable (80.0%). No change.

[2025-04-13 23:12:14] Checking node states...
DR1 Load: 100.0%
[GOSSIP] dr1 is overloaded (100.0%).
 → Redirecting future inserts to: DR2 (gsp_2)
Enjoy exploring decentralized write routing!
This setup mimics real-world load distribution decisions using a gossip-style adaptive strategy.

