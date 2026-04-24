"""
AxesWeighter — plug × axis 매트릭스.

각 플러그가 각 축에 대해 고유 해석 가중치를 가진다.
학파별 편향을 코드로 명시.

참조: WHITEPAPER-v1.0.md §5.3, 부록 C
"""
from __future__ import annotations

from mcp.core.axes import ALL_AXES, AXIS_IDS, extract_all


# ─────────────────────────────────────────────────────────────────
#  PLUG_AXIS_MATRIX
#  rows = plugs, cols = axes
#  각 row 합 = 1.0 (정규화)
# ─────────────────────────────────────────────────────────────────
PLUG_AXIS_MATRIX: dict[str, dict[str, float]] = {
    # Freud: 죄책감/초자아 강조, 해방 약함
    "freud":          {"grief": 0.25, "guilt": 0.35, "eros": 0.25, "rage": 0.10, "liberation": 0.05},
    # Jung: 통합/개성화 = 해방 지배
    "jung":           {"grief": 0.20, "guilt": 0.10, "eros": 0.15, "rage": 0.05, "liberation": 0.50},
    # Family Systems: 죄책감 + 해방 (분화) 양쪽
    "family_systems": {"grief": 0.15, "guilt": 0.30, "eros": 0.05, "rage": 0.20, "liberation": 0.30},
    # Shaman_ko: 한 = grief 압도
    "shaman_ko":      {"grief": 0.40, "guilt": 0.20, "eros": 0.05, "rage": 0.15, "liberation": 0.20},
    # Sufi: 비움 = 해방 극대
    "sufi":           {"grief": 0.10, "guilt": 0.10, "eros": 0.15, "rage": 0.05, "liberation": 0.60},
    # Ayahuasca: 해체-재조립 = 해방
    "ayahuasca":      {"grief": 0.15, "guilt": 0.10, "eros": 0.20, "rage": 0.15, "liberation": 0.40},
    # Mass: 고해(guilt) → 파견(liberation)
    "mass_protocol":  {"grief": 0.25, "guilt": 0.30, "eros": 0.05, "rage": 0.05, "liberation": 0.35},
    # Env Trigger: 장소-기억 = grief/liberation 양쪽
    "env_trigger":    {"grief": 0.30, "guilt": 0.15, "eros": 0.10, "rage": 0.10, "liberation": 0.35},
    # Narrative Meta: 균등 (분석 자체는 축 중립)
    "narrative_meta": {"grief": 0.20, "guilt": 0.20, "eros": 0.20, "rage": 0.20, "liberation": 0.20},
    # Parksy Profile: 톤만 — 축 중립
    "parksy_profile": {"grief": 0.20, "guilt": 0.20, "eros": 0.20, "rage": 0.20, "liberation": 0.20},
    # Guardrail: 시스템 — 축 중립
    "guardrail":      {"grief": 0.20, "guilt": 0.20, "eros": 0.20, "rage": 0.20, "liberation": 0.20},
}

# 직접 추출 vs 간접 기여 혼합 비율 (WHITEPAPER §5.3)
DIRECT_BLEND = 0.6
INDIRECT_BLEND = 0.4


def axis_distribution(
    plug_weights: dict[str, float],
    narrative: str,
    metadata: dict | None = None,
) -> dict[str, float]:
    """
    최종 축 분포 계산.

    1. 직접 추출 (axes.extract)
    2. 간접 기여 (plug weight × PLUG_AXIS_MATRIX)
    3. 혼합 (0.6 : 0.4)
    """
    metadata = metadata or {}

    # 1. 직접
    direct = extract_all(narrative, metadata)

    # 2. 간접
    indirect = {aid: 0.0 for aid in AXIS_IDS}
    for plug_name, pw in plug_weights.items():
        row = PLUG_AXIS_MATRIX.get(plug_name)
        if row is None:
            continue
        for aid, aw in row.items():
            indirect[aid] += pw * aw

    # 3. 혼합 + 정규화 (각 축을 [0, 1] 클램프)
    combined = {
        aid: min(DIRECT_BLEND * direct[aid] + INDIRECT_BLEND * indirect[aid], 1.0)
        for aid in AXIS_IDS
    }
    return combined


def dominant_axis(distribution: dict[str, float]) -> str:
    if not distribution:
        return "liberation"
    return max(distribution, key=distribution.get)


def _josa_wa(word: str) -> str:
    """종성에 따라 '와/과' 자동 선택."""
    if not word:
        return "와"
    last = word[-1]
    if not ('가' <= last <= '힣'):
        return "와"
    has_jongseong = (ord(last) - ord('가')) % 28 != 0
    return "과" if has_jongseong else "와"


def _josa_i(word: str) -> str:
    """종성에 따라 '이/가' 자동 선택."""
    if not word:
        return "이"
    last = word[-1]
    if not ('가' <= last <= '힣'):
        return "이"
    has_jongseong = (ord(last) - ord('가')) % 28 != 0
    return "이" if has_jongseong else "가"


def axis_narrative(distribution: dict[str, float]) -> str:
    """
    축 분포를 한 줄 한국어 요약으로.
    예: "애도와 해방감이 주축으로 같이 올라온 상태"
    """
    sorted_axes = sorted(distribution.items(), key=lambda x: -x[1])
    top = sorted_axes[0]
    second = sorted_axes[1] if len(sorted_axes) > 1 else None

    name_map = {
        "grief": "애도",
        "guilt": "죄책감",
        "eros": "삶의 욕구",
        "rage": "분노",
        "liberation": "해방감",
    }

    if top[1] < 0.1:
        return "축 신호 약함 — 중립 상태"

    top_ko = name_map[top[0]]

    if second and second[1] >= top[1] * 0.7:
        second_ko = name_map[second[0]]
        return f"{top_ko}{_josa_wa(top_ko)} {second_ko}{_josa_i(second_ko)} 주축으로 같이 올라온 상태"
    return f"{top_ko}{_josa_i(top_ko)} 지배적"
