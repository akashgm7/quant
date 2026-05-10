import httpx
import os
import logging
from typing import Dict, Any

class TelegramService:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        self.logger = logging.getLogger(__name__)

    async def send_signal(self, signal: Dict[str, Any]):
        if not self.bot_token or not self.chat_id:
            return

        emoji = "🎯" if signal['direction'] == "LONG" else "🔻"
        
        message = (
            f"🎯 **QUANT-X FIBONACCI SNIPER SETUP** 🎯\n\n"
            f"**Asset:** {signal['symbol']}\n"
            f"**Type:** {signal.get('setup_type', 'Golden Setup')}\n"
            f"**Direction:** {emoji} {signal['direction']}\n"
            f"--------------------------------\n"
            f"📐 **Fib Zone:** {signal.get('fib_zone', '0.618 - 0.786')}\n"
            f"📊 **Trend Bias:** Confirmed (4H/1H)\n"
            f"--------------------------------\n"
            f"💎 **Entry:** {signal['entry']}\n"
            f"🛑 **Stop Loss:** {signal['stop_loss']}\n"
            f"✅ **TP 1 (Target):** {signal['take_profit_1']}\n"
            f"🚀 **TP 2 (Moon):** {signal['take_profit_2']}\n"
            f"⚖️ **RR Ratio:** {signal['risk_reward']}\n"
            f"--------------------------------\n"
            f"🧠 **AI Confidence:** {signal['confidence']}%\n"
            f"📝 **Confluences Detected:**\n"
        )
        
        for reason in signal['reasons']:
            message += f"• {reason}\n"
            
        message += f"\n📊 [View Sniper Dashboard](https://quant-five-alpha.vercel.app/)"

        async with httpx.AsyncClient() as client:
            try:
                await client.post(self.base_url, json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False
                })
            except Exception as e:
                self.logger.error(f"Error sending Telegram message: {e}")

telegram_service = TelegramService()
