"""
ParksyProfilePlug — 박씨 톤 강제 (가중치 고정 1.0, 모든 입력에 작동).

참조: ~/dtslib-papyrus/filters/parksy_voice_filter.md (227줄 마스터 필터)
"""
from __future__ import annotations

from pathlib import Path

from mcp.plugs.base import Plug


VOICE_FILTER_PATH = Path.home() / "dtslib-papyrus" / "filters" / "parksy_voice_filter.md"


class ParksyProfilePlug(Plug):
    name = "parksy_profile"
    gate_id = None                       # 백그라운드
    weight_default = 1.0
    keywords_trigger: list[str] = []     # 항상 작동

    _cached_tone_rules: str | None = None

    def score(self, ctx: dict) -> float:
        """항상 1.0 고정."""
        return 1.0

    def _load_tone_rules(self) -> str:
        if self._cached_tone_rules is None:
            if VOICE_FILTER_PATH.exists():
                self._cached_tone_rules = VOICE_FILTER_PATH.read_text(encoding="utf-8")
            else:
                self._cached_tone_rules = "(voice filter not found, fallback 기본 룰)"
        return self._cached_tone_rules

    def frame(self, ctx: dict) -> dict:
        return {
            "name": self.name,
            "gate": None,
            "lens": "박씨 톤 · 한국어 · 짧고 직설",
            "directive": (
                "출력 톤: 짧고 직설. 존댓말 금지. 단언형 종결. "
                "설명 전 즉시 핵심. 추임새 ~거든/~잖아 과용 금지."
            ),
            "tone_rules_src": str(VOICE_FILTER_PATH),
            "verdict_template": (
                "참고. 네 판단이 최종이다. 레시피 아님, 레퍼런스임."
            ),
            "forbidden": [
                "존댓말 어미",
                "'아시다시피' 류 서두",
                "과도한 공감 수사",
                "의료 진단/처방 언급",
            ],
        }
