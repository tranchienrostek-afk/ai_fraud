#!/bin/bash
set -e

echo "[Dashboard] Waiting for Neo4j Bolt at ${NEO4J_URI:-bolt://neo4j:7687}..."

# Extract host and port from NEO4J_URI
NEO4J_HOST=$(echo "${NEO4J_URI:-bolt://neo4j:7687}" | sed 's|bolt://||' | cut -d: -f1)
NEO4J_PORT=$(echo "${NEO4J_URI:-bolt://neo4j:7687}" | sed 's|bolt://||' | cut -d: -f2)

python -c "
import socket, time, sys
host = '${NEO4J_HOST}'
port = int('${NEO4J_PORT}')
for i in range(60):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((host, port))
        s.close()
        print(f'Neo4j Bolt ready at {host}:{port}')
        sys.exit(0)
    except Exception as e:
        print(f'Waiting for Neo4j... ({i+1}/60) {e}')
        time.sleep(2)
print('ERROR: Neo4j not available after 120s')
sys.exit(1)
"

echo "[Dashboard] Starting SIU Dashboard..."
exec uvicorn app:app --host 0.0.0.0 --port 5000 --workers 2
