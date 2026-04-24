"""
NarrativeMetaPlug (Gate VI · The Forbidden Gate — 꿈 속 추론)

박씨 2026-04-24 로그 대표 케이스:
"업소여성을 만나고 부랴부랴 뛰어오다 까먹고 전화한 사람일 거라고 꿈속에서 추론했다"
→ 주체가 꿈 안에서 자기 해석을 시도하는 2차 메타텍스트.

참조:
- Lacan's Four Discourses
  https://nosubject.com/Four_Discourses
- Eco — A Theory of Semiotics
"""
from __future__ import annotations

import re

from alex_mcp.plugs.base import Plug


META_REFLECTION_PATTERNS: list[tuple[str, float]] = [
    (r"추론\s*했", 0.18),
    (r"돌이켜\s*보니", 0.15),
    (r"알고\s*보니", 0.12),
    (r"생각해\s*보면", 0.10),
    (r"꿈\s*속에서\s*도", 0.15),
    (r"나중에\s*보니", 0.10),
    (r"아마\s*[가-힣]+(일|ㄹ)\s*거", 0.10),
]


class NarrativeMetaPlug(Plug):
    name = "narrative_meta"
    gate_id = "VI"
    weight_default = 0.08
    keywords_trigger = [
        "추론", "돌이켜보니", "알고보니",
        "생각해보면", "아마", "추측", "꿈속에서도",
    ]

    def score(self, ctx: dict) -> float:
        base = super().score(ctx)
        narrative = ctx.get("narrative", "") or ""

        # 꿈+메타 추론 조합 강화 (박씨 2026-04-24 시그니처)
        is_dream = (ctx.get("metadata", {}) or {}).get("is_dream", False)
        for pat, w in META_REFLECTION_PATTERNS:
            if re.search(pat, narrative):
                base += w
                if is_dream:
                    base += 0.05   # 꿈 속 추론은 더 가중

        return min(base, 0.60)

    def frame(self, ctx: dict) -> dict:
        narrative = ctx.get("narrative", "") or ""
        detected = [
            pat for pat, _ in META_REFLECTION_PATTERNS
            if re.search(pat, narrative)
        ]

        return {
            "name": self.name,
            "gate": self.gate_id,
            "lens": "2차 메타텍스트 · 주체가 꿈 안에서 자기 해석",
            "questions": [
                "꿈 속에서 이미 자기 해석을 시도했는가?",
                "그 추론이 현실에 대한 무의식의 주석인가?",
                "Lacan: 주체가 타자의 욕망을 되물음 구조인가?",
            ],
            "cautions": [
                "'이미 다 알고 있었다' 식 결론 금지",
                "메타 반영이 있다고 회복 완료로 오판 말 것",
            ],
            "detected_meta_patterns": detected,
            "parksy_specific": {
                "이미_디버깅_중": "박씨가 스스로 해석하는 모드 — 도움보다 확인이 필요",
                "insight_level": "높음 — 해석 공급 말고 축 확인만",
            },
        }
