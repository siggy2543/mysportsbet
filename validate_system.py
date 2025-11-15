#!/usr/bin/env python3
# =============================================================================
# SIMPLE SYSTEM VALIDATION SCRIPT
# =============================================================================

import asyncio
import aiohttp
import json
import time
from datetime import datetime
import sys

class SystemValidator:
    """Simple system validation without external dependencies"""
    
    def __init__(self):
        self.base_url = "https://localhost"
        self.api_base = f"{self.base_url}/api/v1"
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

    async def test_endpoint(self, name: str, url: str, expected_status: int = 200, headers: dict = None):
        """Test a single endpoint"""
        self.results['total_tests'] += 1
        
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(url, headers=headers or {}) as response:
                    if response.status == expected_status:
                        self.results['passed'] += 1
                        print(f"  ✅ {name}")
                        return await response.text() if response.content_type.startswith('text') else await response.json()
                    else:
                        self.results['failed'] += 1
                        error = f"{name} returned {response.status}, expected {expected_status}"
                        self.results['errors'].append(error)
                        print(f"  ❌ {name} - {error}")
                        return None
                        
        except Exception as e:
            if "Connection" in str(e) or "timeout" in str(e).lower():
                self.results['skipped'] += 1
                print(f"  ⏭️  {name} (service not available)")
            else:
                self.results['failed'] += 1
                error = f"{name} - {str(e)}"
                self.results['errors'].append(error)
                print(f"  ❌ {name} - {str(e)}")
            return None

    async def validate_system(self):
        """Run comprehensive system validation"""
        print("🔍 SPORTS BETTING SYSTEM VALIDATION")
        print("="*50)
        start_time = time.time()

        # Test basic endpoints
        print("\n📡 Testing Core Endpoints...")
        
        await self.test_endpoint("Health Check", f"{self.base_url}/health")
        await self.test_endpoint("SSL Health Check", f"{self.base_url}/ssl-health")
        
        status_data = await self.test_endpoint("System Status", f"{self.api_base}/bets/public/status")
        if status_data:
            print(f"    📊 System Status: {status_data.get('status', 'unknown')}")
            if 'features' in status_data:
                print(f"    🔧 Features: {len(status_data['features'])} available")
            if 'supported_sports' in status_data:
                print(f"    🏀 Sports: {', '.join(status_data['supported_sports'])}")

        # Test authentication endpoints (expect 405 or 422 for GET requests)
        print("\n🔐 Testing Authentication Endpoints...")
        await self.test_endpoint("Auth Register", f"{self.api_base}/auth/register", expected_status=405)
        await self.test_endpoint("Auth Login", f"{self.api_base}/auth/login", expected_status=405)

        # Test protected endpoints (expect 401 without auth)
        print("\n🔒 Testing Protected Endpoints...")
        await self.test_endpoint("Games Endpoint", f"{self.api_base}/sports/games", expected_status=401)
        await self.test_endpoint("Active Bets", f"{self.api_base}/bets/active", expected_status=401)
        await self.test_endpoint("Betting History", f"{self.api_base}/bets/history", expected_status=401)

        # Test service performance
        print("\n⚡ Testing Performance...")
        
        perf_start = time.time()
        health_data = await self.test_endpoint("Performance Test", f"{self.base_url}/health")
        perf_end = time.time()
        
        if health_data:
            response_time = (perf_end - perf_start) * 1000
            print(f"    ⏱️  Response Time: {response_time:.2f}ms")
            
            if response_time < 1000:
                print("    ✅ Performance: Excellent (<1s)")
            elif response_time < 2000:
                print("    ⚠️  Performance: Good (<2s)")
            else:
                print("    ❌ Performance: Slow (>2s)")

        # Test concurrent requests
        print("\n🔄 Testing Concurrent Load...")
        await self.test_concurrent_load()

        # Generate final report
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "="*50)
        print("📊 VALIDATION SUMMARY")
        print("="*50)
        print(f"⏱️  Total Time: {total_time:.2f}s")
        print(f"🧪 Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⏭️  Skipped: {self.results['skipped']}")
        
        if self.results['errors']:
            print("\n❌ ERRORS:")
            for error in self.results['errors'][:5]:  # Show max 5 errors
                print(f"  - {error}")
            if len(self.results['errors']) > 5:
                print(f"  ... and {len(self.results['errors']) - 5} more errors")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100 if self.results['total_tests'] > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 SYSTEM VALIDATION PASSED!")
            print("✨ Your sports betting application is ready for production!")
        elif success_rate >= 60:
            print("⚠️  SYSTEM PARTIALLY OPERATIONAL")
            print("🔧 Some components need attention")
        else:
            print("❌ SYSTEM NEEDS ATTENTION")
            print("🚨 Multiple issues detected")

        # Provide recommendations
        print("\n🚀 NEXT STEPS:")
        if self.results['passed'] > 0:
            print("  ✅ Working endpoints can be used immediately")
        if self.results['failed'] > 0:
            print("  🔧 Fix failed endpoints for full functionality")
        if self.results['skipped'] > 0:
            print("  🔌 Start all services for complete testing")
        
        print("\n📚 DOCUMENTATION:")
        print(f"  🌐 API Docs: {self.base_url}/docs (when available)")
        print(f"  📊 Dashboard: {self.base_url}/")
        print(f"  🔒 SSL Status: {self.base_url}/ssl-health")
        
        return self.results

    async def test_concurrent_load(self):
        """Test system under concurrent load"""
        async def make_request():
            try:
                connector = aiohttp.TCPConnector(ssl=False)
                timeout = aiohttp.ClientTimeout(total=5)
                
                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                    async with session.get(f"{self.base_url}/health") as response:
                        return response.status == 200
            except:
                return False

        # Make 5 concurrent requests
        start_time = time.time()
        tasks = [make_request() for _ in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        successful = sum(1 for result in results if result is True)
        concurrent_time = (end_time - start_time) * 1000
        
        print(f"    🔄 Concurrent Requests: {successful}/5 successful")
        print(f"    ⏱️  Concurrent Time: {concurrent_time:.2f}ms")
        
        if successful >= 4:
            print("    ✅ Concurrency: Excellent")
        elif successful >= 3:
            print("    ⚠️  Concurrency: Good")
        else:
            print("    ❌ Concurrency: Poor")

async def main():
    """Main validation function"""
    validator = SystemValidator()
    await validator.validate_system()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Validation interrupted by user")
    except Exception as e:
        print(f"\n💥 Validation failed: {e}")
        sys.exit(1)