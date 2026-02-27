"""Web scraper for Amazon rankings and OEM factory data."""

import os
from typing import Optional


# Demo factory data for when scraping is not available
DEMO_FACTORIES = [
    {
        "name": "三生医薬株式会社",
        "prefecture": "静岡県",
        "categories": "サプリメント,健康食品",
        "dosage_forms": "錠剤,カプセル,粉末,ゼリー",
        "min_lot": 3000,
        "url": "https://example.com/sansho",
        "contact_url": "https://example.com/sansho/contact",
        "certifications": "GMP,ISO9001",
        "features": "サプリメントOEM実績50年以上。小ロットから対応可能。錠剤・カプセル・粉末・ゼリーなど多様な剤形に対応。",
    },
    {
        "name": "東洋カプセル株式会社",
        "prefecture": "富山県",
        "categories": "サプリメント",
        "dosage_forms": "カプセル,ソフトカプセル",
        "min_lot": 5000,
        "url": "https://example.com/toyocap",
        "contact_url": "https://example.com/toyocap/contact",
        "certifications": "GMP,ISO22000,HACCP",
        "features": "ソフトカプセル製造のパイオニア。品質管理体制が充実。海外輸出実績あり。",
    },
    {
        "name": "株式会社バスクリン製造",
        "prefecture": "東京都",
        "categories": "入浴剤",
        "dosage_forms": "バスソルト,重炭酸,バブル系,粉末",
        "min_lot": 1000,
        "url": "https://example.com/bathklin",
        "contact_url": "https://example.com/bathklin/contact",
        "certifications": "GMP,ISO9001",
        "features": "入浴剤専門OEMメーカー。バスソルト・重炭酸タブレット・バブルバスなど幅広く対応。小ロット1000個から。",
    },
    {
        "name": "株式会社アピ",
        "prefecture": "愛知県",
        "categories": "サプリメント,健康食品",
        "dosage_forms": "錠剤,カプセル,粉末,ドリンク",
        "min_lot": 10000,
        "url": "https://example.com/api-corp",
        "contact_url": "https://example.com/api-corp/contact",
        "certifications": "GMP,ISO9001,ISO22000,HACCP",
        "features": "健康食品OEM国内トップシェア。大量生産に強み。研究開発支援あり。原料調達から一貫対応。",
    },
    {
        "name": "株式会社コスメテック・ジャパン",
        "prefecture": "大阪府",
        "categories": "スキンケア,化粧品",
        "dosage_forms": "クリーム,美容液,ローション,パック",
        "min_lot": 2000,
        "url": "https://example.com/cosmetech",
        "contact_url": "https://example.com/cosmetech/contact",
        "certifications": "GMP,ISO22716",
        "features": "化粧品・スキンケアOEM専門。処方開発から製造まで一貫対応。オーガニック原料にも対応。",
    },
    {
        "name": "日本バルク薬品株式会社",
        "prefecture": "群馬県",
        "categories": "サプリメント,入浴剤",
        "dosage_forms": "錠剤,粉末,バスソルト",
        "min_lot": 2000,
        "url": "https://example.com/nihon-bulk",
        "contact_url": "https://example.com/nihon-bulk/contact",
        "certifications": "GMP",
        "features": "サプリメントと入浴剤の両方に対応。原料の品質にこだわり。少量生産の相談可。",
    },
    {
        "name": "富山薬品工業株式会社",
        "prefecture": "富山県",
        "categories": "サプリメント",
        "dosage_forms": "錠剤,カプセル,粉末,顆粒",
        "min_lot": 5000,
        "url": "https://example.com/toyama-pharma",
        "contact_url": "https://example.com/toyama-pharma/contact",
        "certifications": "GMP,ISO9001,HACCP",
        "features": "製薬会社の技術力を活かした高品質サプリメント製造。顆粒・打錠技術に定評。",
    },
    {
        "name": "株式会社ナチュラルファクトリー",
        "prefecture": "北海道",
        "categories": "サプリメント,スキンケア",
        "dosage_forms": "カプセル,粉末,美容液",
        "min_lot": 1000,
        "url": "https://example.com/natural-factory",
        "contact_url": "https://example.com/natural-factory/contact",
        "certifications": "GMP,有機JAS",
        "features": "北海道産原料にこだわったオーガニックサプリ・コスメOEM。有機JAS認証取得。小ロット対応可。",
    },
    {
        "name": "株式会社温泉科学研究所",
        "prefecture": "神奈川県",
        "categories": "入浴剤",
        "dosage_forms": "バスソルト,重炭酸,バスボム",
        "min_lot": 500,
        "url": "https://example.com/onsen-lab",
        "contact_url": "https://example.com/onsen-lab/contact",
        "certifications": "GMP",
        "features": "入浴剤専門。温泉成分を再現した入浴剤開発が得意。バスボム・バスソルトの小ロット対応。最小500個から。",
    },
    {
        "name": "協和薬品工業株式会社",
        "prefecture": "新潟県",
        "categories": "サプリメント,健康食品",
        "dosage_forms": "錠剤,カプセル,ゼリー,ドリンク",
        "min_lot": 3000,
        "url": "https://example.com/kyowa-pharma",
        "contact_url": "https://example.com/kyowa-pharma/contact",
        "certifications": "GMP,ISO9001,ISO22000",
        "features": "ゼリー・ドリンク型サプリメントに強み。味の開発力が高い。スティックゼリーの実績多数。",
    },
    {
        "name": "株式会社コスモビューティ",
        "prefecture": "大阪府",
        "categories": "化粧品,スキンケア,入浴剤",
        "dosage_forms": "クリーム,ローション,バスソルト,シャンプー",
        "min_lot": 3000,
        "url": "https://example.com/cosmo-beauty",
        "contact_url": "https://example.com/cosmo-beauty/contact",
        "certifications": "GMP,ISO22716,ISO9001",
        "features": "化粧品・入浴剤の複合OEM。シャンプー・ボディケア製品にも対応。大阪・東京に拠点あり。",
    },
    {
        "name": "株式会社サンヘルス",
        "prefecture": "埼玉県",
        "categories": "サプリメント",
        "dosage_forms": "錠剤,粉末,カプセル",
        "min_lot": 1500,
        "url": "https://example.com/sunhealth",
        "contact_url": "https://example.com/sunhealth/contact",
        "certifications": "GMP",
        "features": "中小ロット対応のサプリメントOEM。短納期対応可。パッケージデザインの支援サービスあり。",
    },
]


