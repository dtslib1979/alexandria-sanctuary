"""
AyahuascaPlug (Gate V · Sound & Soul — 식물 영 / 비전)

참조:
- Frontiers in Psychiatry — Ayahuasca research
  https://www.frontiersin.org/search?query=ayahuasca%20psychiatry
- Gabor Maté's integration work

박씨 원칙: 실제 약물 복용 권장 X. 비전/해체-재조립 구조만 레시피로.
"""
from __future__ import annotations

from alex_mcp.plugs.base import Plug


class AyahuascaPlug(Plug):
    name = "ayahuasca"
    gate_id = "V"
    weight_default = 0.06
    keywords_trigger = [
        "비전", "환각", "각성",
        "식물", "정글",
        "해체", "재조립", "자기해체",
        "죽음과_재생",
    ]

    def frame(self, ctx: dict) -> dict:
        return {
            "name": self.name,
            "gate": self.gate_id,
            "lens": "해체-재조립 · 비전 · 식물 영",
            "questions": [
                "자아가 분해-재조립되는 장면이 있는가?",
                "비전 이미지가 trauma 재통합을 의도하는가?",
                "'식물 영'을 무의식/Self로 번역하면 어떻게 읽히는가?",
            ],
            "cautions": [
                "실제 약물 의례 권장 절대 금지",
                "비전 내용을 객관 사실로 취급 말 것",
                "'치유되었다' 단정 금지",
            ],
            "parksy_specific": {
                "박씨_적용도_낮음": "박씨 로그에 아야와스카 직접 경험 없음 — 은유 차용만",
            },
        }
