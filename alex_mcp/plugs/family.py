"""
FamilySystemsPlug (Gate IV · Inside & Outside)

참조:
- Bowen Center for the Study of the Family
  https://www.thebowencenter.org/
- Minuchin's Structural Family Therapy

박씨 맥락: 의무부양자 → 분리 독립 → 주 1회 방문 돌봄 전환 (2년 전 3/13)
"""
from __future__ import annotations

from alex_mcp.plugs.base import Plug


class FamilySystemsPlug(Plug):
    name = "family_systems"
    gate_id = "IV"
    weight_default = 0.10
    keywords_trigger = [
        "부양", "책임", "동거", "의무", "부양자",
        "가족", "간병", "돌봄",
        "삼각관계", "누나", "누이", "형제", "자매",
        "부모", "아버지", "어머니", "부모님",
        "유족", "연금", "임대주택",
    ]

    def score(self, ctx: dict) -> float:
        base = super().score(ctx)
        metadata = ctx.get("metadata", {}) or {}
        if metadata.get("is_family_event"):
            base += 0.25
        return min(base, 0.55)

    def frame(self, ctx: dict) -> dict:
        return {
            "name": self.name,
            "gate": self.gate_id,
            "lens": "보웬 분화 · 삼각관계 · 다세대 전승",
            "questions": [
                "가족 내 역할(부양자/구원자/방관자)은 무엇인가?",
                "삼각관계가 어떻게 형성·해제되는가?",
                "세대 간 전승되는 패턴은?",
                "분화(differentiation) 수준은 어디까지 왔는가?",
            ],
            "cautions": [
                "'건강한 가족' 이상향 강요 금지",
                "개인을 병리화 말고 시스템으로 볼 것",
            ],
            "parksy_specific": {
                "의무부양자": "법적/정서적 고정 역할, 물리 분리 후에도 지속",
                "40년_간병": "다세대 전승 없는 1세대 완결 지옥 구조",
                "이식형_관계": "붙어있지도 완전 분리도 아닌 '방문 돌봄' 형태",
            },
        }
