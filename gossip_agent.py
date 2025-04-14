import psycopg2
import time
from datetime import datetime

# Map logical node IDs to actual PostgreSQL database names
nodes = {
    "prod": "gsp_prod",
    "dr1": "gsp_1",
    "dr2": "gsp_2",
    "dr3": "gsp_3"
}

MAX_LOAD_RECORDS = 10  # Maximum number of rows representing 100% load


def update_load(dbname):
    """
    Connects to a PostgreSQL DB, calculates current load, and updates node_state.
    Returns a dictionary with node_id and load percentage.
    """
    conn = psycopg2.connect(dbname=dbname, user="postgres", host="localhost")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM sensor_data;")
    count = cur.fetchone()[0]
    load = min((count / MAX_LOAD_RECORDS) * 100, 100)

    cur.execute("SELECT node_id FROM node_state;")
    node_id = cur.fetchone()[0]

    cur.execute("""
        UPDATE node_state
        SET load_percent = %s, last_updated = CURRENT_TIMESTAMP
        WHERE node_id = %s;
    """, (load, node_id))
    conn.commit()

    cur.close()
    conn.close()

    return {"node_id": node_id, "load": load}


def gossip_decision(all_nodes):
    """
    Checks if the current active target is overloaded (>80%).
    If so, redirects future inserts to a new underloaded node (<20%).
    Otherwise, does nothing.
    """
    # Load current active target from file
    try:
        with open("active_target.txt", "r") as f:
            current_target_db = f.read().strip()
    except FileNotFoundError:
        current_target_db = "gsp_prod"

    # Resolve node_id from database name
    current_target_node = None
    for node_id, db in nodes.items():
        if db == current_target_db:
            current_target_node = node_id
            break

    # Get the load of the current target
    target_state = next((n for n in all_nodes if n["node_id"] == current_target_node), None)
    if not target_state:
        print(" → ERROR: Current target not found in node list.")
        return

    if target_state["load"] < 80.0:
        print(f" → Current target {current_target_node.upper()} is stable ({target_state['load']:.1f}%). No change.")
        return

    # Current target is overloaded, we need to redirect
    print(f"[GOSSIP] {current_target_node} is overloaded ({target_state['load']}%).")

    # Find other nodes that are truly underloaded
    candidates = [
        node for node in all_nodes
        if node["node_id"] != current_target_node and node["load"] < 20.0
    ]

    if not candidates:
        print(" → No suitable underloaded node found. Staying with current.")
        return

    # Pick the first suitable node
    new_node = candidates[0]
    new_db = nodes[new_node["node_id"]]

    with open("active_target.txt", "w") as f:
        f.write(new_db)

    print(f" → Redirecting future inserts to: {new_node['node_id'].upper()} ({new_db})")


def main_loop():
    """
    Main loop: every second, updates all loads and triggers gossip logic.
    """
    print("\n[INFO] Starting Gossip Monitoring...\n")

    while True:
        print(f"\n[{datetime.now()}] Checking node states...")

        all_states = []

        # Get updated load info for each node
        for node_id, dbname in nodes.items():
            state = update_load(dbname)
            all_states.append(state)
            print(f"{node_id.upper()} Load: {state['load']:.1f}%")

        # Gossip logic: should we change write target?
        gossip_decision(all_states)

        time.sleep(1)


if __name__ == "__main__":
    main_loop()
