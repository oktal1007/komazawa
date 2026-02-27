"""
Web scraper for Amazon rankings and OEM factory data.
Uses requests + BeautifulSoup with robots.txt compliance.
Falls back to demo data for reliable dashboard operation.
"""

import os
import random
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import aiohttp
from bs4 import BeautifulSoup


class WebScraper:
    """Web scraper for market data and factory information."""

    USER_AGENT = (
        "Mozilla/5.0 (compatible; OEMResearchBot/1.0; +https://example.com/bot)"
    )
    REQUEST_DELAY = 2.0  # Seconds between requests

    def __init__(self) -> None:
        self._robot_parsers: Dict[str, RobotFileParser] = {}
        self._last_request_time: float = 0.0

    def _can_fetch(self, url: str) -> bool:
        """Check if scraping is allowed by robots.txt."""
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        if domain not in self._robot_parsers:
            rp = RobotFileParser()
            rp.set_url(f"{domain}/robots.txt")
            try:
                rp.read()
            except Exception:
                # If we can't read robots.txt, assume disallowed
                return False
            self._robot_parsers[domain] = rp

        return self._robot_parsers[domain].can_fetch(self.USER_AGENT, url)

    async def _throttled_request(self, url: str) -> Optional[str]:
        """Make a rate-limited HTTP request."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.REQUEST_DELAY:
            import asyncio
            await asyncio.sleep(self.REQUEST_DELAY - elapsed)

        if not self._can_fetch(url):
            return None

        headers = {"User-Agent": self.USER_AGENT}
        self._last_request_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        return await response.text()
                    return None
        except Exception:
            return None

    async def scrape_amazon_rankings(
        self, category: str = "supplement"
    ) -> List[Dict[str, Any]]:
        """
        Scrape Amazon.co.jp supplement/health product rankings.
        Returns demo data as Amazon actively blocks scraping.
        """
        # Amazon actively blocks scraping and this would violate ToS.
        # In production, use the Keepa API or SP-API instead.
        # Return demo data for dashboard demonstration.
        return self._get_mock_rankings(category)

    async def scrape_factory_data(
        self, query: str = "OEM サプリメント 製造"
    ) -> List[Dict[str, Any]]:
        """
        Scrape OEM factory information from search results.
        Falls back to demo data for reliable operation.
        """
        use_live = os.getenv("ENABLE_LIVE_SCRAPING", "false").lower() == "true"

        if use_live:
            try:
                results = await self._scrape_factory_search(query)
                if results:
                    return results
            except Exception:
                pass

        return self._get_mock_factory_data()

    async def _scrape_factory_search(
        self, query: str
    ) -> List[Dict[str, Any]]:
        """Attempt to scrape factory data from search results."""
        # This is a simplified example. In production, you would use
        # a proper search API or curated factory database.
        search_url = f"https://www.google.com/search?q={query}"
        html = await self._throttled_request(search_url)

        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        results: List[Dict[str, Any]] = []

        for item in soup.select(".g"):
            title_elem = item.select_one("h3")
            link_elem = item.select_one("a")
            snippet_elem = item.select_one(".VwiC3b")

            if title_elem and link_elem:
                results.append({
                    "name": title_elem.get_text(strip=True),
                    "url": link_elem.get("href", ""),
                    "description": snippet_elem.get_text(strip=True)
                    if snippet_elem
                    else "",
                })

        return results

    def _get_mock_rankings(self, category: str) -> List[Dict[str, Any]]:
        """Return realistic Amazon.co.jp ranking demo data."""
        rankings: List[Dict[str, Any]] = [
            {
                "rank": 1,
                "asin": "B0CUVWX901",
                "title": "ビタミンD3 5000IU 365粒 1年分 小粒 飲みやすい",
                "brand": "サンシャインヘルス",
                "price": 1480,
                "rating": 4.6,
                "review_count": 6789,
                "estimated_sales": 5200,
            },
            {
                "rank": 2,
                "asin": "B0DFGHI901",
                "title": "エプソムソルト 入浴剤 3kg 国産 硫酸マグネシウム",
                "brand": "バスリフレ",
                "price": 1580,
                "rating": 4.4,
                "review_count": 9876,
                "estimated_sales": 6200,
            },
            {
                "rank": 3,
                "asin": "B0DABCD567",
                "title": "マルチビタミン&ミネラル 240粒 約8ヶ月分",
                "brand": "ヘルスライフ",
                "price": 1980,
                "rating": 4.1,
                "review_count": 8934,
                "estimated_sales": 4800,
            },
            {
                "rank": 4,
                "asin": "B0CBCDE678",
                "title": "コラーゲン ペプチド 粉末 無味 国産 低分子 100日分",
                "brand": "美コラーゲン",
                "price": 1880,
                "rating": 4.3,
                "review_count": 7234,
                "estimated_sales": 4600,
            },
            {
                "rank": 5,
                "asin": "B0CEFGH890",
                "title": "乳酸菌 サプリ ビフィズス菌 1000億個 30日分 腸活",
                "brand": "腸美人",
                "price": 2480,
                "rating": 4.2,
                "review_count": 5621,
                "estimated_sales": 4100,
            },
            {
                "rank": 6,
                "asin": "B0DNOPQ567",
                "title": "亜鉛 サプリ 50mg 高含有 120粒 4ヶ月分",
                "brand": "ジンクパワー",
                "price": 980,
                "rating": 4.1,
                "review_count": 5678,
                "estimated_sales": 3800,
            },
            {
                "rank": 7,
                "asin": "B0DQRST678",
                "title": "クレアチン モノハイドレート 500g パウダー 100回分",
                "brand": "マッスルテック",
                "price": 2780,
                "rating": 4.5,
                "review_count": 4567,
                "estimated_sales": 3600,
            },
            {
                "rank": 8,
                "asin": "B0CXYZ1234",
                "title": "NMN サプリメント 18000mg 高純度99.9% 60粒 日本製",
                "brand": "REVITA",
                "price": 4980,
                "rating": 4.3,
                "review_count": 2847,
                "estimated_sales": 3200,
            },
            {
                "rank": 9,
                "asin": "B0DIJKL012",
                "title": "エクオール 大豆イソフラボン 30日分 更年期 女性サプリ",
                "brand": "フェミナチュール",
                "price": 3280,
                "rating": 4.0,
                "review_count": 3456,
                "estimated_sales": 2400,
            },
            {
                "rank": 10,
                "asin": "B0DYZA2345",
                "title": "ルテイン 40mg ゼアキサンチン配合 60粒 アイケア",
                "brand": "アイプロテクト",
                "price": 2180,
                "rating": 4.2,
                "review_count": 2345,
                "estimated_sales": 2100,
            },
        ]
        return rankings

    def _get_mock_factory_data(self) -> List[Dict[str, Any]]:
        """Return realistic OEM factory demo data for Japan."""
        factories: List[Dict[str, Any]] = [
            {
                "name": "三生医薬株式会社",
                "prefecture": "静岡県",
                "categories": ["サプリメント", "健康食品", "プロテイン"],
                "dosage_forms": ["錠剤", "カプセル", "粉末", "顆粒"],
                "min_lot": "5,000個",
                "url": "https://www.example-sanseiiyaku.co.jp",
                "contact_url": "https://www.example-sanseiiyaku.co.jp/contact",
                "certifications": ["GMP", "ISO22000", "HACCP", "有機JAS"],
                "features": "業界トップクラスの製造実績。小ロットから大量生産まで対応可能。独自の造粒技術により飲みやすい小粒錠剤の製造が得意。",
            },
            {
                "name": "アピ株式会社",
                "prefecture": "岐阜県",
                "categories": ["サプリメント", "健康食品", "化粧品", "医薬部外品"],
                "dosage_forms": ["ソフトカプセル", "ハードカプセル", "錠剤", "ドリンク", "ゼリー"],
                "min_lot": "3,000個",
                "url": "https://www.example-api.co.jp",
                "contact_url": "https://www.example-api.co.jp/oem/contact",
                "certifications": ["GMP", "ISO9001", "FSSC22000", "HACCP"],
                "features": "ソフトカプセル製造で国内シェアNo.1。原料調達から最終製品まで一貫体制。海外への輸出実績も豊富。",
            },
            {
                "name": "東洋カプセル株式会社",
                "prefecture": "静岡県",
                "categories": ["サプリメント", "医薬品"],
                "dosage_forms": ["ハードカプセル", "ソフトカプセル"],
                "min_lot": "10,000個",
                "url": "https://www.example-toyo-capsule.co.jp",
                "contact_url": "https://www.example-toyo-capsule.co.jp/inquiry",
                "certifications": ["GMP", "ISO9001"],
                "features": "カプセル製造50年以上の専門メーカー。植物性カプセル（HPMC）の製造にも対応。品質管理体制が充実。",
            },
            {
                "name": "バイホロン株式会社",
                "prefecture": "富山県",
                "categories": ["サプリメント", "健康食品", "青汁", "プロテイン"],
                "dosage_forms": ["粉末", "顆粒", "スティック", "錠剤"],
                "min_lot": "1,000個",
                "url": "https://www.example-biohoron.co.jp",
                "contact_url": "https://www.example-biohoron.co.jp/oem",
                "certifications": ["GMP", "HACCP", "有機JAS"],
                "features": "小ロット1,000個から対応可能で新規参入者に人気。富山の医薬品製造の伝統を活かした高品質な製品づくり。粉末製品が得意。",
            },
            {
                "name": "協和薬品工業株式会社",
                "prefecture": "大阪府",
                "categories": ["サプリメント", "健康食品", "美容サプリ"],
                "dosage_forms": ["錠剤", "カプセル", "ドリンク", "粉末"],
                "min_lot": "5,000個",
                "url": "https://www.example-kyowayakuhin.co.jp",
                "contact_url": "https://www.example-kyowayakuhin.co.jp/contact",
                "certifications": ["GMP", "ISO22000", "HACCP"],
                "features": "美容系サプリメントの製造実績が豊富。コラーゲン、プラセンタなどの美容成分配合に強み。パッケージデザインの提案も可能。",
            },
            {
                "name": "日本ヘルスケア製造株式会社",
                "prefecture": "東京都",
                "categories": ["サプリメント", "健康食品", "CBD製品"],
                "dosage_forms": ["ソフトカプセル", "オイル", "グミ", "タブレット"],
                "min_lot": "3,000個",
                "url": "https://www.example-jhc.co.jp",
                "contact_url": "https://www.example-jhc.co.jp/oem-inquiry",
                "certifications": ["GMP", "ISO9001", "HACCP"],
                "features": "新素材・トレンド成分への対応が早い。CBD製品の製造実績あり。グミ・チュアブルなど新剤形の開発力が高い。",
            },
            {
                "name": "九州健康産業株式会社",
                "prefecture": "福岡県",
                "categories": ["サプリメント", "健康食品", "入浴剤", "コスメ"],
                "dosage_forms": ["錠剤", "カプセル", "粉末", "入浴剤"],
                "min_lot": "2,000個",
                "url": "https://www.example-kyushu-health.co.jp",
                "contact_url": "https://www.example-kyushu-health.co.jp/contact",
                "certifications": ["GMP", "HACCP"],
                "features": "九州の自然素材を活用した製品づくりが特徴。入浴剤・バスソルトの製造にも対応。コスト競争力が高い。",
            },
            {
                "name": "北海道ナチュラルサイエンス株式会社",
                "prefecture": "北海道",
                "categories": ["サプリメント", "健康食品", "乳酸菌製品"],
                "dosage_forms": ["カプセル", "粉末", "ドリンク", "ヨーグルト"],
                "min_lot": "5,000個",
                "url": "https://www.example-hokkaido-ns.co.jp",
                "contact_url": "https://www.example-hokkaido-ns.co.jp/oem",
                "certifications": ["GMP", "ISO22000", "HACCP", "有機JAS"],
                "features": "北海道産乳酸菌・ビフィズス菌を使用した独自の発酵技術。プロバイオティクス製品の製造に特化。冷蔵管理体制も完備。",
            },
            {
                "name": "中部サプリメント工業株式会社",
                "prefecture": "愛知県",
                "categories": ["サプリメント", "プロテイン", "スポーツ栄養"],
                "dosage_forms": ["粉末", "錠剤", "プロテインバー", "ゼリー"],
                "min_lot": "3,000個",
                "url": "https://www.example-chubu-supple.co.jp",
                "contact_url": "https://www.example-chubu-supple.co.jp/inquiry",
                "certifications": ["GMP", "HACCP", "NSF認証"],
                "features": "スポーツ栄養製品の製造に強み。プロテイン製品のフレーバー開発力が高い。アンチドーピング対応のNSF認証取得済み。",
            },
            {
                "name": "湘南ファーマテック株式会社",
                "prefecture": "神奈川県",
                "categories": ["サプリメント", "健康食品", "NMN", "エイジングケア"],
                "dosage_forms": ["カプセル", "錠剤", "粉末"],
                "min_lot": "2,000個",
                "url": "https://www.example-shonan-pharma.co.jp",
                "contact_url": "https://www.example-shonan-pharma.co.jp/oem",
                "certifications": ["GMP", "ISO9001", "HACCP"],
                "features": "NMN・エイジングケア成分の製造実績が豊富。高純度原料の調達ネットワークを保有。最新の品質分析機器を完備。",
            },
        ]
        return factories
