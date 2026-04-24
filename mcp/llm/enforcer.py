"""
Enforcer — LLM 출력을 mcp/rules/ 강제 규칙 파이프에 통과시킴.

박씨 구조:
  LLM (로데이터) → Enforcer (강제 규칙) → 박씨 톤 최종 리포트

이 모듈이 박씨 MCP 의 핵심 심장부.
rules/ + plugs/ + core/ + safety/ 전부 여기서 호출.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Optional

from mcp.core.plutchik import emotion_profile
from mcp.core.axes_weighter import axis_distribution, dominant_axis, axis_narrative
from mcp.plugs import ALL_PLUGS
from mcp.plug_orchestrator import compute_weights
from mcp.safety.crisis_detector import detect as crisis_detect

# rules/
from mcp.rules.parksy_tone import tone_score, rewrite_tone
from mcp.rules.parksy_forbidden import (
    scan as scan_forbidden, has_critical_forbidden,
)
from mcp.rules.parksy_negative import risk_score as negative_risk, should_regenerate
from mcp.rules.parksy_positive import positive_score
from mcp.rules.parksy_eval_rubric import evaluate


# ─────────────────────────────────────────────────────────────────
#  에스컬레이션 (crisis L2)
# ─────────────────────────────────────────────────────────────────
ESCALATION_MESSAGE = """지금은 분석보다 사람이 필요한 순간 같다.

24시간 전화 상담:
- 자살예방상담전화 1393 (무료, 24h)
- 정신건강위기상담 1577-0199 (무료, 24h)
- 청소년전화 1388

텍스트:
- 카카오톡 채널 "마들렌"
- web 1393 채팅 https://www.spckorea.or.kr

지금 바로 연결 못 해도 괜찮다. 숨만 쉬고 있어도 된다.
이 엔진은 지금은 닫힌다. 내일 다시 열린다."""


@dataclass
class EnforceResult:
    final_narrative: str
    citations: list = field(default_factory=list)
    dominant_themes: list = field(default_factory=list)
    structured: dict = field(default_factory=dict)
    safety_verdict: dict = field(default_factory=dict)
    rubric: dict = field(default_factory=dict)
    transformations: list = field(default_factory=list)  # 적용된 변환 로그
    parksy_tone_verdict: str = "참고. 네 판단이 최종이다. 레시피 아님, 레퍼런스임."

    def to_dict(self) -> dict:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────
#  메인 API
# ─────────────────────────────────────────────────────────────────

def enforce(
    llm_output: dict,
    narrative: str,
    metadata: Optional[dict] = None,
    forced_gate: Optional[str] = None,
) -> EnforceResult:
    """
    LLM 1차 해석 → 박씨 rules/ 강제 통과.

    Args:
        llm_output: {"interpretation": "...", "citations": [...], "dominant_themes": [...]}
        narrative: 원본 사용자 입력 (crisis 재검증용)
        metadata: is_dream / date / is_family_event / anniversary_within_30d 등
        forced_gate: UI에서 Gate 강제 선택 시 (옵션)
    """
    metadata = metadata or {}
    transformations: list[str] = []

    # ─────────────────────────────────────────────
    # STAGE 1: Crisis 이중 체크 (입력 + LLM 출력)
    # ─────────────────────────────────────────────
    v_input = crisis_detect(narrative, metadata)
    v_output = crisis_detect(llm_output.get("interpretation", ""), {})

    if v_input.level == 2 or v_output.level == 2:
        return EnforceResult(
            final_narrative=ESCALATION_MESSAGE,
            safety_verdict={
                "level": 2,
                "input_level": v_input.level,
                "output_level": v_output.level,
                "escalated": True,
            },
            transformations=["crisis_escalation"],
        )

    # ─────────────────────────────────────────────
    # STAGE 2: 치명 금기 (medical 등) 전면 차단
    # ─────────────────────────────────────────────
    interp = llm_output.get("interpretation", "")
    if has_critical_forbidden(interp):
        return EnforceResult(
            final_narrative=(
                "[엔진 차단] LLM 출력에 의료 진단/처방 표현 감지. "
                "의료 관련 판단은 이 엔진 범위 밖임. "
                "정신과 이슈는 전문의 상담."
            ),
            safety_verdict={"level": 0, "medical_blocked": True},
            transformations=["critical_forbidden_block"],
        )

    # ─────────────────────────────────────────────
    # STAGE 3: 박씨 부정 패턴 감지 → regenerate 플래그
    # ─────────────────────────────────────────────
    neg_regen, neg_reasons = should_regenerate(interp, threshold=0.7)
    if neg_regen:
        transformations.append(f"negative_risk_high:{','.join(neg_reasons)}")

    # ─────────────────────────────────────────────
    # STAGE 4: 금기 패턴 치환 (의료 제외 — 이미 차단)
    # ─────────────────────────────────────────────
    forbidden_hits = scan_forbidden(interp)
    sanitized = interp
    for hit in forbidden_hits:
        if hit.category == "medical":
            continue  # 이미 STAGE 2에서 차단됨
        # 존댓말/과공감 등은 rewrite_tone 에서 처리

    # ─────────────────────────────────────────────
    # STAGE 5: 박씨 톤 강제 치환
    # ─────────────────────────────────────────────
    toned, rewrite_count = rewrite_tone(sanitized)
    if rewrite_count > 0:
        transformations.append(f"tone_rewrite:{rewrite_count}")

    # ─────────────────────────────────────────────
    # STAGE 6: Plutchik + Axis + Plug 강제 매핑
    # ─────────────────────────────────────────────
    plutchik = emotion_profile(narrative, metadata)
    plug_weights = compute_weights(narrative, metadata, forced_gate)
    axes = axis_distribution(plug_weights, narrative, metadata)

    active_gates = sorted({
        p.gate_id for p in ALL_PLUGS
        if p.gate_id and plug_weights.get(p.name, 0) > 0.15
    })

    # ─────────────────────────────────────────────
    # STAGE 7: 박씨 루브릭 평가
    # ─────────────────────────────────────────────
    rubric_result = evaluate(toned)

    # ─────────────────────────────────────────────
    # STAGE 8: verdict_template 강제 삽입
    # ─────────────────────────────────────────────
    if "레시피 아님" not in toned:
        toned += "\n\n—\n참고. 네 판단이 최종이다. 레시피 아님, 레퍼런스임."
        transformations.append("verdict_injected")

    # ─────────────────────────────────────────────
    # STAGE 9: 긍정 신호 측정 (자가 검증용)
    # ─────────────────────────────────────────────
    pos_score = positive_score(toned)

    return EnforceResult(
        final_narrative=toned,
        citations=llm_output.get("citations", []),
        dominant_themes=llm_output.get("dominant_themes", []),
        structured={
            "plutchik": plutchik,
            "axis_profile": {k: round(v, 3) for k, v in axes.items()},
            "dominant_axis": dominant_axis(axes),
            "axis_narrative": axis_narrative(axes),
            "active_gates": active_gates,
            "plug_weights": {k: round(v, 3) for k, v in plug_weights.items()},
        },
        safety_verdict={
            "level": max(v_input.level, v_output.level),
            "input_level": v_input.level,
            "output_level": v_output.level,
        },
        rubric={
            "structure": rubric_result.structure,
            "practicality": rubric_result.practicality,
            "tone": rubric_result.tone,
            "overreach_penalty": rubric_result.overreach_penalty,
            "automation": rubric_result.automation,
            "final_score": rubric_result.final_score,
            "verdict": rubric_result.verdict,
            "positive_score": pos_score,
            "notes": rubric_result.notes,
        },
        transformations=transformations,
    )
