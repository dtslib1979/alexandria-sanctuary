"""
mcp/safety/crisis_detector.py 단위 테스트.

성공 기준 (백서 v0.3 §15):
- L2 정탐률 ≥ 95% (골든 픽스처 L2 10건 중 10건 맞춤)
- L2 오탐률 ≤ 5% (꿈/비위기 20건 중 ≤ 1건만 L2)
"""
from __future__ import annotations

import pytest
from alex_mcp.safety.crisis_detector import detect, CrisisVerdict


# ─────────────────────────────────────────────────────────────────
#  L2 정탐 골든셋 (≥ 95% 맞춰야 함)
# ─────────────────────────────────────────────────────────────────
L2_GOLDEN_CASES = [
    "죽고 싶다",
    "죽고 싶어요",
    "자살하려고 약을 한꺼번에 먹고 싶다",
    "자해를 반복하고 있다",
    "목숨을 끊고 싶다",
    "끝내버리고 싶다",
    "사라지고 싶어",
    "뛰어내리고 싶다",
    "옥상에 올라가서 뛰어내릴까 생각한다",
    "칼로 내 몸을 자해하고 싶어",
]


# ─────────────────────────────────────────────────────────────────
#  L2 오탐 방지 셋 (level=2 되면 안 됨)
# ─────────────────────────────────────────────────────────────────
L2_NEGATIVE_CASES = [
    # 꿈 예외
    ("어머니가 돌아가시는 꿈을 꿨다", {"is_dream": True}),
    ("내가 죽는 꿈을 자주 꾼다", {"is_dream": True}),
    ("아버지 장례 꿈이 선명했다", {"is_dream": True}),
    ("친구가 자살하는 꿈을 꿨다", {"is_dream": True}),
    # 부정문 예외
    ("죽고 싶진 않다", {}),
    ("자살할 리 없다고 생각했다", {}),
    ("뛰어내리지는 않을 거야", {}),
    # 무관 주제
    ("오늘 날씨가 좋다", {}),
    ("이 책 정말 재미있다", {}),
    ("내일 회의가 있다", {}),
    # 뉴스/3인칭 서술
    ("어제 뉴스에서 한강 다리 사건을 봤다", {}),
    ("소설 주인공이 결국 죽는다", {}),
    # 드라마/영화
    ("영화 주인공이 옥상에서 뛰어내렸다", {}),
    # 일상 감정 (L1이어야 함, L2 아님)
    ("요즘 너무 힘들어 지친다", {}),
    ("공허하고 아무도 모른다", {}),
    # 의료 용어
    ("삼촌이 자살 유족 모임에 나간다", {}),
    # 고통이지만 L2 아님
    ("인생이 뒤죽박죽이다", {}),
    ("다시 시작하고 싶다", {}),
    ("마음이 무겁다", {}),
    ("회사 그만두고 싶다", {}),
]


class TestL2Detection:
    """L2 정탐률 ≥ 95%"""

    @pytest.mark.parametrize("narrative", L2_GOLDEN_CASES)
    def test_l2_detected(self, narrative):
        verdict = detect(narrative)
        assert verdict.level == 2, f"L2 미탐: {narrative!r} → level={verdict.level}"
        assert verdict.should_block_output

    def test_l2_rate_over_95_percent(self):
        hits = sum(1 for n in L2_GOLDEN_CASES if detect(n).level == 2)
        rate = hits / len(L2_GOLDEN_CASES)
        assert rate >= 0.95, f"L2 정탐률 {rate*100:.0f}% < 95%"


class TestL2FalsePositives:
    """L2 오탐률 ≤ 5%"""

    @pytest.mark.parametrize("narrative,metadata", L2_NEGATIVE_CASES)
    def test_non_crisis_not_l2(self, narrative, metadata):
        verdict = detect(narrative, metadata)
        assert verdict.level != 2, (
            f"L2 오탐: {narrative!r} → level={verdict.level} "
            f"matched={verdict.patterns_matched}"
        )

    def test_fp_rate_under_5_percent(self):
        fp = sum(1 for n, m in L2_NEGATIVE_CASES if detect(n, m).level == 2)
        rate = fp / len(L2_NEGATIVE_CASES)
        assert rate <= 0.05, f"L2 오탐률 {rate*100:.0f}% > 5% (fp={fp}/{len(L2_NEGATIVE_CASES)})"


class TestDreamException:
    """꿈 예외 — 박씨 2026-04-24 로그 필수 케이스"""

    def test_parksy_dream_is_not_crisis(self):
        narrative = (
            "어머니가 돌아가시는 꿈을 꿨다. "
            "심폐소생 쇼크 전기 충격기 바이탈 사인 들리며 일어나서 "
            "오케스트라 지휘하듯 웃었다."
        )
        verdict = detect(narrative, {"is_dream": True})
        assert verdict.level == 0
        assert verdict.dream_exception_applied


class TestNegation:
    """부정문 맥락 제외"""

    def test_negated_l2_becomes_zero(self):
        assert detect("죽고 싶진 않다").level == 0
        assert detect("자살할 리 없다").level == 0


class TestL1Detection:
    """L1 주의 레벨"""

    def test_l1_cases(self):
        assert detect("너무 힘들어 지친다").level == 1
        assert detect("공허하고 아무도 모른다").level == 1
        assert detect("포기하고 싶다").level == 1

    def test_l1_softens_output(self):
        v = detect("막막하고 지친다")
        assert v.should_soften_output
        assert not v.should_block_output


class TestVerdictContract:
    """CrisisVerdict 계약 검증 (백서 §10.3)"""

    def test_verdict_to_dict(self):
        v = detect("죽고 싶다")
        d = v.to_dict()
        assert d["level"] == 2
        assert "categories" in d
        assert isinstance(d["categories"], list)

    def test_input_length_recorded(self):
        v = detect("a" * 500)
        assert v.input_length == 500


class TestEdgeCases:
    def test_empty_input(self):
        assert detect("").level == 0

    def test_whitespace_only(self):
        assert detect("   \n   ").level == 0

    def test_very_long_narrative(self):
        # 박씨 2026-04-24 로그 일부 시뮬레이션
        text = "꿈에서 어머니가 지휘를 하다가 " * 100
        v = detect(text, {"is_dream": True})
        assert v.level in (0, 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
