"""Claude APIを使った鑑定文生成サービス"""

import json
from typing import Optional

import anthropic

SYSTEM_PROMPT = """あなたは古代エジプトの女神バステトの化身「月花の守猫 バステリア・ルア」です。
月の満ち欠けに合わせた霊視と数千年の叡智によってお客様の運命を鑑定します。

【語り口の絶対ルール】
- お客様を「〇〇様」と名前で呼び、各章に2〜3回織り交ぜる
- 「バステト女神からの啓示により」「女神の導きによって」を自然に使う
- すべて断言形で書く（「〜です」「〜となります」）
- ネガティブな内容は必ず「魂の成長」「宇宙の計画」として肯定変換する
- 具体的な情景・場面・タイミングを描写して臨場感を出す
- 文学的・詩的な表現を随所に使う（特に後半）

【必須構成（この順序を厳守）】
- タイトル：「バステト女神からの【鑑定メニュー名】」
- P1本文（600字以内）：感謝メッセージ + 共感・受容 + 明るい展望の結論
- P2本文（900字以内）：展望の理由（占術根拠）+ 悩みの原因（世界観的）+ 解決策
- P3本文（800字以内）：未来ビジョンの情景描写 + セールストーク + 署名

【文字数が多い場合のルール】
各パートが上限を超える場合は、内容を「追加ページ本文」として分割すること。
追加ページは何ページでも追加してよい（1ページあたり900字以内）。
必ずJSONで以下の構造で返すこと：

{
  "title": "バステト女神からの【鑑定メニュー名】",
  "pages": [
    {"page_role": "cover", "text": "P1本文（600字以内）"},
    {"page_role": "body", "text": "P2本文（900字以内）"},
    {"page_role": "body", "text": "追加ページがあればここに（900字以内）"},
    {"page_role": "closing", "text": "最終ページ本文（800字以内・必ず署名で終わる）"}
  ]
}

page_roleは cover / body / closing の3種類のみ。
closingは必ず最後の1ページのみ。bodyは何ページでも追加可能。
署名「月の光と古代の叡智に包まれて\\n月花の守猫 バステリア・ルア」は必ずclosingの末尾に入れる。

【重要】JSONのみを返してください。JSON以外のテキストは一切含めないでください。"""


def _build_user_prompt(
    customer_name: str,
    category: str,
    menu_name: str,
    consultation_content: str,
    divination_methods: list[str],
    numerology_result: Optional[dict],
    astrology_result: Optional[dict],
    four_pillars_result: Optional[dict],
    additional_memo: str = "",
) -> str:
    """ユーザープロンプトを構築"""
    prompt_parts = [
        f"【お客様名】{customer_name}",
        f"【鑑定カテゴリ】{category}",
        f"【鑑定メニュー名】{menu_name}",
        f"【お客様のご相談内容】\n{consultation_content}",
    ]

    if additional_memo:
        prompt_parts.append(f"【追加メモ】\n{additional_memo}")

    # 占術結果を追加
    if numerology_result and "数秘術" in divination_methods:
        lp = numerology_result["life_path"]
        soul = numerology_result["soul"]
        pers = numerology_result["personality"]
        prompt_parts.append(
            f"【数秘術の計算結果】\n"
            f"・ライフパスナンバー: {lp['number']}（{lp['keyword']}）- {lp['description']}\n"
            f"・ソウルナンバー: {soul['number']} - {soul['description']}\n"
            f"・パーソナリティナンバー: {pers['number']} - {pers['description']}"
        )

    if astrology_result and "西洋占星術" in divination_methods:
        parts = [f"・太陽星座: {astrology_result['sun_sign']['sign']} - {astrology_result['sun_sign']['trait']}"]
        if "moon_sign" in astrology_result:
            parts.append(f"・月星座: {astrology_result['moon_sign']['sign']} - {astrology_result['moon_sign']['trait']}")
        if "ascendant" in astrology_result:
            parts.append(f"・上昇星座(ASC): {astrology_result['ascendant']['sign']} - {astrology_result['ascendant']['trait']}")
        prompt_parts.append("【西洋占星術の計算結果】\n" + "\n".join(parts))

    if four_pillars_result and "四柱推命" in divination_methods:
        fp = four_pillars_result
        lines = []
        for pillar_name, key in [("年柱", "year_pillar"), ("月柱", "month_pillar"), ("日柱", "day_pillar"), ("時柱", "hour_pillar")]:
            if key in fp:
                p = fp[key]
                lines.append(f"・{pillar_name}: {p['stem']}{p['branch']}（{p['stem_detail'].get('description', '')}）")
        # 五行バランス
        balance = fp.get("five_elements_balance", {})
        balance_str = "、".join(f"{k}:{v}" for k, v in balance.items())
        lines.append(f"・五行バランス: {balance_str}")
        prompt_parts.append("【四柱推命の計算結果】\n" + "\n".join(lines))

    prompt_parts.append(
        "\n上記の情報をもとに、鑑定7ステップ構文に従って鑑定レポートを生成してください。\n"
        "必ずJSON形式のみで返答してください。"
    )

    return "\n\n".join(prompt_parts)


async def generate_divination_report(
    api_key: str,
    customer_name: str,
    category: str,
    menu_name: str,
    consultation_content: str,
    divination_methods: list[str],
    numerology_result: Optional[dict] = None,
    astrology_result: Optional[dict] = None,
    four_pillars_result: Optional[dict] = None,
    additional_memo: str = "",
) -> dict:
    """Claude APIで鑑定レポートを生成"""
    client = anthropic.AsyncAnthropic(api_key=api_key)

    user_prompt = _build_user_prompt(
        customer_name=customer_name,
        category=category,
        menu_name=menu_name,
        consultation_content=consultation_content,
        divination_methods=divination_methods,
        numerology_result=numerology_result,
        astrology_result=astrology_result,
        four_pillars_result=four_pillars_result,
        additional_memo=additional_memo,
    )

    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    response_text = message.content[0].text.strip()

    # JSONブロックを抽出（```json ... ``` でラップされている場合に対応）
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        json_lines = []
        in_json = False
        for line in lines:
            if line.startswith("```") and not in_json:
                in_json = True
                continue
            elif line.startswith("```") and in_json:
                break
            elif in_json:
                json_lines.append(line)
        response_text = "\n".join(json_lines)

    return json.loads(response_text)
