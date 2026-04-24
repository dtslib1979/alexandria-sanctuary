"""
박씨 AI 평가 루브릭 — 박씨가 멀티에이전트 답변 평가할 때 쓰는 기준.

소스: 박씨 5808줄 로그에서 추출
참조: 박씨가 Gemini/Grok/ChatGPT/Claude 각각 평가한 패턴
      발화 #1~#20에서 평가 축 도출.

핵심 루브릭 5축:
1. 구조 점수     — 축/레이어/플러그 분해 명확
2. 실용 점수     — 박씨 체감 실현 가능
3. 톤 점수       — 존댓말 없음, 단언형
4. 과장 감점     — 교과서/권위/완벽주의
5. 자동화 점수   — 세 번 이상 반복 가능 구조
"""
from __future__ import annotations

from dataclasses import dataclass, field

from mcp.rules.parksy_tone import tone_score
from mcp.rules.parksy_negative import risk_score as negative_risk
from mcp.rules.parksy_positive import positive_score
from mcp.rules.parksy_forbidden import scan as scan_forbidden, has_critical_forbidden


@dataclass
class EvalResult:
    structure: float        # 0~1
    practicality: float     # 0~1
    tone: float             # 0~1
    overreach_penalty: float # 0~1 (감점)
    automation: float       # 0~1
    final_score: float      # 0~10
    verdict: str            # "pass" | "regenerate" | "reject"
    notes: list[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────
#  AXIS 1: 구조 점수
#  박씨가 자주 인정: "축 3개로 갈린다", "레이어별로", "Phase"
# ─────────────────────────────────────────────────────────────────
STRUCTURE_MARKERS = [
    "축", "레이어", "Layer", "Phase", "Step",
    "분해", "매핑", "매트릭스",
    "플러그", "모듈",
    "→",  # 흐름 표시
]


def structure_score(text: str) -> float:
    hits = sum(1 for m in STRUCTURE_MARKERS if m in text)
    # 숫자 리스트 있는지 (1. 2. 3. or - )
    import re
    bullets = len(re.findall(r"^\s*[-•\d]+[.\)]\s", text, re.MULTILINE))
    score = min(hits * 0.10 + bullets * 0.05, 1.0)
    return round(score, 3)


# ─────────────────────────────────────────────────────────────────
#  AXIS 2: 실용 점수
#  박씨 체감: 실행 명령, 파일 경로, 숫자
# ─────────────────────────────────────────────────────────────────
PRACTICALITY_MARKERS = [
    "bash", "python", "pytest",
    ".py", ".md", ".json",
    "실행", "호출", "명령",
    "commit", "push",
    "mcp/", "docs/", "library/",
]


def practicality_score(text: str) -> float:
    import re
    hits = sum(1 for m in PRACTICALITY_MARKERS if m in text)
    # 숫자 기반 근거
    numeric = len(re.findall(r"\d+\s*(줄|%|분|초|건|회|개|번)", text))
    score = min(hits * 0.08 + numeric * 0.06, 1.0)
    return round(score, 3)


# ─────────────────────────────────────────────────────────────────
#  AXIS 3: 톤 점수 (parksy_tone.py 재활용)
# ─────────────────────────────────────────────────────────────────

def get_tone(text: str) -> float:
    return tone_score(text)["total"]


# ─────────────────────────────────────────────────────────────────
#  AXIS 4: 과장 감점 (parksy_negative + parksy_forbidden)
# ─────────────────────────────────────────────────────────────────

def overreach_penalty(text: str) -> float:
    neg = negative_risk(text)
    forbidden_hits = len(scan_forbidden(text))
    penalty = min(neg + forbidden_hits * 0.05, 1.0)
    return round(penalty, 3)


# ─────────────────────────────────────────────────────────────────
#  AXIS 5: 자동화 점수 (박씨 "세 번 이상 = 자동화")
# ─────────────────────────────────────────────────────────────────
AUTOMATION_MARKERS = [
    "자동화", "반복", "재사용",
    "cron", "배치",
    "재활용", "재실행",
    "3회", "세 번", "여러 번",
    "플러그", "강제", "규칙",
]


def automation_score(text: str) -> float:
    hits = sum(1 for m in AUTOMATION_MARKERS if m in text)
    return round(min(hits * 0.10, 1.0), 3)


# ─────────────────────────────────────────────────────────────────
#  종합 평가
# ─────────────────────────────────────────────────────────────────
WEIGHTS = {
    "structure": 0.20,
    "practicality": 0.25,
    "tone": 0.20,
    "overreach_penalty": 0.20,  # 감점
    "automation": 0.15,
}


def evaluate(text: str) -> EvalResult:
    """
    박씨 루브릭으로 LLM 답변 평가.
    """
    if not text:
        return EvalResult(
            structure=0, practicality=0, tone=0,
            overreach_penalty=0, automation=0,
            final_score=0.0, verdict="reject",
            notes=["empty text"],
        )

    s = structure_score(text)
    p = practicality_score(text)
    t = get_tone(text)
    o = overreach_penalty(text)
    a = automation_score(text)

    # 최종 점수 (0~10)
    raw = (
        s * WEIGHTS["structure"]
        + p * WEIGHTS["practicality"]
        + t * WEIGHTS["tone"]
        + a * WEIGHTS["automation"]
        - o * WEIGHTS["overreach_penalty"]
    )
    final = max(0.0, min(raw * 10, 10.0))

    notes = []
    if has_critical_forbidden(text):
        notes.append("CRITICAL: 의료 진단/처방 감지 — 전면 차단")
        verdict = "reject"
    elif o >= 0.7:
        notes.append(f"과장 위험 높음 (penalty={o}) — 재생성 권장")
        verdict = "regenerate"
    elif final >= 2.5:        # 박씨 실제 발화 톤/구조 기준
        verdict = "pass"
    elif final >= 1.5:
        verdict = "regenerate"
    else:
        verdict = "reject"

    return EvalResult(
        structure=s,
        practicality=p,
        tone=t,
        overreach_penalty=o,
        automation=a,
        final_score=round(final, 2),
        verdict=verdict,
        notes=notes,
    )
