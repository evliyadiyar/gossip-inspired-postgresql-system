import psycopg2
import time
import random

def get_target_db():
    # Read target DB name from shared file
    try:
        with open("active_target.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "gsp_prod"  # fallback to prod if file not found

def insert_sensor_data():
    while True:
        db_name = get_target_db()

        conn = psycopg2.connect(dbname=db_name, user="postgres", host="localhost")
        cur = conn.cursor()

        # Optional: cap total inserts to avoid flooding
        cur.execute("SELECT COUNT(*) FROM sensor_data;")
        count = cur.fetchone()[0]

        if count < 10:
            sensor_id = random.randint(1, 5)
            value = round(random.uniform(20, 40), 2)

            cur.execute(
                "INSERT INTO sensor_data (sensor_id, value) VALUES (%s, %s);",
                (sensor_id, value)
            )
            conn.commit()

            print(f"[{db_name}] Wrote 1 row (total: {count + 1})")
        else:
            print(f"[{db_name}] Load limit reached. Waiting...")

        cur.close()
        conn.close()
        time.sleep(1)

if __name__ == "__main__":
    insert_sensor_data()
