"""
6-Axis Domain ISA — 학파 중립 감정 좌표계 (v1.2).

박씨 2026-04-24 로그의 F(꿈) = Grief ∘ Guilt ∘ Eros ∘ Rage 합성함수를
Liberation + Anxiety 로 확장하여 6축 체계.

v1.1 → v1.2 변경:
- Anxiety 축 신설 (성과/압박/불안/수행 실패 주제 포착)
- grief 메타포 확장 (사라지/투명/보이지 않)
- guilt 키워드 확장 (방치/제대로/못 받은/돌봐주지 못)

참조:
- WHITEPAPER-v1.2.md §5
- A Survey of LLMs in Psychotherapy — arxiv 2502.11095
- 박씨 2026-04-24 꿈 로그 + Perplexity 프로토타입 3세트 (2026-04-24 검증)
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
#  A1 · Grief (애도)  — v1.2: 사라짐/투명 메타포 확장
# ─────────────────────────────────────────────────────────────────
class GriefAxis(Axis):
    id = "grief"
    name_ko = "애도"
    keywords = [
        "죽음", "죽는", "돌아가", "상실",
        "떠났", "보냈", "마지막",
        "작별", "이별", "끝",
    ]
    metaphors = [
        "장례", "무덤", "겨울", "저물", "사라", "묘지", "소실",
        "투명해지", "흐릿해지", "보이지 않", "흩어",   # v1.2 추가
    ]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.12
        indirect = self._count(narrative, self.metaphors) * 0.06
        death_markers = ["죽", "장례", "돌아가", "떠났", "보냈"]
        if metadata.get("is_dream") and any(m in narrative for m in death_markers):
            direct += 0.25
        if metadata.get("anniversary_within_30d"):
            direct += 0.15
        return min(direct + indirect, 1.0)


# ─────────────────────────────────────────────────────────────────
#  A2 · Guilt (죄책감)  — v1.2: 방치/돌봄실패 키워드 확장
# ─────────────────────────────────────────────────────────────────
class GuiltAxis(Axis):
    id = "guilt"
    name_ko = "죄책감"
    keywords = [
        "미안", "죄책", "잘못", "책임",
        "빚", "부채", "병신",
        "외면", "배신", "실수",
        "방치", "못 받은", "제대로 못",            # v1.2 추가
        "돌봐주지 못", "챙겨주지 못", "놓쳤",       # v1.2 추가
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
        "따뜻", "만지고", "손을 잡",             # v1.2 추가
    ]
    metaphors = ["봄", "꽃", "빛", "불", "체온", "가슴이 따뜻"]

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
        "화가 난", "그만해",                      # v1.2 추가
    ]
    metaphors = ["불길", "폭발", "칼날", "소리 없는 비명"]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.14
        indirect = self._count(narrative, self.metaphors) * 0.06
        return min(direct + indirect, 1.0)


# ─────────────────────────────────────────────────────────────────
#  A5 · Liberation (해방 · 종료 후 자유)
# ─────────────────────────────────────────────────────────────────
class LiberationAxis(Axis):
    id = "liberation"
    name_ko = "해방"
    keywords = [
        "편하", "가볍", "자유", "해방",
        "놓아", "벗어", "시원",
        "맑", "트인", "열린",
        "끝났", "마무리", "허용",                 # v1.2 추가
    ]
    metaphors = ["아침", "창문", "새소리", "햇빛", "바람"]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.12
        indirect = self._count(narrative, self.metaphors) * 0.08
        return min(direct + indirect, 1.0)


# ─────────────────────────────────────────────────────────────────
#  A6 · Anxiety (불안 · 압박 · 수행 실패)  🆕 v1.2
#  박씨 프로토타입 꿈 2 검증으로 공백 확인 후 신설.
# ─────────────────────────────────────────────────────────────────
class AnxietyAxis(Axis):
    id = "anxiety"
    name_ko = "불안"
    keywords = [
        "불안", "압박", "압박감",
        "준비 안", "준비가 안", "준비 못",
        "끌려", "막막", "떨림",
        "완성도", "미루", "늦을", "늦어",
        "실패", "못 한", "부담",
        "완벽", "부족", "모자라",
    ]
    metaphors = [
        "침묵이 이어", "끝도 없는", "새까만 어둠", "어둠만",
        "엉켜", "엉킨", "흐릿해", "흐릿했",
        "안 보이", "입에서 아무 말도",
        "목소리가 안", "소리 없는",
        "텅 빈", "빈 무대",
    ]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.13
        indirect = self._count(narrative, self.metaphors) * 0.08
        # 꿈 + 수행 실패 메타포 조합 → 강한 anxiety
        perf_markers = ["프레젠테이션", "발표", "무대", "시험", "면접", "마이크"]
        if metadata.get("is_dream") and any(m in narrative for m in perf_markers):
            direct += 0.20
        return min(direct + indirect, 1.0)


ALL_AXES: list[Axis] = [
    GriefAxis(),
    GuiltAxis(),
    ErosAxis(),
    RageAxis(),
    LiberationAxis(),
    AnxietyAxis(),                # 🆕 v1.2
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
    # Self-test (v1.2 6축)
    tests = [
        ("박씨 꿈 (애도)",
         "어머니가 돌아가시는 꿈을 꿨다. 오케스트라 지휘하듯 웃었다. 상가집 가는 길에 병신이라고 욕했다.",
         {"is_dream": True}),
        ("꿈 2 (불안)",
         "무대 뒤 대본 엉켜 있었다 준비 안 된 상태로 끌려나왔다 새까만 어둠 입에서 아무 말도 안 나와 침묵 이어졌다 불안감 압박감 완성도 미루",
         {"is_dream": True}),
        ("꿈 3 (해방+에로스)",
         "낯선 여자와 손을 잡았다 가슴이 따뜻해졌다 허용된 자유 해방감",
         {"is_dream": True}),
    ]
    for label, text, meta in tests:
        d = extract_all(text, meta)
        print(f"\n[{label}]")
        for aid, v in sorted(d.items(), key=lambda x: -x[1]):
            bar = "█" * int(v * 25)
            print(f"  {aid:12s} {v:.3f} {bar}")
        print(f"  → dominant: {dominant_axis(d)}")
