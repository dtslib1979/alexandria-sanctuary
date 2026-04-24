"""
mcp/core 5축 axes + weighter 단위 테스트.
"""
from __future__ import annotations

import pytest

from mcp.core.axes import (
    ALL_AXES, AXIS_IDS, extract_all,
    GriefAxis, GuiltAxis, ErosAxis, RageAxis, LiberationAxis, AnxietyAxis,
)
from mcp.core.axes_weighter import (
    PLUG_AXIS_MATRIX, axis_distribution, dominant_axis, axis_narrative,
)


class TestAxesRegistry:
    def test_six_axes(self):
        """v1.2: Anxiety 축 추가 → 6축."""
        assert len(ALL_AXES) == 6

    def test_axis_ids(self):
        assert set(AXIS_IDS) == {"grief", "guilt", "eros", "rage", "liberation", "anxiety"}

    def test_extract_all_returns_all_ids(self):
        dist = extract_all("test", {})
        assert set(dist.keys()) == set(AXIS_IDS)
        for v in dist.values():
            assert 0.0 <= v <= 1.0


class TestGrief:
    def test_dream_death_combo(self):
        v = GriefAxis().extract("어머니가 돌아가시는 꿈", {"is_dream": True})
        assert v > 0.25, f"grief 꿈+죽음 콤보 너무 약함: {v}"

    def test_anniversary_boost(self):
        v = GriefAxis().extract("마지막이었다", {"anniversary_within_30d": True})
        assert v > 0.25


class TestGuilt:
    def test_self_blame(self):
        v = GuiltAxis().extract("미안하고 죄책감 잘못 했다", {})
        assert v > 0.3


class TestEros:
    def test_loneliness(self):
        v = ErosAxis().extract("외롭고 그립고 누군가 접촉이 필요하다", {})
        assert v > 0.3


class TestRage:
    def test_anger(self):
        v = RageAxis().extract("짜증 억울 씨발 병신", {})
        assert v > 0.3


class TestLiberation:
    def test_freedom(self):
        v = LiberationAxis().extract("편하고 가볍고 자유 해방감", {})
        assert v > 0.4

    def test_waking_metaphors(self):
        v = LiberationAxis().extract("창문 열고 새소리 햇빛 바람", {})
        assert v > 0.2


class TestAnxiety:
    """v1.2 신규: 성과/수행 불안 축."""

    def test_performance_anxiety(self):
        v = AnxietyAxis().extract(
            "불안 압박 준비 안 된 끌려나갔다 완성도 부담",
            {"is_dream": True}
        )
        assert v > 0.4, f"performance anxiety 포착 실패: {v}"

    def test_stage_dream_bonus(self):
        """무대/발표 메타데이터 부스트."""
        v = AnxietyAxis().extract(
            "무대 뒤에서 마이크 잡고 말하려 했지만 입에서 아무 말도 안 나왔다",
            {"is_dream": True}
        )
        assert v > 0.25

    def test_silence_darkness_metaphors(self):
        v = AnxietyAxis().extract(
            "새까만 어둠 끝도 없는 침묵이 이어 흐릿해 엉킨",
            {}
        )
        assert v > 0.3

    def test_no_anxiety_for_neutral(self):
        v = AnxietyAxis().extract("오늘 날씨 좋다", {})
        assert v == 0.0


class TestMatrix:
    def test_matrix_has_all_plugs(self):
        expected = {
            "freud", "jung", "family_systems", "shaman_ko", "sufi",
            "ayahuasca", "mass_protocol", "env_trigger",
            "narrative_meta", "parksy_profile", "guardrail",
        }
        assert set(PLUG_AXIS_MATRIX.keys()) == expected

    def test_each_row_sums_to_one(self):
        """v1.2: 6축이라 허용오차 약간 크게."""
        for plug, row in PLUG_AXIS_MATRIX.items():
            s = sum(row.values())
            assert abs(s - 1.0) < 0.01, f"{plug}: row sum = {s}"

    def test_matrix_has_anxiety_column(self):
        """v1.2: 모든 row에 anxiety 키 포함."""
        for plug, row in PLUG_AXIS_MATRIX.items():
            assert "anxiety" in row, f"{plug}: anxiety 열 누락"

    def test_each_row_has_all_axes(self):
        for plug, row in PLUG_AXIS_MATRIX.items():
            assert set(row.keys()) == set(AXIS_IDS)


class TestAxisDistribution:
    def test_distribution_returns_all_axes(self):
        dist = axis_distribution({"freud": 0.3, "jung": 0.2}, "test", {})
        assert set(dist.keys()) == set(AXIS_IDS)

    def test_dominant_liberation_for_waking(self):
        plug_w = {"parksy_profile": 1.0, "env_trigger": 0.3, "guardrail": 1.0}
        narr = "창문 열고 잘 잤다 마음 편하다 해방감"
        dist = axis_distribution(plug_w, narr, {})
        assert dominant_axis(dist) == "liberation", f"{dist}"

    def test_narrative_summary_ko(self):
        dist = {"grief": 0.5, "guilt": 0.4, "eros": 0.1, "rage": 0.05, "liberation": 0.1}
        s = axis_narrative(dist)
        assert "애도" in s


class TestParksyDream20260424:
    """박씨 2026-04-24 꿈 실입력 → 축 프로파일 검증"""

    PARKSY_DREAM = (
        "어머니가 돌아가시는 꿈을 꿨다. "
        "심폐 소생 쇼크 전기 충격기 바이탈 사인이 들리며 갑자기 일어나서 "
        "오케스트라를 지휘하듯 한 사람 한 사람 눈을 맞추며 웃었다. "
        "상가집 준비하러 가는 길에 모르는 전화에 병신이라고 욕했다. "
        "꿈 속에서도 추론했다 아마 업소여성과 관계 후에 부랴부랴 뛰어오다 까먹은 사람일 거라고."
    )
    META = {"is_dream": True, "date": "2026-04-24"}

    def test_grief_strong(self):
        # FreudPlug + ShamanKoPlug + EnvTriggerPlug 간접 기여 합
        plug_w = {
            "freud": 0.40,
            "jung": 0.35,
            "family_systems": 0.20,
            "shaman_ko": 0.15,
            "env_trigger": 0.25,
            "narrative_meta": 0.30,
            "mass_protocol": 0.08,
            "parksy_profile": 1.0,
            "guardrail": 1.0,
            "sufi": 0.06,
            "ayahuasca": 0.06,
        }
        dist = axis_distribution(plug_w, self.PARKSY_DREAM, self.META)
        assert dist["grief"] > 0.15, f"grief 너무 약함: {dist}"

    def test_multiple_axes_active(self):
        plug_w = {p: 0.2 for p in PLUG_AXIS_MATRIX}
        plug_w["parksy_profile"] = 1.0
        plug_w["guardrail"] = 1.0
        plug_w["freud"] = 0.4
        plug_w["jung"] = 0.35
        dist = axis_distribution(plug_w, self.PARKSY_DREAM, self.META)
        active = [aid for aid, v in dist.items() if v >= 0.15]
        # 백서 §15 성공 기준: axis 다양성 ≥ 2
        assert len(active) >= 2, f"활성 축 부족: {dist}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
