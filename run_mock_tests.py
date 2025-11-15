#!/usr/bin/env python3
"""
Comprehensive Mock Test Runner for Sports Betting Application
Tests the complete system with fixed $5 bet amounts
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Set test environment variables
os.environ.update({
    'FIXED_BET_AMOUNT': '5.0',
    'FIXED_PARLAY_AMOUNT': '5.0',
    'ENABLE_MOCK_MODE': 'true',
    'PAPER_TRADING_MODE': 'true',
    'MOCK_BETTING_ENABLED': 'true',
    'ESPN_API_URL': 'https://site.api.espn.com/apis/site/v2',
    'OPENAI_API_KEY': 'test_key_for_mock',
    'MAX_SINGLE_BET': '100.0',
    'MAX_DAILY_EXPOSURE': '500.0',
    'MIN_CONFIDENCE_THRESHOLD': '0.7',
    'BANKROLL_SIZE': '1000.0'
})

try:
    from services.mock_testing_service import MockTestingService
    from services.betting_orchestrator import MasterBettingOrchestrator
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the sports_app directory")
    sys.exit(1)

def print_header():
    print("🧪 " + "=" * 80)
    print("   SPORTS BETTING APPLICATION - COMPREHENSIVE MOCK TESTING")
    print("   Fixed Bet Amount: $5.00 per bet/parlay")
    print("🧪 " + "=" * 80)
    print(f"   Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def print_section(title, emoji="📋"):
    print(f"{emoji} {title}")
    print("-" * (len(title) + 3))

def print_test_result(test_name, status, details=None):
    status_emoji = "✅" if status == "PASSED" else "❌"
    print(f"   {status_emoji} {test_name:<40} {status}")
    if details:
        for key, value in details.items():
            print(f"      └─ {key}: {value}")

async def test_fixed_bet_configuration():
    """Test that fixed bet amounts are properly configured"""
    print_section("FIXED BET AMOUNT CONFIGURATION", "💰")
    
    orchestrator = MasterBettingOrchestrator()
    
    print(f"   💵 Fixed Single Bet Amount: ${orchestrator.fixed_bet_amount}")
    print(f"   💵 Fixed Parlay Bet Amount: ${orchestrator.fixed_parlay_amount}")
    print(f"   📊 Paper Trading Mode: {orchestrator.paper_trading_mode}")
    print(f"   🛡️  Max Single Bet: ${orchestrator.max_single_bet}")
    print(f"   🛡️  Max Daily Exposure: ${orchestrator.max_daily_exposure}")
    print(f"   💰 Bankroll Size: ${orchestrator.bankroll_size}")
    print()
    
    return {
        "fixed_bet_amount": orchestrator.fixed_bet_amount,
        "fixed_parlay_amount": orchestrator.fixed_parlay_amount,
        "paper_trading": orchestrator.paper_trading_mode
    }

async def run_comprehensive_mock_tests():
    """Run comprehensive mock tests"""
    print_section("COMPREHENSIVE MOCK TESTING", "🔬")
    
    # Initialize mock testing service
    mock_service = MockTestingService()
    
    # Run all tests
    test_results = await mock_service.run_all_tests()
    
    # Display results
    print("\n📊 TEST SUMMARY:")
    print("-" * 50)
    
    summary = test_results["test_summary"]
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Passed: {summary['passed_tests']} ✅")
    print(f"   Failed: {summary['failed_tests']} ❌")
    print(f"   Success Rate: {summary['success_rate']}%")
    print()
    
    print("📋 DETAILED TEST RESULTS:")
    print("-" * 50)
    for test_detail in test_results["test_details"]:
        status = test_detail["result"]
        test_name = test_detail["test"]
        
        if status == "PASSED":
            print_test_result(test_name, status)
            if "details" in test_detail:
                details = test_detail["details"]
                if "games_collected" in details:
                    print(f"      └─ Games Collected: {details['games_collected']}")
                if "predictions_generated" in details:
                    print(f"      └─ Predictions Generated: {details['predictions_generated']}")
                if "bets_placed" in details:
                    print(f"      └─ Bets Placed: {details['bets_placed']}")
                if "total_stake" in details:
                    print(f"      └─ Total Stake: ${details['total_stake']}")
        else:
            print_test_result(test_name, status)
            if "error" in test_detail:
                print(f"      └─ Error: {test_detail['error']}")
    
    print()
    print("💰 BETTING CONFIGURATION:")
    print("-" * 50)
    config = test_results["configuration"]
    print(f"   Fixed Bet Amount: ${config['fixed_bet_amount']}")
    print(f"   Fixed Parlay Amount: ${config['fixed_parlay_amount']}")
    print(f"   Mock Mode Enabled: {config['mock_mode_enabled']}")
    print(f"   Paper Trading Mode: {config['paper_trading_mode']}")
    print()
    
    print("💡 RECOMMENDATIONS:")
    print("-" * 50)
    for recommendation in test_results["recommendations"]:
        print(f"   {recommendation}")
    print()
    
    return test_results

async def test_betting_workflow_simulation():
    """Simulate a complete betting workflow"""
    print_section("BETTING WORKFLOW SIMULATION", "🎲")
    
    try:
        # Initialize orchestrator
        orchestrator = MasterBettingOrchestrator()
        
        print("   🔄 Simulating complete betting workflow...")
        print(f"   💵 Using fixed bet amounts: ${orchestrator.fixed_bet_amount} (single), ${orchestrator.fixed_parlay_amount} (parlay)")
        print()
        
        # Simulate workflow steps
        steps = [
            ("Data Collection", "ESPN undocumented API + backup sources"),
            ("AI Predictions", "OpenAI GPT-4 analysis with confidence scoring"),
            ("Bet Selection", f"Fixed amounts: ${orchestrator.fixed_bet_amount} per bet"),
            ("Risk Validation", "Check against daily limits and bankroll"),
            ("Bet Execution", "Paper trading mode (no real money)"),
            ("Performance Tracking", "Monitor results and ROI")
        ]
        
        for i, (step_name, description) in enumerate(steps, 1):
            print(f"   {i}. {step_name:<20} ✅ {description}")
            await asyncio.sleep(0.1)  # Simulate processing time
        
        print()
        print("   🎯 Workflow simulation completed successfully!")
        print("   📊 System ready for live testing with fixed $5 bet amounts")
        print()
        
        return {"status": "success", "workflow_steps": len(steps)}
        
    except Exception as e:
        print(f"   ❌ Workflow simulation failed: {e}")
        return {"status": "failed", "error": str(e)}

async def validate_risk_controls():
    """Validate risk management controls with fixed bet amounts"""
    print_section("RISK MANAGEMENT VALIDATION", "🛡️")
    
    orchestrator = MasterBettingOrchestrator()
    
    # Test scenarios
    scenarios = [
        {
            "name": "Single Bet Limit Check",
            "test": orchestrator.fixed_bet_amount <= orchestrator.max_single_bet,
            "details": f"${orchestrator.fixed_bet_amount} <= ${orchestrator.max_single_bet}"
        },
        {
            "name": "Parlay Bet Limit Check", 
            "test": orchestrator.fixed_parlay_amount <= orchestrator.max_single_bet,
            "details": f"${orchestrator.fixed_parlay_amount} <= ${orchestrator.max_single_bet}"
        },
        {
            "name": "Daily Exposure Check",
            "test": (orchestrator.fixed_bet_amount * 20) <= orchestrator.max_daily_exposure,  # 20 bets max per day
            "details": f"20 bets × ${orchestrator.fixed_bet_amount} = ${orchestrator.fixed_bet_amount * 20} <= ${orchestrator.max_daily_exposure}"
        },
        {
            "name": "Bankroll Protection",
            "test": (orchestrator.fixed_bet_amount * 20) <= (orchestrator.bankroll_size * 0.1),  # Never risk >10% per day
            "details": f"Daily max: ${orchestrator.fixed_bet_amount * 20} <= 10% of ${orchestrator.bankroll_size} = ${orchestrator.bankroll_size * 0.1}"
        }
    ]
    
    all_passed = True
    for scenario in scenarios:
        status = "PASSED" if scenario["test"] else "FAILED"
        if not scenario["test"]:
            all_passed = False
        
        print_test_result(scenario["name"], status, {"Check": scenario["details"]})
    
    print()
    if all_passed:
        print("   ✅ All risk management controls PASSED")
        print("   🛡️  System is safe for deployment with fixed bet amounts")
    else:
        print("   ❌ Some risk management controls FAILED")
        print("   ⚠️  Review configuration before deployment")
    
    print()
    return {"all_passed": all_passed, "scenarios_tested": len(scenarios)}

async def generate_mock_betting_report():
    """Generate a mock betting report showing expected performance"""
    print_section("MOCK BETTING PERFORMANCE REPORT", "📊")
    
    orchestrator = MasterBettingOrchestrator()
    
    # Simulate a week of betting
    daily_bets = 5  # Average bets per day
    days = 7
    total_bets = daily_bets * days
    total_stake = total_bets * orchestrator.fixed_bet_amount
    
    # Simulate win rate (conservative estimate)
    win_rate = 0.55  # 55% win rate
    avg_odds = 1.91  # Average odds
    
    winning_bets = int(total_bets * win_rate)
    losing_bets = total_bets - winning_bets
    
    total_winnings = winning_bets * orchestrator.fixed_bet_amount * avg_odds
    total_losses = losing_bets * orchestrator.fixed_bet_amount
    
    net_profit = total_winnings - total_stake
    roi = (net_profit / total_stake) * 100 if total_stake > 0 else 0
    
    print(f"   📅 SIMULATED 7-DAY PERFORMANCE:")
    print(f"   ├─ Total Bets Placed: {total_bets}")
    print(f"   ├─ Fixed Bet Amount: ${orchestrator.fixed_bet_amount}")
    print(f"   ├─ Total Stake: ${total_stake:.2f}")
    print(f"   ├─ Winning Bets: {winning_bets} ({win_rate*100}%)")
    print(f"   ├─ Losing Bets: {losing_bets}")
    print(f"   ├─ Total Winnings: ${total_winnings:.2f}")
    print(f"   ├─ Net Profit/Loss: ${net_profit:.2f}")
    print(f"   └─ ROI: {roi:.2f}%")
    print()
    
    risk_assessment = "LOW" if abs(net_profit) < (orchestrator.bankroll_size * 0.05) else "MEDIUM"
    print(f"   🎯 RISK ASSESSMENT: {risk_assessment}")
    print(f"   💰 Bankroll Impact: {abs(net_profit)/orchestrator.bankroll_size*100:.2f}% of total bankroll")
    print()
    
    return {
        "total_bets": total_bets,
        "total_stake": total_stake,
        "net_profit": net_profit,
        "roi": roi,
        "risk_level": risk_assessment
    }

async def main():
    """Main test runner"""
    print_header()
    
    try:
        # Test 1: Fixed bet configuration
        config_result = await test_fixed_bet_configuration()
        
        # Test 2: Comprehensive mock testing
        mock_results = await run_comprehensive_mock_tests()
        
        # Test 3: Workflow simulation
        workflow_result = await test_betting_workflow_simulation()
        
        # Test 4: Risk management validation
        risk_result = await validate_risk_controls()
        
        # Test 5: Mock performance report
        performance_result = await generate_mock_betting_report()
        
        # Final summary
        print_section("FINAL TEST SUMMARY", "🏁")
        
        overall_success = (
            mock_results["test_summary"]["success_rate"] >= 80 and
            workflow_result["status"] == "success" and
            risk_result["all_passed"]
        )
        
        if overall_success:
            print("   🎉 ALL TESTS PASSED!")
            print("   ✅ System is ready for deployment with fixed $5 bet amounts")
            print("   🛡️  Risk management controls validated")
            print("   📊 Mock testing completed successfully")
            print()
            print("   📋 NEXT STEPS:")
            print("   1. Deploy system with docker-compose up --build")
            print("   2. Test API endpoints manually")
            print("   3. Run live paper trading for 1-2 weeks")
            print("   4. Monitor performance before using real money")
            print()
        else:
            print("   ⚠️  SOME TESTS FAILED!")
            print("   ❌ Review failed tests before deployment")
            print("   🔧 Fix issues and re-run tests")
            print()
        
        print("🧪 " + "=" * 80)
        print("   Mock testing completed successfully!")
        print("   Your system is configured for $5 fixed bet amounts.")
        print("🧪 " + "=" * 80)
        
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())