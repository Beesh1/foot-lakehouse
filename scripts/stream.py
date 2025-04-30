import duckdb
import sqlite3
import json
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Define the data structure for the incoming scan data
class ScanData(BaseModel):
    customer_id: int
    left_length: float
    left_width: float
    left_girth: float
    left_instep: float
    left_arch_height: float
    right_length: float
    right_width: float
    right_girth: float
    right_instep: float
    right_arch_height: float
    left_pressure: list
    right_pressure: list
    recommendations: dict
    left_depth: str  # Base64-encoded binary data
    right_depth: str  # Base64-encoded binary data

# Initialize FastAPI app (the webhook server)
app = FastAPI()

# Connect to DuckDB and SQLite
conn_duck = duckdb.connect('/app/data/foot.db')
conn_sqlite = sqlite3.connect('/app/data/foot_sqlite.db')

# Create the table in DuckDB if it doesn't exist
conn_duck.execute("""
CREATE TABLE IF NOT EXISTS foot_measurements (
    customer_id INTEGER PRIMARY KEY,
    left_length FLOAT, left_width FLOAT, left_girth FLOAT, left_instep FLOAT, left_arch_height FLOAT,
    right_length FLOAT, right_width FLOAT, right_girth FLOAT, right_instep FLOAT, right_arch_height FLOAT,
    left_pressure JSON, right_pressure JSON,
    recommendations JSON,
    left_depth BLOB, right_depth BLOB
)
""")

# Create the table in SQLite if it doesn't exist
conn_sqlite.execute("PRAGMA journal_mode=WAL;")
conn_sqlite.execute("""
CREATE TABLE IF NOT EXISTS foot_measurements (
    customer_id INTEGER PRIMARY KEY,
    left_length REAL, left_width REAL, left_girth REAL, left_instep REAL, left_arch_height REAL,
    right_length REAL, right_width REAL, right_girth REAL, right_instep REAL, right_arch_height REAL,
    left_pressure TEXT, right_pressure TEXT,
    recommendations TEXT,
    left_depth BLOB, right_depth BLOB
)
""")
conn_sqlite.commit()

# Define the webhook endpoint
@app.post("/scan")
async def receive_scan(data: ScanData):
    try:
        # Decode the base64-encoded depth data
        left_depth = base64.b64decode(data.left_depth)
        right_depth = base64.b64decode(data.right_depth)

        # Insert the data into DuckDB
        conn_duck.execute("""
        INSERT INTO foot_measurements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (customer_id) DO UPDATE SET
            left_length = excluded.left_length,
            left_width = excluded.left_width,
            left_girth = excluded.left_girth,
            left_instep = excluded.left_instep,
            left_arch_height = excluded.left_arch_height,
            right_length = excluded.right_length,
            right_width = excluded.right_width,
            right_girth = excluded.right_girth,
            right_instep = excluded.right_instep,
            right_arch_height = excluded.right_arch_height,
            left_pressure = excluded.left_pressure,
            right_pressure = excluded.right_pressure,
            recommendations = excluded.recommendations,
            left_depth = excluded.left_depth,
            right_depth = excluded.right_depth
        """, (
            data.customer_id,
            data.left_length, data.left_width, data.left_girth, data.left_instep, data.left_arch_height,
            data.right_length, data.right_width, data.right_girth, data.right_instep, data.right_arch_height,
            json.dumps(data.left_pressure),
            json.dumps(data.right_pressure),
            json.dumps(data.recommendations),
            left_depth,
            right_depth
        ))

        # Copy the data to SQLite
        conn_sqlite.execute("""
        INSERT INTO foot_measurements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (customer_id) DO UPDATE SET
            left_length = excluded.left_length,
            left_width = excluded.left_width,
            left_girth = excluded.left_girth,
            left_instep = excluded.left_instep,
            left_arch_height = excluded.left_arch_height,
            right_length = excluded.right_length,
            right_width = excluded.right_width,
            right_girth = excluded.right_girth,
            right_instep = excluded.right_instep,
            right_arch_height = excluded.right_arch_height,
            left_pressure = excluded.left_pressure,
            right_pressure = excluded.right_pressure,
            recommendations = excluded.recommendations,
            left_depth = excluded.left_depth,
            right_depth = excluded.right_depth
        """, (
            data.customer_id,
            data.left_length, data.left_width, data.left_girth, data.left_instep, data.left_arch_height,
            data.right_length, data.right_width, data.right_girth, data.right_instep, data.right_arch_height,
            json.dumps(data.left_pressure),
            json.dumps(data.right_pressure),
            json.dumps(data.recommendations),
            left_depth,
            right_depth
        ))
        conn_sqlite.commit()

        return {"message": f"Scan data for customer {data.customer_id} saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the webhook server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)