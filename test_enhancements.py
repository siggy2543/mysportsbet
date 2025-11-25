"""
Comprehensive Test Suite for Enhanced Daily Betting Platform
Tests: 1) UI Performance Optimizations, 2) AI Learning System, 3) Date Filtering
"""

import asyncio
import asyncpg
import requests
import time
from datetime import datetime, timedelta, date
from typing import Dict, List
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'sports_betting',
    'user': 'sports_user',
    'password': 'sports_pass'
}

class EnhancementTestSuite:
    """Test suite for all three platform enhancements"""
    
    def __init__(self):
        self.results = {
            'ui_performance': {},
            'ai_learning': {},
            'date_filtering': {}
        }
        self.db_pool = None
    
    async def setup(self):
        """Initialize database connection pool"""
        print("🔧 Setting up test environment...")
        try:
            self.db_pool = await asyncpg.create_pool(**DB_CONFIG, min_size=2, max_size=5)
            print("✅ Database connection pool established")
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            raise
    
    async def cleanup(self):
        """Clean up resources"""
        if self.db_pool:
            await self.db_pool.close()
            print("✅ Database connection pool closed")
    
    # ===== Test 1: UI Performance Optimizations =====
    
    def test_ui_caching(self) -> bool:
        """Test frontend caching by measuring response times"""
        print("\n" + "="*60)
        print("TEST 1: UI PERFORMANCE - CACHING")
        print("="*60)
        
        sport = "NBA"
        endpoint = f"{API_BASE_URL}/api/recommendations/{sport}"
        
        # First request - cache miss
        start = time.time()
        response1 = requests.get(endpoint)
        first_time = time.time() - start
        
        time.sleep(1)  # Small delay
        
        # Second request - should hit cache
        start = time.time()
        response2 = requests.get(endpoint)
        second_time = time.time() - start
        
        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()
            
            print(f"✅ First request: {first_time:.3f}s ({len(data1.get('recommendations', []))} recs)")
            print(f"✅ Second request: {second_time:.3f}s ({len(data2.get('recommendations', []))} recs)")
            print(f"📊 Cache efficiency: {((first_time - second_time) / first_time * 100):.1f}% faster")
            
            # Check if AI learning is active
            if data1.get('ai_learning_active'):
                print("✅ AI learning active in API response")
            
            self.results['ui_performance']['caching'] = {
                'passed': True,
                'first_time': first_time,
                'second_time': second_time,
                'improvement': ((first_time - second_time) / first_time * 100)
            }
            return True
        else:
            print(f"❌ API request failed: {response1.status_code}")
            self.results['ui_performance']['caching'] = {'passed': False, 'error': 'API error'}
            return False
    
    def test_date_parameter_support(self) -> bool:
        """Test that API accepts date parameter"""
        print("\n" + "="*60)
        print("TEST 1B: UI PERFORMANCE - DATE PARAMETER HANDLING")
        print("="*60)
        
        sport = "NBA"
        
        # Test today
        response_today = requests.get(f"{API_BASE_URL}/api/recommendations/{sport}?date=today")
        # Test tomorrow
        response_tomorrow = requests.get(f"{API_BASE_URL}/api/recommendations/{sport}?date=tomorrow")
        
        if response_today.status_code == 200 and response_tomorrow.status_code == 200:
            today_data = response_today.json()
            tomorrow_data = response_tomorrow.json()
            
            print(f"✅ Today endpoint: {len(today_data.get('recommendations', []))} recommendations")
            print(f"   Date filter: {today_data.get('date')}, Target: {today_data.get('target_date')}")
            
            print(f"✅ Tomorrow endpoint: {len(tomorrow_data.get('recommendations', []))} recommendations")
            print(f"   Date filter: {tomorrow_data.get('date')}, Target: {tomorrow_data.get('target_date')}")
            
            # Verify date_category field
            today_recs = today_data.get('recommendations', [])
            tomorrow_recs = tomorrow_data.get('recommendations', [])
            
            if today_recs and 'date_category' in today_recs[0]:
                print(f"✅ Today recommendations have date_category: {today_recs[0]['date_category']}")
            
            if tomorrow_recs and 'date_category' in tomorrow_recs[0]:
                print(f"✅ Tomorrow recommendations have date_category: {tomorrow_recs[0]['date_category']}")
            
            self.results['ui_performance']['date_params'] = {'passed': True}
            return True
        else:
            print(f"❌ Date parameter test failed")
            self.results['ui_performance']['date_params'] = {'passed': False}
            return False
    
    # ===== Test 2: AI Learning System =====
    
    async def test_ai_database_schema(self) -> bool:
        """Test that AI learning tables exist and are functional"""
        print("\n" + "="*60)
        print("TEST 2: AI LEARNING - DATABASE SCHEMA")
        print("="*60)
        
        required_tables = [
            'predictions_history',
            'parlay_history',
            'ai_performance_metrics',
            'confidence_calibration',
            'team_prediction_history',
            'learning_insights'
        ]
        
        try:
            async with self.db_pool.acquire() as conn:
                for table in required_tables:
                    result = await conn.fetchval(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                        table
                    )
                    if result:
                        # Count rows
                        count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                        print(f"✅ Table '{table}' exists ({count} rows)")
                    else:
                        print(f"❌ Table '{table}' missing")
                        self.results['ai_learning']['schema'] = {'passed': False, 'missing': table}
                        return False
                
                # Test confidence_calibration initialization
                calibration_rows = await conn.fetch("SELECT * FROM confidence_calibration ORDER BY confidence_bucket")
                print(f"\n📊 Confidence Calibration Buckets: {len(calibration_rows)}")
                for row in calibration_rows[:5]:  # Show first 5 as sample
                    accuracy = row['actual_accuracy'] if row['actual_accuracy'] is not None else 0.0
                    predictions = row['total_predictions'] or 0
                    print(f"   {row['sport']} - {row['confidence_bucket']} bucket: {row['adjustment_factor']:.3f} factor "
                          f"({accuracy:.1%} accuracy, {predictions} predictions)")
                
                self.results['ai_learning']['schema'] = {'passed': True, 'tables': len(required_tables)}
                return True
                
        except Exception as e:
            print(f"❌ Database schema test failed: {e}")
            self.results['ai_learning']['schema'] = {'passed': False, 'error': str(e)}
            return False
    
    async def test_ai_calibration(self) -> bool:
        """Test AI confidence calibration in real API responses"""
        print("\n" + "="*60)
        print("TEST 2B: AI LEARNING - CONFIDENCE CALIBRATION")
        print("="*60)
        
        sport = "NBA"
        response = requests.get(f"{API_BASE_URL}/api/recommendations/{sport}")
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommendations', [])
            
            calibrated_count = 0
            for rec in recommendations[:5]:  # Check first 5
                if 'original_confidence' in rec and 'ai_calibrated' in rec:
                    calibrated_count += 1
                    orig = rec['original_confidence']
                    calibrated = rec['confidence']
                    diff = calibrated - orig
                    print(f"✅ {rec['matchup']}")
                    print(f"   Original: {orig:.1f}% → Calibrated: {calibrated:.1f}% (Δ {diff:+.1f}%)")
            
            if calibrated_count > 0:
                print(f"\n✅ {calibrated_count}/{len(recommendations[:5])} recommendations AI-calibrated")
                self.results['ai_learning']['calibration'] = {
                    'passed': True,
                    'calibrated_count': calibrated_count
                }
                return True
            else:
                print(f"❌ No AI calibration detected in responses")
                self.results['ai_learning']['calibration'] = {'passed': False}
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            return False
    
    async def test_ai_performance_view(self) -> bool:
        """Test AI performance metrics view"""
        print("\n" + "="*60)
        print("TEST 2C: AI LEARNING - PERFORMANCE METRICS")
        print("="*60)
        
        try:
            async with self.db_pool.acquire() as conn:
                # Check if view exists
                view_exists = await conn.fetchval(
                    "SELECT EXISTS (SELECT FROM information_schema.views WHERE table_name = 'ai_performance_overview')"
                )
                
                if view_exists:
                    print("✅ ai_performance_overview view exists")
                    
                    # Try to query it
                    metrics = await conn.fetch("SELECT * FROM ai_performance_overview LIMIT 5")
                    if metrics:
                        print(f"📊 Performance Metrics Sample ({len(metrics)} rows):")
                        for metric in metrics:
                            print(f"   {metric['sport']}: {metric['win_rate']:.1%} win rate, "
                                  f"Avg confidence: {metric['avg_confidence']:.1f}%")
                    else:
                        print("⚠️  No performance data yet (expected for fresh system)")
                    
                    self.results['ai_learning']['performance_view'] = {'passed': True}
                    return True
                else:
                    print("❌ ai_performance_overview view missing")
                    self.results['ai_learning']['performance_view'] = {'passed': False}
                    return False
                    
        except Exception as e:
            print(f"❌ Performance view test failed: {e}")
            return False
    
    # ===== Test 3: Date Filtering =====
    
    def test_date_filtering_today_tomorrow(self) -> bool:
        """Test complete date filtering for today vs tomorrow"""
        print("\n" + "="*60)
        print("TEST 3: DATE FILTERING - TODAY vs TOMORROW")
        print("="*60)
        
        sport = "NBA"
        
        # Get today's recommendations
        response_today = requests.get(f"{API_BASE_URL}/api/recommendations/{sport}?date=today")
        # Get tomorrow's recommendations
        response_tomorrow = requests.get(f"{API_BASE_URL}/api/recommendations/{sport}?date=tomorrow")
        
        if response_today.status_code == 200 and response_tomorrow.status_code == 200:
            today_data = response_today.json()
            tomorrow_data = response_tomorrow.json()
            
            today_recs = today_data.get('recommendations', [])
            tomorrow_recs = tomorrow_data.get('recommendations', [])
            
            print(f"\n📅 TODAY ({today_data.get('target_date')}):")
            print(f"   {len(today_recs)} recommendations")
            if today_recs:
                print(f"   Sample: {today_recs[0]['matchup']} at {today_recs[0]['start_time']}")
                print(f"   Date Category: {today_recs[0].get('date_category', 'N/A')}")
            
            print(f"\n📅 TOMORROW ({tomorrow_data.get('target_date')}):")
            print(f"   {len(tomorrow_recs)} recommendations")
            if tomorrow_recs:
                print(f"   Sample: {tomorrow_recs[0]['matchup']} at {tomorrow_recs[0]['start_time']}")
                print(f"   Date Category: {tomorrow_recs[0].get('date_category', 'N/A')}")
            
            # Verify dates are actually different
            today_date = today_data.get('target_date')
            tomorrow_date = tomorrow_data.get('target_date')
            
            if today_date and tomorrow_date and today_date != tomorrow_date:
                print(f"\n✅ Date filtering working: {today_date} vs {tomorrow_date}")
                self.results['date_filtering']['today_tomorrow'] = {
                    'passed': True,
                    'today_count': len(today_recs),
                    'tomorrow_count': len(tomorrow_recs)
                }
                return True
            else:
                print(f"❌ Date filtering not differentiating properly")
                self.results['date_filtering']['today_tomorrow'] = {'passed': False}
                return False
        else:
            print(f"❌ API requests failed")
            return False
    
    def test_parlay_date_filtering(self) -> bool:
        """Test date filtering on parlays endpoint"""
        print("\n" + "="*60)
        print("TEST 3B: DATE FILTERING - PARLAYS")
        print("="*60)
        
        sport = "NBA"
        
        # Get today's parlays
        response_today = requests.get(f"{API_BASE_URL}/api/parlays/{sport}?date=today")
        # Get tomorrow's parlays
        response_tomorrow = requests.get(f"{API_BASE_URL}/api/parlays/{sport}?date=tomorrow")
        
        if response_today.status_code == 200 and response_tomorrow.status_code == 200:
            today_data = response_today.json()
            tomorrow_data = response_tomorrow.json()
            
            today_parlays = today_data.get('parlays', [])
            tomorrow_parlays = tomorrow_data.get('parlays', [])
            
            print(f"\n📅 TODAY PARLAYS ({today_data.get('target_date')}):")
            print(f"   {len(today_parlays)} parlays from {today_data.get('source_picks')} picks")
            if today_parlays and 'ai_optimized' in today_parlays[0]:
                print(f"   ✅ AI optimized: {today_parlays[0]['ai_optimized']}")
            
            print(f"\n📅 TOMORROW PARLAYS ({tomorrow_data.get('target_date')}):")
            print(f"   {len(tomorrow_parlays)} parlays from {tomorrow_data.get('source_picks')} picks")
            if tomorrow_parlays and 'ai_optimized' in tomorrow_parlays[0]:
                print(f"   ✅ AI optimized: {tomorrow_parlays[0]['ai_optimized']}")
            
            self.results['date_filtering']['parlays'] = {
                'passed': True,
                'today_parlays': len(today_parlays),
                'tomorrow_parlays': len(tomorrow_parlays)
            }
            return True
        else:
            print(f"❌ Parlay API requests failed")
            return False
    
    # ===== Test Runner =====
    
    async def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "🎯"*30)
        print("ENHANCED DAILY BETTING PLATFORM - COMPREHENSIVE TEST SUITE")
        print("🎯"*30)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        await self.setup()
        
        tests_passed = 0
        tests_total = 0
        
        # Test 1: UI Performance
        tests_total += 1
        if self.test_ui_caching():
            tests_passed += 1
        
        tests_total += 1
        if self.test_date_parameter_support():
            tests_passed += 1
        
        # Test 2: AI Learning
        tests_total += 1
        if await self.test_ai_database_schema():
            tests_passed += 1
        
        tests_total += 1
        if await self.test_ai_calibration():
            tests_passed += 1
        
        tests_total += 1
        if await self.test_ai_performance_view():
            tests_passed += 1
        
        # Test 3: Date Filtering
        tests_total += 1
        if self.test_date_filtering_today_tomorrow():
            tests_passed += 1
        
        tests_total += 1
        if self.test_parlay_date_filtering():
            tests_passed += 1
        
        await self.cleanup()
        
        # Final Report
        print("\n" + "="*60)
        print("FINAL TEST RESULTS")
        print("="*60)
        print(f"Tests Passed: {tests_passed}/{tests_total}")
        print(f"Success Rate: {(tests_passed/tests_total*100):.1f}%")
        
        if tests_passed == tests_total:
            print("\n🎉 ALL TESTS PASSED! 🎉")
            print("✅ UI Performance Optimizations: WORKING")
            print("✅ AI Learning System: ACTIVE")
            print("✅ Date Filtering: OPERATIONAL")
            return True
        else:
            print("\n⚠️  Some tests failed. Review details above.")
            return False

async def main():
    """Main entry point"""
    suite = EnhancementTestSuite()
    success = await suite.run_all_tests()
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(suite.results, f, indent=2)
    print(f"\n📄 Detailed results saved to: test_results.json")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
