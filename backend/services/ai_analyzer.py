"""
Claude AI analyzer for review analysis and trend reporting.
Uses the Anthropic Python SDK to generate insights from product reviews
and market trend data. Falls back to demo data when API key is not configured.
"""

import json
import os
from typing import Any, Dict, List, Optional

try:
    import anthropic
except ImportError:
    anthropic = None  # type: ignore


class AIAnalyzer:
    """AI-powered analyzer using Claude for review analysis and trend reports."""

    MODEL = "claude-sonnet-4-20250514"

    def __init__(self) -> None:
        self.api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        self.client: Optional[Any] = None
        if self.api_key and anthropic:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    @property
    def is_configured(self) -> bool:
        """Check if the Anthropic API key is configured."""
        return self.client is not None

    async def analyze_reviews(
        self, reviews: List[Dict[str, Any]], asin: str
    ) -> Dict[str, Any]:
        """
        Analyze product reviews using Claude AI.
        Returns negative categories with counts, gap analysis,
        differentiation points, and strengths/weaknesses summary.
        """
        if not self.is_configured:
            return self._get_mock_review_analysis(asin)

        reviews_text = "\n".join(
            [
                f"[Rating: {r.get('rating', 'N/A')}] {r.get('title', '')}: {r.get('body', '')}"
                for r in reviews[:200]  # Limit to 200 reviews for token management
            ]
        )

        prompt = f"""以下はAmazon商品（ASIN: {asin}）のレビュー一覧です。これらのレビューを分析して、以下の形式でJSON形式で回答してください。

レビュー:
{reviews_text}

以下のJSON形式で回答してください:
{{
    "negative_categories": [
        {{"category": "カテゴリ名", "count": 件数, "severity": "high/medium/low", "examples": ["例1", "例2"]}}
    ],
    "gap_analysis": [
        {{"gap": "改善ポイント", "frequency": "high/medium/low", "opportunity": "ビジネス機会の説明"}}
    ],
    "differentiation_points": [
        {{"point": "差別化ポイント", "description": "詳細説明", "priority": "high/medium/low"}}
    ],
    "strengths": [
        {{"strength": "強み", "mention_count": 件数}}
    ],
    "weaknesses": [
        {{"weakness": "弱み", "mention_count": 件数, "improvement_suggestion": "改善提案"}}
    ],
    "overall_sentiment": {{
        "positive_ratio": 0.0,
        "neutral_ratio": 0.0,
        "negative_ratio": 0.0,
        "summary": "全体的な感情の要約"
    }}
}}"""

        try:
            message = self.client.messages.create(
                model=self.MODEL,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
            else:
                return {"error": "Failed to parse AI response", "raw": response_text}
        except Exception as e:
            return {"error": str(e)}

    async def generate_trend_report(
        self, trends_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a weekly trend report using Claude AI.
        Returns top 5 ingredients, predictions, and market entry timing.
        """
        if not self.is_configured:
            return self._get_mock_trend_report()

        trends_text = json.dumps(trends_data, ensure_ascii=False, indent=2)

        prompt = f"""以下はサプリメント・健康食品市場の成分トレンドデータです。このデータを分析して、週次トレンドレポートを作成してください。

トレンドデータ:
{trends_text}

以下のJSON形式で回答してください:
{{
    "report_date": "YYYY-MM-DD",
    "top_ingredients": [
        {{
            "rank": 1,
            "name": "成分名",
            "mention_count": 件数,
            "growth_rate": 成長率（%）,
            "trend_direction": "up/stable/down",
            "market_potential": "high/medium/low",
            "summary": "この成分に関するトレンドの要約"
        }}
    ],
    "predictions": [
        {{
            "ingredient": "成分名",
            "prediction": "予測内容",
            "confidence": "high/medium/low",
            "timeframe": "3ヶ月/6ヶ月/1年"
        }}
    ],
    "market_entry_timing": [
        {{
            "ingredient": "成分名",
            "recommended_timing": "今すぐ/3ヶ月以内/6ヶ月以内/様子見",
            "reason": "理由",
            "risk_level": "high/medium/low"
        }}
    ],
    "overall_market_summary": "市場全体の要約"
}}"""

        try:
            message = self.client.messages.create(
                model=self.MODEL,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
            else:
                return {"error": "Failed to parse AI response", "raw": response_text}
        except Exception as e:
            return {"error": str(e)}

    def _get_mock_review_analysis(self, asin: str) -> Dict[str, Any]:
        """Return realistic mock review analysis data."""
        return {
            "negative_categories": [
                {
                    "category": "粒の大きさ・飲みにくさ",
                    "count": 45,
                    "severity": "high",
                    "examples": [
                        "粒が大きくて飲みにくい",
                        "高齢者には辛いサイズ",
                        "もう少し小さくしてほしい",
                    ],
                },
                {
                    "category": "効果の実感がない",
                    "count": 38,
                    "severity": "medium",
                    "examples": [
                        "1ヶ月飲んでも変化なし",
                        "期待したほどの効果は感じない",
                        "プラセボかもしれない",
                    ],
                },
                {
                    "category": "パッケージの品質",
                    "count": 28,
                    "severity": "medium",
                    "examples": [
                        "ジッパーが閉まらない",
                        "湿気やすい",
                        "デザインが安っぽい",
                    ],
                },
                {
                    "category": "価格が高い",
                    "count": 22,
                    "severity": "low",
                    "examples": [
                        "含有量に対して割高",
                        "継続するには高い",
                        "もう少し安ければリピートする",
                    ],
                },
                {
                    "category": "お腹の不調",
                    "count": 15,
                    "severity": "medium",
                    "examples": [
                        "お腹が緩くなった",
                        "胃もたれする",
                        "体質に合わなかった",
                    ],
                },
            ],
            "gap_analysis": [
                {
                    "gap": "小粒タイプの需要",
                    "frequency": "high",
                    "opportunity": "高齢者や錠剤が苦手な層向けに小粒・分割可能なサプリメントの需要が高い。競合の多くが大粒タイプのため、差別化の好機。",
                },
                {
                    "gap": "効果の可視化",
                    "frequency": "high",
                    "opportunity": "体感効果を測定・記録できるアプリ連携や、血液検査キット同梱など効果を実感できる仕組みの導入。",
                },
                {
                    "gap": "パッケージデザインの改善",
                    "frequency": "medium",
                    "opportunity": "遮光・防湿に優れた個包装タイプの需要。持ち運びやすさも重要なポイント。",
                },
                {
                    "gap": "成分の透明性",
                    "frequency": "medium",
                    "opportunity": "第三者機関による検査結果の公開や、原料産地の開示を求める声が増加。トレーサビリティの確保が差別化要因に。",
                },
            ],
            "differentiation_points": [
                {
                    "point": "小粒設計 + 個包装",
                    "description": "業界で少ない小粒（8mm以下）タイプを個包装で提供。飲みやすさと携帯性を両立。",
                    "priority": "high",
                },
                {
                    "point": "成分検査証明書の同梱",
                    "description": "ロットごとの第三者機関検査結果を同梱し、成分含有量の信頼性を担保。",
                    "priority": "high",
                },
                {
                    "point": "定期購入での体調管理サポート",
                    "description": "LINE連携で毎日の体調記録とAI分析による効果の可視化機能を提供。",
                    "priority": "medium",
                },
                {
                    "point": "環境配慮パッケージ",
                    "description": "バイオマスプラスチック使用のエコパッケージで環境意識の高い層にアピール。",
                    "priority": "low",
                },
            ],
            "strengths": [
                {"strength": "コストパフォーマンスの高さ", "mention_count": 89},
                {"strength": "国内製造・GMP認定の安心感", "mention_count": 76},
                {"strength": "成分含有量の多さ", "mention_count": 65},
                {"strength": "定期購入の利便性", "mention_count": 43},
            ],
            "weaknesses": [
                {
                    "weakness": "粒のサイズが大きい",
                    "mention_count": 45,
                    "improvement_suggestion": "直径8mm以下の小粒タイプに変更。または粉末・液体タイプの展開を検討。",
                },
                {
                    "weakness": "効果の実感に時間がかかる",
                    "mention_count": 38,
                    "improvement_suggestion": "摂取ガイドラインの同梱と、期待値の適切な設定。3ヶ月継続プログラムの提案。",
                },
                {
                    "weakness": "パッケージの密閉性",
                    "mention_count": 28,
                    "improvement_suggestion": "ジッパー式からスクリューキャップ式ボトルへの変更を検討。",
                },
            ],
            "overall_sentiment": {
                "positive_ratio": 0.58,
                "neutral_ratio": 0.22,
                "negative_ratio": 0.20,
                "summary": "全体的にポジティブな評価が多いが、粒の大きさとパッケージの品質に関する改善要望が目立つ。成分品質と価格のバランスは高く評価されている。新規参入者は小粒設計とパッケージ品質の改善で差別化が可能。",
            },
        }

    def _get_mock_trend_report(self) -> Dict[str, Any]:
        """Return realistic mock trend report data."""
        return {
            "report_date": "2025-01-20",
            "top_ingredients": [
                {
                    "rank": 1,
                    "name": "NMN（ニコチンアミドモノヌクレオチド）",
                    "mention_count": 12450,
                    "growth_rate": 34.5,
                    "trend_direction": "up",
                    "market_potential": "high",
                    "summary": "エイジングケア市場で急成長中。高純度・高含有量の製品が人気。価格帯は3,000〜15,000円と幅広い。",
                },
                {
                    "rank": 2,
                    "name": "エクオール",
                    "mention_count": 8920,
                    "growth_rate": 28.3,
                    "trend_direction": "up",
                    "market_potential": "high",
                    "summary": "更年期対策として女性市場で急速に認知度が向上。大豆イソフラボンからの進化系として注目。",
                },
                {
                    "rank": 3,
                    "name": "乳酸菌・ビフィズス菌",
                    "mention_count": 15600,
                    "growth_rate": 12.1,
                    "trend_direction": "stable",
                    "market_potential": "high",
                    "summary": "腸活ブームの継続で安定成長。菌株の差別化が進み、特定の効果を謳う製品が増加。",
                },
                {
                    "rank": 4,
                    "name": "CBD（カンナビジオール）",
                    "mention_count": 6780,
                    "growth_rate": 45.2,
                    "trend_direction": "up",
                    "market_potential": "medium",
                    "summary": "リラックス・睡眠市場で急成長。ただし規制リスクと消費者の認知度にばらつきあり。",
                },
                {
                    "rank": 5,
                    "name": "クレアチン",
                    "mention_count": 9340,
                    "growth_rate": 18.7,
                    "trend_direction": "up",
                    "market_potential": "medium",
                    "summary": "筋トレ市場の拡大に伴い成長。フィットネスブームでターゲット層が女性にも拡大中。",
                },
            ],
            "predictions": [
                {
                    "ingredient": "NMN",
                    "prediction": "価格競争が激化し、平均単価は下がるが市場規模は拡大。高純度差別化が重要に。",
                    "confidence": "high",
                    "timeframe": "6ヶ月",
                },
                {
                    "ingredient": "エクオール",
                    "prediction": "テレビCM効果で一般認知度がさらに上昇。大手メーカー参入により競争激化の可能性。",
                    "confidence": "medium",
                    "timeframe": "3ヶ月",
                },
                {
                    "ingredient": "ウロリチン",
                    "prediction": "次のNMNとして注目度が急上昇の兆し。早期参入で先行者利益が期待できる。",
                    "confidence": "medium",
                    "timeframe": "6ヶ月",
                },
                {
                    "ingredient": "マグネシウム",
                    "prediction": "SNSでのバズをきっかけに若年層での認知度が急上昇中。入浴剤市場との相乗効果も。",
                    "confidence": "high",
                    "timeframe": "3ヶ月",
                },
            ],
            "market_entry_timing": [
                {
                    "ingredient": "NMN",
                    "recommended_timing": "今すぐ",
                    "reason": "市場拡大中だが競争も激化。高純度・低価格の差別化で参入余地あり。",
                    "risk_level": "medium",
                },
                {
                    "ingredient": "エクオール",
                    "recommended_timing": "3ヶ月以内",
                    "reason": "認知度上昇に伴い需要増加が見込まれる。OEM製造の準備期間を考慮すると今から動くべき。",
                    "risk_level": "low",
                },
                {
                    "ingredient": "ウロリチン",
                    "recommended_timing": "6ヶ月以内",
                    "reason": "まだ市場形成の初期段階。先行投資としてのリスクはあるが、先行者メリットが大きい。",
                    "risk_level": "medium",
                },
                {
                    "ingredient": "CBD",
                    "recommended_timing": "様子見",
                    "reason": "規制環境が不透明。法改正の動向を注視してからの参入が安全。",
                    "risk_level": "high",
                },
            ],
            "overall_market_summary": "健康食品・サプリメント市場は堅調に成長を続けており、特にエイジングケア、腸活、女性の健康に関連する成分が好調。NMNとエクオールは参入のタイミングとして適切。消費者は成分の品質と透明性をますます重視する傾向にあり、第三者検査や原料のトレーサビリティが差別化の鍵となる。ECチャネルでの販売が引き続き主流で、Amazon FBAを活用した低リスクでの市場参入が有効。",
        }
