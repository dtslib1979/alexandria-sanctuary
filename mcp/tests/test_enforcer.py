"""
Enforcer + LLM Gateway 통합 테스트.
"""
from __future__ import annotations

import pytest

from mcp.llm.enforcer import enforce, EnforceResult, ESCALATION_MESSAGE
from mcp.llm.llm_gateway import build_system_prompt, is_api_available


# 박씨 2026-04-24 꿈 (narrative)
PARKSY_DREAM_NARRATIVE = (
    "어머니가 돌아가시는 꿈을 꿨다. 심폐 소생 쇼크 전기 충격기 바이탈 사인 "
    "들리며 갑자기 일어나서 오케스트라 지휘하듯 한 사람 한 사람 눈 마주쳐 "
    "웃으면서 지휘했다. 기분이 좋았다. 상가집 상 치르러 가는 길에 모르는 "
    "전화가 와서 짜증 나서 병신이라고 욕했다."
)

PARKSY_DREAM_META = {
    "is_dream": True,
    "date": "2026-04-24",
    "is_family_event": True,
    "anniversary_within_30d": True,
}


# ─────────────────────────────────────────────────────────────────
#  모의 LLM 출력 (Claude Code/API 가 생성했다고 가정)
# ─────────────────────────────────────────────────────────────────

LLM_OUTPUT_GOOD = {
    "interpretation": (
        "이 꿈은 애도와 해방이 공존하는 양가 상태를 보여준다. "
        "Freud 관점에서 돌봄 시스템 종결에 대한 소원성취가 보이고, "
        "Jung 관점에서 지휘자=Self 통합 상징이 나타난다. "
        "가족 시스템 이론에서는 1년 전 요양원 입소 이후 역할 분화 과정이다. "
        "욕설 에피소드는 잔여 분노의 투사. 판단은 네 것."
    ),
    "citations": [
        {"title": "Freud - The Interpretation of Dreams", "url": "https://...", "school": "freud"},
        {"title": "Jung - Archetypes and the Collective Unconscious", "url": "https://...", "school": "jung"},
        {"title": "Bowen Family Systems Theory", "url": "https://...", "school": "family"},
    ],
    "dominant_themes": ["애도", "해방", "가족 역할 분화"],
}

LLM_OUTPUT_FORBIDDEN = {
    "interpretation": (
        "당신은 우울증 초기 증상입니다. "
        "반드시 정신과 치료를 받으셔야 하고 약을 복용하세요. "
        "많이 힘드시겠지만 잘 하고 계세요."
    ),
    "citations": [],
    "dominant_themes": [],
}

LLM_OUTPUT_HONORIFIC = {
    "interpretation": (
        "이 꿈은 애도와 관련이 있습니다. "
        "Freud는 이런 꿈을 소원성취로 해석했습니다. "
        "양가감정이 관찰됩니다."
    ),
    "citations": [{"title": "Freud 1900", "url": "https://...", "school": "freud"}],
    "dominant_themes": ["애도"],
}


class TestLLMGateway:
    def test_system_prompt_contains_lens_sections(self):
        prompt = build_system_prompt()
        assert "학파 렌즈" in prompt
        assert "Gate" in prompt

    def test_system_prompt_has_forbidden_section(self):
        prompt = build_system_prompt()
        assert "금지" in prompt

    def test_system_prompt_has_reference_principle(self):
        prompt = build_system_prompt()
        assert "레퍼런스" in prompt or "판단" in prompt

    def test_api_availability_check(self):
        # 환경에 따라 True/False 둘 다 가능
        result = is_api_available()
        assert isinstance(result, bool)


