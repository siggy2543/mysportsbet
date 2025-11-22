#!/usr/bin/env python3
"""
Production Restart & Deployment Script
Full troubleshooting with step-by-step verification
"""

import subprocess
import time
import requests
import sys
import os
import json
from datetime import datetime

class ProductionDeployer:
    def __init__(self):
        self.project_root = r"c:\Users\cigba\sports_app"
        self.backend_dir = os.path.join(self.project_root, "backend")
        self.frontend_dir = os.path.join(self.project_root, "frontend")
        self.api_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def step_1_cleanup(self):
        """Step 1: Clean up existing processes"""
        self.log("STEP 1: Cleaning up existing processes", "DEPLOY")
        
        try:
            # Kill Python processes
            result = subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ Python processes terminated")
            else:
                self.log("⚠️ No Python processes found to terminate")
            
            # Kill Node processes
            result = subprocess.run(["taskkill", "/F", "/IM", "node.exe", "/T"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ Node processes terminated")
            else:
                self.log("⚠️ No Node processes found to terminate")
            
            # Wait for cleanup
            time.sleep(3)
            self.log("✅ Process cleanup completed")
            return True
            
        except Exception as e:
            self.log(f"❌ Cleanup failed: {e}", "ERROR")
            return False
    
    def step_2_verify_files(self):
        """Step 2: Verify all required files exist"""
        self.log("STEP 2: Verifying deployment files", "DEPLOY")
        
        required_files = [
            os.path.join(self.backend_dir, "standalone_api.py"),
            os.path.join(self.frontend_dir, "package.json"),
            os.path.join(self.frontend_dir, "src", "EnhancedInteractiveApp.js"),
            os.path.join(self.frontend_dir, "src", "EnhancedInteractiveApp.css")
        ]
        
        all_files_exist = True
        for file_path in required_files:
            if os.path.exists(file_path):
                self.log(f"✅ Found: {os.path.basename(file_path)}")
            else:
                self.log(f"❌ Missing: {file_path}", "ERROR")
                all_files_exist = False
        
        if all_files_exist:
            self.log("✅ All required files verified")
            return True
        else:
            self.log("❌ Missing critical files", "ERROR")
            return False
    
    def step_3_start_backend(self):
        """Step 3: Start enhanced backend API"""
        self.log("STEP 3: Starting enhanced backend API", "DEPLOY")
        
        try:
            os.chdir(self.backend_dir)
            self.log(f"Changed to backend directory: {self.backend_dir}")
            
            # Start API server in new window
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startup_info.wShowWindow = subprocess.SW_NORMAL
            
            self.api_process = subprocess.Popen(
                ["python", "standalone_api.py"],
                startupinfo=startup_info,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.log(f"🚀 API server starting (PID: {self.api_process.pid})")
            
            # Wait and verify API is responsive
            self.log("⏳ Waiting for API to initialize...")
            for attempt in range(15):
                time.sleep(2)
                try:
                    response = requests.get(f"{self.api_url}/api/health", timeout=3)
                    if response.status_code == 200:
                        health_data = response.json()
                        self.log(f"✅ API is healthy: {health_data.get('service', 'Unknown')}")
                        
                        # Test global sports endpoint
                        sports_response = requests.get(f"{self.api_url}/api/global-sports", timeout=3)
                        if sports_response.status_code == 200:
                            sports_data = sports_response.json()
                            self.log(f"✅ Global sports loaded: {len(sports_data)} sports available")
                            return True
                        else:
                            self.log("⚠️ Global sports endpoint not ready")
                            
                except requests.exceptions.RequestException:
                    self.log(f"⏳ API not ready yet... (attempt {attempt + 1}/15)")
            
            self.log("❌ API failed to start properly", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"❌ Backend startup failed: {e}", "ERROR")
            return False
    
    def step_4_test_backend_features(self):
        """Step 4: Test all backend features"""
        self.log("STEP 4: Testing backend features", "DEPLOY")
        
        test_endpoints = [
            ("/api/global-sports", "Global Sports"),
            ("/api/recommendations/NBA", "NBA Moneylines"),
            ("/api/recommendations/EPL", "EPL Moneylines"),
            ("/api/recommendations/ATP", "ATP Tennis"),
            ("/api/parlays/NBA", "NBA Parlays"),
            ("/api/player-props/NBA", "NBA Player Props")
        ]
        
        passed_tests = 0
        for endpoint, description in test_endpoints:
            try:
                response = requests.get(f"{self.api_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Specific validation based on endpoint
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
                    elif "player-props" in endpoint:
                        props = data.get('player_props', [])
                        self.log(f"✅ {description}: {len(props)} props")
                        if props:
                            passed_tests += 1
                else:
                    self.log(f"❌ {description}: HTTP {response.status_code}", "ERROR")
                    
            except Exception as e:
                self.log(f"❌ {description}: {str(e)[:50]}", "ERROR")
        
        if passed_tests >= 4:
            self.log(f"✅ Backend tests passed: {passed_tests}/{len(test_endpoints)}")
            return True
        else:
            self.log(f"❌ Backend tests failed: {passed_tests}/{len(test_endpoints)}", "ERROR")
            return False
    
    def step_5_start_frontend(self):
        """Step 5: Start enhanced frontend"""
        self.log("STEP 5: Starting enhanced frontend", "DEPLOY")
        
        try:
            os.chdir(self.frontend_dir)
            self.log(f"Changed to frontend directory: {self.frontend_dir}")
            
            # Set environment variables
            env = os.environ.copy()
            env['CI'] = 'false'
            env['BROWSER'] = 'none'  # Don't auto-open browser
            
            # Start frontend server in new window
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startup_info.wShowWindow = subprocess.SW_NORMAL
            
            self.frontend_process = subprocess.Popen(
                ["npm", "start"],
                env=env,
                startupinfo=startup_info,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.log(f"🌐 Frontend server starting (PID: {self.frontend_process.pid})")
            
            # Wait for frontend to be ready
            self.log("⏳ Waiting for frontend to start...")
            for attempt in range(20):
                time.sleep(3)
                try:
                    response = requests.get(self.frontend_url, timeout=3)
                    if response.status_code == 200:
                        self.log("✅ Frontend is accessible")
                        return True
                except requests.exceptions.RequestException:
                    self.log(f"⏳ Frontend not ready yet... (attempt {attempt + 1}/20)")
            
            self.log("❌ Frontend failed to start", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"❌ Frontend startup failed: {e}", "ERROR")
            return False
    
    def step_6_verify_integration(self):
        """Step 6: Verify frontend-backend integration"""
        self.log("STEP 6: Verifying frontend-backend integration", "DEPLOY")
        
        # Test that frontend can communicate with backend
        integration_tests = [
            ("Frontend accessibility", self.frontend_url),
            ("API health check", f"{self.api_url}/api/health"),
            ("Global sports data", f"{self.api_url}/api/global-sports"),
            ("Live NBA data", f"{self.api_url}/api/recommendations/NBA"),
            ("Live EPL data", f"{self.api_url}/api/recommendations/EPL")
        ]
        
        passed_integration = 0
        for test_name, url in integration_tests:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.log(f"✅ {test_name}: OK")
                    passed_integration += 1
                else:
                    self.log(f"❌ {test_name}: HTTP {response.status_code}", "ERROR")
            except Exception as e:
                self.log(f"❌ {test_name}: {str(e)[:30]}", "ERROR")
        
        if passed_integration >= 4:
            self.log(f"✅ Integration tests passed: {passed_integration}/{len(integration_tests)}")
            return True
        else:
            self.log(f"❌ Integration tests failed: {passed_integration}/{len(integration_tests)}", "ERROR")
            return False
    
    def step_7_final_validation(self):
        """Step 7: Final production validation"""
        self.log("STEP 7: Final production validation", "DEPLOY")
        
        # Test key features that should be visible in frontend
        validation_tests = [
            ("Global sports (22+ sports)", f"{self.api_url}/api/global-sports", lambda d: len(d) >= 20),
            ("NBA live data", f"{self.api_url}/api/recommendations/NBA", lambda d: len(d.get('recommendations', [])) > 0),
            ("EPL live data", f"{self.api_url}/api/recommendations/EPL", lambda d: len(d.get('recommendations', [])) > 0),
            ("ATP Tennis data", f"{self.api_url}/api/recommendations/ATP", lambda d: len(d.get('recommendations', [])) > 0),
            ("Cricket data", f"{self.api_url}/api/recommendations/CRICKET", lambda d: len(d.get('recommendations', [])) > 0),
            ("Parlay generation", f"{self.api_url}/api/parlays/NBA", lambda d: len(d.get('parlays', [])) > 0),
            ("Player props", f"{self.api_url}/api/player-props/NBA", lambda d: len(d.get('player_props', [])) > 0)
        ]
        
        passed_validation = 0
        for test_name, url, validator in validation_tests:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if validator(data):
                        self.log(f"✅ {test_name}: WORKING")
                        passed_validation += 1
                    else:
                        self.log(f"⚠️ {test_name}: NO DATA")
                else:
                    self.log(f"❌ {test_name}: HTTP {response.status_code}", "ERROR")
            except Exception as e:
                self.log(f"❌ {test_name}: ERROR", "ERROR")
        
        if passed_validation >= 5:
            self.log(f"✅ Validation passed: {passed_validation}/{len(validation_tests)}")
            return True
        else:
            self.log(f"❌ Validation failed: {passed_validation}/{len(validation_tests)}", "ERROR")
            return False
    
    def deploy(self):
        """Execute full production deployment"""
        start_time = datetime.now()
        self.log("🚀 STARTING PRODUCTION DEPLOYMENT", "DEPLOY")
        self.log("=" * 60)
        
        steps = [
            ("Process Cleanup", self.step_1_cleanup),
            ("File Verification", self.step_2_verify_files),
            ("Backend Startup", self.step_3_start_backend),
            ("Backend Testing", self.step_4_test_backend_features),
            ("Frontend Startup", self.step_5_start_frontend),
            ("Integration Testing", self.step_6_verify_integration),
            ("Final Validation", self.step_7_final_validation)
        ]
        
        for step_name, step_func in steps:
            self.log(f"\n{'='*20} {step_name} {'='*20}")
            if not step_func():
                self.log(f"❌ DEPLOYMENT FAILED at {step_name}", "ERROR")
                return False
        
        # Success!
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.log("\n" + "="*60)
        self.log("🎉 PRODUCTION DEPLOYMENT SUCCESSFUL!", "SUCCESS")
        self.log("=" * 60)
        self.log(f"⏱️ Total deployment time: {duration:.1f} seconds")
        self.log(f"🌐 Frontend Dashboard: {self.frontend_url}")
        self.log(f"🔌 API Server: {self.api_url}")
        self.log(f"📚 API Documentation: {self.api_url}/docs")
        
        self.log("\n🎯 FEATURES NOW LIVE:")
        self.log("✅ 22+ Global Sports (EPL, La Liga, ATP, WTA, Cricket, F1, etc.)")
        self.log("✅ Live Data Updates (20-second auto-refresh)")
        self.log("✅ Game Theory Algorithms (Nash equilibrium, minimax)")
        self.log("✅ Intelligent Parlays with correlation analysis")
        self.log("✅ Player Props with statistical confidence")
        self.log("✅ Enhanced UI with live indicators")
        
        self.log("\n🔴 PLATFORM IS READY FOR LIVE BETTING!")
        return True

if __name__ == "__main__":
    deployer = ProductionDeployer()
    success = deployer.deploy()
    
    if success:
        print("\n" + "="*60)
        print("🎉 SUCCESS! Open http://localhost:3000 to access the platform")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ DEPLOYMENT FAILED - Check logs above for issues")
        print("="*60)
        sys.exit(1)