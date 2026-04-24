"""
Plug Orchestrator — 가중치 계산 + 프롬프트 빌더 + 통합 분석.

WHITEPAPER-v1.0.md §3.1 실행 흐름 구현:
  input → crisis check → axes → plugs → weight → compose → (LLM) → sanitize

이 모듈은 LLM 호출 없이도 의미 있는 **pre-LLM 리포트**를 뽑을 수 있다.
MentaLLaMA/Qwen2.5 앙상블은 Phase 1 Day 7~9 이후 통합.
"""
from __future__ import annotations

from typing import Optional

from alex_mcp.plugs import ALL_PLUGS
from alex_mcp.core.axes_weighter import (
    axis_distribution, dominant_axis, axis_narrative,
)
from alex_mcp.core.plutchik import emotion_profile as plutchik_profile
from alex_mcp.safety.crisis_detector import detect as crisis_detect


# ─────────────────────────────────────────────────────────────────
#  플러그 가중치 계산
# ─────────────────────────────────────────────────────────────────
def compute_weights(
    narrative: str,
    metadata: Optional[dict] = None,
    forced_gate: Optional[str] = None,
) -> dict[str, float]:
    """
    WHITEPAPER-v1.0.md §4.1 공식.

    1. 각 플러그의 기본 score
    2. 메타 부스트 (is_dream, is_family_event, anniversary)
    3. forced_gate 부스트 (UI 클릭)
    4. parksy_profile / guardrail 고정 1.0
    """
    metadata = metadata or {}

    weights: dict[str, float] = {}
    for p in ALL_PLUGS:
        weights[p.name] = p.score({"narrative": narrative, "metadata": metadata})

    # 메타 부스트 (각 plug 자체의 score 로직에서 is_dream 처리, 여기선 전역 추가)
    if metadata.get("is_dream"):
        weights["freud"] = min(weights.get("freud", 0) + 0.15, 0.60)
        weights["jung"] = min(weights.get("jung", 0) + 0.15, 0.60)

    if metadata.get("is_family_event"):
        weights["family_systems"] = min(weights.get("family_systems", 0) + 0.25, 0.65)

    if metadata.get("anniversary_within_30d"):
        weights["env_trigger"] = min(weights.get("env_trigger", 0) + 0.30, 0.70)

    # UI gate 강제 (박씨가 특정 Gate 클릭)
    if forced_gate:
        for p in ALL_PLUGS:
            if p.gate_id == forced_gate:
                weights[p.name] = min(weights.get(p.name, 0) + 0.40, 0.80)

    # 백그라운드 고정
    weights["parksy_profile"] = 1.0
    weights["guardrail"] = 1.0

    return weights


# ─────────────────────────────────────────────────────────────────
#  통합 분석 — LLM 없이도 유용한 중간 산출물
# ─────────────────────────────────────────────────────────────────
def analyze_full(
    narrative: str,
    metadata: Optional[dict] = None,
    forced_gate: Optional[str] = None,
) -> dict:
    """
    LLM 호출 없이 다음을 반환:
    - safety_verdict (CrisisDetector)
    - plug_weights (활성 플러그)
    - axis_profile (5축 분포)
    - dominant_axis
    - active_gates (가중치 > 0.15인 Gate)
    - plug_frames (상위 플러그의 해석 프레임)
    - prompt_skeleton (Phase 1.9 LLM 호출용 사전 조립)

    이 결과만으로도 박씨가 "엔진이 내 입력을 어떻게 보는지" 확인 가능.
    """
    metadata = metadata or {}

    # 1. Crisis 체크
    verdict = crisis_detect(narrative, metadata)
    safety = verdict.to_dict()

    # L2 → 즉시 escalation (분석 생략)
    if verdict.should_block_output:
        from alex_mcp.safety.escalation import escalation_response
        return {
            "safety_verdict": safety,
            "escalation": escalation_response(),
            "analysis_skipped": True,
        }

    # 2. Layer 1 — Plutchik 8 기본 감정 프로파일
    plutchik = plutchik_profile(narrative, metadata)

    # 3. 플러그 가중치
    weights = compute_weights(narrative, metadata, forced_gate)

    # 4. Layer 2 — 도메인 축 분포 (Plutchik 기여 포함)
    axes = axis_distribution(weights, narrative, metadata)
    dom = dominant_axis(axes)
    narr = axis_narrative(axes)

    # 4. 활성 Gate (가중치 > 0.15)
    active_gates = sorted({
        p.gate_id for p in ALL_PLUGS
        if p.gate_id is not None and weights.get(p.name, 0) > 0.15
    })

    # 5. 활성 플러그 상위 5개 + 프레임
    top_plugs = sorted(
        [(p.name, weights[p.name]) for p in ALL_PLUGS if weights.get(p.name, 0) > 0.05],
        key=lambda x: -x[1],
    )[:5]

    plug_frames = {}
    for name, w in top_plugs:
        plug = next(p for p in ALL_PLUGS if p.name == name)
        plug_frames[name] = {
            "weight": round(w, 3),
            "frame": plug.frame({"narrative": narrative, "metadata": metadata}),
        }

    # 6. 프롬프트 스켈레톤 (Phase 1.9 LLM 호출시 사용)
    prompt_skeleton = _compose_prompt_skeleton(narrative, weights, axes, plug_frames)

    return {
        "safety_verdict": safety,
        "plutchik_layer": plutchik,          # 🆕 v1.3 — Layer 1
        "plug_weights": {k: round(v, 3) for k, v in weights.items()},
        "axis_profile": {k: round(v, 3) for k, v in axes.items()},
        "dominant_axis": dom,
        "axis_narrative": narr,
        "active_gates": active_gates,
        "top_plugs": [{"name": n, "weight": round(w, 3)} for n, w in top_plugs],
        "plug_frames": plug_frames,
        "prompt_skeleton": prompt_skeleton,
        "parksy_tone_verdict": "참고. 네 판단이 최종이다. 레시피 아님, 레퍼런스임.",
    }


