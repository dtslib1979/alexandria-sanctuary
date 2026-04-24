"""
mcp/plugs 단위 테스트 (11 플러그).
"""
from __future__ import annotations

import pytest

from mcp.plugs import ALL_PLUGS, Plug
from mcp.plugs.parksy_profile import ParksyProfilePlug
from mcp.plugs.env_trigger import EnvTriggerPlug
from mcp.plugs.freud import FreudPlug
from mcp.plugs.jung import JungPlug
from mcp.plugs.family import FamilySystemsPlug
from mcp.plugs.shaman_ko import ShamanKoPlug
from mcp.plugs.sufi import SufiPlug
from mcp.plugs.ayahuasca import AyahuascaPlug
from mcp.plugs.mass import MassProtocolPlug
from mcp.plugs.narrative_meta import NarrativeMetaPlug
from mcp.plugs.guardrail import GuardrailPlug


VALID_GATES = {"I", "II", "III", "IV", "V", "VI", "VII", None}


class TestRegistry:
    def test_all_plugs_loaded(self):
        assert len(ALL_PLUGS) == 11

    def test_all_plugs_are_plug_instances(self):
        for p in ALL_PLUGS:
            assert isinstance(p, Plug)

    def test_all_plugs_have_unique_names(self):
        names = [p.name for p in ALL_PLUGS]
        assert len(names) == len(set(names))

    def test_all_plugs_valid_gate_ids(self):
        for p in ALL_PLUGS:
            assert p.gate_id in VALID_GATES

    def test_all_plugs_score_returns_float(self):
        ctx = {"narrative": "test", "metadata": {}}
        for p in ALL_PLUGS:
            v = p.score(ctx)
            assert isinstance(v, float)
            assert 0.0 <= v <= 1.0

    def test_all_plugs_frame_returns_dict(self):
        ctx = {"narrative": "test", "metadata": {}}
        for p in ALL_PLUGS:
            f = p.frame(ctx)
            assert isinstance(f, dict)
            assert f["name"] == p.name

    def test_keywords_trigger_is_list(self):
        for p in ALL_PLUGS:
            assert isinstance(p.keywords_trigger, list)


class TestParksyProfile:
    def test_score_always_one(self):
        p = ParksyProfilePlug()
        assert p.score({}) == 1.0
        assert p.score({"narrative": "", "metadata": {}}) == 1.0

    def test_frame_has_directive(self):
        p = ParksyProfilePlug()
        f = p.frame({})
        assert "directive" in f
        assert "verdict_template" in f
        assert "존댓말" in f["directive"] or "존댓말" in str(f)


class TestGuardrail:
    def test_score_always_one(self):
        assert GuardrailPlug().score({}) == 1.0

    def test_frame_has_forbidden(self):
        f = GuardrailPlug().frame({})
        assert "forbidden_phrasings" in f
        assert len(f["forbidden_phrasings"]) >= 3


class TestEnvTrigger:
    def test_old_room_detected(self):
        p = EnvTriggerPlug()
        v = p.score({"narrative": "옛 방에서 잤다", "metadata": {}})
        assert v > self.default_for(p)

    def test_parksy_anniversary(self):
        """2026-03-13 ± 30일 = 창립/요양원 입소 중첩"""
        p = EnvTriggerPlug()
        v = p.score({"narrative": "그냥 오늘", "metadata": {"date": "2026-03-15"}})
        assert v >= 0.40, f"애니버서리 부스트 미작동: {v}"

    def test_detected_anniversaries_frame(self):
        p = EnvTriggerPlug()
        f = p.frame({"narrative": "옛 방", "metadata": {"date": "2026-03-13"}})
        assert len(f["detected_anniversaries"]) >= 1

    @staticmethod
    def default_for(p):
        return p.weight_default


class TestFreud:
    def test_dream_bonus(self):
        p = FreudPlug()
        no_dream = p.score({"narrative": "어머니 꿈", "metadata": {}})
        is_dream = p.score({"narrative": "어머니 꿈", "metadata": {"is_dream": True}})
        assert is_dream > no_dream

    def test_frame_has_cautions(self):
        f = FreudPlug().frame({})
        assert any("죽이고 싶" in c for c in f["cautions"])


