# 📱 Alert System Setup Guide

## Quick Setup (15 minutes)

### 1. Add to your .env file:
```bash
# Alert Configuration
ALERT_EMAIL=your-email@gmail.com
ALERT_PHONE=2055551234@txt.att.net  # Your phone's email-to-SMS
SMTP_EMAIL=your-gmail@gmail.com      # Gmail to send FROM
SMTP_PASSWORD=your-app-password      # Gmail app password (not regular password!)
DAILY_BUDGET=50                      # Your daily $ limit
```

### 2. Email-to-SMS Gateways by Carrier:
- **AT&T**: `number@txt.att.net`
- **Verizon**: `number@vtext.com`
- **T-Mobile**: `number@tmomail.net`
- **Sprint**: `number@messaging.sprintpcs.com`

Example: If your number is (205) 555-1234 on AT&T:
`ALERT_PHONE=2055551234@txt.att.net`

### 3. Get Gmail App Password:
1. Go to https://myaccount.google.com/security
2. Enable 2-factor authentication
3. Search for "App passwords"
4. Generate new app password
5. Use this as SMTP_PASSWORD (not your regular password!)

### 4. Integrate into your main.py:

```python
# At the top of main.py
from alert_system import alert_system

# In your AIClient class, after each API call:
async def call_claude(self, prompt):
    response = await self.claude_client.messages.create(...)
    
    # Track usage for alerts
    tokens = response.usage.total_tokens
    alert_system.track_api_usage(tokens, service='claude')
    
    return response

# Same for OpenAI:
async def call_openai(self, prompt):
    response = await self.openai_client.chat.completions.create(...)
    
    # Track usage
    tokens = response.usage.total_tokens
    alert_system.track_api_usage(tokens, service='openai')
    
    return response
```

### 5. Test your alerts:
```python
# Run this to test:
python -c "
from alert_system import alert_system
# Force a test alert
alert_system.CRITICAL_THRESHOLD = 0.01  # Set super low
alert_system.track_api_usage(1000, 'claude')  # Trigger alert
"
```

## What You'll Get

### 75% Warning (Email only):
```
Subject: ⚠️ Warning: SEO Agent at capacity

⚠️ WARNINGS (75%+):

💰 Daily Budget: At 75% of $50.00
Details: Spent $37.50 today

⚠️ Claude API: At 78% of rate limit
Details: 31,200/40,000 tokens

Time: 2025-01-02 14:30:45
```

### 90% Critical (Email + SMS):
```
SMS Text:
🚨 SEO Agent Critical:
- 🚨 MEMORY: At 92% capacity!
- 🚨 DAILY BUDGET: At 91% of $50!
```

## Auto-Actions at 90%

The system automatically:
- **API Limits**: Pauses for 30 seconds
- **Memory**: Triggers garbage collection
- **Budget**: Switches to economy mode
- **Disk**: Suggests cleanup

## Monitor Status Anytime

```python
# Add this endpoint to main.py
@app.route('/api/system-status')
def system_status():
    return jsonify(alert_system.get_status())
```

Returns:
```json
{
    "claude_usage": "45%",
    "openai_usage": "23%", 
    "memory": "67%",
    "disk": "43%",
    "daily_spend": "$23.45",
    "budget_used": "47%"
}
```

## Troubleshooting

**Not getting emails?**
- Check spam folder
- Verify Gmail app password (not regular password)
- Make sure 2FA is enabled on Gmail

**Not getting texts?**
- Verify carrier email-to-SMS gateway
- Some carriers block automated texts
- Try Twilio for guaranteed delivery

**Too many alerts?**
- Adjust WARNING_THRESHOLD to 0.85 (85%)
- Increase alert intervals in _already_alerted()

## Cost to Run
- Email alerts: FREE
- Email-to-SMS: FREE (carrier may have limits)
- Monitoring: ~0.1% CPU usage

That's it! You'll now get alerts BEFORE hitting limits, not after!