"""
박씨 긍정 평가 패턴 — 박씨가 AI 답변에 "맞다/쓸만하다/가능하다" 인정한 신호.

소스: 박씨 실제 발화 17개 + Perplexity 응답 중 박씨가 인정한 부분
추출 근거:
- #13 박씨 MCP 원안 "플러그 + 확률 분포 + 파이선"
- #15 "레퍼런스로 하겠다"
- #20 "1000년 임상 실험 끝난 거"
- #29 "A급 정신상담사 = 무당 샤먼" (박씨 본인 도달 결론)
- #42 "천주교 미사 = 표준화된 샤먼 의례" (박씨 힌트)
"""
from __future__ import annotations

import re


# ─────────────────────────────────────────────────────────────────
#  박씨 긍정 키워드 (AI 답변 인정 시 박씨가 쓰는 말)
# ─────────────────────────────────────────────────────────────────
PARKSY_POSITIVE_MARKERS = [
    "맞다",
    "맞네",
    "맞어",
    "쓸만한",
    "쓸 만",
    "가능하다",
    "정확하다",
    "명확하다",
    "충분히",
    "힌트",
    "도움",
    "좋은 포인트",
    "괜찮다",
    "잘 잡",
    "정석",
    "현실적",
]


# ─────────────────────────────────────────────────────────────────
#  박씨가 인정하는 AI 답변 특징 (positive output patterns)
# ─────────────────────────────────────────────────────────────────
POSITIVE_OUTPUT_PATTERNS = [
    # 1. 자기 비판/한계 인정 (박씨 인정 1순위)
    (r"(내|우리)가\s*(틀렸|잘못|과장|오해)", "self_correction"),
    (r"(이건|저건)\s*(과장|오버|지나친)", "admit_overreach"),

    # 2. 박씨 맥락 구체적 인용
    (r"박씨\s*(2026|로그|발화|얘기)", "parksy_specific"),
    (r"네\s*(꿈|로그|상황|맥락|발화)\s*에서", "context_anchored"),

    # 3. 경제/시간 비교 (박씨 ROI 사고)
    (r"\$\d+[.\d]*\s*/\s*(월|회|년)", "cost_explicit"),
    (r"\d+\s*(분|시간)\s*(안에|이내)", "time_explicit"),
    (r"(vs|대비)\s*\S+", "comparison_explicit"),

    # 4. 구조화 + 숫자 (박씨 엔지니어 사고)
    (r"재활용률?\s*\d+\s*%", "recycle_rate"),
    (r"줄\s*수?\s*\d+", "loc_count"),
    (r"(Phase|Step)\s*\d", "phase_numbered"),

    # 5. 레퍼런스 명시 (레시피 아님)
    (r"레퍼런스", "reference_not_recipe"),
    (r"판단은\s*(네|박씨)\s*것", "final_judgment_user"),

    # 6. 실패/폐기 기록 (헌법 §2)
    (r"(폐기|실패|접|취소)\s*(결정|선언|이력)", "deprecate_recorded"),
    (r"삭제는\s*없", "no_delete_principle"),

    # 7. 실행 가능 상태
    (r"pytest\s*\d+\s*(passed|/)", "tests_passed"),
    (r"✅\s*동작", "working_confirmed"),
    (r"실증", "empirically_verified"),
]


# 점수 매핑
POSITIVE_WEIGHT = {
    "self_correction": 0.25,
    "admit_overreach": 0.20,
    "parksy_specific": 0.20,
    "context_anchored": 0.15,
    "cost_explicit": 0.15,
    "time_explicit": 0.10,
    "comparison_explicit": 0.10,
    "recycle_rate": 0.15,
    "loc_count": 0.10,
    "phase_numbered": 0.08,
    "reference_not_recipe": 0.20,
    "final_judgment_user": 0.20,
    "deprecate_recorded": 0.15,
    "no_delete_principle": 0.15,
    "tests_passed": 0.25,
    "working_confirmed": 0.20,
    "empirically_verified": 0.20,
}


def scan_positive(text: str) -> list[dict]:
    """긍정 평가 신호 감지."""
    signals = []
    for pat, code in POSITIVE_OUTPUT_PATTERNS:
        for m in re.finditer(pat, text):
            signals.append({
                "code": code,
                "matched": m.group(0),
                "position": m.start(),
                "weight": POSITIVE_WEIGHT.get(code, 0.10),
            })
    return signals


def positive_score(text: str) -> float:
    """
    박씨 긍정 평가 가능성 점수 0.0~1.0.
    0.5 이상 = 박씨 수용 가능성 높음.
    """
    signals = scan_positive(text)
    if not signals:
        return 0.0
    # 서로 다른 코드 종류 수 × 평균 가중치
    codes = {s["code"] for s in signals}
    avg_w = sum(s["weight"] for s in signals) / len(signals)
    score = min(len(codes) * 0.12 + avg_w, 1.0)
    return round(score, 3)
