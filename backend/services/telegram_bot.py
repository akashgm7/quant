import httpx
import logging
import os
from dotenv import load_dotenv

load_dotenv()

class TelegramService:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.logger = logging.getLogger(__name__)

    async def send_signal(self, signal_data: dict):
        if not self.token or not self.chat_id:
            self.logger.warning("Telegram credentials not found. Skipping alert.")
            return

        message = (
            f"🚀 *{signal_data['symbol']} {signal_data['direction']} SIGNAL*\n\n"
            f"Entry: `{signal_data['entry']:.5f}`\n"
            f"Stop Loss: `{signal_data['stop_loss']:.5f}`\n"
            f"Take Profit 1: `{signal_data['take_profit_1']:.5f}`\n"
            f"Take Profit 2: `{signal_data['take_profit_2']:.5f}`\n\n"
            f"Risk Reward: `1:{signal_data['risk_reward']}`\n"
            f"Confidence: `{signal_data['confidence']}%`\n\n"
            f"*Reasons:*\n" + "\n".join([f"✓ {r}" for r in signal_data['reasons']]) + "\n\n"
            f"Timeframe: `15m`"
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                )
                if response.status_code != 200:
                    self.logger.error(f"Telegram API Error: {response.text}")
        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {e}")
    async def send_chart(self, photo_path: str, caption: str):
        if not self.token or not self.chat_id:
            return

        try:
            async with httpx.AsyncClient() as client:
                with open(photo_path, "rb") as f:
                    response = await client.post(
                        f"{self.base_url}/sendPhoto",
                        data={"chat_id": self.chat_id, "caption": caption, "parse_mode": "Markdown"},
                        files={"photo": f}
                    )
                if response.status_code != 200:
                    self.logger.error(f"Telegram API Error (Photo): {response.text}")
            
            # Clean up temp file
            if os.path.exists(photo_path):
                os.remove(photo_path)
        except Exception as e:
            self.logger.error(f"Error sending Telegram photo: {e}")

telegram_service = TelegramService()
