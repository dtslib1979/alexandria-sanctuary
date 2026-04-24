"""
박씨 부정 평가 패턴 — 박씨가 AI 출력에 "과장/단정/장사/병신" 판정한 신호.

소스: 박씨 실제 발화 17개에서 추출
추출 근거:
- #7 L3711 "이 사람도 샤먼 흉내에는 학자"
- #8 L3993 "답이라고 받을 게 이 융이라고 하는 사람 해석 같은 거"
- #8     "씨발 LLM 돌려막기로 물어봐도 알 수 있는 거"
- #14 L4757 "저 따위로 만들어도 정신 상담 안 받아도 되고"
- #17 L5259 "저 새끼들은 AI를 사용해서 쓸 수가 없을 거"
- #18 L5438 "표준화 못 한다 = 자기도 모른다 = 가짜"
"""
from __future__ import annotations

import re
from dataclasses import dataclass


# ─────────────────────────────────────────────────────────────────
#  박씨 부정 키워드 (AI 답변 품질 낮을 때 박씨가 쓰는 말)
# ─────────────────────────────────────────────────────────────────
PARKSY_NEGATIVE_MARKERS = [
    "과장",
    "단정",
    "샤먼 흉내",
    "장사해 먹",
    "저 따위",
    "병신 같은",
    "시간 낭비",
    "돈 낭비",
    "쓸데없이",
    "이론 맛",
    "교과서 요약",
    "앵무새",
    "학위 앵무새",
    "LLM 돌려막기",
    "B급",
    "저퀄",
    "답이라고",
    "가짜",
    "지 맘대로",
]


# ─────────────────────────────────────────────────────────────────
#  AI 출력이 박씨 부정 평가를 받을 위험 신호
#  (LLM이 이런 패턴으로 답하면 박씨가 깜) — 사전 차단용
# ─────────────────────────────────────────────────────────────────
NEGATIVE_OUTPUT_PATTERNS = [
    # 1. 교과서 인용만 반복
    (r"(Freud|프로이트|융|Jung|Lacan|라캉)(는|은|이|가)\s*\S+라고\s*(말|주장|설명)",
     "authority_quote_only"),

    # 2. 일반론 (박씨 맥락 없는 위로)
    (r"많은\s*사람들이\s*그렇게", "generic_consolation"),
    (r"인간이라면\s*누구나", "universal_cliche"),

    # 3. 해결책 강요
    (r"\S+해보시는\s*것이\s*좋을", "solution_push"),
    (r"다음과\s*같은\s*방법을?\s*시도", "prescription_form"),

    # 4. 과장 ("완전히", "무조건", "반드시")
    (r"완전히\s*\S+", "absolute_claim"),
    (r"무조건\s*\S+", "absolute_claim"),

    # 5. 판단 보류 남발 (박씨 "단정이다" 반대)
    (r"\S+일\s*수도\s*\S+일\s*수도", "excessive_hedge"),
    (r"경우에\s*따라\s*다르", "wishy_washy"),

    # 6. 동어반복
    (r"(\S+)는\s*\1이다\b", "tautology"),

    # 7. 감정 강요
    (r"더\s*행복해질\s*수\s*있", "forced_positivity"),
    (r"감사하는\s*마음으로", "gratitude_push"),
]


@dataclass
class NegativeSignal:
    pattern: str
    code: str
    matched_text: str
    position: int
    severity: float  # 0.0~1.0 (높을수록 박씨 부정 평가 위험)


# 심각도 매핑
SEVERITY_MAP = {
    "authority_quote_only": 0.85,
    "generic_consolation": 0.70,
    "universal_cliche": 0.65,
    "solution_push": 0.80,
    "prescription_form": 0.85,
    "absolute_claim": 0.75,
    "excessive_hedge": 0.60,
    "wishy_washy": 0.65,
    "tautology": 0.50,
    "forced_positivity": 0.70,
    "gratitude_push": 0.70,
}


def scan(text: str) -> list[NegativeSignal]:
    """LLM 출력에서 박씨 부정 평가 위험 신호 감지."""
    signals: list[NegativeSignal] = []
    for pat, code in NEGATIVE_OUTPUT_PATTERNS:
        for m in re.finditer(pat, text):
            signals.append(NegativeSignal(
                pattern=pat,
                code=code,
                matched_text=m.group(0),
                position=m.start(),
                severity=SEVERITY_MAP.get(code, 0.50),
            ))
    return signals


def risk_score(text: str) -> float:
    """전체 부정 위험 점수 0.0~1.0. 0.7 이상 = 재생성 권장."""
    signals = scan(text)
    if not signals:
        return 0.0
    max_severity = max(s.severity for s in signals)
    count_penalty = min(len(signals) * 0.05, 0.3)
    return min(max_severity + count_penalty, 1.0)


def should_regenerate(text: str, threshold: float = 0.7) -> tuple[bool, list[str]]:
    """재생성 필요 여부 + 이유."""
    signals = scan(text)
    score = risk_score(text)
    reasons = sorted({s.code for s in signals})
    return score >= threshold, reasons
