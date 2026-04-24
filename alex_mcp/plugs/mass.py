"""
MassProtocolPlug (Gate III/VII · 천주교 미사 6단계)

본 엔진의 이론적 앵커. 박씨 2026-04-24 로그 도달 결론:
"미사 = 1000년 임상 완료된 표준화 샤먼 OS. 샤먼 자동화 불가 명제의 반례."

참조:
- 한국 천주교 주교회의 — https://cbck.or.kr/
- Missale Romanum (로마 미사경본) 공식 전례 순서
- Ritual and Mental Health (PMC5954391)
"""
from __future__ import annotations

from alex_mcp.plugs.base import Plug


SIX_STAGES = [
    {
        "stage": 1,
        "name": "입당 (Introit)",
        "kr": "공간 진입",
        "mcp_action": "session_start",
        "parksy_action": "로그 수집 시작",
    },
    {
        "stage": 2,
        "name": "말씀 전례 (Liturgy of the Word)",
        "kr": "상황 서술·듣기",
        "mcp_action": "analyze_narrative",
        "parksy_action": "꿈/사건 서술",
    },
    {
        "stage": 3,
        "name": "복음/강론 (Homily)",
        "kr": "해석·인도",
        "mcp_action": "plug_weighted_report",
        "parksy_action": "리포트 수신",
    },
    {
        "stage": 4,
        "name": "봉헌 (Offertory)",
        "kr": "선택·수용",
        "mcp_action": "user_curation",
        "parksy_action": "받을 해석 큐레이션",
    },
    {
        "stage": 5,
        "name": "성체성사 (Eucharist)",
        "kr": "의례 실행",
        "mcp_action": "propose_ritual",
        "parksy_action": "방 정리/글쓰기/산책",
    },
    {
        "stage": 6,
        "name": "파견 (Ite, missa est)",
        "kr": "일상 복귀",
        "mcp_action": "session_end",
        "parksy_action": "다음 트리거까지 종료",
    },
]


class MassProtocolPlug(Plug):
    name = "mass_protocol"
    gate_id = "III"
    secondary_gate_id = "VII"
    weight_default = 0.08
    keywords_trigger = [
        "미사", "고해", "전례", "파견",
        "공동체", "용서", "구원",
        "봉헌", "성체", "화해",
        "의례", "리추얼", "루틴",
    ]

    def score(self, ctx: dict) -> float:
        base = super().score(ctx)
        narrative = ctx.get("narrative", "") or ""
        if "파견" in narrative or "마무리" in narrative or "일상 복귀" in narrative:
            base += 0.15
        return min(base, 0.55)

    def frame(self, ctx: dict) -> dict:
        return {
            "name": self.name,
            "gate": self.gate_id,
            "secondary_gate": self.secondary_gate_id,
            "lens": "1000년 임상 통과된 표준화 의례 프로토콜",
            "six_stages": SIX_STAGES,
            "questions": [
                "현재 세션이 6단계 중 어느 지점인가?",
                "파견(stage 6) 준비가 되었는가, 아직 봉헌(4) 직전인가?",
                "다음 stage로 넘어갈 신호가 있는가?",
            ],
            "cautions": [
                "종교 강요 금지 — 프로토콜로만 차용",
                "propose_ritual 은 Stage 5 에서만 트리거",
            ],
            "parksy_specific": {
                "박씨_도달_결론": "샤먼 자동화 불가 명제의 반례",
                "본_엔진_사용법": "propose_ritual 호출 시 기본 템플릿",
                "매_세션_구조": "입당 → 말씀 → 강론 → 봉헌 → 성체 → 파견",
            },
        }
