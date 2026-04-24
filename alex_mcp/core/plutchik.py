"""
Plutchik's Wheel of Emotions — 8 기본 감정 + 3-level 강도 + 24 dyad + 대립쌍.

Robert Plutchik (1980) Psychoevolutionary theory of emotion.
심리학 교과서 표준 감정 분류 모델.

8 기본 감정 (4 대립쌍):
  Joy      ↔ Sadness
  Trust    ↔ Disgust
  Fear     ↔ Anger
  Surprise ↔ Anticipation

강도 3-level:
  Joy:          ecstasy / joy / serenity
  Trust:        admiration / trust / acceptance
  Fear:         terror / fear / apprehension
  Surprise:     amazement / surprise / distraction
  Sadness:      grief / sadness / pensiveness
  Disgust:      loathing / disgust / boredom
  Anger:        rage / anger / annoyance
  Anticipation: vigilance / anticipation / interest

Dyad (혼합 감정, 3단계):
  1차 (인접): Joy+Trust=Love 등 8개
  2차 (건너): Joy+Fear=Guilt 등 8개
  3차 (대각선): Joy+Surprise=Delight 등 8개

대립쌍 동시 활성화 = 양가감정(ambivalence).
박씨 2026-04-24 꿈의 "애도+기쁨 공존"이 여기 해당.

참조:
- Plutchik, R. (1980). Emotion: A psychoevolutionary synthesis.
- Wikipedia: https://en.wikipedia.org/wiki/Robert_Plutchik
"""
from __future__ import annotations

from abc import ABC, abstractmethod


# ═══════════════════════════════════════════════════════════════
#  8 기본 감정 기반 클래스
# ═══════════════════════════════════════════════════════════════
class Emotion(ABC):
    id: str = ""
    name_ko: str = ""
    level_labels: dict[str, str] = {}   # {"high": "ecstasy", "mid": "joy", "low": "serenity"}
    keywords: list[str] = []
    metaphors: list[str] = []

    @abstractmethod
    def extract(self, narrative: str, metadata: dict) -> float:
        """감정 강도 0.0 ~ 1.0."""

    def _count(self, text: str, patterns: list[str]) -> int:
        return sum(1 for p in patterns if p in text)

    def intensity_label(self, score: float) -> str:
        """점수 → 3-level 라벨."""
        if score >= 0.7:
            return self.level_labels.get("high", self.id)
        if score >= 0.3:
            return self.level_labels.get("mid", self.id)
        return self.level_labels.get("low", self.id)


# ═══════════════════════════════════════════════════════════════
#  Joy (기쁨) ↔ Sadness (슬픔) 축
# ═══════════════════════════════════════════════════════════════
class Joy(Emotion):
    id = "joy"
    name_ko = "기쁨"
    level_labels = {"high": "ecstasy", "mid": "joy", "low": "serenity"}
    keywords = [
        "기쁨", "기뻤", "기쁜", "기쁘",       # "기쁘고" 커버
        "즐거움", "즐거웠", "즐거운", "즐거",
        "웃음", "웃었", "웃으며", "웃으면서", "웃는",
        "행복", "설렘", "벅참", "반짝",
        "짜릿", "기분 좋", "기분이 좋",
    ]
    metaphors = ["햇빛", "꽃", "불빛"]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.14
        indirect = self._count(narrative, self.metaphors) * 0.06
        return min(direct + indirect, 1.0)


class Sadness(Emotion):
    id = "sadness"
    name_ko = "슬픔"
    level_labels = {"high": "grief", "mid": "sadness", "low": "pensiveness"}
    keywords = [
        "슬픔", "슬펐", "슬픈",
        "눈물", "울었", "울음",
        "외로", "쓸쓸", "그리움",
        "상실", "떠났", "돌아가", "보냈",
        "잃었", "허전",
    ]
    metaphors = ["비", "저녁", "잿빛", "어스름", "장례", "무덤"]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.13
        indirect = self._count(narrative, self.metaphors) * 0.06
        if metadata.get("is_dream") and any(m in narrative for m in ["죽", "장례", "돌아가"]):
            direct += 0.20
        return min(direct + indirect, 1.0)


