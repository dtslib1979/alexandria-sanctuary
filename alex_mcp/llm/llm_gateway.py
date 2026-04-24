"""
LLM Gateway — Claude Code(주) / Claude API(옵션).

박씨 Max 구독 환경:
- Claude Code가 MCP 도구 호출할 때 본인이 LLM이라 외부 API 불필요
- 박씨가 Claude Code 대화에서 꿈 서술 → Claude Code가 내부 해석 → analyze_dream 호출
- analyze_dream 은 rules/ 강제 통과 담당

옵션 (스크립트 단독 실행, 배치용):
- ANTHROPIC_API_KEY 가 있으면 call_llm_direct() 로 직접 호출 가능
- 없으면 이 게이트웨이는 시스템 프롬프트/스키마만 제공
"""
from __future__ import annotations

import os
from typing import Optional

from alex_mcp.plugs import ALL_PLUGS


# ─────────────────────────────────────────────────────────────────
#  Claude Code / Claude API 공용 시스템 프롬프트
#  (박씨 11 플러그 frame() 내용을 주입)
# ─────────────────────────────────────────────────────────────────

def build_system_prompt() -> str:
    """11 플러그 frame() 내용을 LLM 시스템 프롬프트로 조립."""
    lens_sections: list[str] = []
    directives: list[str] = []
    forbiddens: set[str] = set()

    ctx = {"narrative": "", "metadata": {}}
    for plug in ALL_PLUGS:
        f = plug.frame(ctx)
        lens = f.get("lens")
        if lens and f.get("gate"):
            lens_sections.append(f"- {f['name']} (Gate {f['gate']}): {lens}")
        if f.get("directive"):
            directives.append(f["directive"])
        fb = f.get("forbidden") or f.get("forbidden_phrasings") or []
        if isinstance(fb, list):
            forbiddens.update(fb)
        elif isinstance(fb, str):
            forbiddens.add(fb)

    return f"""당신은 정신분석 꿈 해석 보조 AI (Alexandria MCP-Therapy Engine 전단부).

## 역할
사용자(박씨)의 꿈/서사 입력을 받아:
1. 필요시 web_search 로 Freud/Jung/Plutchik 관련 학술자료 검색 (최대 5건)
2. 검색 기반 1차 자연어 해석 생성 (600자 이내)
3. 인용 출처 3건 이상 명시

## 톤 규칙 (강제)
{chr(10).join('- ' + d for d in directives)}

## 학파 렌즈 (이 관점들로 조명)
{chr(10).join(lens_sections)}

## 금지 표현 (출력에 절대 포함 금지)
{chr(10).join('- ' + f for f in sorted(forbiddens))}

## 출력 JSON
{{
  "interpretation": "600자 이내 자연어 해석",
  "citations": [
    {{"title": "...", "url": "...", "school": "freud|jung|plutchik|shaman|mass|기타"}}
  ],
  "dominant_themes": ["주제1", "주제2", "주제3"]
}}

## 주의
- 이 엔진은 의료가 아닌 **레퍼런스**. 진단/처방 금지.
- 판단 강요 금지. 마지막은 박씨가 결정.
- 출처 없는 권위 호소 금지 ('학계에서는', '전문가들은').
"""


# ─────────────────────────────────────────────────────────────────
#  옵션: Claude API 직접 호출 (ANTHROPIC_API_KEY 있을 때)
# ─────────────────────────────────────────────────────────────────

def is_api_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def call_llm_direct(narrative: str, metadata: Optional[dict] = None) -> dict:
    """
    Claude API 직접 호출 (옵션, ANTHROPIC_API_KEY 필요).

    Raises:
        RuntimeError: API key 없을 때
    """
    if not is_api_available():
        raise RuntimeError(
            "ANTHROPIC_API_KEY 없음. Claude Code 클라이언트 경로를 사용하거나 "
            "~/dtslib-papyrus/.env 에 key 추가."
        )

    try:
        import anthropic
    except ImportError as e:
        raise RuntimeError("anthropic SDK 설치 필요: pip install anthropic") from e

    import json as _json

    client = anthropic.Anthropic()
    metadata = metadata or {}

    user_msg = f"꿈/서사 서술:\n\n{narrative}"
    if metadata.get("is_dream"):
        user_msg += "\n\n(이건 꿈이다)"

    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}]

    resp = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        tools=tools,
        system=build_system_prompt(),
        messages=[{"role": "user", "content": user_msg}],
    )

    # JSON 블록 추출
    for block in resp.content:
        txt = getattr(block, "text", "") or ""
        if "{" in txt:
            start = txt.find("{")
            end = txt.rfind("}") + 1
            try:
                return _json.loads(txt[start:end])
            except Exception:
                continue

    return {"interpretation": "", "citations": [], "dominant_themes": []}


# ─────────────────────────────────────────────────────────────────
#  Claude Code 경로 (MCP 클라이언트에서 호출)
# ─────────────────────────────────────────────────────────────────

def prepare_claude_code_payload(narrative: str, metadata: Optional[dict] = None) -> dict:
    """
    Claude Code가 MCP 도구 호출 전에 LLM 해석을 준비할 때 쓰는 페이로드.
    MCP 서버는 이 구조를 enforcer 에 던진다.
    """
    return {
        "narrative": narrative,
        "metadata": metadata or {},
        "system_prompt": build_system_prompt(),
        "instruction": (
            "위 시스템 프롬프트 규칙을 지켜서 해석 생성 후 "
            "analyze_dream_enforced(narrative, llm_interpretation=...) 호출"
        ),
    }
