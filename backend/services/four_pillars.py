"""四柱推命計算サービス"""

import json
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent / "data"

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 月の干支計算用テーブル（年干→月干の開始インデックス）
MONTH_STEM_START = {
    "甲": 2, "己": 2,  # 丙寅から
    "乙": 4, "庚": 4,  # 戊寅から
    "丙": 6, "辛": 6,  # 庚寅から
    "丁": 8, "壬": 8,  # 壬寅から
    "戊": 0, "癸": 0,  # 甲寅から
}

# 時の干支計算用テーブル（日干→時干の開始インデックス）
HOUR_STEM_START = {
    "甲": 0, "己": 0,  # 甲子から
    "乙": 2, "庚": 2,  # 丙子から
    "丙": 4, "辛": 4,  # 戊子から
    "丁": 6, "壬": 6,  # 庚子から
    "戊": 8, "癸": 8,  # 壬子から
}


def _load_four_pillars_data() -> dict:
    with open(DATA_DIR / "four_pillars.json", "r", encoding="utf-8") as f:
        return json.load(f)


def _calc_year_pillar(year: int) -> tuple[str, str]:
    """年柱の計算"""
    stem_idx = (year - 4) % 10
    branch_idx = (year - 4) % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


def _calc_month_pillar(year: int, month: int) -> tuple[str, str]:
    """月柱の計算（節月基準の簡易版）"""
    year_stem = HEAVENLY_STEMS[(year - 4) % 10]
    start = MONTH_STEM_START[year_stem]
    # 月の地支は寅(2)から始まる
    branch_idx = (month + 1) % 12  # 1月→寅(index 2)
    stem_idx = (start + month - 1) % 10
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


def _calc_day_pillar(year: int, month: int, day: int) -> tuple[str, str]:
    """日柱の計算（簡易版 - 基準日からの日数差で計算）"""
    # 基準日: 2000年1月1日 = 甲子(index 0, 0) → 実際は丙辰だが計算上の基準
    from datetime import date

    base_date = date(2000, 1, 1)
    target_date = date(year, month, day)
    diff = (target_date - base_date).days
    # 2000年1月1日は甲辰日（干index=0, 支index=4 → 六十干支の40番目）
    base_sexagenary = 40
    sexagenary = (base_sexagenary + diff) % 60
    stem_idx = sexagenary % 10
    branch_idx = sexagenary % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


def _calc_hour_pillar(day_stem: str, hour: int) -> tuple[str, str]:
    """時柱の計算"""
    # 時刻→地支（2時間ごと）
    branch_idx = ((hour + 1) // 2) % 12
    start = HOUR_STEM_START[day_stem]
    stem_idx = (start + branch_idx) % 10
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


def _calc_five_elements_balance(pillars: list[tuple[str, str]], data: dict) -> dict:
    """五行バランスの計算"""
    balance = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}

    stems_data = data["heavenly_stems"]
    branches_data = data["earthly_branches"]

    for stem, branch in pillars:
        if stem in stems_data:
            balance[stems_data[stem]["element"]] += 1
        if branch in branches_data:
            balance[branches_data[branch]["element"]] += 1

    return balance


def calculate_four_pillars(
    year: int, month: int, day: int, hour: Optional[int] = None
) -> dict:
    """四柱推命の計算結果を返す"""
    data = _load_four_pillars_data()
    stems_data = data["heavenly_stems"]
    branches_data = data["earthly_branches"]

    year_stem, year_branch = _calc_year_pillar(year, )
    month_stem, month_branch = _calc_month_pillar(year, month)
    day_stem, day_branch = _calc_day_pillar(year, month, day)

    pillars = [
        (year_stem, year_branch),
        (month_stem, month_branch),
        (day_stem, day_branch),
    ]

    result = {
        "year_pillar": {
            "stem": year_stem,
            "branch": year_branch,
            "stem_detail": stems_data.get(year_stem, {}),
            "branch_detail": branches_data.get(year_branch, {}),
        },
        "month_pillar": {
            "stem": month_stem,
            "branch": month_branch,
            "stem_detail": stems_data.get(month_stem, {}),
            "branch_detail": branches_data.get(month_branch, {}),
        },
        "day_pillar": {
            "stem": day_stem,
            "branch": day_branch,
            "stem_detail": stems_data.get(day_stem, {}),
            "branch_detail": branches_data.get(day_branch, {}),
        },
    }

    if hour is not None:
        hour_stem, hour_branch = _calc_hour_pillar(day_stem, hour)
        pillars.append((hour_stem, hour_branch))
        result["hour_pillar"] = {
            "stem": hour_stem,
            "branch": hour_branch,
            "stem_detail": stems_data.get(hour_stem, {}),
            "branch_detail": branches_data.get(hour_branch, {}),
        }

    result["five_elements_balance"] = _calc_five_elements_balance(pillars, data)
    result["five_elements_interaction"] = data["five_elements_interaction"]

    return result
