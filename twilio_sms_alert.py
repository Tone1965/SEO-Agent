"""
Direct SMS using Twilio (most reliable)
Works everywhere, including Digital Ocean
"""
import os
from datetime import datetime

def send_twilio_sms(message):
    """Send SMS directly via Twilio"""
    # Twilio credentials from .env
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_phone = os.getenv('TWILIO_PHONE')  # Your Twilio number
    to_phone = os.getenv('YOUR_PHONE', '+12058352631')  # Your cell
    
    if not all([account_sid, auth_token, from_phone]):
        print("❌ Twilio not configured!")
        print("\nTo set up Twilio (10 minutes):")
        print("1. Sign up at twilio.com (free trial includes $15 credit)")
        print("2. Get a phone number ($1/month)")
        print("3. Add to .env:")
        print("   TWILIO_ACCOUNT_SID=your-sid")
        print("   TWILIO_AUTH_TOKEN=your-token")
        print("   TWILIO_PHONE=+1234567890")
        print("   YOUR_PHONE=+12058352631")
        return False
    
    try:
        # Install: pip install twilio
        from twilio.rest import Client
        
        client = Client(account_sid, auth_token)
        
        # Send SMS
        message = client.messages.create(
            body=f"{message}\n\nTime: {datetime.now().strftime('%H:%M')}",
            from_=from_phone,
            to=to_phone
        )
        
        print(f"✅ SMS sent! ID: {message.sid}")
        return True
        
    except ImportError:
        print("❌ Twilio not installed")
        print("Run: pip install twilio")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Test it
if __name__ == "__main__":
    print("=" * 50)
    print("TWILIO SMS TEST")
    print("=" * 50)
    
    test_message = """🚨 SEO Agent Critical Alert:
- Claude API: 92% capacity
- Memory: 89% used
- Daily budget: $47/$50"""
    
    print(f"\nSending test SMS...")
    print(f"Message:\n{test_message}")
    
    if send_twilio_sms(test_message):
        print("\n✅ Check your phone!")
    else:
        print("\n❌ See setup instructions above")