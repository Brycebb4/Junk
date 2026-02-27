# Notification System for CincyJunkBot
# Handles Telegram and SMS notifications for hot leads

import os
import requests
from config import Config

class NotificationManager:
    """Manages notifications for new leads"""

    def __init__(self):
        self.config = Config()
        self.telegram_enabled = bool(self.config.TELEGRAM_BOT_TOKEN and self.config.TELEGRAM_CHAT_ID)
        self.twilio_enabled = bool(self.config.TWILIO_ACCOUNT_SID and self.config.TWILIO_AUTH_TOKEN)

    def send_alert(self, lead):
        """Send notification for a hot lead"""
        if lead.get('priority_score', 0) >= self.config.HOT_LEAD_THRESHOLD:
            if self.config.NOTIFY_HOT_LEADS:
                self._send_telegram(lead)
                if self.twilio_enabled:
                    self._send_sms(lead)

        elif lead.get('priority_score', 0) >= self.config.MEDIUM_LEAD_THRESHOLD:
            if self.config.NOTIFY_MEDIUM_LEADS:
                self._send_telegram(lead)

    def _format_message(self, lead):
        """Format lead as notification message"""
        emoji = self._get_priority_emoji(lead.get('priority_score', 0))

        message = f"""{emoji} *HOT LEAD - {lead.get('estimated_value', 'Unknown Value')}*

*{lead.get('title', 'No Title')}*

📍 {lead.get('location', 'Unknown Location')}
🔗 [View Post]({lead.get('source_url', '')})

Keywords: {', '.join(lead.get('keywords_detected', []))}

Priority Score: {lead.get('priority_score', 0)}/100
"""

        return message

    def _get_priority_emoji(self, score):
        """Get emoji based on priority score"""
        if score >= 90:
            return '🔥'
        elif score >= 75:
            return '⭐'
        else:
            return '💡'

    def _send_telegram(self, lead):
        """Send Telegram message"""
        if not self.telegram_enabled:
            return

        try:
            url = f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}/sendMessage"
            message = self._format_message(lead)

            data = {
                'chat_id': self.config.TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }

            response = requests.post(url, json=data, timeout=10)
            if response.status_code != 200:
                print(f"Telegram send error: {response.text}")
        except Exception as e:
            print(f"Telegram notification error: {e}")

    def _send_sms(self, lead):
        """Send SMS message via Twilio"""
        if not self.twilio_enabled or not self.config.NOTIFY_PHONE:
            return

        try:
            from twilio.rest import Client

            client = Client(self.config.TWILIO_ACCOUNT_SID, self.config.TWILIO_AUTH_TOKEN)

            message_text = f"Hot Lead: {lead.get('title', 'Junk Removal')}\n"
            message_text += f"Location: {lead.get('location', 'Cincinnati area')}\n"
            message_text += f"Value: {lead.get('estimated_value', 'Unknown')}\n"
            message_text += f"Link: {lead.get('source_url', '')[:50]}..."

            message = client.messages.create(
                body=message_text,
                from_=self.config.TWILIO_PHONE_NUMBER,
                to=self.config.NOTIFY_PHONE
            )

            print(f"SMS sent: {message.sid}")
        except ImportError:
            print("Twilio not installed. Install with: pip install twilio")
        except Exception as e:
            print(f"SMS notification error: {e}")

    def send_test_notification(self):
        """Send a test notification"""
        test_lead = {
            'title': 'TEST: Garage Cleanout',
            'location': 'Mason, OH',
            'estimated_value': '$300-$500',
            'source_url': 'https://example.com/test',
            'keywords_detected': ['garage cleanout'],
            'priority_score': 85
        }
        self._send_telegram(test_lead)
        return True
