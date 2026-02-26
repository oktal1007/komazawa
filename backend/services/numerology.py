"""数秘術計算サービス - バステト神の世界観で解釈"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# ローマ字→母音・子音分類用マッピング
VOWELS = set("aeiou")


def _load_numerology_data() -> dict:
    with open(DATA_DIR / "numerology.json", "r", encoding="utf-8") as f:
        return json.load(f)


def _reduce_to_single(n: int) -> int:
    """マスターナンバー(11,22,33)を保持しつつ一桁に還元"""
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n


def _digit_sum(text: str) -> int:
    """文字列中の数字を合計"""
    return sum(int(c) for c in text if c.isdigit())


def calc_life_path_number(year: int, month: int, day: int) -> int:
    """ライフパスナンバー: 生年月日の各桁を合計して還元"""
    total = _digit_sum(f"{year:04d}{month:02d}{day:02d}")
    return _reduce_to_single(total)


def _name_to_numbers(name: str) -> list[int]:
    """名前をピタゴリアン数秘術の数値に変換
    (日本語名はローマ字入力を想定し、アルファベット部分のみ計算)"""
    mapping = {
        "a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9,
        "j": 1, "k": 2, "l": 3, "m": 4, "n": 5, "o": 6, "p": 7, "q": 8, "r": 9,
        "s": 1, "t": 2, "u": 3, "v": 4, "w": 5, "x": 6, "y": 7, "z": 8,
    }
    return [mapping[c] for c in name.lower() if c in mapping]


def calc_soul_number(name: str) -> int:
    """ソウルナンバー: 名前の母音の数値を合計"""
    mapping = {
        "a": 1, "e": 5, "i": 9, "o": 6, "u": 3,
    }
    total = sum(mapping.get(c, 0) for c in name.lower() if c in VOWELS)
    return _reduce_to_single(total) if total > 0 else 1


def calc_personality_number(name: str) -> int:
    """パーソナリティナンバー: 名前の子音の数値を合計"""
    all_nums = _name_to_numbers(name)
    consonant_total = sum(
        n for c, n in zip(name.lower(), all_nums)
        if c.isalpha() and c not in VOWELS
    )
    # 名前にアルファベットが含まれない場合のフォールバック
    if consonant_total == 0:
        consonant_total = sum(all_nums) if all_nums else 1
    return _reduce_to_single(consonant_total)


def calculate_numerology(name: str, year: int, month: int, day: int) -> dict:
    """数秘術の全計算結果を返す"""
    data = _load_numerology_data()

    life_path = calc_life_path_number(year, month, day)
    soul = calc_soul_number(name)
    personality = calc_personality_number(name)

    lp_key = str(life_path)
    soul_key = str(soul if soul <= 9 else _reduce_to_single(soul))
    pers_key = str(personality if personality <= 9 else _reduce_to_single(personality))

    # マスターナンバーはlife_pathのみ対応、soul/personalityは1-9に還元
    if soul_key not in data["soul_number"]:
        soul_key = str(_reduce_to_single(int(soul_key)))
    if pers_key not in data["personality_number"]:
        pers_key = str(_reduce_to_single(int(pers_key)))

    return {
        "life_path": {
            "number": life_path,
            "keyword": data["life_path"].get(lp_key, {}).get("keyword", ""),
            "description": data["life_path"].get(lp_key, {}).get("description", ""),
        },
        "soul": {
            "number": soul,
            "description": data["soul_number"].get(soul_key, ""),
        },
        "personality": {
            "number": personality,
            "description": data["personality_number"].get(pers_key, ""),
        },
    }