# ═══════════════════════════════════════════════════════════════
#  Trust (신뢰) ↔ Disgust (혐오) 축
# ═══════════════════════════════════════════════════════════════
class Trust(Emotion):
    id = "trust"
    name_ko = "신뢰"
    level_labels = {"high": "admiration", "mid": "trust", "low": "acceptance"}
    keywords = [
        "믿음", "믿었", "믿고",
        "의지", "의지하", "기대서",
        "편안", "편한", "편한 느낌", "안심", "안전",
        "안기", "기대어", "품",
        "따뜻한 사람", "따뜻한 손", "온기",
        "손을 잡", "손잡",                 # 애착 접촉
    ]
    metaphors = ["엄마 품", "손길", "체온이 느껴"]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.13
        indirect = self._count(narrative, self.metaphors) * 0.08
        return min(direct + indirect, 1.0)


class Disgust(Emotion):
    id = "disgust"
    name_ko = "혐오"
    level_labels = {"high": "loathing", "mid": "disgust", "low": "boredom"}
    keywords = [
        "혐오", "역겹", "역겨", "더럽",
        "지긋지긋", "구역", "토할",
        "넌더리", "꼴보기 싫", "꼴 보기",
        "지겨", "싫증",
    ]
    metaphors = ["쓰레기", "오물", "썩은"]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.14
        indirect = self._count(narrative, self.metaphors) * 0.06
        return min(direct + indirect, 1.0)


# ═══════════════════════════════════════════════════════════════
#  Fear (공포) ↔ Anger (분노) 축
# ═══════════════════════════════════════════════════════════════
class Fear(Emotion):
    id = "fear"
    name_ko = "공포"
    level_labels = {"high": "terror", "mid": "fear", "low": "apprehension"}
    keywords = [
        "공포", "무서웠", "무서운",
        "두려움", "두려웠", "두려운",
        "겁", "겁나", "떨림", "떨렸",
        "불안", "불안감", "압박감",
        "위험", "도망", "피하",
        "긴장",
    ]
    metaphors = [
        "새까만 어둠", "어둠 속", "쫓기",
        "목소리가 안", "입에서 아무 말",
        "침묵이 이어", "끝도 없는",
    ]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.12
        indirect = self._count(narrative, self.metaphors) * 0.08
        # 수행/발표 상황 꿈
        if metadata.get("is_dream"):
            perf = ["무대", "발표", "프레젠테이션", "시험", "면접"]
            if any(p in narrative for p in perf):
                direct += 0.18
        return min(direct + indirect, 1.0)


class Anger(Emotion):
    id = "anger"
    name_ko = "분노"
    level_labels = {"high": "rage", "mid": "anger", "low": "annoyance"}
    keywords = [
        "분노", "화가 난", "화가 나",
        "짜증", "짜증 나",
        "욕", "씨발", "병신", "꺼져",
        "억울", "치가 떨",
        "그만해", "분해",
    ]
    metaphors = ["불길", "폭발", "칼날", "소리 없는 비명"]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.14
        indirect = self._count(narrative, self.metaphors) * 0.06
        return min(direct + indirect, 1.0)


# ═══════════════════════════════════════════════════════════════
#  Surprise (놀람) ↔ Anticipation (기대) 축
# ═══════════════════════════════════════════════════════════════
class Surprise(Emotion):
    id = "surprise"
    name_ko = "놀람"
    level_labels = {"high": "amazement", "mid": "surprise", "low": "distraction"}
    keywords = [
        "놀람", "놀랐", "놀라운",
        "갑자기", "별안간", "뜬금없이",
        "예상 밖", "뜻밖", "황당",
        "깜짝",
    ]
    metaphors = ["번쩍", "휘릭", "순식간"]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.13
        indirect = self._count(narrative, self.metaphors) * 0.06
        return min(direct + indirect, 1.0)


