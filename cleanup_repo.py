#!/usr/bin/env python3
"""
Repository Cleanup Script
Removes duplicate files, consolidates documentation, and optimizes structure
"""

import os
import shutil
from pathlib import Path

# Files to remove (duplicates, outdated, or unnecessary)
FILES_TO_REMOVE = [
    # Duplicate success reports
    'COMPLETE_SYSTEM_SUCCESS.md',
    'DEPLOYMENT_SUCCESS_FINAL.md',
    'ENHANCED_DAILY_BETTING_SUCCESS.md',
    'ENHANCED_LIVE_BETTING_SUCCESS.md',
    'FINAL_STATUS_REPORT.md',
    'FINAL_SUCCESS_REPORT.md',
    'GITHUB_PUSH_SUCCESS.md',
    'STABLE_PLATFORM_SUCCESS.md',
    'ERROR_RESOLUTION_REPORT.md',
    
    # Duplicate deployment guides
    'DEPLOYMENT_RESTART_GUIDE.md',
    'IMMEDIATE_DEPLOY_GUIDE.md',
    'DOCKER_FIX_GUIDE.md',
    
    # Old deployment scripts
    'deploy_enhanced.py',
    'production_restart_deploy.py',
    'robust_docker_deploy.py',
    'simple_deploy.sh',
    
    # Duplicate batch files
    'DOCKER_DEPLOY.bat',
    'PRODUCTION_RESTART.bat',
    'QUICK_DOCKER_REBUILD.bat',
    'QUICK_RESTART.bat',
    'deploy_guide.bat',
    'manual_start_guide.bat',
    'restart_prod.bat',
    'shutdown_prod.bat',
    'start_api.bat',
    
    # Duplicate validation scripts
    'simple_validate.py',
    'validate_deployment.py',
    'validate_fixed_bets.py',
    'validate_platform.py',
    'validate_system.py',
    'check_system_status.py',
    'final_system_status.py',
    
    # Old test files
    'run_mock_tests.py',
    'test_frontend_sports.py',
    'test_live_data.py',
    
    # Duplicate SSL setup files
    'setup-ssl-windows-fixed.bat',
    'setup-ssl-windows.bat',
    'quick-ssl-check.sh',
    'SSL_SETUP.md',
    'WINDOWS_SSL_SETUP.md',
    
    # Old guide files
    'sports_data_setup_guide.py',
    'PRODUCTION_SCRIPTS_README.md',
    'health-check.ps1',
    
    # System files
    'bash.exe.stackdump'
]

# Directories to clean or remove
DIRS_TO_CLEAN = {
    'logs': 'keep_structure',  # Keep directory, clean old logs
    'monitoring/prometheus.yml': 'remove_if_empty',
    'nginx/nginx.conf': 'keep_main',
    'nginx/ssl;C': 'remove'  # Invalid directory
}

def remove_file(filepath):
    """Safely remove a file"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"✅ Removed: {filepath}")
            return True
        else:
            print(f"⏭️  Skipped (not found): {filepath}")
            return False
    except Exception as e:
        print(f"❌ Error removing {filepath}: {e}")
        return False

def remove_directory(dirpath):
    """Safely remove a directory"""
    try:
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
            print(f"✅ Removed directory: {dirpath}")
            return True
        else:
            print(f"⏭️  Skipped (not found): {dirpath}")
            return False
    except Exception as e:
        print(f"❌ Error removing directory {dirpath}: {e}")
        return False

def clean_logs_directory():
    """Clean old log files but keep structure"""
    logs_dir = Path('logs')
    if not logs_dir.exists():
        return
    
    print("\n🧹 Cleaning logs directory...")
    for subdir in logs_dir.iterdir():
        if subdir.is_dir():
            for logfile in subdir.glob('*'):
                if logfile.is_file():
                    try:
                        logfile.unlink()
                        print(f"  ✅ Removed log: {logfile}")
                    except Exception as e:
                        print(f"  ❌ Error: {e}")

def consolidate_documentation():
    """Keep only essential documentation"""
    print("\n📚 Consolidating documentation...")
    
    essential_docs = [
        'README.md',
        'LICENSE',
        'DEPLOYMENT_SUCCESS_ENHANCEMENTS.md',
        'QUICK_START_ENHANCEMENTS.md'
    ]
    
    print("Essential documentation:")
    for doc in essential_docs:
        if os.path.exists(doc):
            print(f"  ✅ Keeping: {doc}")
        else:
            print(f"  ⚠️  Missing: {doc}")

def main():
    """Main cleanup execution"""
    print("="*60)
    print("REPOSITORY CLEANUP SCRIPT")
    print("="*60)
    print("\n🎯 Removing duplicate and outdated files...\n")
    
    removed_count = 0
    skipped_count = 0
    
    # Remove files
    for filename in FILES_TO_REMOVE:
        if remove_file(filename):
            removed_count += 1
        else:
            skipped_count += 1
    
    # Remove invalid directories
    if os.path.exists('nginx/ssl;C'):
        if remove_directory('nginx/ssl;C'):
            removed_count += 1
    
    # Clean logs
    clean_logs_directory()
    
    # Consolidate documentation
    consolidate_documentation()
    
    print("\n" + "="*60)
    print("CLEANUP SUMMARY")
    print("="*60)
    print(f"✅ Files removed: {removed_count}")
    print(f"⏭️  Files skipped: {skipped_count}")
    print(f"📦 Repository size optimized")
    print(f"🎯 Essential files preserved")
    print("\n✨ Cleanup complete!")

if __name__ == "__main__":
    main()
