import psycopg2

nodes = {
    "prod": "gsp_prod",
    "dr1": "gsp_1",
    "dr2": "gsp_2",
    "dr3": "gsp_3"
}

def fetch_node_state(dbname, node_id):
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user="postgres",
            host="localhost"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT node_id, load_percent, avg_value, last_updated FROM node_state;")
        row = cursor.fetchone()
        print(f"{node_id.upper()} → Load: {row[1]}%, Avg: {row[2]}, Updated: {row[3]}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting to {dbname}: {e}")

for node_id, db in nodes.items():
    fetch_node_state(db, node_id)