class Anticipation(Emotion):
    id = "anticipation"
    name_ko = "기대"
    level_labels = {"high": "vigilance", "mid": "anticipation", "low": "interest"}
    keywords = [
        "기대", "설레", "기다렸", "기다리",
        "예감", "희망",
        "앞으로", "다가올", "곧",
        "준비하", "준비 안",
    ]
    metaphors = ["새벽", "씨앗", "곧 올"]

    def extract(self, narrative, metadata):
        direct = self._count(narrative, self.keywords) * 0.12
        indirect = self._count(narrative, self.metaphors) * 0.06
        return min(direct + indirect, 1.0)


# ═══════════════════════════════════════════════════════════════
#  레지스트리
# ═══════════════════════════════════════════════════════════════
ALL_EMOTIONS: list[Emotion] = [
    Joy(), Trust(), Fear(), Surprise(),
    Sadness(), Disgust(), Anger(), Anticipation(),
]

EMOTION_IDS = [e.id for e in ALL_EMOTIONS]


# 대립쌍 (Plutchik 4 polar pairs)
POLAR_PAIRS: list[tuple[str, str]] = [
    ("joy", "sadness"),
    ("trust", "disgust"),
    ("fear", "anger"),
    ("surprise", "anticipation"),
]


# ═══════════════════════════════════════════════════════════════
#  Dyad 테이블 (혼합 감정)
#  (감정A, 감정B, 거리, 혼합 감정명)
#  거리: 1=인접(primary), 2=건너(secondary), 3=대각선(tertiary)
# ═══════════════════════════════════════════════════════════════
DYADS: list[tuple[str, str, int, str, str]] = [
    # (emotion_a, emotion_b, distance, english, korean)
    # Primary dyads (인접)
    ("joy", "trust",          1, "Love", "사랑"),
    ("trust", "fear",         1, "Submission", "복종"),
    ("fear", "surprise",      1, "Awe", "경외"),
    ("surprise", "sadness",   1, "Disapproval", "실망"),
    ("sadness", "disgust",    1, "Remorse", "후회"),
    ("disgust", "anger",      1, "Contempt", "경멸"),
    ("anger", "anticipation", 1, "Aggressiveness", "공격성"),
    ("anticipation", "joy",   1, "Optimism", "낙관"),
    # Secondary dyads (한 칸 건넌)
    ("joy", "fear",           2, "Guilt", "죄책감"),
    ("trust", "surprise",     2, "Curiosity", "호기심"),
    ("fear", "sadness",       2, "Despair", "절망"),
    ("surprise", "disgust",   2, "Unbelief", "불신"),
    ("sadness", "anger",      2, "Envy", "시기"),
    ("disgust", "anticipation", 2, "Cynicism", "냉소"),
    ("anger", "joy",          2, "Pride", "자부"),
    ("anticipation", "trust", 2, "Hope", "희망"),
    # Tertiary dyads (대각선)
    ("joy", "surprise",       3, "Delight", "환희"),
    ("trust", "sadness",      3, "Sentimentality", "감상"),
    ("fear", "disgust",       3, "Shame", "수치"),
    ("surprise", "anger",     3, "Outrage", "격분"),
    ("sadness", "anticipation", 3, "Pessimism", "비관"),
    ("disgust", "joy",        3, "Morbidness", "병적 쾌락"),
    ("anger", "trust",        3, "Dominance", "지배"),
    ("anticipation", "fear",  3, "Anxiety", "불안"),
]


def _dyad_lookup(a: str, b: str) -> tuple[str, str, int] | None:
    """a,b 쌍의 dyad 반환. 없으면 None (대립쌍은 dyad 없음)."""
    for ea, eb, dist, en, ko in DYADS:
        if {ea, eb} == {a, b}:
            return (en, ko, dist)
    return None


# ═══════════════════════════════════════════════════════════════
#  메인 API
# ═══════════════════════════════════════════════════════════════
def extract_all(narrative: str, metadata: dict | None = None) -> dict[str, float]:
    """8 감정 강도 추출."""
    metadata = metadata or {}
    return {e.id: e.extract(narrative, metadata) for e in ALL_EMOTIONS}


def dominant_emotion(dist: dict[str, float]) -> str:
    if not dist or all(v == 0 for v in dist.values()):
        return "trust"
    return max(dist, key=dist.get)