class TestJung:
    def test_conductor_keyword_boosts(self):
        p = JungPlug()
        base = p.score({"narrative": "test"})
        conductor = p.score({"narrative": "오케스트라 지휘자가 나왔다"})
        assert conductor > base

    def test_parksy_drim_frame(self):
        f = JungPlug().frame({})
        assert "지휘자_어머니" in f["parksy_specific"]


class TestFamily:
    def test_family_keywords(self):
        p = FamilySystemsPlug()
        v = p.score({"narrative": "부양자 책임 누나 간병"})
        assert v > p.weight_default + 0.1


class TestShamanKo:
    def test_cautions_include_no_superstition(self):
        f = ShamanKoPlug().frame({})
        assert any("미신" in c for c in f["cautions"])


class TestSufi:
    def test_basic_load(self):
        p = SufiPlug()
        assert p.gate_id == "III"


class TestAyahuasca:
    def test_cautions_forbid_drugs(self):
        f = AyahuascaPlug().frame({})
        assert any("약물" in c for c in f["cautions"])


class TestMass:
    def test_six_stages(self):
        f = MassProtocolPlug().frame({})
        assert len(f["six_stages"]) == 6
        assert f["six_stages"][0]["name"].startswith("입당")
        assert f["six_stages"][5]["name"].startswith("파견")

    def test_paesin_boost(self):
        p = MassProtocolPlug()
        base = p.score({"narrative": "test"})
        paesin = p.score({"narrative": "파견 마무리"})
        assert paesin > base


class TestNarrativeMeta:
    def test_meta_reflection_detected(self):
        p = NarrativeMetaPlug()
        base = p.score({"narrative": "test"})
        meta = p.score({
            "narrative": "꿈 속에서도 추론했다 아마 업소여성일 거라고",
            "metadata": {"is_dream": True}
        })
        assert meta > base + 0.15

    def test_frame_lists_detected_patterns(self):
        f = NarrativeMetaPlug().frame({
            "narrative": "돌이켜보니 아마 그럴 거라고 추론했다"
        })
        assert len(f["detected_meta_patterns"]) >= 2


class TestParksyDream20260424:
    """박씨 2026-04-24 꿈 입력 핵심 검증 (end-to-end for plugs only)."""

    PARKSY_DREAM = (
        "어머니가 돌아가시는 꿈을 꿨다. "
        "심폐 소생 쇼크 전기 충격기 바이탈 사인이 들리며 갑자기 일어나서 "
        "오케스트라를 지휘하듯 한 사람 한 사람 눈을 맞추며 웃었다. "
        "상가집 준비하러 가는 길에 모르는 전화에 병신이라고 욕했다. "
        "꿈 속에서도 추론했다 아마 업소여성과 관계 후에 부랴부랴 뛰어오다 까먹은 사람일 거라고."
    )
    PARKSY_META = {"is_dream": True, "date": "2026-04-24", "location": "옛 방"}

    def test_freud_activated(self):
        v = FreudPlug().score({"narrative": self.PARKSY_DREAM, "metadata": self.PARKSY_META})
        assert v > 0.3, f"Freud 가중 너무 낮음: {v}"

    def test_jung_activated_by_conductor(self):
        v = JungPlug().score({"narrative": self.PARKSY_DREAM, "metadata": self.PARKSY_META})
        assert v > 0.3, f"Jung 가중 너무 낮음: {v}"

    def test_family_activated(self):
        v = FamilySystemsPlug().score({
            "narrative": self.PARKSY_DREAM, "metadata": self.PARKSY_META
        })
        assert v > 0.1

    def test_narrative_meta_activated(self):
        v = NarrativeMetaPlug().score({
            "narrative": self.PARKSY_DREAM, "metadata": self.PARKSY_META
        })
        assert v > 0.2, f"NarrativeMeta (박씨 꿈 속 추론 시그니처) 가중 너무 낮음: {v}"

    def test_parksy_profile_one(self):
        assert ParksyProfilePlug().score({
            "narrative": self.PARKSY_DREAM
        }) == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
