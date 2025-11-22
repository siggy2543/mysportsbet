#!/bin/bash
# Simple Docker Deployment Commands

echo "=== DOCKER DEPLOYMENT START ==="
cd "C:\Users\cigba\sports_app"

echo "Step 1: Stop containers"
docker-compose down -v

echo "Step 2: Clean system"
docker system prune -f

echo "Step 3: Build images"
docker-compose build --no-cache

echo "Step 4: Start containers"
docker-compose up -d

echo "Step 5: Check status"
docker ps

echo "=== DEPLOYMENT COMPLETE ==="
echo "Frontend: http://localhost:3000" 
echo "API: http://localhost:8000"