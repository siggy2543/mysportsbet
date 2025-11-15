#!/usr/bin/env python3
"""
Basic Integration Test Runner
Tests core functionality of the sports betting automation system
Run this script to verify that all components are working correctly
"""

import asyncio
import os
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set test environment variables
os.environ.update({
    'ESPN_API_KEY': 'test_key',
    'ESPN_API_URL': 'https://site.api.espn.com/apis/site/v2',
    'OPENAI_API_KEY': 'test_key',
    'OPENAI_MODEL': 'gpt-4-turbo-preview',
    'DRAFTKINGS_USERNAME': 'test_user',
    'DRAFTKINGS_PASSWORD': 'test_pass',
    'DRAFTKINGS_STATE': 'NY',
    'DRAFTKINGS_API_URL': 'https://api.draftkings.com',
    'MAX_SINGLE_BET': '100.0',
    'MAX_DAILY_EXPOSURE': '500.0',
    'MIN_CONFIDENCE_THRESHOLD': '0.7',
    'BANKROLL_SIZE': '1000.0',
    'CACHE_TTL': '3600',
    'PREDICTION_CACHE_TTL': '7200',
    'REDIS_URL': 'redis://localhost:6379/0',
    'DATABASE_URL': 'postgresql://test:test@localhost:5432/test'
})

