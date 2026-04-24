"""
AxesWeighter v1.2 — plug × axis 매트릭스 (11 플러그 × 6 축).

v1.1 → v1.2 변경:
- Anxiety 6번째 축 추가로 매트릭스 6열
- narrative_meta 에 anxiety 기여 증가 (메타인지 ↔ 수행 불안 연결)
- freud/jung 에 anxiety 중간 수준 할당
- 모든 row 합 = 1.0 유지

참조: WHITEPAPER-v1.2.md §5.3, 부록 C
"""
from __future__ import annotations

from alex_mcp.core.axes import ALL_AXES, AXIS_IDS, extract_all


# ─────────────────────────────────────────────────────────────────
#  PLUG_AXIS_MATRIX v1.2 (11 plugs × 6 axes, rows sum to 1.0)
# ─────────────────────────────────────────────────────────────────
PLUG_AXIS_MATRIX: dict[str, dict[str, float]] = {
    # Freud: 죄책감/초자아 + 불안(억압→불안) 포함
    "freud": {
        "grief": 0.20, "guilt": 0.30, "eros": 0.20,
        "rage": 0.10, "liberation": 0.05, "anxiety": 0.15,
    },
    # Jung: 통합/개성화 = 해방 지배. 그림자→불안 일부
    "jung": {
        "grief": 0.15, "guilt": 0.08, "eros": 0.12,
        "rage": 0.05, "liberation": 0.45, "anxiety": 0.15,
    },
    # Family Systems: 죄책감+해방 양쪽. 역할 압박=anxiety 소폭
    "family_systems": {
        "grief": 0.15, "guilt": 0.28, "eros": 0.05,
        "rage": 0.18, "liberation": 0.25, "anxiety": 0.09,
    },
    # Shaman_ko: 한=grief 지배. 불안 기여 낮음
    "shaman_ko": {
        "grief": 0.38, "guilt": 0.20, "eros": 0.05,
        "rage": 0.15, "liberation": 0.17, "anxiety": 0.05,
    },
    # Sufi: 비움=해방 극대
    "sufi": {
        "grief": 0.08, "guilt": 0.08, "eros": 0.15,
        "rage": 0.05, "liberation": 0.55, "anxiety": 0.09,
    },
    # Ayahuasca: 해체-재조립 = 해방
    "ayahuasca": {
        "grief": 0.15, "guilt": 0.10, "eros": 0.20,
        "rage": 0.15, "liberation": 0.35, "anxiety": 0.05,
    },
    # Mass: 고해(guilt) → 파견(liberation)
    "mass_protocol": {
        "grief": 0.22, "guilt": 0.28, "eros": 0.05,
        "rage": 0.05, "liberation": 0.30, "anxiety": 0.10,
    },
    # Env Trigger: 장소기억=grief/liberation. 애니버서리 불안 일부
    "env_trigger": {
        "grief": 0.28, "guilt": 0.13, "eros": 0.08,
        "rage": 0.08, "liberation": 0.30, "anxiety": 0.13,
    },
    # Narrative Meta: 메타인지 ↔ 자기평가 불안 강함. v1.2에서 anxiety 부스트
    "narrative_meta": {
        "grief": 0.15, "guilt": 0.15, "eros": 0.15,
        "rage": 0.15, "liberation": 0.15, "anxiety": 0.25,
    },
    # Parksy Profile: 톤만 — 6축 균등
    "parksy_profile": {
        "grief": 1/6, "guilt": 1/6, "eros": 1/6,
        "rage": 1/6, "liberation": 1/6, "anxiety": 1/6,
    },
    # Guardrail: 시스템 — 6축 균등
    "guardrail": {
        "grief": 1/6, "guilt": 1/6, "eros": 1/6,
        "rage": 1/6, "liberation": 1/6, "anxiety": 1/6,
    },
}

# 직접 추출 vs 간접 기여 혼합 비율
DIRECT_BLEND = 0.6
INDIRECT_BLEND = 0.4


def axis_distribution(
    plug_weights: dict[str, float],
    narrative: str,
    metadata: dict | None = None,
) -> dict[str, float]:
    """
    최종 축 분포 (v1.3 — Plutchik 통합).

    1. Layer 2 직접 추출 (axes.extract)
    2. Layer 2 간접 (plug weight × PLUG_AXIS_MATRIX)
    3. Layer 1 Plutchik 기여 (emotion_bridge.plutchik_to_axis_boost)
    4. 혼합 + 클램프

    참조: WHITEPAPER §5 (Plutchik Integration)
    """
    from alex_mcp.core.emotion_bridge import plutchik_to_axis_boost

    metadata = metadata or {}
    direct = extract_all(narrative, metadata)

    indirect = {aid: 0.0 for aid in AXIS_IDS}
    for plug_name, pw in plug_weights.items():
        row = PLUG_AXIS_MATRIX.get(plug_name)
        if row is None:
            continue
        for aid, aw in row.items():
            indirect[aid] += pw * aw

    # Layer 1 (Plutchik) 기여
    plutchik_boost = plutchik_to_axis_boost(narrative, metadata)

    combined = {
        aid: min(
            DIRECT_BLEND * direct[aid]
            + INDIRECT_BLEND * indirect[aid]
            + plutchik_boost.get(aid, 0),
            1.0,
        )
        for aid in AXIS_IDS
    }
    return combined


def dominant_axis(distribution: dict[str, float]) -> str:
    if not distribution:
        return "liberation"
    return max(distribution, key=distribution.get)


# ─────────────────────────────────────────────────────────────────
#  한국어 조사 자동 (종성 감지)
# ─────────────────────────────────────────────────────────────────
def _josa_wa(word: str) -> str:
    if not word or not ('가' <= word[-1] <= '힣'):
        return "와"
    return "과" if (ord(word[-1]) - ord('가')) % 28 != 0 else "와"


def _josa_i(word: str) -> str:
    if not word or not ('가' <= word[-1] <= '힣'):
        return "이"
    return "이" if (ord(word[-1]) - ord('가')) % 28 != 0 else "가"


def axis_narrative(distribution: dict[str, float]) -> str:
    """축 분포를 한 줄 한국어 요약으로."""
    sorted_axes = sorted(distribution.items(), key=lambda x: -x[1])
    top = sorted_axes[0]
    second = sorted_axes[1] if len(sorted_axes) > 1 else None

    name_map = {
        "grief": "애도",
        "guilt": "죄책감",
        "eros": "삶의 욕구",
        "rage": "분노",
        "liberation": "해방감",
        "anxiety": "불안",
    }

    if top[1] < 0.1:
        return "축 신호 약함 — 중립 상태"

    top_ko = name_map[top[0]]

    if second and second[1] >= top[1] * 0.7:
        second_ko = name_map[second[0]]
        return f"{top_ko}{_josa_wa(top_ko)} {second_ko}{_josa_i(second_ko)} 주축으로 같이 올라온 상태"
    return f"{top_ko}{_josa_i(top_ko)} 지배적"
