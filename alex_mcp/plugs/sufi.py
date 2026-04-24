"""
SufiPlug (Gate III · The Touch of God — 수피 영성)

참조:
- Mad in America — Sufi Healing & Modern Psychiatry
  https://www.madinamerica.com/2019/11/sufi-healing-modern-psychiatry/
- Applications EMRO — Pakistan shaman vs psychiatry
"""
from __future__ import annotations

from alex_mcp.plugs.base import Plug


class SufiPlug(Plug):
    name = "sufi"
    gate_id = "III"
    weight_default = 0.06
    keywords_trigger = [
        "성지", "기도", "빛", "성자",
        "사랑", "비움", "통곡",
        "신성", "신의 손길", "깨달음",
    ]

    def frame(self, ctx: dict) -> dict:
        return {
            "name": self.name,
            "gate": self.gate_id,
            "lens": "비움 · 사랑 · 신성 접촉",
            "questions": [
                "자아를 비우는 경험의 상징이 있는가?",
                "'빛' 이미지가 변용을 의미하는가?",
                "관계에서의 초월적 사랑 기호가 있는가?",
            ],
            "cautions": [
                "종교 강요 금지",
                "이슬람 용어 (딸크/자크르) 직수입 지양 — 메타포로만",
                "박씨 맥락에서는 '의식적 비움'의 메타포만 유효",
            ],
            "parksy_specific": {
                "해방": "비움 = Liberation 축의 주요 강화 신호",
            },
        }
