import sqlite3
import os

db_path = "./data/memories.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Table: entities ---")
    cursor.execute("SELECT * FROM entities")
    entities = cursor.fetchall()
    for e in entities:
        print(e)
        
    print("\n--- Table: relationships ---")
    cursor.execute("SELECT * FROM relationships")
    relationships = cursor.fetchall()
    for r in relationships:
        print(r)
        
    print("\n--- Summary ---")
    print(f"Total entities: {len(entities)}")
    print(f"Total relationships: {len(relationships)}")
    
    conn.close()
