"""
Amazon SP-API (Selling Partner API) client for product data and reviews.
Falls back to realistic demo data when credentials are not configured.
"""

import os
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp


class SPAPIClient:
    """Client for interacting with the Amazon Selling Partner API."""

    BASE_URL = "https://sellingpartnerapi-fe.amazon.com"

    def __init__(self) -> None:
        self.client_id: Optional[str] = os.getenv("SP_API_CLIENT_ID")
        self.client_secret: Optional[str] = os.getenv("SP_API_CLIENT_SECRET")
        self.refresh_token: Optional[str] = os.getenv("SP_API_REFRESH_TOKEN")
        self.marketplace_id: str = "A1VC38T7YXB528"  # Amazon.co.jp
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

    @property
    def is_configured(self) -> bool:
        """Check if SP-API credentials are configured."""
        return all([self.client_id, self.client_secret, self.refresh_token])

    async def _ensure_access_token(self) -> str:
        """Obtain or refresh the LWA access token."""
        if self._access_token and self._token_expiry and datetime.utcnow() < self._token_expiry:
            return self._access_token

        token_url = "https://api.amazon.com/auth/o2/token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self._access_token = data["access_token"]
                    self._token_expiry = datetime.utcnow() + timedelta(
                        seconds=data.get("expires_in", 3600) - 60
                    )
                    return self._access_token
                else:
                    raise Exception(f"SP-API token error: {await response.text()}")

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an authenticated request to the SP-API."""
        token = await self._ensure_access_token()

        headers = {
            "x-amz-access-token": token,
            "Content-Type": "application/json",
        }

        url = f"{self.BASE_URL}{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(
                        f"SP-API error {response.status}: {error_text}"
                    )

    async def get_product_info(self, asin: str) -> Dict[str, Any]:
        """Get product catalog information for a given ASIN."""
        if not self.is_configured:
            return self._get_mock_product_info(asin)

        endpoint = f"/catalog/2022-04-01/items/{asin}"
        params = {
            "marketplaceIds": self.marketplace_id,
            "includedData": "summaries,attributes,images,productTypes",
        }

        data = await self._make_request("GET", endpoint, params=params)
        summaries = data.get("summaries", [{}])[0]

        return {
            "asin": asin,
            "title": summaries.get("itemName", ""),
            "brand": summaries.get("brand", ""),
            "manufacturer": summaries.get("manufacturer", ""),
            "category": summaries.get("browseClassification", {}).get(
                "displayName", ""
            ),
            "images": [
                img.get("link", "")
                for img in data.get("images", [{}])[0].get("images", [])
            ],
            "product_type": data.get("productTypes", [{}])[0].get(
                "productType", ""
            ),
        }

    async def get_reviews(
        self, asin: str, max_count: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Get product reviews for a given ASIN.
        Returns up to max_count reviews sorted by most recent.
        """
        if not self.is_configured:
            return self._get_mock_reviews(asin, max_count)

        # Note: SP-API does not have a direct reviews endpoint.
        # In production, you would use the Product Advertising API
        # or scrape reviews with proper authorization.
        # This shows the intended interface.
        reviews: List[Dict[str, Any]] = []
        next_token: Optional[str] = None

        while len(reviews) < max_count:
            params: Dict[str, Any] = {
                "marketplaceIds": self.marketplace_id,
                "asin": asin,
                "pageSize": min(100, max_count - len(reviews)),
            }
            if next_token:
                params["nextToken"] = next_token

            try:
                data = await self._make_request(
                    "GET", "/reviews/2021-11-01/reviews", params=params
                )
                reviews.extend(data.get("reviews", []))
                next_token = data.get("nextToken")
                if not next_token:
                    break
            except Exception:
                break

        return reviews[:max_count]

    async def get_fees_estimate(
        self, asin: str, price: float
    ) -> Dict[str, Any]:
        """
        Get FBA fee estimates for a product.
        Returns breakdown of fulfillment fees for Amazon.co.jp.
        """
        if not self.is_configured:
            return self._get_mock_fees_estimate(asin, price)

        endpoint = "/products/fees/v0/items/{}/feesEstimate".format(asin)
        json_body = {
            "FeesEstimateRequest": {
                "MarketplaceId": self.marketplace_id,
                "IsAmazonFulfilled": True,
                "PriceToEstimateFees": {
                    "ListingPrice": {"CurrencyCode": "JPY", "Amount": price}
                },
                "Identifier": f"fee-estimate-{asin}",
            }
        }

        data = await self._make_request("POST", endpoint, json_body=json_body)
        result = data.get("payload", {}).get("FeesEstimateResult", {})
        fee_detail = result.get("FeesEstimate", {}).get("FeeDetailList", [])

        fees: Dict[str, float] = {}
        total: float = 0.0
        for fee in fee_detail:
            fee_type = fee.get("FeeType", "Unknown")
            amount = fee.get("FinalFee", {}).get("Amount", 0)
            fees[fee_type] = amount
            total += amount

        return {
            "asin": asin,
            "price": price,
            "fees": fees,
            "total_fees": total,
            "referral_fee": fees.get("ReferralFee", 0),
            "fba_fee": fees.get("FBAFees", 0),
            "closing_fee": fees.get("VariableClosingFee", 0),
        }

    def _get_mock_product_info(self, asin: str) -> Dict[str, Any]:
        """Return mock product information."""
        mock_data: Dict[str, Dict[str, Any]] = {
            "B0CXYZ1234": {
                "asin": "B0CXYZ1234",
                "title": "【大容量】NMN サプリメント 18000mg 高純度99.9% 60粒 日本製 GMP認定工場",
                "brand": "REVITA",
                "manufacturer": "株式会社レビータ",
                "category": "ドラッグストア > 栄養補助食品 > サプリメント",
                "images": [],
                "product_type": "DIETARY_SUPPLEMENT",
            },
            "B0DABCD567": {
                "asin": "B0DABCD567",
                "title": "マルチビタミン&ミネラル 240粒 約8ヶ月分",
                "brand": "ヘルスライフ",
                "manufacturer": "ヘルスライフ株式会社",
                "category": "ドラッグストア > 栄養補助食品 > ビタミン",
                "images": [],
                "product_type": "DIETARY_SUPPLEMENT",
            },
        }

        return mock_data.get(asin, {
            "asin": asin,
            "title": f"サプリメント商品 {asin}",
            "brand": "サンプルブランド",
            "manufacturer": "サンプル製造株式会社",
            "category": "ドラッグストア > サプリメント",
            "images": [],
            "product_type": "DIETARY_SUPPLEMENT",
        })

    def _get_mock_reviews(
        self, asin: str, max_count: int
    ) -> List[Dict[str, Any]]:
        """Return realistic mock reviews for Japanese supplement products."""
        positive_templates = [
            {
                "title": "体調が良くなった気がします",
                "body": "飲み始めて2週間ですが、朝の目覚めが良くなった気がします。粒も小さくて飲みやすいです。継続して飲んでみます。",
                "rating": 5,
            },
            {
                "title": "コスパが良い",
                "body": "他社製品と比較して含有量が多く、価格も手頃です。パッケージもしっかりしていて品質に信頼感があります。",
                "rating": 5,
            },
            {
                "title": "リピートしています",
                "body": "3回目の購入です。毎日続けていますが、肌の調子が良くなったように感じます。これからも続けたいと思います。",
                "rating": 4,
            },
            {
                "title": "飲みやすい",
                "body": "カプセルタイプで匂いもなく飲みやすいです。1日1粒でいいのも続けやすいポイントです。",
                "rating": 4,
            },
        ]

        negative_templates = [
            {
                "title": "効果を実感できない",
                "body": "1ヶ月飲みましたが、特に変化を感じません。もう少し続けてみるか迷っています。値段がもう少し安ければ続けやすいのですが。",
                "rating": 2,
            },
            {
                "title": "粒が大きすぎる",
                "body": "粒が大きくて飲みにくいです。特に高齢の母には辛いようです。もう少し小さくするか、分割できるようにしてほしいです。",
                "rating": 2,
            },
            {
                "title": "パッケージが開けにくい",
                "body": "ジッパーが閉まりにくく、湿気が心配です。中身は良さそうなのに、パッケージの品質が残念です。改善を希望します。",
                "rating": 3,
            },
            {
                "title": "お腹が緩くなった",
                "body": "飲み始めて3日目からお腹が緩くなりました。成分自体は良いと思うのですが、体質に合わなかったようです。量を減らして様子を見ます。",
                "rating": 2,
            },
            {
                "title": "匂いが気になる",
                "body": "カプセルを開けると独特の匂いがします。飲む分には問題ありませんが、敏感な方は気になるかもしれません。",
                "rating": 3,
            },
            {
                "title": "配送時に破損",
                "body": "届いた時にパッケージの角が潰れていました。中身に影響はなさそうですが、もう少し丁寧に梱包してほしいです。",
                "rating": 3,
            },
        ]

        neutral_templates = [
            {
                "title": "普通に良い商品です",
                "body": "特別すごいということはありませんが、日常的なサプリメントとして十分な品質だと思います。",
                "rating": 3,
            },
            {
                "title": "まだ分からない",
                "body": "飲み始めたばかりなので効果はまだ分かりません。成分表示がしっかりしているので期待しています。",
                "rating": 3,
            },
        ]

        all_templates = positive_templates + negative_templates + neutral_templates
        reviews: List[Dict[str, Any]] = []
        count = min(max_count, 50)  # Cap mock data at 50

        for i in range(count):
            template = all_templates[i % len(all_templates)]
            review_date = datetime.utcnow() - timedelta(days=random.randint(1, 180))
            reviews.append({
                "review_id": f"R{asin}{i:04d}",
                "asin": asin,
                "title": template["title"],
                "body": template["body"],
                "rating": template["rating"],
                "date": review_date.isoformat(),
                "verified_purchase": random.random() > 0.2,
                "helpful_votes": random.randint(0, 50),
            })

        return reviews

    def _get_mock_fees_estimate(
        self, asin: str, price: float
    ) -> Dict[str, Any]:
        """Return mock FBA fee estimates for Amazon.co.jp."""
        # Referral fee: typically 8-15% depending on category
        referral_fee = round(price * 0.10, 0)
        # FBA fulfillment fee for small standard size (Japan)
        fba_fee = 434.0 if price <= 3000 else 514.0
        # Closing fee for media/supplements
        closing_fee = 0.0
        total = referral_fee + fba_fee + closing_fee

        return {
            "asin": asin,
            "price": price,
            "fees": {
                "ReferralFee": referral_fee,
                "FBAFees": fba_fee,
                "VariableClosingFee": closing_fee,
            },
            "total_fees": total,
            "referral_fee": referral_fee,
            "fba_fee": fba_fee,
            "closing_fee": closing_fee,
        }
