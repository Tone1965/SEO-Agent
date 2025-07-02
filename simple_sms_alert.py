"""
Simple SMS Alert using IFTTT (works with Digital Ocean)
No SMTP needed!
"""
import requests
import os

class SimpleSMSAlert:
    def __init__(self):
        # IFTTT Webhooks (free, reliable)
        self.ifttt_key = os.getenv('IFTTT_KEY', '')
        self.phone = os.getenv('ALERT_PHONE', '2058352631')
        
    def send_sms(self, message):
        """Send SMS using IFTTT"""
        if not self.ifttt_key:
            print("❌ IFTTT_KEY not set in .env")
            print("Get your free key at: https://ifttt.com/maker_webhooks")
            return False
            
        # IFTTT webhook URL
        url = f"https://maker.ifttt.com/trigger/seo_alert/with/key/{self.ifttt_key}"
        
        # Send the alert
        data = {
            "value1": message,
            "value2": self.phone,
            "value3": "SEO Agent Alert"
        }
        
        try:
            response = requests.post(url, json=data, timeout=5)
            if response.status_code == 200:
                print(f"✅ SMS sent to {self.phone}")
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

# Test function
def test_sms():
    print("=" * 50)
    print("SIMPLE SMS TEST")
    print("=" * 50)
    
    sms = SimpleSMSAlert()
    
    # Test message
    message = "🚨 SEO Agent Alert: API at 92% capacity!"
    
    print(f"\nSending test SMS to: {sms.phone}")
    print(f"Message: {message}")
    
    if sms.send_sms(message):
        print("\n✅ Check your phone!")
    else:
        print("\n❌ SMS failed")
        print("\nTo set up IFTTT (5 minutes):")
        print("1. Go to https://ifttt.com")
        print("2. Sign up free")
        print("3. Create applet: Webhooks → SMS")
        print("4. Get your key from Webhooks settings")
        print("5. Add to .env: IFTTT_KEY=your-key-here")

if __name__ == "__main__":
    test_sms()