def detect_dyads(dist: dict[str, float], threshold: float = 0.15) -> list[dict]:
    """
    강한 감정 쌍에서 공식 dyad 찾기.
    threshold 이상인 감정 2개 이상 조합.
    """
    strong = sorted(
        [(eid, v) for eid, v in dist.items() if v >= threshold],
        key=lambda x: -x[1],
    )
    found = []
    for i, (a_id, a_v) in enumerate(strong):
        for b_id, b_v in strong[i + 1:]:
            dyad = _dyad_lookup(a_id, b_id)
            if dyad:
                en, ko, dist_level = dyad
                found.append({
                    "emotions": [a_id, b_id],
                    "english": en,
                    "korean": ko,
                    "distance": dist_level,
                    "strength": round((a_v + b_v) / 2, 3),
                })
    return sorted(found, key=lambda x: -x["strength"])


def detect_ambivalence(dist: dict[str, float], threshold: float = 0.15) -> list[dict]:
    """
    대립쌍이 동시에 강한 경우 = 양가 감정.
    박씨 2026-04-24 "애도+기쁨 공존"이 여기 해당.
    """
    found = []
    for a, b in POLAR_PAIRS:
        if dist.get(a, 0) >= threshold and dist.get(b, 0) >= threshold:
            found.append({
                "polar_pair": [a, b],
                "label_ko": f"{_emotion_ko(a)} ↔ {_emotion_ko(b)} 양가",
                "strength": round((dist[a] + dist[b]) / 2, 3),
            })
    return sorted(found, key=lambda x: -x["strength"])


def _emotion_ko(eid: str) -> str:
    for e in ALL_EMOTIONS:
        if e.id == eid:
            return e.name_ko
    return eid


def emotion_profile(narrative: str, metadata: dict | None = None) -> dict:
    """
    8 기본 감정 + dyad + ambivalence 통합 프로파일.
    """
    dist = extract_all(narrative, metadata)
    return {
        "emotion_levels": {eid: round(v, 3) for eid, v in dist.items()},
        "dominant_emotion": dominant_emotion(dist),
        "intensity_label": _top_intensity_label(dist),
        "dyads": detect_dyads(dist),
        "ambivalence": detect_ambivalence(dist),
    }


def _top_intensity_label(dist: dict[str, float]) -> str:
    """최강 감정의 3-level 라벨."""
    dom = dominant_emotion(dist)
    score = dist.get(dom, 0)
    for e in ALL_EMOTIONS:
        if e.id == dom:
            return e.intensity_label(score)
    return dom


if __name__ == "__main__":
    # Self-test — 박씨 꿈 3세트
    cases = [
        ("박씨 2026-04-24 꿈",
         "어머니가 돌아가시는 꿈 갑자기 일어나 오케스트라 지휘하며 웃으며 상가집 가는 길 병신이라고 욕",
         {"is_dream": True}),
        ("꿈 2 (일/불안)",
         "무대 뒤 대본 엉켜 1분 남았다 새까만 어둠 입에서 아무 말도 안 나와 침묵 이어 불안감 압박",
         {"is_dream": True}),
        ("꿈 3 (에로스/해방)",
         "낯선 편안한 느낌의 사람 손을 잡고 따뜻 해방감 기다렸",
         {"is_dream": True}),
    ]

    for label, text, meta in cases:
        p = emotion_profile(text, meta)
        print(f"\n[{label}]")
        for eid, v in sorted(p["emotion_levels"].items(), key=lambda x: -x[1]):
            bar = "█" * int(v * 20)
            print(f"  {eid:13s} {v:.3f} {bar}")
        print(f"  dominant: {p['dominant_emotion']} ({p['intensity_label']})")
        if p["dyads"]:
            print(f"  dyads:")
            for d in p["dyads"][:3]:
                print(f"    {d['english']}({d['korean']}) = {d['emotions']}, dist={d['distance']}, str={d['strength']}")
        if p["ambivalence"]:
            print(f"  ambivalence:")
            for a in p["ambivalence"]:
                print(f"    {a['label_ko']} (str={a['strength']})")
