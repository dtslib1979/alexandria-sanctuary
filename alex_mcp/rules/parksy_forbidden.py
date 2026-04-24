"""
박씨 금기 — 박씨가 명시적으로 거부한 표현 패턴.

소스: 박씨 5808줄 로그 + 5-Lane 세션 피드백
추출 근거:
- #7 "샤먼 흉내" "장사해 먹는"
- #8 "시간 낭비" "답이라고 받을 게"
- #14 "병신 같은 무당"
- #15 "레시피가 아니라 레퍼런스"
- #17 "저 새끼들은 AI를 사용해서 쓸 수가 없을 거 아니에요"
- #18 "표준화 못 한다 = 자기도 모른다"
"""
from __future__ import annotations

import re
from dataclasses import dataclass


# ─────────────────────────────────────────────────────────────────
#  CATEGORY 1: 존댓말 (박씨 발화엔 0건)
# ─────────────────────────────────────────────────────────────────
FORBIDDEN_HONORIFICS = [
    r"\S+습니다\b",
    r"\S+입니다\b",
    r"\S+합니다\b",
    r"\S+됩니다\b",
    r"\S+세요\b",
    r"\S+주십시오\b",
    r"드리겠\S*",
    r"양해\s*바랍",
    r"감사합",
]


# ─────────────────────────────────────────────────────────────────
#  CATEGORY 2: 과한 공감 (B급 상담사 패턴)
#  박씨 #22: "답이라고 받을 게 이 융이라고 하는 사람 해석 같은 거"
# ─────────────────────────────────────────────────────────────────
FORBIDDEN_OVERSYMPATHY = [
    r"많이\s*힘드시",
    r"이해\s*합",
    r"공감\s*합",
    r"마음이\s*아프",
    r"잘\s*하고\s*계세",
    r"응원합",
    r"위로\S*\s*드립",
    r"당신은\s*잘못이\s*없",
]


# ─────────────────────────────────────────────────────────────────
#  CATEGORY 3: 의료/진단 단정 (법적 리스크 + 박씨 금기)
#  박씨 백서 §2.2 OUT-OF-SCOPE: "진료/처방"
# ─────────────────────────────────────────────────────────────────
FORBIDDEN_MEDICAL = [
    r"(우울증|조현병|PTSD|양극성|불안장애|공황장애|강박장애|경계성)(이|가)?\s*입니다",
    r"(우울증|조현병|PTSD)\s*로\s*보입",
    r"진단을?\s*받으",
    r"약을?\s*(복용|드세요|드셔야|처방)",
    r"병원에?\s*가셔야",
    r"정신과\s*치료\s*(받으|시작)",
    r"상담을?\s*받으셔야\s*한",
]


# ─────────────────────────────────────────────────────────────────
#  CATEGORY 4: 강제형/단정 예언
#  박씨 #15: "레시피가 아니라 레퍼런스로"
# ─────────────────────────────────────────────────────────────────
FORBIDDEN_IMPERATIVE = [
    r"반드시\s*\S+해야",
    r"절대\s*\S+하지\s*마",
    r"꼭\s*\S+해야",
    r"무조건\s*\S+",
    r"당신은\s*반드시",
    r"이것만\s*하면\s*됩",
    r"정답은\s*하나",
]


# ─────────────────────────────────────────────────────────────────
#  CATEGORY 5: 권위 팔이 (박씨가 제일 싫어하는 패턴)
#  박씨 #7: "이 사람도 샤먼 흉내에는 학자"
#  박씨 #8: "씨발 학위 앵무새들"
#  박씨 #22: "융이라고 하는 사람 해석 같은 거"
# ─────────────────────────────────────────────────────────────────
FORBIDDEN_AUTHORITY_APPEAL = [
    r"학계에서는\s*\S+\s*라고",
    r"전문가들은\s*\S+\s*라고",
    r"\S+\s*박사가\s*말하",
    r"\S+\s*교수가\s*주장",
    r"연구\s*결과에?\s*따르면",   # 단, 구체적 인용 있으면 OK — 패턴만 반복되면 차단
]


# ─────────────────────────────────────────────────────────────────
#  CATEGORY 6: 완벽주의/허세 문구
#  박씨 자기평가 반복 "9.6" 과장 반성 후
# ─────────────────────────────────────────────────────────────────
FORBIDDEN_PERFECTION = [
    r"완벽한\s*\S+",
    r"완성형\s*",
    r"최고의\s*\S+",
    r"궁극의\s*",
    r"만점",
    r"100\s*점",
]


# ─────────────────────────────────────────────────────────────────
#  CATEGORY 7: 샤먼/무당 권위 (박씨 명시 금지)
#  박씨 #17, #20
# ─────────────────────────────────────────────────────────────────
FORBIDDEN_MYSTIC_AUTHORITY = [
    r"조상이\s*(노했|화나셨|도우셨)",
    r"터가\s*안\s*좋",
    r"영매가\s*말하",
    r"귀신이\s*붙",
    r"신령\S*\s*말씀",
]


ALL_CATEGORIES: dict[str, list[str]] = {
    "honorifics": FORBIDDEN_HONORIFICS,
    "oversympathy": FORBIDDEN_OVERSYMPATHY,
    "medical": FORBIDDEN_MEDICAL,
    "imperative": FORBIDDEN_IMPERATIVE,
    "authority_appeal": FORBIDDEN_AUTHORITY_APPEAL,
    "perfection": FORBIDDEN_PERFECTION,
    "mystic_authority": FORBIDDEN_MYSTIC_AUTHORITY,
}


@dataclass
class ForbiddenMatch:
    category: str
    pattern: str
    matched_text: str
    position: int


def scan(text: str) -> list[ForbiddenMatch]:
    """LLM 출력에서 모든 금기 매치 찾기."""
    matches: list[ForbiddenMatch] = []
    for category, patterns in ALL_CATEGORIES.items():
        for pat in patterns:
            for m in re.finditer(pat, text):
                matches.append(ForbiddenMatch(
                    category=category,
                    pattern=pat,
                    matched_text=m.group(0),
                    position=m.start(),
                ))
    return matches


def has_critical_forbidden(text: str) -> bool:
    """치명적 금기 (medical) 하나라도 있으면 True → 전면 차단."""
    for pat in FORBIDDEN_MEDICAL:
        if re.search(pat, text):
            return True
    return False
