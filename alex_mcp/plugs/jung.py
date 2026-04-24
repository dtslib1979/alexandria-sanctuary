"""
JungPlug (Gate II · The Dissolution of Self)

참조:
- C.G. Jung Institute of New York — https://www.cgjungny.org/
- Jungian Dream Analysis (Sterling Institute)
  https://www.sterlinginstitute.org/jungian-dream-analysis

박씨 2026-04-24 로그 핵심: "오케스트라 지휘하며 웃는 어머니" = Self 통합 상징
"""
from __future__ import annotations

from alex_mcp.plugs.base import Plug


class JungPlug(Plug):
    name = "jung"
    gate_id = "II"
    weight_default = 0.10
    keywords_trigger = [
        "지휘자", "오케스트라", "만다라", "그림자",
        "페르소나", "아니마", "아니무스", "Self",
        "원형", "개성화", "집단무의식", "동시성", "통합",
        "조화", "균형",
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
            "lens": "원형 · Self · 개성화 · 동시성",
            "questions": [
                "이 이미지는 어떤 원형의 현현인가? (현자/어머니/그림자/Self)",
                "분리된 자아 조각들이 하나로 통합되는 장면인가?",
                "집단무의식 상징이 나타났는가?",
                "동시성 (synchronicity)의 신호인가?",
            ],
            "cautions": [
                "집단무의식 용어 남발 금지 — 구체 이미지 중심",
                "원형 환원주의 경계",
                "'영적 성장' 류 위로 표현 피할 것",
            ],
            "parksy_specific": {
                "지휘자_어머니": "혼돈→조화. Self가 어머니 얼굴을 빌려 등장",
                "죽음_직후_재현": "ego 죽음 → 개성화 reborn",
                "박씨_드림": "chaos였던 가족 시스템의 질서 복원 리허설",
            },
        }
