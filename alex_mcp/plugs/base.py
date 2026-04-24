"""
Plug 추상 베이스 — 11 플러그 공통 인터페이스.

참조: WHITEPAPER-v1.0.md §4.1
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class Plug(ABC):
    """
    정신분석 / 샤먼 / 영성 학파의 해석 렌즈.

    각 Plug는 narrative에 대해:
    - score(): 이 학파가 얼마나 관련 있는가 (0.0~1.0)
    - frame(): 이 학파의 해석 프레임 (프롬프트 빌더 입력)
    """

    name: str = ""
    gate_id: Optional[str] = None        # "I"~"VII" or None (background)
    weight_default: float = 0.10
    keywords_trigger: list[str] = []

    def score(self, ctx: dict) -> float:
        """
        입력 컨텍스트에 대한 이 플러그의 적용 가중치.

        하위 클래스가 오버라이드 가능. 기본 구현은 키워드 hit 기반.
        """
        narrative = ctx.get("narrative", "") or ""
        hits = sum(1 for k in self.keywords_trigger if k in narrative)
        base = self.weight_default + hits * 0.08
        return min(base, 0.45)

    @abstractmethod
    def frame(self, ctx: dict) -> dict:
        """
        이 학파의 해석 프레임을 프롬프트 변수로 반환.

        반환 스키마:
        {
            "name": str,
            "gate": str | None,
            "lens": str,              # 한 줄 관점
            "questions": list[str],   # LLM에게 던질 질문 2~4개
            "cautions": list[str],    # 금지/완화 규칙
            "parksy_specific": dict,  # 박씨 맥락 전용 힌트 (optional)
        }
        """
        ...
