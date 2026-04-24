"""
Plutchik Layer 1 + Bridge 단위 테스트.
"""
from __future__ import annotations

import pytest

from mcp.core.plutchik import (
    ALL_EMOTIONS, EMOTION_IDS, POLAR_PAIRS, DYADS,
    Joy, Sadness, Trust, Disgust, Fear, Anger, Surprise, Anticipation,
    extract_all, dominant_emotion, detect_dyads, detect_ambivalence,
    emotion_profile,
)
from mcp.core.emotion_bridge import (
    EMOTION_TO_AXIS, plutchik_to_axis_boost, validate_mapping,
)


class TestRegistry:
    def test_eight_emotions(self):
        assert len(ALL_EMOTIONS) == 8

    def test_emotion_ids(self):
        assert set(EMOTION_IDS) == {
            "joy", "trust", "fear", "surprise",
            "sadness", "disgust", "anger", "anticipation",
        }

    def test_four_polar_pairs(self):
        assert len(POLAR_PAIRS) == 4

    def test_24_dyads(self):
        """Plutchik 공식 24 dyad (primary 8 + secondary 8 + tertiary 8)."""
        assert len(DYADS) == 24

    def test_dyad_distribution(self):
        by_distance = {1: 0, 2: 0, 3: 0}
        for _, _, dist, _, _ in DYADS:
            by_distance[dist] += 1
        assert by_distance == {1: 8, 2: 8, 3: 8}


class TestEmotionExtraction:
    def test_joy_keywords(self):
        v = Joy().extract("웃으며 기쁘고 행복했다", {})
        assert v > 0.3

    def test_sadness_death(self):
        v = Sadness().extract("어머니가 돌아가시는 꿈", {"is_dream": True})
        assert v > 0.3

    def test_trust_warmth(self):
        v = Trust().extract("편안한 느낌의 사람 손을 잡", {})
        assert v > 0.2

    def test_disgust(self):
        v = Disgust().extract("지긋지긋 역겹다", {})
        assert v > 0.2

    def test_fear_performance(self):
        v = Fear().extract("무대에서 불안감 압박 떨림", {"is_dream": True})
        assert v > 0.3

    def test_anger(self):
        v = Anger().extract("짜증 화가 난 씨발 병신", {})
        assert v > 0.3

    def test_surprise(self):
        v = Surprise().extract("갑자기 예상 밖 뜻밖", {})
        assert v > 0.2

    def test_anticipation(self):
        v = Anticipation().extract("기대 설레 기다렸다", {})
        assert v > 0.2


class TestIntensityLabels:
    def test_joy_intensity_levels(self):
        j = Joy()
        assert j.intensity_label(0.8) == "ecstasy"
        assert j.intensity_label(0.5) == "joy"
        assert j.intensity_label(0.1) == "serenity"

    def test_fear_intensity_levels(self):
        f = Fear()
        assert f.intensity_label(0.8) == "terror"
        assert f.intensity_label(0.5) == "fear"
        assert f.intensity_label(0.1) == "apprehension"


class TestDyads:
    def test_love_dyad(self):
        dist = {"joy": 0.5, "trust": 0.4, "fear": 0, "surprise": 0,
                "sadness": 0, "disgust": 0, "anger": 0, "anticipation": 0}
        dyads = detect_dyads(dist)
        names = [d["english"] for d in dyads]
        assert "Love" in names

    def test_optimism_dyad(self):
        dist = {"joy": 0.4, "anticipation": 0.3,
                "trust": 0, "fear": 0, "surprise": 0,
                "sadness": 0, "disgust": 0, "anger": 0}
        dyads = detect_dyads(dist)
        assert any(d["english"] == "Optimism" for d in dyads)

    def test_anxiety_tertiary_dyad(self):
        """Fear + Anticipation = Anxiety (Plutchik 3차 dyad)."""
        dist = {"fear": 0.5, "anticipation": 0.4,
                "joy": 0, "trust": 0, "surprise": 0,
                "sadness": 0, "disgust": 0, "anger": 0}
        dyads = detect_dyads(dist)
        assert any(d["english"] == "Anxiety" and d["distance"] == 3 for d in dyads)

    def test_no_dyad_for_polar_opposites(self):
        """대립쌍은 dyad 아님."""
        dist = {"joy": 0.5, "sadness": 0.5,
                "trust": 0, "fear": 0, "surprise": 0,
                "disgust": 0, "anger": 0, "anticipation": 0}
        dyads = detect_dyads(dist)
        # joy-sadness 쌍은 dyad에 없음 — 대립
        for d in dyads:
            assert set(d["emotions"]) != {"joy", "sadness"}


class TestAmbivalence:
    def test_joy_sadness_ambivalence(self):
        """박씨 2026-04-24 '어머니 죽음에 기쁨' 케이스."""
        dist = {"joy": 0.35, "sadness": 0.35,
                "trust": 0, "fear": 0, "surprise": 0,
                "disgust": 0, "anger": 0, "anticipation": 0}
        amb = detect_ambivalence(dist)
        assert len(amb) >= 1
        assert set(amb[0]["polar_pair"]) == {"joy", "sadness"}

    def test_no_ambivalence_single_emotion(self):
        dist = {"joy": 0.5,
                "trust": 0, "fear": 0, "surprise": 0,
                "sadness": 0, "disgust": 0, "anger": 0, "anticipation": 0}
        assert detect_ambivalence(dist) == []


class TestBridge:
    def test_mapping_valid(self):
        assert validate_mapping()

    def test_all_emotions_mapped(self):
        assert set(EMOTION_TO_AXIS.keys()) == set(EMOTION_IDS)

    def test_sadness_boosts_grief(self):
        boost = plutchik_to_axis_boost("돌아가시는 꿈 슬픔 눈물", {"is_dream": True})
        # grief 축이 가장 많이 올라야
        top = max(boost, key=boost.get)
        assert top == "grief"

    def test_fear_boosts_anxiety(self):
        boost = plutchik_to_axis_boost("무대 불안감 압박 떨림", {"is_dream": True})
        assert boost["anxiety"] > boost["grief"]

    def test_trust_boosts_eros(self):
        boost = plutchik_to_axis_boost("편안한 느낌 손을 잡", {})
        assert boost["eros"] > 0


class TestParksyDream20260424:
    """박씨 2026-04-24 꿈 → Plutchik Layer 1 실증."""

    TEXT = (
        "어머니가 돌아가시는 꿈 갑자기 일어나서 오케스트라 지휘하듯 "
        "웃으며 지휘했다 기분이 좋았다 상가집 가는 길 모르는 전화에 "
        "병신이라고 욕했다"
    )
    META = {"is_dream": True}

    def test_sadness_and_joy_both_active(self):
        p = emotion_profile(self.TEXT, self.META)
        emo = p["emotion_levels"]
        assert emo["sadness"] > 0.15
        assert emo["joy"] > 0.1

    def test_ambivalence_detected(self):
        """'애도+기쁨 공존' = Joy↔Sadness 양가."""
        p = emotion_profile(self.TEXT, self.META)
        amb_pairs = [set(a["polar_pair"]) for a in p["ambivalence"]]
        assert {"joy", "sadness"} in amb_pairs

    def test_anger_from_bs_curse(self):
        p = emotion_profile(self.TEXT, self.META)
        assert p["emotion_levels"]["anger"] > 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
