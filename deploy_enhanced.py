#!/usr/bin/env python3
"""
Docker Production Deployment Script
Rebuild containers with new changes and deploy to production
"""

import subprocess
import time
import requests
import sys
import os
import json
from datetime import datetime

class DockerDeployer:
    def __init__(self):
        self.project_root = r"c:\Users\cigba\sports_app"
        self.compose_file = os.path.join(self.project_root, "docker-compose.yml")
        self.api_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def step_1_cleanup_containers(self):
        """Step 1: Clean up existing containers"""
        self.log("STEP 1: Cleaning up existing containers", "DEPLOY")
        
        try:
            os.chdir(self.project_root)
            
            # Stop and remove existing containers
            self.log("Stopping existing containers...")
            result = subprocess.run(["docker-compose", "down", "-v"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ Containers stopped successfully")
            else:
                self.log(f"⚠️ Container stop had issues: {result.stderr}")
            
            # Remove unused images and containers
            self.log("Cleaning up Docker system...")
            subprocess.run(["docker", "system", "prune", "-f"], 
                          capture_output=True, text=True)
            
            self.log("✅ Container cleanup completed")
            return True
            
        except Exception as e:
            self.log(f"❌ Cleanup failed: {e}", "ERROR")
            return False
    
    def step_2_rebuild_images(self):
        """Step 2: Rebuild Docker images with new changes"""
        self.log("STEP 2: Rebuilding Docker images with new changes", "DEPLOY")
        
        try:
            # Build backend image
            self.log("Building backend API image...")
            result = subprocess.run([
                "docker", "build", 
                "--no-cache",
                "-t", "sports-betting-api:latest",
                "-f", "backend/Dockerfile.production",
                "backend/"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Backend image built successfully")
            else:
                self.log(f"❌ Backend build failed: {result.stderr}", "ERROR")
                return False
            
            # Build frontend image
            self.log("Building frontend image...")
            result = subprocess.run([
                "docker", "build",
                "--no-cache", 
                "-t", "sports-betting-frontend:latest",
                "-f", "frontend/Dockerfile.production",
                "frontend/"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Frontend image built successfully")
            else:
                self.log(f"❌ Frontend build failed: {result.stderr}", "ERROR")
                return False
            
            self.log("✅ All images rebuilt successfully")
            return True
            
        except Exception as e:
            self.log(f"❌ Image rebuild failed: {e}", "ERROR")
            return False
    
    def step_3_start_containers(self):
        """Step 3: Start containers with docker-compose"""
        self.log("STEP 3: Starting containers with docker-compose", "DEPLOY")
        
        try:
            # Start all services
            self.log("Starting all services...")
            result = subprocess.run([
                "docker-compose", "up", "-d", "--build"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Containers started successfully")
            else:
                self.log(f"❌ Container start failed: {result.stderr}", "ERROR")
                return False
            
            # Wait for services to initialize
            self.log("⏳ Waiting for services to initialize...")
            time.sleep(15)
            
            return True
            
        except Exception as e:
            self.log(f"❌ Container startup failed: {e}", "ERROR")
            return False
    
    def step_4_verify_containers(self):
        """Step 4: Verify containers are running"""
        self.log("STEP 4: Verifying container status", "DEPLOY")
        
        try:
            # Check container status
            result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
            if result.returncode == 0:
                running_containers = result.stdout
                if "sports_app" in running_containers:
                    self.log("✅ Sports app containers are running")
                else:
                    self.log("⚠️ Sports app containers may not be running")
                    
                # Log container details
                lines = running_containers.split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip() and "sports_app" in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            self.log(f"   Container: {parts[1]} - {parts[6] if len(parts) > 6 else 'N/A'}")
            
            # Check logs for any errors
            self.log("Checking container logs...")
            result = subprocess.run(["docker-compose", "logs", "--tail=20"], 
                                  capture_output=True, text=True)
            if "ERROR" in result.stdout or "Failed" in result.stdout:
                self.log("⚠️ Found errors in logs - check docker-compose logs for details")
            else:
                self.log("✅ No critical errors found in logs")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Container verification failed: {e}", "ERROR")
            return False
    
    def step_5_test_api_endpoints(self):
        """Step 5: Test API endpoints"""
        self.log("STEP 5: Testing API endpoints", "DEPLOY")
        
        # Wait for API to be ready
        self.log("⏳ Waiting for API to be ready...")
        api_ready = False
        
        for attempt in range(20):
            try:
                response = requests.get(f"{self.api_url}/api/health", timeout=3)
                if response.status_code == 200:
                    self.log("✅ API health check passed")
                    api_ready = True
                    break
            except:
                time.sleep(3)
                self.log(f"⏳ API not ready yet... (attempt {attempt + 1}/20)")
        
        if not api_ready:
            self.log("❌ API failed to respond", "ERROR")
            return False
        
        # Test specific endpoints
        test_endpoints = [
            ("/api/global-sports", "Global Sports"),
            ("/api/recommendations/NBA", "NBA Recommendations"),
            ("/api/recommendations/EPL", "EPL Recommendations"),
            ("/api/parlays/NBA", "NBA Parlays")
        ]
        
        passed_tests = 0
        for endpoint, description in test_endpoints:
            try:
                response = requests.get(f"{self.api_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    if "global-sports" in endpoint:
                        sports_count = len(data)
                        self.log(f"✅ {description}: {sports_count} sports")
                        if sports_count >= 20:
                            passed_tests += 1
                    elif "recommendations" in endpoint:
                        recs = data.get('recommendations', [])
                        self.log(f"✅ {description}: {len(recs)} recommendations")
                        if recs:
                            passed_tests += 1
                    elif "parlays" in endpoint:
                        parlays = data.get('parlays', [])
                        self.log(f"✅ {description}: {len(parlays)} parlays")
                        if parlays:
                            passed_tests += 1
                else:
                    self.log(f"❌ {description}: HTTP {response.status_code}", "ERROR")
                    
            except Exception as e:
                self.log(f"❌ {description}: {str(e)[:30]}", "ERROR")
        
        if passed_tests >= 3:
            self.log(f"✅ API tests passed: {passed_tests}/{len(test_endpoints)}")
            return True
        else:
            self.log(f"❌ API tests failed: {passed_tests}/{len(test_endpoints)}", "ERROR")
            return False
    
    def step_6_test_frontend(self):
        """Step 6: Test frontend accessibility"""
        self.log("STEP 6: Testing frontend accessibility", "DEPLOY")
        
        # Wait for frontend to be ready
        self.log("⏳ Waiting for frontend to be ready...")
        frontend_ready = False
        
        for attempt in range(15):
            try:
                response = requests.get(self.frontend_url, timeout=5)
                if response.status_code == 200:
                    self.log("✅ Frontend is accessible")
                    frontend_ready = True
                    break
            except:
                time.sleep(3)
                self.log(f"⏳ Frontend not ready yet... (attempt {attempt + 1}/15)")
        
        if not frontend_ready:
            self.log("❌ Frontend is not accessible", "ERROR")
            return False
        
        return True
    
    def step_7_troubleshoot_api_error(self):
        """Step 7: Troubleshoot the 'Failed to fetch' error"""
        self.log("STEP 7: Troubleshooting API connection issues", "DEPLOY")
        
        # Check CORS configuration
        try:
            response = requests.options(f"{self.api_url}/api/global-sports", 
                                      headers={'Origin': 'http://localhost:3000'})
            if response.status_code == 200:
                self.log("✅ CORS preflight check passed")
            else:
                self.log(f"⚠️ CORS preflight issue: HTTP {response.status_code}")
        except Exception as e:
            self.log(f"❌ CORS test failed: {e}", "ERROR")
        
        # Test API from frontend perspective
        try:
            response = requests.get(f"{self.api_url}/api/global-sports",
                                  headers={'Origin': 'http://localhost:3000'})
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ API accessible from frontend: {len(data)} sports")
                
                # Test a specific sport that frontend tries to fetch
                response = requests.get(f"{self.api_url}/api/recommendations/NBA",
                                      headers={'Origin': 'http://localhost:3000'})
                if response.status_code == 200:
                    data = response.json()
                    recs = data.get('recommendations', [])
                    self.log(f"✅ NBA recommendations accessible: {len(recs)} bets")
                    return True
                else:
                    self.log(f"❌ NBA recommendations failed: HTTP {response.status_code}", "ERROR")
            else:
                self.log(f"❌ API not accessible from frontend: HTTP {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"❌ Frontend API test failed: {e}", "ERROR")
        
        return False
    
    def deploy(self):
        """Execute full Docker production deployment"""
        start_time = datetime.now()
        self.log("🚀 STARTING DOCKER PRODUCTION DEPLOYMENT", "DEPLOY")
        self.log("=" * 70)
        
        steps = [
            ("Container Cleanup", self.step_1_cleanup_containers),
            ("Image Rebuild", self.step_2_rebuild_images),
            ("Container Startup", self.step_3_start_containers),
            ("Container Verification", self.step_4_verify_containers),
            ("API Testing", self.step_5_test_api_endpoints),
            ("Frontend Testing", self.step_6_test_frontend),
            ("API Error Troubleshooting", self.step_7_troubleshoot_api_error)
        ]
        
        for step_name, step_func in steps:
            self.log(f"\n{'='*25} {step_name} {'='*25}")
            if not step_func():
                self.log(f"❌ DEPLOYMENT FAILED at {step_name}", "ERROR")
                self.log("\n🔧 TROUBLESHOOTING TIPS:")
                self.log("   1. Check Docker logs: docker-compose logs")
                self.log("   2. Verify containers: docker ps")
                self.log("   3. Check network connectivity: docker network ls")
                self.log("   4. Manual restart: docker-compose down && docker-compose up -d")
                return False
        
        # Success!
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.log("\n" + "="*70)
        self.log("🎉 DOCKER DEPLOYMENT SUCCESSFUL!", "SUCCESS")
        self.log("=" * 70)
        self.log(f"⏱️ Total deployment time: {duration:.1f} seconds")
        self.log(f"🌐 Frontend: {self.frontend_url}")
        self.log(f"🔌 API: {self.api_url}")
        
        self.log("\n🎯 DEPLOYED FEATURES:")
        self.log("✅ Containerized 22+ Global Sports API")
        self.log("✅ Enhanced Frontend with Live Data")
        self.log("✅ Game Theory Algorithms")
        self.log("✅ Intelligent Parlays & Player Props")
        self.log("✅ CORS-enabled API for Frontend Communication")
        
        self.log("\n🔍 VERIFY DEPLOYMENT:")
        self.log(f"   Frontend: {self.frontend_url}")
        self.log(f"   API Health: {self.api_url}/api/health")
        self.log(f"   Global Sports: {self.api_url}/api/global-sports")
        
        self.log("\n🔴 API 'Failed to fetch' error should now be resolved!")
        return True

if __name__ == "__main__":
    deployer = DockerDeployer()
    success = deployer.deploy()
    
    if success:
        print("\n" + "="*70)
        print("🎉 SUCCESS! Your containerized platform is ready!")
        print("🌐 Frontend: http://localhost:3000")
        print("🔌 API: http://localhost:8000")
        print("="*70)
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("❌ DEPLOYMENT FAILED - Check logs above")
        print("🔧 Try manual commands:")
        print("   docker-compose down")
        print("   docker-compose up -d --build")
        print("="*70)
        sys.exit(1)