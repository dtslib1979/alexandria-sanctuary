"""
Alexandria MCP-Therapy · Crisis Detector
=========================================

위기 감지 2-level 분류기.

참조:
- Verily Mental Health Guardrail (npj Digital Medicine 2026)
  https://www.nature.com/articles/s41746-026-02579-5
- "Between Help and Harm: LLM Crisis Handling" (arxiv 2509.24857)
  https://arxiv.org/html/2509.24857v1
- Korea 자살예방상담전화 1393 / 정신건강위기상담 1577-0199

설계 원칙:
1. 꿈 맥락 예외 처리 (false positive 최소화)
2. 한국어 구어체 패턴 포함 ("죽고 싶어", "사라지고 싶다" 등)
3. 부정문 제외 ("죽고 싶진 않다")
4. Decision은 deterministic — LLM 호출 없음

라이선스: Apache 2.0 (parksy)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────
#  Level 2 패턴 (차단 + 에스컬레이션)
#  근거: Verily guardrail + Korea 109 핫라인 카테고리
# ─────────────────────────────────────────────────────────────────
CRISIS_L2_PATTERNS: list[tuple[str, str]] = [
    (r"죽고\s*싶", "ideation_direct"),
    (r"자살\s*(하|할|하고)", "suicide_verb"),
    (r"자해", "self_harm"),
    (r"목숨\s*을?\s*끊", "life_terminate"),
    (r"끝내(고|버리(고|려))\s*싶", "end_it"),      # 끝내고 싶 / 끝내버리고 싶 / 끝내버려
    (r"사라지(고|려)\s*싶", "disappear"),
    (r"뛰어내리(고|려|ㄹ까)", "jump"),
    (r"뛰어내릴까", "jump_contemplate"),
    (r"약을?\s*(먹고|한꺼번에).*(죽|자|끝)", "overdose_intent"),
    (r"(칼로|칼을)\s*(자|나|베)", "cutting"),
    (r"옥상(에서|에\s*올라|에\s*가서|올라가)", "rooftop"),  # 에/에서/에 올라 모두 커버
    (r"한강\s*(다리|에서\s*뛰)", "bridge_hangang"),
    (r"목을?\s*매", "hanging"),
]

# ─────────────────────────────────────────────────────────────────
#  3인칭 / 픽션 맥락 마커 (같은 문장에 있으면 L2 오탐 억제)
# ─────────────────────────────────────────────────────────────────
THIRD_PARTY_MARKERS: list[str] = [
    r"뉴스(에서|에|를)",
    r"영화(에서|에|를|\s+주인공)",
    r"드라마(에서|에|를|\s+주인공)",
    r"소설(에서|에|\s+주인공)",
    r"책(에서|에)",
    r"기사(에서|에|를)",
    r"주인공(이|은|을)",
    r"누군가",
    r"(친구|선배|삼촌|이모)\s*(가|는|이)",   # 타인 주어
]

# ─────────────────────────────────────────────────────────────────
#  Level 1 패턴 (주의 · 가중치 완화 + 공감 강제)
# ─────────────────────────────────────────────────────────────────
CRISIS_L1_PATTERNS: list[tuple[str, str]] = [
    (r"너무\s*힘들", "overwhelm"),
    (r"지친다", "exhausted"),
    (r"(살\s*의미|삶의\s*의미)\s*(없|모르)", "meaningless"),
    (r"혼자(\s*있|\s*인|야|다)", "isolation"),
    (r"공허", "emptiness"),
    (r"아무도\s*모르", "nobody_knows"),
    (r"포기(하고\s*싶|하자)", "give_up"),
    (r"못\s*견디", "cannot_endure"),
    (r"다\s*끝났", "all_over"),
    (r"막막", "stuck"),
]

# ─────────────────────────────────────────────────────────────────
#  꿈 맥락 예외 (False Positive 방지)
#  박씨 2026-04-24 로그: "어머니가 돌아가시는 꿈" — L2 아님
# ─────────────────────────────────────────────────────────────────
DREAM_EXCEPTION_PATTERNS: list[str] = [
    r"죽는\s*꿈",
    r"돌아가시는\s*꿈",
    r"장례\s*꿈",
    r"죽으시는\s*꿈",
    r"자살\s*(하는\s*)?꿈",
]

# ─────────────────────────────────────────────────────────────────
#  부정문 예외 (False Positive 방지)
#  "죽고 싶진 않다", "자살할 리 없다"
# ─────────────────────────────────────────────────────────────────
NEGATION_WINDOW = 20  # 패턴 매치 후 N자 이내 부정어 검색 (한국어 여유)

NEGATION_MARKERS: list[str] = [
    r"지\s*않",          # "하지 않", "있지 않"
    r"진\s*않",          # "싶진 않다" (축약형)
    r"지는\s*않",        # "하지는 않"
    r"\s*리\s*없",       # "할 리 없다", "자살할 리 없다"
    r"싶지\s*않",        # "죽고 싶지 않"
    r"할\s*생각\s*없",
    r"그럴\s*리",
    r"절대\s*아니",
    r"는\s*거\s*아니",   # "자살하는 거 아니"
]


@dataclass
class CrisisVerdict:
    """
    위기 감지 결과. deterministic.
    """
    level: int                              # 0=정상, 1=주의, 2=차단
    patterns_matched: list[tuple[str, str]] = field(default_factory=list)  # (pattern, category)
    dream_exception_applied: bool = False
    negation_applied: bool = False
    input_length: int = 0

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "categories": [c for _, c in self.patterns_matched],
            "dream_exception_applied": self.dream_exception_applied,
            "negation_applied": self.negation_applied,
            "input_length": self.input_length,
        }

    @property
    def should_block_output(self) -> bool:
        """level 2는 엔진 출력 차단, escalation 메시지 대체."""
        return self.level == 2

    @property
    def should_soften_output(self) -> bool:
        """level 1은 출력에 공감 강제 + 레퍼런스 톤 유지."""
        return self.level == 1


# ─────────────────────────────────────────────────────────────────
#  메인 API
# ─────────────────────────────────────────────────────────────────
def detect(narrative: str, metadata: Optional[dict] = None) -> CrisisVerdict:
    """
    입력 narrative 에 대해 위기 레벨 판정.

    Parameters
    ----------
    narrative : str
        사용자 입력 텍스트
    metadata : dict, optional
        {"is_dream": bool, "date": "YYYY-MM-DD", ...}

    Returns
    -------
    CrisisVerdict
    """
    metadata = metadata or {}
    is_dream = metadata.get("is_dream", False)

    # 꿈 예외 검사 (L2 매칭 전 확인)
    dream_exception = False
    if is_dream:
        for pat in DREAM_EXCEPTION_PATTERNS:
            if re.search(pat, narrative):
                dream_exception = True
                break

    # 3인칭/픽션 맥락 사전 검사
    third_party_context = any(re.search(p, narrative) for p in THIRD_PARTY_MARKERS)

    # L2 검사
    l2_hits: list[tuple[str, str]] = []
    for pat, cat in CRISIS_L2_PATTERNS:
        match = re.search(pat, narrative)
        if match:
            # 부정문 체크: 매치 직후 NEGATION_WINDOW 자 이내
            end = match.end()
            window = narrative[end : end + NEGATION_WINDOW]
            negated = any(re.search(neg, window) for neg in NEGATION_MARKERS)
            if not negated:
                l2_hits.append((pat, cat))

    # 3인칭 서술이면 L2 → L0 강등 (뉴스/영화/타인 주어)
    if l2_hits and third_party_context:
        l2_hits = []

    if l2_hits and not dream_exception:
        return CrisisVerdict(
            level=2,
            patterns_matched=l2_hits,
            dream_exception_applied=False,
            negation_applied=False,
            input_length=len(narrative),
        )

    # L1 검사
    l1_hits: list[tuple[str, str]] = []
    for pat, cat in CRISIS_L1_PATTERNS:
        if re.search(pat, narrative):
            l1_hits.append((pat, cat))

    if l1_hits:
        return CrisisVerdict(
            level=1,
            patterns_matched=l1_hits,
            dream_exception_applied=dream_exception,
            negation_applied=False,
            input_length=len(narrative),
        )

    # 정상
    return CrisisVerdict(
        level=0,
        patterns_matched=[],
        dream_exception_applied=dream_exception,
        negation_applied=False,
        input_length=len(narrative),
    )


# ─────────────────────────────────────────────────────────────────
#  Self-test (python -m mcp.safety.crisis_detector)
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cases = [
        ("죽고 싶다", {}, 2, "L2 직접 ideation"),
        ("너무 힘들어 지친다", {}, 1, "L1 overwhelm"),
        ("어머니가 돌아가시는 꿈을 꿨다", {"is_dream": True}, 0, "꿈 예외"),
        ("오늘 날씨가 좋다", {}, 0, "정상"),
        ("죽고 싶진 않다", {}, 0, "부정문 예외"),
        ("자살할 리 없다고 생각했다", {}, 0, "부정문"),
        ("한강 다리에서 뛰어내리는 상상", {}, 2, "L2 복합"),
        ("공허하고 아무도 모른다", {}, 1, "L1 다중"),
    ]

    print("─" * 60)
    print("Alexandria MCP-Therapy · CrisisDetector Self-Test")
    print("─" * 60)
    all_pass = True
    for i, (text, meta, expected, label) in enumerate(cases, 1):
        v = detect(text, meta)
        ok = v.level == expected
        all_pass = all_pass and ok
        mark = "✅" if ok else "❌"
        print(f"{mark} [{i}] {label}")
        print(f"    input: {text!r}")
        print(f"    expected level={expected} / got level={v.level} / categories={[c for _, c in v.patterns_matched]}")
    print("─" * 60)
    print("RESULT:", "ALL PASS" if all_pass else "FAILURE")
