"""
Keepa API client for Amazon product data retrieval.
Provides product search, detail fetching, and sales estimation.
Falls back to realistic demo data when API key is not configured.
"""

import asyncio
import os
import time
import random
from typing import Any, Dict, List, Optional

import aiohttp


class KeepaClient:
    """Client for interacting with the Keepa API."""

    BASE_URL = "https://api.keepa.com"
    TOKENS_PER_MINUTE = 60

    def __init__(self) -> None:
        self.api_key: Optional[str] = os.getenv("KEEPA_API_KEY")
        self._last_request_time: float = 0.0
        self._tokens_used: int = 0
        self._token_reset_time: float = time.time()

    @property
    def is_configured(self) -> bool:
        """Check if the Keepa API key is configured."""
        return self.api_key is not None and len(self.api_key) > 0

    async def _rate_limit(self) -> None:
        """Enforce rate limiting of 60 tokens per minute."""
        now = time.time()
        if now - self._token_reset_time >= 60:
            self._tokens_used = 0
            self._token_reset_time = now

        if self._tokens_used >= self.TOKENS_PER_MINUTE:
            wait_time = 60 - (now - self._token_reset_time)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self._tokens_used = 0
            self._token_reset_time = time.time()

        self._tokens_used += 1

    async def _make_request(
        self, endpoint: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make an authenticated request to the Keepa API."""
        await self._rate_limit()

        params["key"] = self.api_key
        url = f"{self.BASE_URL}{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(
                        f"Keepa API error {response.status}: {error_text}"
                    )

    async def search_products(
        self, keyword: str, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search products by keyword and optional category.
        Returns up to 50 products with market data.
        """
        if not self.is_configured:
            return self._get_mock_search_results(keyword)

        params: Dict[str, Any] = {
            "domain": 5,  # Amazon.co.jp
            "type": "product",
            "term": keyword,
            "stats": 180,
            "page": 0,
        }
        if category:
            params["category"] = category

        data = await self._make_request("/search", params)
        products: List[Dict[str, Any]] = []

        for item in data.get("products", [])[:50]:
            csv_data = item.get("csv", [])
            stats = item.get("stats", {})

            current_price = None
            if csv_data and len(csv_data) > 0 and csv_data[0]:
                price_list = csv_data[0]
                if price_list and len(price_list) >= 2:
                    current_price = price_list[-1] / 100  # Keepa uses cents

            sales_rank = None
            if csv_data and len(csv_data) > 3 and csv_data[3]:
                rank_list = csv_data[3]
                if rank_list and len(rank_list) >= 2:
                    sales_rank = rank_list[-1]

            monthly_sales = self.estimate_monthly_sales(
                sales_rank, category or "health"
            ) if sales_rank else 0

            products.append({
                "asin": item.get("asin", ""),
                "title": item.get("title", ""),
                "brand": item.get("brand", ""),
                "price": current_price,
                "review_count": stats.get("current", {}).get("reviewCount", 0),
                "rating": (stats.get("current", {}).get("rating", 0) or 0) / 10,
                "sales_rank": sales_rank,
                "monthly_sales": monthly_sales,
                "monthly_revenue": (current_price or 0) * monthly_sales,
                "category": item.get("categoryTree", [{}])[-1].get("name", "")
                if item.get("categoryTree")
                else "",
                "image_url": f"https://images-na.ssl-images-amazon.com/images/I/{item.get('imagesCSV', '').split(',')[0]}"
                if item.get("imagesCSV")
                else None,
            })

        return products

    async def get_product_details(self, asin: str) -> Dict[str, Any]:
        """
        Get detailed product information including price history
        and sales rank history.
        """
        if not self.is_configured:
            return self._get_mock_product_details(asin)

        params: Dict[str, Any] = {
            "domain": 5,  # Amazon.co.jp
            "asin": asin,
            "stats": 365,
            "history": 1,
            "offers": 20,
        }

        data = await self._make_request("/product", params)
        product = data.get("products", [{}])[0]
        csv_data = product.get("csv", [])
        stats = product.get("stats", {})

        price_history: List[Dict[str, Any]] = []
        if csv_data and len(csv_data) > 0 and csv_data[0]:
            prices = csv_data[0]
            for i in range(0, len(prices) - 1, 2):
                price_history.append({
                    "timestamp": prices[i],
                    "price": prices[i + 1] / 100 if prices[i + 1] > 0 else None,
                })

        rank_history: List[Dict[str, Any]] = []
        if csv_data and len(csv_data) > 3 and csv_data[3]:
            ranks = csv_data[3]
            for i in range(0, len(ranks) - 1, 2):
                rank_history.append({
                    "timestamp": ranks[i],
                    "rank": ranks[i + 1] if ranks[i + 1] > 0 else None,
                })

        current_stats = stats.get("current", {})

        return {
            "asin": asin,
            "title": product.get("title", ""),
            "brand": product.get("brand", ""),
            "price": current_stats.get("price", 0) / 100
            if current_stats.get("price")
            else None,
            "review_count": current_stats.get("reviewCount", 0),
            "rating": (current_stats.get("rating", 0) or 0) / 10,
            "sales_rank": current_stats.get("salesRank", 0),
            "price_history": price_history[-90:],  # Last 90 data points
            "rank_history": rank_history[-90:],
            "offers_count": product.get("offersCount", 0),
            "category": product.get("categoryTree", [{}])[-1].get("name", "")
            if product.get("categoryTree")
            else "",
            "fba_fees": product.get("fbaFees", {}),
            "variations": product.get("variations", []),
        }

    def estimate_monthly_sales(
        self, sales_rank: Optional[int], category: str = "health"
    ) -> int:
        """
        Estimate monthly sales from sales rank using category-specific curves.
        Based on empirical data for Amazon.co.jp marketplace.
        """
        if not sales_rank or sales_rank <= 0:
            return 0

        # Category-specific base multipliers for Amazon.co.jp
        category_multipliers: Dict[str, float] = {
            "health": 1.2,
            "beauty": 1.1,
            "food": 1.5,
            "supplement": 1.2,
            "drugstore": 1.0,
            "baby": 0.8,
            "pet": 0.7,
        }

        multiplier = category_multipliers.get(category.lower(), 1.0)

        # Approximate monthly sales based on rank (Amazon.co.jp health category)
        if sales_rank <= 10:
            estimated = 5000 - (sales_rank * 200)
        elif sales_rank <= 100:
            estimated = 3000 - (sales_rank * 20)
        elif sales_rank <= 1000:
            estimated = 1000 - int(sales_rank * 0.8)
        elif sales_rank <= 5000:
            estimated = 300 - int(sales_rank * 0.04)
        elif sales_rank <= 20000:
            estimated = 120 - int(sales_rank * 0.004)
        elif sales_rank <= 50000:
            estimated = 50 - int(sales_rank * 0.0006)
        else:
            estimated = max(1, int(30000 / sales_rank))

        return max(1, int(estimated * multiplier))

    def _get_mock_search_results(self, keyword: str) -> List[Dict[str, Any]]:
        """Return realistic Japanese supplement market demo data."""
        mock_products: List[Dict[str, Any]] = [
            {
                "asin": "B0CXYZ1234",
                "title": "【大容量】NMN サプリメント 18000mg 高純度99.9% 60粒 日本製 GMP認定工場",
                "brand": "REVITA",
                "price": 4980,
                "review_count": 2847,
                "rating": 4.3,
                "sales_rank": 45,
                "monthly_sales": 3200,
                "monthly_revenue": 15936000,
                "category": "ドラッグストア",
                "image_url": None,
            },
            {
                "asin": "B0DABCD567",
                "title": "マルチビタミン&ミネラル 240粒 約8ヶ月分 ビタミンC ビタミンD 亜鉛 鉄分",
                "brand": "ヘルスライフ",
                "price": 1980,
                "review_count": 8934,
                "rating": 4.1,
                "sales_rank": 12,
                "monthly_sales": 4800,
                "monthly_revenue": 9504000,
                "category": "ドラッグストア",
                "image_url": None,
            },
            {
                "asin": "B0CEFGH890",
                "title": "乳酸菌 サプリ ビフィズス菌 1000億個 30日分 腸活 善玉菌 プロバイオティクス",
                "brand": "腸美人",
                "price": 2480,
                "review_count": 5621,
                "rating": 4.2,
                "sales_rank": 23,
                "monthly_sales": 4100,
                "monthly_revenue": 10168000,
                "category": "ドラッグストア",
                "image_url": None,
            },
            {
                "asin": "B0DIJKL012",
                "title": "エクオール 大豆イソフラボン 30日分 更年期 女性サプリ 国内製造",
                "brand": "フェミナチュール",
                "price": 3280,
                "review_count": 3456,
                "rating": 4.0,
                "sales_rank": 67,
                "monthly_sales": 2400,
                "monthly_revenue": 7872000,
                "category": "ドラッグストア",
                "image_url": None,
            },
            {
                "asin": "B0CMNOP345",
                "title": "CBDオイル 高濃度 10% ブロードスペクトラム 10ml 国内検査済み",
                "brand": "GREENZ",
                "price": 6980,
                "review_count": 1234,
                "rating": 4.4,
                "sales_rank": 156,
                "monthly_sales": 1200,
                "monthly_revenue": 8376000,
                "category": "ドラッグストア",
                "image_url": None,
            },
            {
                "asin": "B0DQRST678",
                "title": "クレアチン モノハイドレート 500g パウダー 100回分 筋トレ 無味無臭",
                "brand": "マッスルテック",
                "price": 2780,
                "review_count": 4567,
                "rating": 4.5,
                "sales_rank": 34,
                "monthly_sales": 3600,
                "monthly_revenue": 10008000,
                "category": "ドラッグストア",
                "image_url": None,
            },
            {
                "asin": "B0CUVWX901",
                "title": "ビタミンD3 5000IU 365粒 1年分 小粒 飲みやすい 太陽のビタミン",
                "brand": "サンシャインヘルス",
                "price": 1480,
                "review_count": 6789,
                "rating": 4.6,
                "sales_rank": 8,
                "monthly_sales": 5200,
                "monthly_revenue": 7696000,
                "category": "ドラッグストア",
                "image_url": None,
            },
            {
                "asin": "B0DYZA2345",
                "title": "ルテイン 40mg ゼアキサンチン配合 60粒 アイケア ブルーライト対策",
                "brand": "アイプロテクト",
                "price": 2180,
                "review_count": 2345,
                "rating": 4.2,
                "sales_rank": 89,
                "monthly_sales": 2100,
                "monthly_revenue": 4578000,
                "category": "ドラッグストア",
                "image_url": None,
            },
            {
                "asin": "B0CBCDE678",
                "title": "コラーゲン ペプチド 粉末 無味 国産 低分子 100日分 美容 関節サポート",
                "brand": "美コラーゲン",
                "price": 1880,
                "review_count": 7234,
                "rating": 4.3,
                "sales_rank": 15,
                "monthly_sales": 4600,
                "monthly_revenue": 8648000,
                "category": "ドラッグストア",
                "image_url": None,
            },
            {
                "asin": "B0DFGHI901",
                "title": "エプソムソルト 入浴剤 3kg 国産 硫酸マグネシウム バスソルト 無香料",
                "brand": "バスリフレ",
                "price": 1580,
                "review_count": 9876,
                "rating": 4.4,
                "sales_rank": 5,
                "monthly_sales": 6200,
                "monthly_revenue": 9796000,
                "category": "ビューティー",
                "image_url": None,
            },
            {
                "asin": "B0CJKLM234",
                "title": "GABA ギャバ サプリメント 200mg 60日分 リラックス 睡眠サポート",
                "brand": "スリープウェル",
                "price": 1280,
                "review_count": 3456,
                "rating": 3.9,
                "sales_rank": 112,
                "monthly_sales": 1800,
                "monthly_revenue": 2304000,
                "category": "ドラッグストア",
                "image_url": None,
            },
            {
                "asin": "B0DNOPQ567",
                "title": "亜鉛 サプリ 50mg 高含有 120粒 4ヶ月分 免疫力 男性サポート",
                "brand": "ジンクパワー",
                "price": 980,
                "review_count": 5678,
                "rating": 4.1,
                "sales_rank": 28,
                "monthly_sales": 3800,
                "monthly_revenue": 3724000,
                "category": "ドラッグストア",
                "image_url": None,
            },
        ]

        # Filter by keyword loosely
        keyword_lower = keyword.lower()
        filtered = [
            p
            for p in mock_products
            if keyword_lower in p["title"].lower()
            or keyword_lower in p["brand"].lower()
            or keyword_lower in p["category"].lower()
        ]

        # If no exact match, return all mock products (simulating a broad search)
        return filtered if filtered else mock_products

    def _get_mock_product_details(self, asin: str) -> Dict[str, Any]:
        """Return mock product details for a given ASIN."""
        base_price = random.randint(1000, 6000)
        return {
            "asin": asin,
            "title": f"【高品質】サプリメント {asin} 日本製 GMP認定工場 60粒",
            "brand": "デモブランド",
            "price": base_price,
            "review_count": random.randint(500, 5000),
            "rating": round(random.uniform(3.5, 4.8), 1),
            "sales_rank": random.randint(5, 500),
            "price_history": [
                {"timestamp": i, "price": base_price + random.randint(-500, 500)}
                for i in range(90)
            ],
            "rank_history": [
                {"timestamp": i, "rank": random.randint(10, 600)}
                for i in range(90)
            ],
            "offers_count": random.randint(1, 15),
            "category": "ドラッグストア",
            "fba_fees": {"pick_pack": 434, "weight_handling": 48, "storage": 36},
            "variations": [],
        }
