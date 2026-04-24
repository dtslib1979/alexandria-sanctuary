"""
GuardrailPlug — 11번째 플러그, 가중치 고정 1.0.

역할: 모든 출력에 "레퍼런스 아님/의료 금지/강제형 금지" 지시를 강제 주입.
CrisisDetector/OutputSanitizer와 별개로 프롬프트 레벨 방어.

참조: WHITEPAPER-v1.0.md §8
"""
from __future__ import annotations

from alex_mcp.plugs.base import Plug


class GuardrailPlug(Plug):
    name = "guardrail"
    gate_id = None                       # 백그라운드
    weight_default = 1.0                 # 항상 고정
    keywords_trigger: list[str] = []

    def score(self, ctx: dict) -> float:
        return 1.0

    def frame(self, ctx: dict) -> dict:
        return {
            "name": self.name,
            "gate": None,
            "lens": "시스템 가드레일 — 프롬프트 레벨 방어",
            "directive": (
                "의료 진단 금지 / 약물 처방 금지 / 강제형 금지 / "
                "레퍼런스 선언 필수"
            ),
            "format_rule": "출력은 레퍼런스. 판단은 박씨 것.",
            "forbidden_phrasings": [
                "당신은 [질병명]입니다",
                "[약]을 복용하세요",
                "반드시 ~해야 한다",
                "절대 ~하지 마라",
            ],
            "required_closing": (
                "참고. 네 판단이 최종이다. 레시피 아님, 레퍼런스임."
            ),
        }