def _compose_prompt_skeleton(
    narrative: str,
    weights: dict,
    axes: dict,
    plug_frames: dict,
) -> str:
    """Phase 1.9 LLM 호출시 이 스켈레톤을 Jinja로 렌더링."""
    sorted_plugs = sorted(plug_frames.items(), key=lambda x: -x[1]["weight"])
    sorted_axes = sorted(axes.items(), key=lambda x: -x[1])

    lines = [
        "# Alexandria MCP-Therapy · Session",
        "",
        "## 톤 규칙",
        "짧고 직설. 존댓말 금지. 단언형 종결. 레퍼런스 아님 선언 필수.",
        "",
        "## 활성 플러그 (top 5)",
    ]
    for name, data in sorted_plugs:
        lines.append(f"- **{name}** (Gate {data['frame'].get('gate') or '—'}, weight {data['weight']:.2f})")
        lens = data["frame"].get("lens", "")
        if lens:
            lines.append(f"  렌즈: {lens}")

    lines += [
        "",
        "## 축 프로파일 (5-axis ISA)",
    ]
    for aid, v in sorted_axes:
        lines.append(f"- {aid}: {v:.2f}")

    lines += [
        "",
        "## 사용자 입력",
        narrative,
        "",
        "## 출력 규칙",
        "1. one_line: 핵심을 한 문장으로",
        "2. layered_by_axis: grief/guilt/eros/rage/liberation 분석",
        "3. dissenting_views: 소수 의견 1~2개",
        "4. parksy_tone_verdict: 레퍼런스 선언 고정",
        "",
        "## 금지",
        "- 존댓말 · 의료/약물 언급 · '~해야 한다' 강제형",
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────
#  v1.4 — LLM Gateway + Enforcer 통합 파이프
# ─────────────────────────────────────────────────────────────────

def analyze_full_with_llm(
    narrative: str,
    llm_interpretation: Optional[dict] = None,
    metadata: Optional[dict] = None,
    forced_gate: Optional[str] = None,
) -> dict:
    """
    박씨 구조 v1.4 통합 함수.

    Args:
        narrative: 박씨 꿈/서사 입력
        llm_interpretation: 외부 LLM (Claude Code/Claude API) 1차 해석.
            없으면 ANTHROPIC_API_KEY 체크 후 직접 호출 시도.
            스키마: {"interpretation", "citations", "dominant_themes"}
        metadata: is_dream / date / is_family_event / anniversary_within_30d
        forced_gate: "I"~"VII" (옵션)

    Returns:
        EnforceResult.to_dict() — 최종 박씨 톤 리포트 + structured
    """
    from alex_mcp.llm.enforcer import enforce
    from alex_mcp.llm.llm_gateway import call_llm_direct, is_api_available

    if llm_interpretation is None:
        if is_api_available():
            llm_interpretation = call_llm_direct(narrative, metadata)
        else:
            # Claude Code 클라이언트 경로: LLM 해석을 받아야 분석 진행 가능
            return {
                "error": "LLM_INTERPRETATION_REQUIRED",
                "message": (
                    "ANTHROPIC_API_KEY 없음. Claude Code 대화에서 해석 먼저 생성한 뒤 "
                    "analyze_full_with_llm(narrative, llm_interpretation={...}) 호출"
                ),
                "system_prompt_hint": "mcp.llm.llm_gateway.build_system_prompt() 참고",
            }

    result = enforce(llm_interpretation, narrative, metadata, forced_gate)
    return result.to_dict()
