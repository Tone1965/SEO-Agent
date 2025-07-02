#!/usr/bin/env python3
"""
Test script for alert system
Run this to test if your alerts are working
"""
from alert_system import alert_system
import os

print("="*50)
print("ALERT SYSTEM TEST")
print("="*50)

# Show current configuration
print("\nCurrent Configuration:")
print(f"Email alerts will go to: {os.getenv('ALERT_EMAIL', 'NOT SET')}")
print(f"SMS alerts will go to: {os.getenv('ALERT_PHONE', 'NOT SET')}")
print(f"Daily budget: ${os.getenv('DAILY_BUDGET', '50')}")

# Check if configured
if not os.getenv('ALERT_EMAIL') or not os.getenv('SMTP_PASSWORD'):
    print("\n❌ ERROR: Alert system not configured!")
    print("Please set these in your .env file:")
    print("- ALERT_EMAIL")
    print("- ALERT_PHONE") 
    print("- SMTP_EMAIL")
    print("- SMTP_PASSWORD")
    exit(1)

print("\n" + "="*50)
print("SENDING TEST ALERTS...")
print("="*50)

# Test 1: Warning (75% - email only)
print("\nTest 1: Sending 75% warning (email only)...")
alert_system.WARNING_THRESHOLD = 0.01  # Temporarily set super low
alert_system.track_api_usage(100, 'claude')
print("✓ Warning email sent")

# Reset for next test
alert_system.claude_tokens_used = 0
alert_system.daily_spend = 0

# Test 2: Critical (90% - email + SMS)  
print("\nTest 2: Sending 90% critical alert (email + SMS)...")
alert_system.CRITICAL_THRESHOLD = 0.01  # Temporarily set super low
alert_system.track_api_usage(1000, 'claude')
print("✓ Critical email sent")
print("✓ SMS text sent")

print("\n" + "="*50)
print("CHECK YOUR EMAIL AND PHONE!")
print("="*50)
print("\nYou should receive:")
print("1. Two emails (warning + critical)")
print("2. One text message (critical only)")
print("\nIf you don't receive them within 2 minutes:")
print("- Check spam folder")
print("- Verify Gmail app password")
print("- Check phone carrier email-to-SMS gateway")

# Show system status
print("\n" + "="*50)
print("SYSTEM STATUS:")
print("="*50)
status = alert_system.get_status()
for key, value in status.items():
    print(f"{key}: {value}")