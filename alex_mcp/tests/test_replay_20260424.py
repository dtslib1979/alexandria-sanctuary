"""
박씨 2026-04-24 꿈 재현 테스트.

실제 ParksyLog_20260424_082123.md 내용을 입력으로 넣어서
플러그 × 축 × 가드레일 전체 파이프라인 동작을 검증한다.

v1.0 성공 기준 (WHITEPAPER §15):
- safety_verdict.level == 0 (꿈 예외)
- axis 다양성 최소 2축 ≥ 0.15
- dominant_axis ∈ {grief, liberation} (2차 해석 고려)
- 활성 Gate 최소 3개
- parksy_tone_verdict 고정 문구 존재
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from alex_mcp.plug_orchestrator import analyze_full


# ─────────────────────────────────────────────────────────────────
#  1차 진술 — 꿈 내용만
# ─────────────────────────────────────────────────────────────────
PARKSY_DREAM_PRIMARY = """
어머니가 돌아가시는 꿈을 꿨다. 심폐 소생 쇼크 전기 충격기로 바이탈 사인
들리면서 갑자기 일어나서 오케스트라 지휘하듯 한 사람 한 사람 얼굴을 마주
치고 눈을 마주쳐주고 웃으면서 지휘를 했다. 상가집 상 치르러 가는 길에
이상한 전화가 왔고 짜증 나서 말을 안 하니까 병신이라고 욕했다. 아마
업소여성을 만나고 관계가 끝난 후에 상 치르러 부랴부랴 달려오다가
까먹었던 사람일 거라고 꿈 속에서도 추론했다.
""".strip()

PARKSY_DREAM_META = {
    "is_dream": True,
    "date": "2026-04-24",
    "is_family_event": True,
}


# ─────────────────────────────────────────────────────────────────
#  2차 진술 — 수면 환경 + 애니버서리 맥락
# ─────────────────────────────────────────────────────────────────
PARKSY_DREAM_WITH_CONTEXT = PARKSY_DREAM_PRIMARY + """

이 꿈을 꾼 장소는 2년 전 내가 살던 옛 방이다. 작은누나 도와주러 갔다가
창문 열어놓고 잤다. 약간 추웠지만 장판 따뜻하고 햇빛 들어오고 새소리
들리며 오랜만에 마음 편하게 잘 잤다. 2년 전 3월 13일은 내 1인 출판사
창립기념일이고, 1년 전 3월 13일은 어머니 요양원 입소 날이다.
"""

PARKSY_CONTEXT_META = {
    "is_dream": True,
    "date": "2026-04-24",
    "is_family_event": True,
    "location": "옛 방",
    "anniversary_within_30d": True,
}


class TestPrimaryDream:
    """1차 꿈 입력 검증"""

    @pytest.fixture
    def report(self):
        return analyze_full(PARKSY_DREAM_PRIMARY, PARKSY_DREAM_META)

    def test_safety_level_zero_dream_exception(self, report):
        """'어머니가 돌아가시는 꿈' → 꿈 예외로 level=0"""
        assert report["safety_verdict"]["level"] == 0
        assert report["safety_verdict"]["dream_exception_applied"]

    def test_axis_diversity(self, report):
        """최소 2축 활성"""
        axes = report["axis_profile"]
        active = [aid for aid, v in axes.items() if v >= 0.15]
        assert len(active) >= 2, f"활성 축 부족: {axes}"

    def test_dominant_axis_valid(self, report):
        assert report["dominant_axis"] in {"grief", "guilt", "liberation", "rage"}

    def test_freud_and_jung_active(self, report):
        w = report["plug_weights"]
        assert w["freud"] > 0.20, f"freud 약함: {w['freud']}"
        assert w["jung"] > 0.20, f"jung 약함: {w['jung']}"

    def test_narrative_meta_detects_cum_reasoning(self, report):
        """박씨 '꿈 속에서도 추론했다' 시그니처"""
        assert report["plug_weights"]["narrative_meta"] > 0.15

    def test_parksy_tone_verdict_fixed(self, report):
        assert "레시피 아님" in report["parksy_tone_verdict"]

    def test_active_gates_count(self, report):
        """7 Gate 중 최소 3개 활성"""
        assert len(report["active_gates"]) >= 3, f"Gate 부족: {report['active_gates']}"


class TestWithContext:
    """2차 진술 — 애니버서리 + 옛 방 포함"""

    @pytest.fixture
    def report(self):
        return analyze_full(PARKSY_DREAM_WITH_CONTEXT, PARKSY_CONTEXT_META)

    def test_env_trigger_strongly_active(self, report):
        """옛 방 + 3/13 애니버서리 → env_trigger 가중치 확 올라야"""
        w = report["plug_weights"]["env_trigger"]
        assert w > 0.40, f"env_trigger 부스트 실패: {w}"

    def test_liberation_axis_rises(self, report):
        """창문/새소리/햇빛/마음 편하다 → liberation 강화"""
        lib = report["axis_profile"]["liberation"]
        assert lib >= 0.15, f"liberation 너무 약함: {lib}"

    def test_grief_and_liberation_coexist(self, report):
        """박씨 실제 상태: 애도와 해방감이 공존"""
        axes = report["axis_profile"]
        top2 = sorted(axes.values(), reverse=True)[:2]
        assert top2[1] >= 0.15, f"2위 축 약함: {axes}"


class TestSampleReportGeneration:
    """샘플 리포트 JSON을 디스크에 저장 — 박씨 확인용"""

    def test_save_primary_dream_report(self, tmp_path):
        report = analyze_full(PARKSY_DREAM_PRIMARY, PARKSY_DREAM_META)
        out = tmp_path / "sample.json"
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
        loaded = json.loads(out.read_text())
        assert loaded["safety_verdict"]["level"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
