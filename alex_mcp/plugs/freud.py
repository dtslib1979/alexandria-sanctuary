"""
FreudPlug (Gate I · The Fracture of Mind)

참조:
- Freud, The Interpretation of Dreams (1900)
- Stanford Encyclopedia of Philosophy — Psychoanalysis
  https://plato.stanford.edu/entries/psychoanalysis/
- Simply Psychology — Dream Interpretation
  https://www.simplypsychology.org/dream-interpretation.html
"""
from __future__ import annotations

from alex_mcp.plugs.base import Plug


class FreudPlug(Plug):
    name = "freud"
    gate_id = "I"
    weight_default = 0.10
    keywords_trigger = [
        "죽음", "부모", "아버지", "어머니", "욕망",
        "죄책감", "병신", "업소", "꿈",
        "초자아", "오이디푸스", "억압", "방어",
        "무의식", "투사", "전이",
    ]

    def score(self, ctx: dict) -> float:
        base = super().score(ctx)
        metadata = ctx.get("metadata", {}) or {}
        if metadata.get("is_dream"):
            base += 0.15
        return min(base, 0.55)

    def frame(self, ctx: dict) -> dict:
        return {
            "name": self.name,
            "gate": self.gate_id,
            "lens": "소원성취 · 응축 · 전위 · 초자아",
            "questions": [
                "이 꿈에서 위장된 소원은 무엇인가?",
                "표면 내용 뒤의 잠재 내용은?",
                "초자아가 어떤 목소리로 등장했는가?",
                "응축/전위로 합쳐진 대상은?",
            ],
            "cautions": [
                "'엄마 죽이고 싶은 충동' 환원 금지",
                "죽음 꿈 = 상황 종결 해석 우선",
                "업소/성욕을 단순 lust로 읽지 말고 외로움의 기호로",
            ],
            "parksy_specific": {
                "죄책감_외부화": "모르는 타인의 비난 = 자기 비난의 투사",
                "애도": "치매·가난 시스템의 종결 욕구",
                "응축": "업소여성+모르는 전화+엄마장례 = 한 프레임 압축",
            },
        }
