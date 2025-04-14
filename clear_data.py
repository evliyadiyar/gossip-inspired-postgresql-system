import psycopg2

# 🔗 Mapping of node names to their PostgreSQL database names
databases = {
    "prod": "gsp_prod",
    "dr1": "gsp_1",
    "dr2": "gsp_2",
    "dr3": "gsp_3"
}

def clear_sensor_data_all():
    """
    Connects to each database listed in `databases` and deletes all rows
    from the `sensor_data` table. Table structure and other data remain intact.
    """
    for node_id, dbname in databases.items():
        try:
            # Connect to the target PostgreSQL database
            conn = psycopg2.connect(dbname=dbname, user="postgres", host="localhost")
            cur = conn.cursor()

            # Delete all rows from sensor_data
            cur.execute("DELETE FROM sensor_data;")
            conn.commit()

            print(f"[{dbname}] ✅ All rows in 'sensor_data' have been deleted.")

            cur.close()
            conn.close()

        except Exception as e:
            print(f"[{dbname}] ❌ Error clearing sensor_data: {e}")

if __name__ == "__main__":
    clear_sensor_data_all()
