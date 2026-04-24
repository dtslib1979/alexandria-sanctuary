"""
5-Axis Domain ISA — 학파 중립 감정 좌표계.

박씨 2026-04-24 로그의 F(꿈) = Grief ∘ Guilt ∘ Eros ∘ Rage 합성함수를
Liberation 축 추가해서 확장.

참조:
- WHITEPAPER-v1.0.md §5
- A Survey of LLMs in Psychotherapy — arxiv 2502.11095
- 박씨 2026-04-24 꿈 로그 (원천 요구사항)
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class Axis(ABC):
    id: str = ""
    name_ko: str = ""
    keywords: list[str] = []
    metaphors: list[str] = []

    @abstractmethod
    def extract(self, narrative: str, metadata: dict) -> float:
        """이 축의 강도 (0.0 ~ 1.0)."""

    def _count(self, text: str, patterns: list[str]) -> int:
        return sum(1 for p in patterns if p in text)


# ─────────────────────────────────────────────────────────────────
#  A1 · Grief (애도)
# ─────────────────────────────────────────────────────────────────
class GriefAxis(Axis):
    id = "grief"
    name_ko = "애도"
    keywords = [
        "죽음", "죽는", "돌아가", "상실",
        "떠났", "보냈", "마지막",
        "작별", "이별", "끝",
    ]
    metaphors = ["장례", "무덤", "겨울", "저물", "사라", "묘지", "소실"]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.12
        indirect = self._count(narrative, self.metaphors) * 0.06
        # 꿈 + 죽음/이별 조합 → 강한 grief (한국어 완곡어 포함)
        death_markers = ["죽", "장례", "돌아가", "떠났", "보냈"]
        if metadata.get("is_dream") and any(m in narrative for m in death_markers):
            direct += 0.25
        # 1년 기일/애니버서리
        if metadata.get("anniversary_within_30d"):
            direct += 0.15
        return min(direct + indirect, 1.0)


# ─────────────────────────────────────────────────────────────────
#  A2 · Guilt (죄책감)
# ─────────────────────────────────────────────────────────────────
class GuiltAxis(Axis):
    id = "guilt"
    name_ko = "죄책감"
    keywords = [
        "미안", "죄책", "잘못", "책임",
        "빚", "부채", "병신",
        "외면", "배신", "실수",
    ]
    metaphors = ["그림자", "짐", "빚", "오점", "얼룩"]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.13
        indirect = self._count(narrative, self.metaphors) * 0.06
        return min(direct + indirect, 1.0)


# ─────────────────────────────────────────────────────────────────
#  A3 · Eros (삶의 욕구 · 접촉 · 외로움)
# ─────────────────────────────────────────────────────────────────
class ErosAxis(Axis):
    id = "eros"
    name_ko = "삶의 욕구"
    keywords = [
        "외롭", "그립", "사랑",
        "살고 싶", "접촉", "누군가",
        "관계", "업소", "스킨십",
        "따뜻", "만지고",
    ]
    metaphors = ["봄", "꽃", "빛", "불", "체온"]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.12
        indirect = self._count(narrative, self.metaphors) * 0.05
        return min(direct + indirect, 1.0)


# ─────────────────────────────────────────────────────────────────
#  A4 · Rage (분노 · 피로 · 반발)
# ─────────────────────────────────────────────────────────────────
class RageAxis(Axis):
    id = "rage"
    name_ko = "분노"
    keywords = [
        "짜증", "분노", "욕", "씨발",
        "병신", "꺼져", "지긋지긋",
        "불공평", "억울", "치가 떨",
        "화가 난",
    ]
    metaphors = ["불길", "폭발", "칼날"]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.14
        indirect = self._count(narrative, self.metaphors) * 0.06
        return min(direct + indirect, 1.0)


# ─────────────────────────────────────────────────────────────────
#  A5 · Liberation (해방 · 종료 후 자유) 🆕
# ─────────────────────────────────────────────────────────────────
class LiberationAxis(Axis):
    id = "liberation"
    name_ko = "해방"
    keywords = [
        "편하", "가볍", "자유", "해방",
        "놓아", "벗어", "시원",
        "맑", "트인", "열린",
        "끝났", "마무리",
    ]
    metaphors = ["아침", "창문", "새소리", "햇빛", "바람"]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.12
        indirect = self._count(narrative, self.metaphors) * 0.08
        return min(direct + indirect, 1.0)


ALL_AXES: list[Axis] = [
    GriefAxis(),
    GuiltAxis(),
    ErosAxis(),
    RageAxis(),
    LiberationAxis(),
]

AXIS_IDS = [a.id for a in ALL_AXES]


def extract_all(narrative: str, metadata: dict | None = None) -> dict[str, float]:
    """입력에 대해 모든 축의 직접 강도 추출."""
    metadata = metadata or {}
    return {a.id: a.extract(narrative, metadata) for a in ALL_AXES}


def dominant_axis(distribution: dict[str, float]) -> str:
    """가장 강한 축 id 반환. 모두 0이면 'liberation' 기본값."""
    if not distribution or all(v == 0 for v in distribution.values()):
        return "liberation"
    return max(distribution, key=distribution.get)


if __name__ == "__main__":
    # Self-test
    parksy_dream = (
        "어머니가 돌아가시는 꿈을 꿨다. "
        "심폐소생 쇼크 전기 충격기 바이탈 사인 들리며 일어나서 "
        "오케스트라 지휘하듯 웃었다. "
        "상가집 가는 길 모르는 전화에 병신이라고 욕했다."
    )
    parksy_waking = (
        "창문 열어놓고 잤는데 새소리 들리고 햇빛 들어와서 오랜만에 잘 잤다. "
        "마음이 편하다."
    )
    print("박씨 꿈 입력:")
    for aid, v in extract_all(parksy_dream, {"is_dream": True}).items():
        print(f"  {aid}: {v:.3f}")
    print(f"  dominant → {dominant_axis(extract_all(parksy_dream, {'is_dream': True}))}")

    print("\n박씨 기상 입력:")
    for aid, v in extract_all(parksy_waking, {}).items():
        print(f"  {aid}: {v:.3f}")
    print(f"  dominant → {dominant_axis(extract_all(parksy_waking, {}))}")
