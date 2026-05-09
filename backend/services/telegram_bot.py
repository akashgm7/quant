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
            self.logger.warning("Telegram credentials missing.")
            return

        emoji = "🚀" if signal['direction'] == "LONG" else "📉"
        session_emoji = "🇬🇧" if signal.get('session') == "LONDON" else "🇺🇸" if signal.get('session') == "NEW_YORK" else "🌐"
        
        message = (
            f"⚡️ **QUANT-X SCALPING SIGNAL** ⚡️\n\n"
            f"**Pair:** {signal['symbol']} ({signal.get('timeframe', '15m')})\n"
            f"**Setup:** {signal.get('setup_type', 'Confluence Setup')}\n"
            f"**Action:** {emoji} {signal['direction']}\n"
            f"**Session:** {session_emoji} {signal.get('session', 'N/A')}\n"
            f"--------------------------------\n"
            f"🎯 **Entry:** {signal['entry']}\n"
            f"🛑 **Stop Loss:** {signal['stop_loss']}\n"
            f"✅ **TP 1:** {signal['take_profit_1']}\n"
            f"💎 **TP 2:** {signal['take_profit_2']}\n"
            f"⚖️ **RR Ratio:** {signal['risk_reward']}\n"
            f"--------------------------------\n"
            f"🧠 **AI Confidence:** {signal['confidence']}%\n"
            f"📝 **Reasoning:**\n"
        )
        
        for reason in signal['reasons']:
            message += f"• {reason}\n"
            
        message += f"\n📊 [View Live Dashboard](https://quant-five-alpha.vercel.app/)"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.base_url, json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False
                })
                return response.json()
            except Exception as e:
                self.logger.error(f"Error sending Telegram message: {e}")
                return None

telegram_service = TelegramService()
