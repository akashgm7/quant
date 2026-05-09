import httpx
import logging
import os
from dotenv import load_dotenv

load_dotenv()

class ExternalDataService:
    def __init__(self):
        self.cryptopanic_api_key = os.getenv("CRYPTOPANIC_API_KEY")
        self.logger = logging.getLogger(__name__)

    async def fetch_market_news(self):
        """
        Fetches latest news and sentiment from CryptoPanic.
        """
        if not self.cryptopanic_api_key:
            return self._get_mock_news()

        try:
            async with httpx.AsyncClient() as client:
                url = f"https://cryptopanic.com/api/v1/posts/?auth_token={self.cryptopanic_api_key}&kind=news&filter=hot"
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json().get("results", [])
        except Exception as e:
            self.logger.error(f"Error fetching news: {e}")
            
        return self._get_mock_news()

    async def fetch_onchain_alerts(self):
        """
        Mocks institutional on-chain data (Whale moves, exchange flows).
        """
        return [
            {"type": "WHALE_MOVE", "description": "5,000 BTC moved from Unknown Wallet to Coinbase", "impact": "BEARISH", "time": "5m ago"},
            {"type": "EXCHANGE_FLOW", "description": "Large USDC inflow detected on Binance ($200M)", "impact": "BULLISH", "time": "12m ago"},
            {"type": "LIQUIDATION", "description": "$50M Longs liquidated on ETH in last 1H", "impact": "NEUTRAL", "time": "30m ago"}
        ]

    def _get_mock_news(self):
        return [
            {"title": "Bitcoin Hits New Local Resistance as Institutional Buying Slows", "sentiment": "Neutral", "source": "MockNews"},
            {"title": "Ethereum L2 Usage Spikes to All-Time Highs Amid Mainnet Upgrade", "sentiment": "Bullish", "source": "MockNews"},
            {"title": "US CPI Data Expected Tomorrow: Market Braces for Volatility", "sentiment": "Bearish", "source": "MockNews"}
        ]

external_data_service = ExternalDataService()
