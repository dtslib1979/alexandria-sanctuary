"""
mcp/rules/ 5개 모듈 단위 테스트.

핵심 검증:
- 박씨 실제 발화 → 높은 톤 점수
- 교과서 존댓말 → 금기 감지
- 박씨 부정 표현 위험 패턴 감지
- 루브릭 verdict 정확
"""
from __future__ import annotations

import pytest

from mcp.rules.parksy_tone import tone_score, rewrite_tone
from mcp.rules.parksy_forbidden import scan, has_critical_forbidden
from mcp.rules.parksy_negative import risk_score, should_regenerate
from mcp.rules.parksy_positive import positive_score
from mcp.rules.parksy_eval_rubric import evaluate


# 박씨 실제 발화 (5808줄 로그에서 추출)
PARKSY_REAL_1 = (
    "그리고 그 플러그들만 확률 분포로 선형적인 파이선 코드로만 짜게 되면 "
    "MCP로 만들게 되면 LLM이 로우 데이터 케이스로 가지고 오는 모든 정신 분석 "
    "케이스와 사례들 이거를 강제하게 되는 플러그 뒤에만 붙이면 정신분석 "
    "정신과 상담 AI 모델을 내가 만들 수도 있어."
)

PARKSY_REAL_2 = (
    "그러니까 적어도 저거를 만들게 되고 내가 세 번 이상 이걸 반복하게 될 "
    "거라고 생각을 해서 반복을 하겠다고 하는 게 시발 프로그래밍이니까 "
    "그게 자동화니까."
)

# 교과서 존댓말 (박씨가 싫어함)
TEXTBOOK_EXAMPLE = (
    "당신은 현재 우울증 초기 증상을 보이고 계십니다. "
    "반드시 정신과 치료를 받으셔야 하고 약을 복용하시는 것이 좋습니다. "
    "많이 힘드시겠지만 잘 하고 계세요. 응원합니다."
)

# B급 위로 (부정 위험)
GENERIC_CONSOLATION = (
    "많은 사람들이 그렇게 힘들어합니다. "
    "인간이라면 누구나 겪는 일이에요. "
    "감사하는 마음으로 하루하루 살아가시면 더 행복해질 수 있습니다."
)

# 좋은 MCP 답변 예시 (박씨 톤 + 구조)
GOOD_MCP_ANSWER = (
    "플러그 3개 만들면 된다. "
    "파이썬 코드 175줄. pytest 41/41 통과. "
    "재활용률 95%. 레퍼런스 엔진이지 레시피 아님. "
    "판단은 박씨 것. 세 번 이상 반복되면 자동화."
)


class TestToneScore:
    def test_parksy_real_high_tone(self):
        s = tone_score(PARKSY_REAL_1)["total"]
        assert s >= 0.3, f"박씨 실제 발화 톤 점수 낮음: {s}"

    def test_textbook_low_tone(self):
        s = tone_score(TEXTBOOK_EXAMPLE)["total"]
        assert s < 0.2, f"교과서 문장이 박씨 톤 점수 받음: {s}"

    def test_abstraction_vocab(self):
        d = tone_score(PARKSY_REAL_1)["details"]
        assert d["abstraction"] >= 2  # "플러그", "MCP", "확률 분포" 등


class TestToneRewrite:
    def test_honorific_rewrite(self):
        result, count = rewrite_tone("이것은 훌륭한 것입니다")
        assert count > 0
        assert "입니다" not in result

    def test_sympathetic_rewrite(self):
        result, _ = rewrite_tone("많이 힘드시겠어요")
        assert "힘드시겠" not in result or "힘들겠" in result


class TestForbidden:
    def test_medical_critical(self):
        assert has_critical_forbidden(TEXTBOOK_EXAMPLE)

    def test_benign_text_no_forbidden(self):
        assert not has_critical_forbidden(GOOD_MCP_ANSWER)
        assert not has_critical_forbidden(PARKSY_REAL_1)

    def test_honorific_detected(self):
        matches = scan(TEXTBOOK_EXAMPLE)
        categories = {m.category for m in matches}
        assert "honorifics" in categories
        assert "medical" in categories

    def test_good_answer_clean(self):
        matches = scan(GOOD_MCP_ANSWER)
        assert len(matches) == 0, f"박씨 톤 답변에 금기 감지됨: {matches}"


class TestNegative:
    def test_generic_consolation_high_risk(self):
        score = risk_score(GENERIC_CONSOLATION)
        assert score >= 0.6, f"B급 위로가 위험 점수 낮음: {score}"

    def test_textbook_high_risk(self):
        # 교과서 예시는 negative가 아닌 forbidden_medical로 걸림 (정상)
        # 여기서는 has_critical_forbidden 로 확인
        from mcp.rules.parksy_forbidden import has_critical_forbidden
        assert has_critical_forbidden(TEXTBOOK_EXAMPLE)

    def test_good_answer_low_risk(self):
        assert risk_score(GOOD_MCP_ANSWER) < 0.3


class TestPositive:
    def test_good_answer_positive(self):
        s = positive_score(GOOD_MCP_ANSWER)
        assert s >= 0.3, f"좋은 답변 긍정 점수 낮음: {s}"

    def test_textbook_low_positive(self):
        s = positive_score(TEXTBOOK_EXAMPLE)
        assert s < 0.3


class TestEvalRubric:
    def test_good_answer_passes(self):
        r = evaluate(GOOD_MCP_ANSWER)
        assert r.verdict in ("pass", "regenerate")
        assert r.final_score >= 2.5, f"좋은 답변 최종 점수: {r.final_score}"

    def test_textbook_rejects(self):
        r = evaluate(TEXTBOOK_EXAMPLE)
        assert r.verdict == "reject"
        assert any("CRITICAL" in n or "과장" in n for n in r.notes)

    def test_generic_consolation_regenerate(self):
        r = evaluate(GENERIC_CONSOLATION)
        # B급 위로는 regenerate 또는 reject
        assert r.verdict in ("regenerate", "reject")

    def test_evaluation_returns_all_axes(self):
        r = evaluate(GOOD_MCP_ANSWER)
        assert 0 <= r.structure <= 1
        assert 0 <= r.practicality <= 1
        assert 0 <= r.tone <= 1
        assert 0 <= r.overreach_penalty <= 1
        assert 0 <= r.automation <= 1


class TestParksyReal:
    """박씨 실제 발화 품질 검증 (self-consistency)."""

    def test_parksy_real_not_forbidden(self):
        for text in [PARKSY_REAL_1, PARKSY_REAL_2]:
            matches = scan(text)
            critical = [m for m in matches if m.category == "medical"]
            assert len(critical) == 0, f"박씨 발화 자체가 금기에 걸림: {critical}"

    def test_parksy_real_tone_above_textbook(self):
        parksy_tone = tone_score(PARKSY_REAL_1)["total"]
        textbook_tone = tone_score(TEXTBOOK_EXAMPLE)["total"]
        assert parksy_tone > textbook_tone


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