async def scrape_amazon_rankings(category: str = "supplement") -> list[dict]:
    """Scrape Amazon supplement rankings. Returns demo data as fallback."""
    # In production, this would scrape Amazon rankings
    # For now, return demo data
    demo_products = [
        {"name": "NMN サプリメント 9000mg", "category": category, "rank": 1},
        {"name": "マグネシウム サプリ 400mg", "category": category, "rank": 2},
        {"name": "ビタミンD3 サプリメント", "category": category, "rank": 3},
    ]
    return demo_products


async def scrape_factory_data(query: Optional[str] = None) -> list[dict]:
    """
    Scrape OEM factory data. Returns demo data as fallback.
    In production, would search Google and OEM matching sites.
    """
    factories = DEMO_FACTORIES
    if query:
        query_lower = query.lower()
        factories = [
            f
            for f in factories
            if query_lower in f["name"].lower()
            or query_lower in f["categories"].lower()
            or query_lower in f["features"].lower()
            or query_lower in f["dosage_forms"].lower()
        ]
    return factories


async def scrape_ingredient_trends() -> list[dict]:
    """
    Scrape ingredient trend data from Amazon, iHerb, health media.
    Returns demo data as fallback.
    """
    demo_trends = [
        {
            "ingredient_name": "NMN（ニコチンアミドモノヌクレオチド）",
            "mention_count": 1250,
            "growth_rate": 0.45,
            "market_size": 15000000000,
        },
        {
            "ingredient_name": "マグネシウム",
            "mention_count": 980,
            "growth_rate": 0.32,
            "market_size": 12000000000,
        },
        {
            "ingredient_name": "ビタミンD3",
            "mention_count": 870,
            "growth_rate": 0.28,
            "market_size": 10000000000,
        },
        {
            "ingredient_name": "CBDオイル",
            "mention_count": 750,
            "growth_rate": 0.55,
            "market_size": 8000000000,
        },
        {
            "ingredient_name": "重炭酸（入浴剤）",
            "mention_count": 680,
            "growth_rate": 0.38,
            "market_size": 6000000000,
        },
        {
            "ingredient_name": "エクオール",
            "mention_count": 620,
            "growth_rate": 0.25,
            "market_size": 5500000000,
        },
        {
            "ingredient_name": "ラクトフェリン",
            "mention_count": 550,
            "growth_rate": 0.18,
            "market_size": 4500000000,
        },
        {
            "ingredient_name": "GABA",
            "mention_count": 520,
            "growth_rate": 0.22,
            "market_size": 4000000000,
        },
        {
            "ingredient_name": "エプソムソルト（入浴剤）",
            "mention_count": 480,
            "growth_rate": 0.35,
            "market_size": 3500000000,
        },
        {
            "ingredient_name": "アシュワガンダ",
            "mention_count": 450,
            "growth_rate": 0.62,
            "market_size": 2000000000,
        },
        {
            "ingredient_name": "5-ALA",
            "mention_count": 380,
            "growth_rate": 0.48,
            "market_size": 1800000000,
        },
        {
            "ingredient_name": "ターメリック（クルクミン）",
            "mention_count": 350,
            "growth_rate": 0.15,
            "market_size": 3000000000,
        },
    ]
    return demo_trends
