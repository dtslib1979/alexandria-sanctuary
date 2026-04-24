"""
EnvTriggerPlug — 장소·날짜·애니버서리 효과.

박씨 2026-04-24 로그 핵심 요소:
- 옛 방에서 잔 수면 환경
- 3/13 = 창립기념일 + 어머니 요양원 입소일 중첩

참조: Anniversary Reaction (PMC articles on grief anniversary effects)
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Optional

from alex_mcp.plugs.base import Plug


# ─────────────────────────────────────────────────────────────────
#  박씨 특수 기념일 (수동 큐레이션, 박씨 확장 가능)
#  format: "MM-DD": [events]
# ─────────────────────────────────────────────────────────────────
PARKSY_ANNIVERSARIES: dict[str, list[str]] = {
    "03-13": ["창립기념일 (2024)", "어머니 요양원 입소 (2025)"],
}


LOCATION_TRIGGERS: list[tuple[str, float]] = [
    (r"옛\s*방", 0.30),
    (r"예전\s*집", 0.25),
    (r"살던\s*방", 0.20),
    (r"고향", 0.15),
    (r"어릴\s*적\s*(집|방)", 0.20),
]


TIME_TRIGGERS: list[tuple[str, float]] = [
    (r"기일", 0.25),
    (r"제사", 0.15),
    (r"창립\s*기념일", 0.25),
    (r"요양원\s*입소일", 0.30),
    (r"(봄|가을|겨울|여름)\s*(이\s*되면|마다)", 0.10),
    (r"명절", 0.10),
]


def _date_within_window(target: str, ref_date: str, window_days: int = 30) -> bool:
    """target = 'MM-DD', ref_date = 'YYYY-MM-DD'. window 이내면 True."""
    try:
        mm, dd = map(int, target.split("-"))
        ref = datetime.strptime(ref_date, "%Y-%m-%d").date()
        # 올해 + 내년 모두 체크 (연말/연초 겹침)
        for year in (ref.year, ref.year + 1, ref.year - 1):
            try:
                anniv = date(year, mm, dd)
            except ValueError:
                continue
            delta = abs((ref - anniv).days)
            if delta <= window_days:
                return True
        return False
    except (ValueError, TypeError):
        return False


class EnvTriggerPlug(Plug):
    name = "env_trigger"
    gate_id = None                       # 백그라운드
    weight_default = 0.12
    keywords_trigger = ["옛 방", "기일", "창립기념일", "요양원"]

    def score(self, ctx: dict) -> float:
        narrative = ctx.get("narrative", "") or ""
        metadata = ctx.get("metadata", {}) or {}

        boost = self.weight_default

        # 장소 트리거
        for pat, w in LOCATION_TRIGGERS:
            if re.search(pat, narrative):
                boost += w

        # 시간 트리거
        for pat, w in TIME_TRIGGERS:
            if re.search(pat, narrative):
                boost += w

        # 메타 입력 날짜가 박씨 기념일 윈도우
        ref_date = metadata.get("date")
        if ref_date:
            for anniv_key in PARKSY_ANNIVERSARIES:
                if _date_within_window(anniv_key, ref_date, window_days=30):
                    boost += 0.30
                    break

        return min(boost, 0.80)

    def frame(self, ctx: dict) -> dict:
        narrative = ctx.get("narrative", "") or ""
        metadata = ctx.get("metadata", {}) or {}

        detected_locations = [pat for pat, _ in LOCATION_TRIGGERS if re.search(pat, narrative)]

        detected_anniversaries: list[str] = []
        ref_date = metadata.get("date")
        if ref_date:
            for key, events in PARKSY_ANNIVERSARIES.items():
                if _date_within_window(key, ref_date):
                    detected_anniversaries.extend([f"{key}: {ev}" for ev in events])

        return {
            "name": self.name,
            "gate": None,
            "lens": "장소-기억 × 애니버서리 효과",
            "questions": [
                "이 공간이 과거에 어떤 역할을 했는가?",
                "이 시기에 반복되는 감정 패턴이 있는가?",
                "장소의 변화가 역할의 종료를 말하는가?",
            ],
            "cautions": [
                "'무의식이 안다' 식 미신 해석 금지",
                "날짜 우연을 과대해석 하지 말 것",
            ],
            "detected_locations": detected_locations,
            "detected_anniversaries": detected_anniversaries,
            "parksy_specific": {
                "3-13": "창립일 × 요양원 입소일 중첩 — 애니버서리 리포트 모드",
                "옛 방": "돌봄 노동 OS가 실행되던 샌드박스",
            },
        }
