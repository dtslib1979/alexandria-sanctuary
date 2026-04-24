"""
Plutchik (Layer 1) ↔ Domain Axes (Layer 2) 매핑.

- Layer 1: Plutchik 8 기본 감정 (universal, detection)
- Layer 2: 6 도메인 축 (박씨 치료 특화, 해석)

EmotionBridge = Layer 1 분포를 Layer 2 축에 추가 기여로 주입.

매핑 이론 근거:
- Grief = Sadness(주) + Trust-loss(애착 상실)
- Guilt = Fear + Disgust(자기혐오) = Plutchik 3차 dyad "Shame"에 근접
- Eros = Trust + Joy + Anticipation
- Rage = Anger (직접)
- Liberation = Joy + Anticipation (= Optimism dyad) + Surprise
- Anxiety = Fear + Anticipation (= Plutchik 3차 dyad "Anxiety" 정확 매핑)

대립쌍 (ambivalence) 특수 처리:
- Joy↔Sadness 양가 → Liberation 축과 Grief 축 동시 상승 (박씨 2026-04-24 꿈)
"""
from __future__ import annotations

from alex_mcp.core.axes import AXIS_IDS
from alex_mcp.core.plutchik import extract_all as plutchik_extract


# Plutchik 감정 → Domain 축 기여 매트릭스
# row 합이 1.0일 필요 없음 (각 감정이 여러 축에 기여 가능)
EMOTION_TO_AXIS: dict[str, dict[str, float]] = {
    "sadness":      {"grief": 0.70, "guilt": 0.15, "liberation": 0.05},
    "anger":        {"rage": 0.80, "guilt": 0.10},
    "fear":         {"anxiety": 0.70, "guilt": 0.15},
    "disgust":      {"guilt": 0.30, "rage": 0.25, "grief": 0.10},
    "joy":          {"liberation": 0.60, "eros": 0.25},
    "trust":        {"eros": 0.55, "liberation": 0.20},
    "surprise":     {"liberation": 0.35, "anxiety": 0.25},
    "anticipation": {"eros": 0.25, "liberation": 0.30, "anxiety": 0.20},
}

# Plutchik 기여의 전체 가중치 (도메인 직접 추출 대비)
# 0.4 = 플러그 간접 기여와 비슷한 수준
PLUTCHIK_CONTRIBUTION_WEIGHT = 0.4


def plutchik_to_axis_boost(narrative: str, metadata: dict | None = None) -> dict[str, float]:
    """
    Plutchik 분포를 축 기여로 변환.
    반환: {axis_id: boost_value} — axis_distribution()에 덧셈 주입.
    """
    metadata = metadata or {}
    emo = plutchik_extract(narrative, metadata)

    boost = {aid: 0.0 for aid in AXIS_IDS}
    for emo_id, emo_score in emo.items():
        contributions = EMOTION_TO_AXIS.get(emo_id, {})
        for axis_id, ratio in contributions.items():
            boost[axis_id] += emo_score * ratio * PLUTCHIK_CONTRIBUTION_WEIGHT

    return boost


def validate_mapping() -> bool:
    """매핑이 모든 축/감정 커버하는지 체크."""
    from alex_mcp.core.plutchik import EMOTION_IDS

    for eid in EMOTION_IDS:
        if eid not in EMOTION_TO_AXIS:
            return False

    # 각 축은 최소 하나 이상의 감정에서 기여받아야 함
    axis_coverage = {aid: False for aid in AXIS_IDS}
    for emo_row in EMOTION_TO_AXIS.values():
        for aid in emo_row:
            if aid in axis_coverage:
                axis_coverage[aid] = True
    return all(axis_coverage.values())


if __name__ == "__main__":
    assert validate_mapping(), "매핑 불완전"
    print("EMOTION_TO_AXIS validation: OK")

    # 박씨 꿈 사례
    text = "어머니가 돌아가시는 꿈 갑자기 일어나 오케스트라 지휘하며 웃으며"
    boost = plutchik_to_axis_boost(text, {"is_dream": True})
    print(f"\n박씨 꿈 Plutchik 기반 축 부스트:")
    for aid, v in sorted(boost.items(), key=lambda x: -x[1]):
        bar = "█" * int(v * 40)
        print(f"  {aid:12s} {v:.4f} {bar}")
