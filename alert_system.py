"""
Alert System for SEO Agent - Get notified at 90% capacity
Monitors: API limits, memory, disk, daily spending
"""
import os
import time
import psutil
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import logging

logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self):
        # Alert thresholds
        self.WARNING_THRESHOLD = 0.75  # 75% - Email only
        self.CRITICAL_THRESHOLD = 0.90  # 90% - Email + SMS
        
        # Your details (set these in .env)
        self.YOUR_EMAIL = os.getenv('ALERT_EMAIL', 'your-email@gmail.com')
        self.YOUR_PHONE = os.getenv('ALERT_PHONE', '2055551234@txt.att.net')  # Email-to-SMS
        self.SMTP_EMAIL = os.getenv('SMTP_EMAIL')  # Email to send FROM
        self.SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')  # App password
        
        # API Limits
        self.CLAUDE_LIMIT = 40000  # tokens per minute
        self.OPENAI_LIMIT = 90000  # tokens per minute
        self.DAILY_BUDGET = float(os.getenv('DAILY_BUDGET', '50'))  # dollars
        
        # Track usage
        self.claude_tokens_used = 0
        self.openai_tokens_used = 0
        self.daily_spend = 0
        self.last_reset = datetime.now()
        self.alerts_sent = {}  # Prevent spam
        
    def track_api_usage(self, tokens, service='claude'):
        """Call this after each API request"""
        if service == 'claude':
            self.claude_tokens_used += tokens
            cost = (tokens / 1_000_000) * 3  # $3 per million
        else:  # openai
            self.openai_tokens_used += tokens
            cost = (tokens / 1_000_000) * 30  # $30 per million
            
        self.daily_spend += cost
        
        # Check if we need to alert
        self.check_all_limits()
        
    def check_all_limits(self):
        """Check all resources and send alerts if needed"""
        alerts = []
        
        # 1. Check API Rate Limits
        claude_percent = self.claude_tokens_used / self.CLAUDE_LIMIT
        if claude_percent >= self.CRITICAL_THRESHOLD:
            if not self._already_alerted('claude_90', 5):
                alerts.append({
                    'type': '🚨 CLAUDE API',
                    'message': f'At {claude_percent*100:.0f}% of rate limit!',
                    'details': f'{self.claude_tokens_used:,}/{self.CLAUDE_LIMIT:,} tokens',
                    'action': 'Pausing for 30 seconds',
                    'critical': True
                })
                time.sleep(30)  # Auto-pause
        elif claude_percent >= self.WARNING_THRESHOLD:
            if not self._already_alerted('claude_75', 15):
                alerts.append({
                    'type': '⚠️ Claude API',
                    'message': f'At {claude_percent*100:.0f}% of rate limit',
                    'details': f'{self.claude_tokens_used:,}/{self.CLAUDE_LIMIT:,} tokens',
                    'critical': False
                })
        
        # 2. Check Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent / 100
        if memory_percent >= self.CRITICAL_THRESHOLD:
            if not self._already_alerted('memory_90', 5):
                alerts.append({
                    'type': '🚨 MEMORY',
                    'message': f'At {memory.percent:.0f}% capacity!',
                    'details': f'Only {memory.available/1e9:.1f}GB free',
                    'action': 'May crash soon',
                    'critical': True
                })
        
        # 3. Check Daily Spending
        spend_percent = self.daily_spend / self.DAILY_BUDGET
        if spend_percent >= self.CRITICAL_THRESHOLD:
            if not self._already_alerted('spend_90', 30):
                alerts.append({
                    'type': '🚨 DAILY BUDGET',
                    'message': f'At {spend_percent*100:.0f}% of ${self.DAILY_BUDGET}!',
                    'details': f'Spent ${self.daily_spend:.2f} today',
                    'action': 'Will stop at 100%',
                    'critical': True
                })
        elif spend_percent >= self.WARNING_THRESHOLD:
            if not self._already_alerted('spend_75', 60):
                alerts.append({
                    'type': '💰 Daily Budget',
                    'message': f'At {spend_percent*100:.0f}% of ${self.DAILY_BUDGET}',
                    'details': f'Spent ${self.daily_spend:.2f} today',
                    'critical': False
                })
        
        # 4. Check Disk Space
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent / 100
        if disk_percent >= self.CRITICAL_THRESHOLD:
            if not self._already_alerted('disk_90', 30):
                alerts.append({
                    'type': '🚨 DISK SPACE',
                    'message': f'At {disk.percent:.0f}% capacity!',
                    'details': f'Only {disk.free/1e9:.1f}GB free',
                    'action': 'Clean up needed',
                    'critical': True
                })
        
        # Send alerts
        if alerts:
            self._send_alerts(alerts)
            
        # Reset counters every minute
        if datetime.now() - self.last_reset > timedelta(minutes=1):
            self.claude_tokens_used = 0
            self.openai_tokens_used = 0
            self.last_reset = datetime.now()
            
    def _send_alerts(self, alerts):
        """Send consolidated alerts via email and SMS"""
        # Separate critical and warning alerts
        critical_alerts = [a for a in alerts if a.get('critical', False)]
        warning_alerts = [a for a in alerts if not a.get('critical', False)]
        
        # Build message
        message = "SEO Agent Alert Report\n" + "="*30 + "\n\n"
        
        if critical_alerts:
            message += "🚨 CRITICAL ALERTS (90%+):\n\n"
            for alert in critical_alerts:
                message += f"{alert['type']}: {alert['message']}\n"
                message += f"Details: {alert['details']}\n"
                if 'action' in alert:
                    message += f"Action: {alert['action']}\n"
                message += "\n"
                
        if warning_alerts:
            message += "⚠️ WARNINGS (75%+):\n\n"
            for alert in warning_alerts:
                message += f"{alert['type']}: {alert['message']}\n"
                message += f"Details: {alert['details']}\n"
                message += "\n"
        
        # Add timestamp
        message += f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Send email (always)
        self._send_email(
            subject=f"{'🚨 CRITICAL' if critical_alerts else '⚠️ Warning'}: SEO Agent at capacity",
            body=message
        )
        
        # Send SMS if critical
        if critical_alerts:
            sms_message = "🚨 SEO Agent Critical:\n"
            for alert in critical_alerts[:2]:  # Limit SMS length
                sms_message += f"- {alert['type']}: {alert['message']}\n"
            self._send_sms(sms_message)
    
    def _send_email(self, subject, body):
        """Send email alert"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.SMTP_EMAIL
            msg['To'] = self.YOUR_EMAIL
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.SMTP_EMAIL, self.SMTP_PASSWORD)
                server.send_message(msg)
                
            logger.info(f"Email alert sent: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
    
    def _send_sms(self, message):
        """Send SMS via email-to-SMS gateway"""
        try:
            msg = MIMEText(message)
            msg['From'] = self.SMTP_EMAIL
            msg['To'] = self.YOUR_PHONE
            msg['Subject'] = ""  # Keep SMS short
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.SMTP_EMAIL, self.SMTP_PASSWORD)
                server.send_message(msg)
                
            logger.info("SMS alert sent")
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
    
    def _already_alerted(self, alert_type, minutes):
        """Prevent alert spam"""
        last_alert = self.alerts_sent.get(alert_type)
        if not last_alert:
            self.alerts_sent[alert_type] = datetime.now()
            return False
            
        if datetime.now() - last_alert > timedelta(minutes=minutes):
            self.alerts_sent[alert_type] = datetime.now()
            return False
            
        return True

    def get_status(self):
        """Get current system status"""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'claude_usage': f"{(self.claude_tokens_used/self.CLAUDE_LIMIT)*100:.0f}%",
            'openai_usage': f"{(self.openai_tokens_used/self.OPENAI_LIMIT)*100:.0f}%",
            'memory': f"{memory.percent:.0f}%",
            'disk': f"{disk.percent:.0f}%",
            'daily_spend': f"${self.daily_spend:.2f}",
            'budget_used': f"{(self.daily_spend/self.DAILY_BUDGET)*100:.0f}%"
        }


# Global alert system instance
alert_system = AlertSystem()

# Example usage in your main.py:
"""
from alert_system import alert_system

# After each API call:
response = await claude_api_call(prompt)
tokens_used = response.usage.total_tokens
alert_system.track_api_usage(tokens_used, service='claude')

# Check status anytime:
status = alert_system.get_status()
print(f"System Status: {status}")
"""