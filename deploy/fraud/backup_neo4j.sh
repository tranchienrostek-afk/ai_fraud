#!/bin/bash
set -e

# ========================================
# Neo4j Data Migration — Local → Server
# Run this on your LOCAL machine
# ========================================

LOCAL_CONTAINER="fraud_neo4j"
SERVER="10.14.190.28"
SERVER_DIR="/root/workspace/fraud_detection"
DUMP_FILE="neo4j.dump"

echo "========================================"
echo "   Neo4j Data Export & Transfer"
echo "========================================"

# Step 1: Check local container
echo ""
echo "[1/4] Checking local Neo4j container..."
if ! docker ps -a --format '{{.Names}}' | grep -q "^${LOCAL_CONTAINER}$"; then
    echo "ERROR: Container '$LOCAL_CONTAINER' not found!"
    echo "Please start it first: docker start $LOCAL_CONTAINER"
    exit 1
fi

# Step 2: Stop Neo4j (required for consistent dump)
echo ""
echo "[2/4] Stopping Neo4j for consistent dump..."
docker stop "$LOCAL_CONTAINER" 2>/dev/null || true
sleep 5

# Step 3: Export dump
echo ""
echo "[3/4] Exporting Neo4j database dump..."
docker run --rm \
    -v 04_fraud_detection_neo4j_data:/data \
    -v "$(pwd):/backup" \
    neo4j:5.12.0 \
    neo4j-admin database dump neo4j --to-path=/backup/

echo "   Dump created: $(ls -lh $DUMP_FILE | awk '{print $5}')"

# Restart local Neo4j
docker start "$LOCAL_CONTAINER"
echo "   Local Neo4j restarted"

# Step 4: Transfer to server
echo ""
echo "[4/4] Transferring dump to server..."
echo "   Running: scp $DUMP_FILE root@$SERVER:$SERVER_DIR/"
scp "$DUMP_FILE" "root@${SERVER}:${SERVER_DIR}/"

echo ""
echo "========================================"
echo "   Transfer Complete!"
echo "========================================"
echo ""
echo "Next steps on server:"
echo "   ssh root@$SERVER"
echo "   cd $SERVER_DIR"
echo "   ./deploy/fraud/deploy_prod.sh"