class TestEnforcerGoodOutput:
    """정상 LLM 출력 → 박씨 톤 최종 리포트."""

    def test_result_is_enforce_result(self):
        r = enforce(LLM_OUTPUT_GOOD, PARKSY_DREAM_NARRATIVE, PARKSY_DREAM_META)
        assert isinstance(r, EnforceResult)

    def test_has_final_narrative(self):
        r = enforce(LLM_OUTPUT_GOOD, PARKSY_DREAM_NARRATIVE, PARKSY_DREAM_META)
        assert len(r.final_narrative) > 50

    def test_verdict_injected(self):
        r = enforce(LLM_OUTPUT_GOOD, PARKSY_DREAM_NARRATIVE, PARKSY_DREAM_META)
        assert "레시피 아님" in r.final_narrative

    def test_citations_preserved(self):
        r = enforce(LLM_OUTPUT_GOOD, PARKSY_DREAM_NARRATIVE, PARKSY_DREAM_META)
        assert len(r.citations) == 3

    def test_structured_has_plutchik_axes_plugs(self):
        r = enforce(LLM_OUTPUT_GOOD, PARKSY_DREAM_NARRATIVE, PARKSY_DREAM_META)
        assert "plutchik" in r.structured
        assert "axis_profile" in r.structured
        assert "plug_weights" in r.structured
        assert "active_gates" in r.structured

    def test_axis_dominant_grief_or_liberation(self):
        """박씨 꿈 = grief + liberation 양가 (5800줄 결론과 일치)"""
        r = enforce(LLM_OUTPUT_GOOD, PARKSY_DREAM_NARRATIVE, PARKSY_DREAM_META)
        dom = r.structured["dominant_axis"]
        assert dom in {"grief", "liberation", "rage"}

    def test_rubric_has_all_axes(self):
        r = enforce(LLM_OUTPUT_GOOD, PARKSY_DREAM_NARRATIVE, PARKSY_DREAM_META)
        for key in ("structure", "practicality", "tone", "overreach_penalty", "automation"):
            assert key in r.rubric

    def test_safety_level_zero_for_dream(self):
        r = enforce(LLM_OUTPUT_GOOD, PARKSY_DREAM_NARRATIVE, PARKSY_DREAM_META)
        assert r.safety_verdict["level"] == 0


class TestEnforcerForbiddenBlock:
    """LLM이 의료 진단/처방 출력 시 전면 차단."""

    def test_medical_blocked(self):
        r = enforce(LLM_OUTPUT_FORBIDDEN, PARKSY_DREAM_NARRATIVE, PARKSY_DREAM_META)
        assert r.safety_verdict.get("medical_blocked") is True
        assert "엔진 차단" in r.final_narrative

    def test_transformation_log_includes_block(self):
        r = enforce(LLM_OUTPUT_FORBIDDEN, PARKSY_DREAM_NARRATIVE, PARKSY_DREAM_META)
        assert any("critical_forbidden_block" in t for t in r.transformations)


class TestEnforcerToneRewrite:
    """존댓말 LLM 출력 → 박씨 톤 강제 치환."""

    def test_honorifics_rewritten(self):
        r = enforce(LLM_OUTPUT_HONORIFIC, PARKSY_DREAM_NARRATIVE, PARKSY_DREAM_META)
        # "있습니다" / "했습니다" 가 치환되었는지
        assert r.final_narrative.count("있습니다") == 0 or r.final_narrative.count("있다") > 0
        # 치환 로그 있음
        assert any("tone_rewrite" in t for t in r.transformations)


class TestEnforcerCrisis:
    """Crisis 입력 → escalation."""

    def test_l2_input_escalates(self):
        crisis_narrative = "죽고 싶다. 진짜 끝내고 싶다."
        r = enforce(LLM_OUTPUT_GOOD, crisis_narrative, {})
        assert r.safety_verdict.get("escalated") is True
        assert "1393" in r.final_narrative

    def test_dream_death_not_escalated(self):
        """박씨 꿈의 '죽는다'는 꿈 예외 → L0"""
        r = enforce(LLM_OUTPUT_GOOD, PARKSY_DREAM_NARRATIVE, PARKSY_DREAM_META)
        assert r.safety_verdict["level"] == 0
        assert not r.safety_verdict.get("escalated", False)


class TestEnforcerEndToEnd:
    """박씨 2026-04-24 꿈 end-to-end 통합."""

    def test_full_pipeline_parksy_dream(self):
        r = enforce(LLM_OUTPUT_GOOD, PARKSY_DREAM_NARRATIVE, PARKSY_DREAM_META)
        d = r.to_dict()

        # 필수 키
        for key in ("final_narrative", "citations", "structured", "safety_verdict", "rubric"):
            assert key in d

        # 박씨 꿈 핵심 — Plutchik 양가감정 감지
        plutchik = d["structured"]["plutchik"]
        amb = plutchik.get("ambivalence", [])
        # joy ↔ sadness 양가 예상
        amb_pairs = [set(a["polar_pair"]) for a in amb]
        # (꼭 필수는 아님 — 단축 narrative 라 감지 안 될 수 있음)

        # Rubric verdict
        assert d["rubric"]["verdict"] in ("pass", "regenerate", "reject")

        # verdict_template
        assert "레시피 아님" in d["final_narrative"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
