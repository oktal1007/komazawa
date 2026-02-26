"""西洋占星術計算サービス - Swiss Ephemeris使用"""

from datetime import datetime
from typing import Optional

try:
    import swisseph as swe

    SWE_AVAILABLE = True
except ImportError:
    SWE_AVAILABLE = False

# 星座名（日本語）
ZODIAC_SIGNS = [
    "牡羊座", "牡牛座", "双子座", "蟹座",
    "獅子座", "乙女座", "天秤座", "蠍座",
    "射手座", "山羊座", "水瓶座", "魚座",
]

# 星座の特性（バステト神世界観）
ZODIAC_TRAITS = {
    "牡羊座": "火の戦士の星。バステト女神の炎の祝福により、情熱と勇気で道を切り拓きます。",
    "牡牛座": "地の守護の星。大地母神の恵みにより、豊かさと安定を引き寄せます。",
    "双子座": "風の知恵の星。トト神の叡智により、多彩な才能と柔軟な思考が宿ります。",
    "蟹座": "月の慈愛の星。イシス女神の月光により、深い愛情と保護の力が宿ります。",
    "獅子座": "太陽の王者の星。ラー神の輝きにより、カリスマ性と創造力が宿ります。",
    "乙女座": "地の奉仕の星。マアト女神の秩序により、分析力と献身の精神が宿ります。",
    "天秤座": "風の調和の星。ハトホル女神の美により、バランスと美的感覚が宿ります。",
    "蠍座": "水の変容の星。アヌビス神の神秘により、深い洞察力と再生の力が宿ります。",
    "射手座": "火の探求の星。ホルス神の翼により、高い理想と冒険心が宿ります。",
    "山羊座": "地の達成の星。プタハ神の創造により、野心と忍耐力が宿ります。",
    "水瓶座": "風の革新の星。シュー神の自由により、独創性と博愛の精神が宿ります。",
    "魚座": "水の霊感の星。ヌト女神の星空により、豊かな直感と共感力が宿ります。",
}


def _ecliptic_to_sign(longitude: float) -> str:
    """黄経から星座名を返す"""
    index = int(longitude / 30) % 12
    return ZODIAC_SIGNS[index]


def _datetime_to_jd(year: int, month: int, day: int, hour: float = 12.0) -> float:
    """日時をユリウス日に変換"""
    if SWE_AVAILABLE:
        return swe.julday(year, month, day, hour)
    # フォールバック: 簡易計算
    from datetime import datetime, timedelta

    epoch = datetime(2000, 1, 1, 12, 0, 0)
    target = datetime(year, month, day, int(hour), int((hour % 1) * 60))
    diff = (target - epoch).total_seconds() / 86400.0
    return 2451545.0 + diff


def _simple_sun_sign(month: int, day: int) -> str:
    """Swiss Ephemeris不使用時の簡易太陽星座計算"""
    dates = [
        (1, 20, "水瓶座"), (2, 19, "魚座"), (3, 21, "牡羊座"),
        (4, 20, "牡牛座"), (5, 21, "双子座"), (6, 21, "蟹座"),
        (7, 23, "獅子座"), (8, 23, "乙女座"), (9, 23, "天秤座"),
        (10, 23, "蠍座"), (11, 22, "射手座"), (12, 22, "山羊座"),
    ]
    sign = "山羊座"
    for m, d, s in dates:
        if (month == m and day >= d) or (month == m + 1 and day < dates[dates.index((m, d, s)) + 1][1] if m < 12 else month == 1 and day < 20):
            sign = s
            break
    # シンプル版
    boundaries = [
        (1, 20), (2, 19), (3, 21), (4, 20), (5, 21), (6, 21),
        (7, 23), (8, 23), (9, 23), (10, 23), (11, 22), (12, 22),
    ]
    signs_ordered = [
        "山羊座", "水瓶座", "魚座", "牡羊座", "牡牛座", "双子座",
        "蟹座", "獅子座", "乙女座", "天秤座", "蠍座", "射手座",
    ]
    for i, (m, d) in enumerate(boundaries):
        if month == m and day < d:
            return signs_ordered[i]
        if month == m and day >= d:
            return signs_ordered[(i + 1) % 12]
    return "山羊座"


def calculate_astrology(
    year: int, month: int, day: int, hour: Optional[float] = None
) -> dict:
    """西洋占星術の計算結果を返す"""
    birth_hour = hour if hour is not None else 12.0

    if SWE_AVAILABLE:
        jd = _datetime_to_jd(year, month, day, birth_hour)

        # 太陽の位置
        sun_pos = swe.calc_ut(jd, swe.SUN)[0]
        sun_sign = _ecliptic_to_sign(sun_pos[0])

        # 月の位置
        moon_pos = swe.calc_ut(jd, swe.MOON)[0]
        moon_sign = _ecliptic_to_sign(moon_pos[0])

        # ASC（上昇星座）- 出生時刻がある場合のみ正確
        if hour is not None:
            # 簡易的なASC計算（東京緯度35.68 経度139.77を仮定）
            houses = swe.houses(jd, 35.68, 139.77, b"P")
            asc_sign = _ecliptic_to_sign(houses[1][0])
        else:
            asc_sign = None
    else:
        sun_sign = _simple_sun_sign(month, day)
        moon_sign = None
        asc_sign = None

    result = {
        "sun_sign": {
            "sign": sun_sign,
            "trait": ZODIAC_TRAITS.get(sun_sign, ""),
        },
    }

    if moon_sign:
        result["moon_sign"] = {
            "sign": moon_sign,
            "trait": ZODIAC_TRAITS.get(moon_sign, ""),
        }

    if asc_sign:
        result["ascendant"] = {
            "sign": asc_sign,
            "trait": ZODIAC_TRAITS.get(asc_sign, ""),
        }

    return result