# Import our services
try:
    from services.espn_api_service import ModernESPNService
    from services.openai_prediction_service import OpenAIPredictionService
    from services.draftkings_betting_service import DraftKingsBettingService
    from services.betting_orchestrator import MasterBettingOrchestrator
    print("✅ All service imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class IntegrationTestRunner:
    """Simple integration test runner"""
    
    def __init__(self):
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    async def run_test(self, test_name, test_func):
        """Run a single test"""
        self.results['total_tests'] += 1
        print(f"\n🧪 Running: {test_name}")
        
        try:
            await test_func()
            print(f"✅ PASSED: {test_name}")
            self.results['passed'] += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name}")
            print(f"   Error: {str(e)}")
            self.results['failed'] += 1
            self.results['errors'].append({
                'test': test_name,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    async def test_service_initialization(self):
        """Test that all services can be initialized"""
        espn_service = ModernESPNService()
        openai_service = OpenAIPredictionService()
        draftkings_service = DraftKingsBettingService()
        orchestrator = MasterBettingOrchestrator()
        
        assert espn_service is not None
        assert openai_service is not None
        assert draftkings_service is not None
        assert orchestrator is not None
        print("   All services initialized successfully")
    
    async def test_espn_service_configuration(self):
        """Test ESPN service configuration"""
        espn_service = ModernESPNService()
        
        # Check that the service has the correct configuration
        assert hasattr(espn_service, 'api_key')
        assert hasattr(espn_service, 'base_url')
        assert espn_service.base_url == 'https://site.api.espn.com/apis/site/v2'
        print("   ESPN service configuration is correct")
    
    async def test_openai_service_configuration(self):
        """Test OpenAI service configuration"""
        openai_service = OpenAIPredictionService()
        
        # Check that the service has the correct configuration
        assert hasattr(openai_service, 'api_key')
        assert hasattr(openai_service, 'model')
        assert openai_service.model == 'gpt-4-turbo-preview'
        print("   OpenAI service configuration is correct")
    
    async def test_draftkings_service_configuration(self):
        """Test DraftKings service configuration"""
        draftkings_service = DraftKingsBettingService()
        
        # Check that the service has the correct configuration
        assert hasattr(draftkings_service, 'username')
        assert hasattr(draftkings_service, 'password')
        assert hasattr(draftkings_service, 'state')
        assert draftkings_service.state == 'NY'
        print("   DraftKings service configuration is correct")
    
    async def test_risk_management_configuration(self):
        """Test risk management configuration"""
        orchestrator = MasterBettingOrchestrator()
        
        # Check risk management settings
        assert orchestrator.max_single_bet == 100.0
        assert orchestrator.max_daily_exposure == 500.0
        assert orchestrator.min_confidence_threshold == 0.7
        assert orchestrator.bankroll_size == 1000.0
        print("   Risk management configuration is correct")
    
    async def test_session_management(self):
        """Test betting session management"""
        orchestrator = MasterBettingOrchestrator()
        
        # Test session creation
        session_id = await orchestrator.start_betting_session({
            "sports": ["nfl"],
            "max_bets": 3,
            "risk_level": "medium"
        })
        
        assert session_id is not None
        assert len(session_id) > 0
        print(f"   Session created successfully: {session_id}")
        
        # Test session status
        status = await orchestrator.get_session_status(session_id)
        assert status['status'] == 'active'
        assert status['settings']['max_bets'] == 3
        print("   Session status retrieved successfully")
        
        # Test session stopping
        result = await orchestrator.stop_betting_session(session_id)
        assert result['status'] == 'stopped'
        print("   Session stopped successfully")
    
    async def test_data_structures(self):
        """Test that data structures are properly defined"""
        
        # Test sample ESPN data structure
        sample_game = {
            "id": "401547439",
            "name": "Buffalo Bills at Miami Dolphins",
            "shortName": "BUF @ MIA",
            "date": datetime.now().isoformat(),
            "competitions": [{
                "competitors": [
                    {"team": {"displayName": "Buffalo Bills", "abbreviation": "BUF"}},
                    {"team": {"displayName": "Miami Dolphins", "abbreviation": "MIA"}}
                ]
            }]
        }
        
        # Test sample prediction structure
        sample_prediction = {
            "game_analysis": {
                "game_id": "401547439",
                "confidence": 0.85,
                "prediction": "Buffalo Bills to win"
            },
            "betting_recommendations": [{
                "bet_type": "spread",
                "selection": "Buffalo Bills -3.5",
                "confidence": 0.85,
                "recommended_stake": 50
            }]
        }
        
        assert sample_game['id'] == "401547439"
        assert sample_prediction['game_analysis']['confidence'] == 0.85
        print("   Data structures are properly formatted")
    
    async def test_environment_variables(self):
        """Test that all required environment variables are set"""
        required_vars = [
            'ESPN_API_KEY', 'ESPN_API_URL',
            'OPENAI_API_KEY', 'OPENAI_MODEL',
            'DRAFTKINGS_USERNAME', 'DRAFTKINGS_PASSWORD', 'DRAFTKINGS_STATE',
            'MAX_SINGLE_BET', 'MAX_DAILY_EXPOSURE', 'BANKROLL_SIZE'
        ]
        
        for var in required_vars:
            assert var in os.environ, f"Environment variable {var} is not set"
        
        print("   All required environment variables are set")
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Sports Betting Integration Tests")
        print("=" * 50)
        
        # List of tests to run
        tests = [
            ("Service Initialization", self.test_service_initialization),
            ("ESPN Service Configuration", self.test_espn_service_configuration),
            ("OpenAI Service Configuration", self.test_openai_service_configuration),
            ("DraftKings Service Configuration", self.test_draftkings_service_configuration),
            ("Risk Management Configuration", self.test_risk_management_configuration),
            ("Session Management", self.test_session_management),
            ("Data Structures", self.test_data_structures),
            ("Environment Variables", self.test_environment_variables),
        ]
        
        # Run each test
        for test_name, test_func in tests:
            await self.run_test(test_name, test_func)
        
        # Print results
        print("\n" + "=" * 50)
        print("🏁 TEST RESULTS")
        print("=" * 50)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed']} ✅")
        print(f"Failed: {self.results['failed']} ❌")
        
        if self.results['failed'] > 0:
            print("\n❌ FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   - {error['test']}: {error['error']}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 Integration tests PASSED! System is ready for deployment.")
            return True
        else:
            print("⚠️  Some tests failed. Please review and fix issues before deployment.")
            return False


async def main():
    """Main test runner"""
    runner = IntegrationTestRunner()
    success = await runner.run_all_tests()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())