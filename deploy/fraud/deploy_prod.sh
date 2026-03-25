#!/bin/bash
set -e

# ========================================
# Deploy Script — Fraud Detection System
# Server: 10.14.190.28
# ========================================

APP_DIR="/root/workspace/fraud_detection"
DEPLOY_DIR="$APP_DIR/deploy/fraud"
BRANCH="main"
COMPOSE_FILE="$DEPLOY_DIR/docker-compose.prod.yml"

echo "========================================"
echo "   Fraud Detection — Auto Deploy"
echo "   Server: $(hostname -I | awk '{print $1}')"
echo "========================================"

cd "$APP_DIR"

# 0. Pre-flight checks
echo ""
echo "[0/5] Pre-flight checks..."
echo "   Disk: $(df -h / | tail -1 | awk '{print $5}')"
echo "   Memory: $(free -h | grep Mem | awk '{print $3"/"$2}')"
echo "   Docker: $(docker --version | cut -d' ' -f3)"

# 1. Update Code
echo ""
echo "[1/5] Pulling latest code from GitHub..."
git fetch origin
git reset --hard origin/$BRANCH
echo "   Code updated"

# 2. Check .env.prod exists
if [ ! -f "$DEPLOY_DIR/.env.prod" ]; then
    echo ""
    echo "ERROR: $DEPLOY_DIR/.env.prod not found!"
    echo "Please create it from the template first."
    exit 1
fi

# 3. Import Neo4j dump (if exists and first deploy)
NEO4J_DUMP="$APP_DIR/neo4j.dump"
if [ -f "$NEO4J_DUMP" ]; then
    echo ""
    echo "[2/5] Importing Neo4j dump..."

    # Start only neo4j to import
    docker-compose -f "$COMPOSE_FILE" up -d neo4j
    echo "   Waiting 30s for Neo4j to initialize..."
    sleep 30

    # Stop neo4j for import
    docker-compose -f "$COMPOSE_FILE" stop neo4j

    # Copy dump into container and import
    docker cp "$NEO4J_DUMP" fraud_prod_neo4j:/data/neo4j.dump
    docker run --rm \
        -v fraud_neo4j_data:/data \
        neo4j:5.12.0 \
        neo4j-admin database load neo4j --from-path=/data/ --overwrite-destination=true

    echo "   Neo4j dump imported"
    # Rename to avoid re-import
    mv "$NEO4J_DUMP" "$NEO4J_DUMP.imported"
else
    echo ""
    echo "[2/5] No neo4j.dump found, skipping import (using existing data)"
fi

# 4. Stop old containers
echo ""
echo "[3/5] Stopping old containers..."
docker-compose -f "$COMPOSE_FILE" down 2>/dev/null || true
echo "   Old containers removed"

# 5. Build & Start
echo ""
echo "[4/5] Building & Starting all services..."
docker-compose -f "$COMPOSE_FILE" --env-file "$DEPLOY_DIR/.env.prod" up -d --build

echo ""
echo "   Waiting 60s for all services to start..."
sleep 60

# 6. Health checks
echo ""
echo "[5/5] Health checks..."

check_service() {
    local name=$1
    local url=$2
    if curl -sf --max-time 5 "$url" > /dev/null 2>&1; then
        echo "   $name: OK"
    else
        echo "   $name: FAILED ($url)"
    fi
}

check_service "Dashboard"  "http://localhost:5001/api/overview"
check_service "Neo4j"      "http://localhost:17474"
check_service "App API"    "http://localhost:8002/docs"

echo ""
echo "========================================"
echo "   Deploy Complete!"
echo "========================================"
echo ""
echo "Services:"
docker-compose -f "$COMPOSE_FILE" ps
echo ""
echo "URLs:"
echo "   Dashboard:    http://10.14.190.28:5001"
echo "   Neo4j Browser: http://10.14.190.28:17474"
echo "   App API:      http://10.14.190.28:8002/docs"
