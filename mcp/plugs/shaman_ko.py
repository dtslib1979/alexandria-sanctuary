"""
ShamanKoPlug (Gate V · Sound & Soul — 한국 무속 레이어)

참조:
- 한국무속학회 아카이브 (KISS)
- Minato et al. — East Asian folk healing vs psychiatry
  https://minato.sip21c.org/

박씨 원칙: "무당은 자동화 불가능 = 장사 모델". 레시피로 차용하되 신봉 X.
"""
from __future__ import annotations

from mcp.plugs.base import Plug


class ShamanKoPlug(Plug):
    name = "shaman_ko"
    gate_id = "V"
    weight_default = 0.08
    keywords_trigger = [
        "제사", "묘소", "조상", "터",
        "한", "恨", "굿", "영매",
        "귀신", "넋", "혼", "기일",
        "당집", "산신", "해원",
    ]

    def frame(self, ctx: dict) -> dict:
        return {
            "name": self.name,
            "gate": self.gate_id,
            "lens": "한(恨) · 조상 · 터 · 해원",
            "questions": [
                "집안 내력이나 터와 연결된 반복 패턴인가?",
                "풀지 못한 한이 누구의 것인가?",
                "꿈의 인물이 조상적 상징으로 기능하는가?",
            ],
            "cautions": [
                "'조상이 도우신다/화나셨다' 류 미신 해석 금지",
                "패턴 데이터로만 차용, 신봉 X",
                "박씨 원칙: 레시피 아니라 레퍼런스",
            ],
            "parksy_specific": {
                "40년_간병": "한(恨)의 물리적 침전",
                "3-13_기일적_중첩": "돌봄 OS 종료일 = 개인 해원 의례",
            },
        }
