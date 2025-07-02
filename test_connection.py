#!/usr/bin/env python3
"""
Test network connectivity for alerts
"""
import socket
import ssl
import os

print("Network Connectivity Test")
print("=" * 50)

# Test basic internet
print("\n1. Testing basic internet connection...")
try:
    socket.create_connection(("google.com", 80), timeout=5)
    print("✓ Internet connection: OK")
except Exception as e:
    print(f"✗ Internet connection: FAILED - {e}")

# Test Gmail SMTP
print("\n2. Testing Gmail SMTP connection...")
try:
    sock = socket.create_connection(("smtp.gmail.com", 587), timeout=5)
    print("✓ Gmail SMTP port 587: OK")
    sock.close()
except Exception as e:
    print(f"✗ Gmail SMTP: FAILED - {e}")

# Test alternative Gmail port
print("\n3. Testing Gmail SMTP port 465 (SSL)...")
try:
    sock = socket.create_connection(("smtp.gmail.com", 465), timeout=5)
    print("✓ Gmail SMTP port 465: OK")
    sock.close()
except Exception as e:
    print(f"✗ Gmail SMTP 465: FAILED - {e}")

# Test DNS resolution
print("\n4. Testing DNS resolution...")
try:
    ip = socket.gethostbyname("smtp.gmail.com")
    print(f"✓ DNS resolution: OK (smtp.gmail.com = {ip})")
except Exception as e:
    print(f"✗ DNS resolution: FAILED - {e}")

# Show current settings
print("\n5. Current Alert Settings:")
print(f"ALERT_EMAIL: {os.getenv('ALERT_EMAIL', 'NOT SET')}")
print(f"SMTP_EMAIL: {os.getenv('SMTP_EMAIL', 'NOT SET')}")
print(f"SMTP_PASSWORD: {'SET' if os.getenv('SMTP_PASSWORD') else 'NOT SET'}")

print("\n" + "=" * 50)
print("Diagnosis:")
if all([
    os.getenv('ALERT_EMAIL'),
    os.getenv('SMTP_EMAIL'),
    os.getenv('SMTP_PASSWORD')
]):
    print("✓ Environment variables are set")
else:
    print("✗ Missing environment variables")

print("\nIf Gmail SMTP failed, try:")
print("1. Check if Digital Ocean blocks port 587/465")
print("2. Use a different SMTP service (SendGrid, etc.)")
print("3. Use Twilio for direct SMS instead")