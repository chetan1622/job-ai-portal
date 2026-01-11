import sqlite3

conn = sqlite3.connect('job_ai.db')
c = conn.cursor()

# Get all tables
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
print('Current tables:', [t[0] for t in tables])

# Get columns for each table
for table in tables:
    table_name = table[0]
    c.execute(f'PRAGMA table_info({table_name})')
    columns = c.fetchall()
    print(f'{table_name} columns:', [col[1] for col in columns])

conn.close()