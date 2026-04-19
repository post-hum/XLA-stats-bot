import aiohttp
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)
POOL_API_URL = "https://pool.scalaproject.io/api/stats"

class PoolData:
    def __init__(self, raw_data: dict):
        self.raw = raw_data
        self.network = raw_data.get("network", {})
        self.pool_stats = raw_data.get("pool", {}).get("stats", {})
        self.last_block = raw_data.get("lastblock", {})
        self.config = raw_data.get("config", {})
        self.pool_info = raw_data.get("pool", {})
        
    @property
    def network_height(self) -> int:
        return int(self.network.get("height", 0))
    
    @property
    def network_difficulty(self) -> int:
        return int(self.network.get("difficulty", 0))
    
    @property
    def network_hashrate_mh(self) -> float:
        diff = self.network_difficulty
        return diff / 120 / 1_000_000 if diff else 0
    
    @property
    def pool_hashrate_kh(self) -> float:
        hr = self.pool_info.get("hashrate", 0)
        return hr / 1000 if hr else 0
    
    @property
    def active_miners(self) -> int:
        return self.pool_info.get("miners", 0)
    
    @property
    def active_workers(self) -> int:
        return self.pool_info.get("workers", 0)
    
    @property
    def last_block_height(self) -> int:
        return int(self.pool_stats.get("lastblock_height", 0))
    
    @property
    def last_block_reward(self) -> float:
        reward = int(self.pool_stats.get("lastblock_lastReward", 0))
        return reward / 100.0 if reward else 0
    
    @property
    def last_block_time(self) -> str:
        ts = int(self.pool_stats.get("lastblock_timestamp", 0))
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else "N/A"
    
    @property
    def round_effort(self) -> float:
        shares = int(self.pool_stats.get("roundSharesprops", 0))
        diff = self.network_difficulty
        return (shares / diff * 100) if diff else 0
    
    @property
    def blocks_found_24h(self) -> int:
        charts = self.raw.get("charts", {})
        blocks_data = charts.get("blocks", {})
        today = datetime.now().strftime("%Y-%m-%d")
        return blocks_data.get(today, 0)

async def fetch_pool_stats() -> Optional[PoolData]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(POOL_API_URL, timeout=10) as resp:
                data = await resp.json()
                return PoolData(data)
    except Exception as e:
        logger.error(f"Failed to fetch pool stats: {e}")
        return None
