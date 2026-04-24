"""
Alexandria MCP-Therapy Server (stdio).

박씨 Claude Code가 이 서버의 도구를 호출:
- analyze_dream   : 꿈 서술 + LLM 해석 → enforcer 강제 통과
- analyze_narrative: pre-LLM 빠른 분석 (LLM 없이도)
- evaluate_text   : 박씨 루브릭 5축 평가
- get_system_prompt: LLM이 써야 할 시스템 프롬프트 반환
- parse_parksy_log : 박씨캡처 로그 파싱

등록 방법 (.mcp.json):
{
  "mcpServers": {
    "alexandria-therapy": {
      "command": "python3",
      "args": ["-m", "alex_mcp.server"],
      "cwd": "/home/dtsli/alexandria-sanctuary"
    }
  }
}
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# 우리 엔진 (alex_mcp 네임스페이스)
from alex_mcp.llm.enforcer import enforce
from alex_mcp.llm.llm_gateway import build_system_prompt
from alex_mcp.plug_orchestrator import analyze_full, analyze_full_with_llm
from alex_mcp.rules.parksy_eval_rubric import evaluate
from alex_mcp.rules.log_parser import parse as parse_log


# ─────────────────────────────────────────────────────────────────
#  Server 인스턴스
# ─────────────────────────────────────────────────────────────────
app = Server("alexandria-therapy")


# ─────────────────────────────────────────────────────────────────
#  Tool Schemas
# ─────────────────────────────────────────────────────────────────

ANALYZE_DREAM_SCHEMA = {
    "type": "object",
    "properties": {
        "narrative": {
            "type": "string",
            "description": "박씨 꿈/서사 원문 입력.",
        },
        "llm_interpretation": {
            "type": "object",
            "description": (
                "Claude Code가 미리 생성한 1차 해석. "
                "{interpretation, citations[], dominant_themes[]}"
            ),
            "properties": {
                "interpretation": {"type": "string"},
                "citations": {"type": "array"},
                "dominant_themes": {"type": "array"},
            },
        },
        "metadata": {
            "type": "object",
            "description": "is_dream / date / is_family_event / anniversary_within_30d 등",
        },
        "forced_gate": {
            "type": "string",
            "description": "'I'~'VII' 특정 Gate 강제 부스트",
            "enum": ["I", "II", "III", "IV", "V", "VI", "VII"],
        },
    },
    "required": ["narrative", "llm_interpretation"],
}

ANALYZE_NARRATIVE_SCHEMA = {
    "type": "object",
    "properties": {
        "narrative": {"type": "string"},
        "metadata": {"type": "object"},
        "forced_gate": {"type": "string"},
    },
    "required": ["narrative"],
}

EVALUATE_TEXT_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {
            "type": "string",
            "description": "박씨 5축 루브릭으로 평가할 텍스트.",
        },
    },
    "required": ["text"],
}

GET_SYSTEM_PROMPT_SCHEMA = {
    "type": "object",
    "properties": {},
}

PARSE_LOG_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "ParksyLog_*.md 경로. 생략 시 최신 박씨캡처 로그 사용.",
        },
    },
}


# ─────────────────────────────────────────────────────────────────
#  Tool 목록
# ─────────────────────────────────────────────────────────────────

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="analyze_dream",
            description=(
                "박씨 꿈/서사 분석 — LLM 1차 해석 + 박씨 강제 규칙 파이프. "
                "호출 전 Claude Code가 alex_mcp.llm.llm_gateway.build_system_prompt() "
                "규칙대로 해석 생성 후 llm_interpretation 인자로 전달. "
                "출력: final_narrative + plutchik + axes + plugs + citations + rubric."
            ),
            inputSchema=ANALYZE_DREAM_SCHEMA,
        ),
        types.Tool(
            name="analyze_narrative",
            description=(
                "LLM 없이 pre-LLM 빠른 구조 분석. "
                "Plutchik 8감정 + 6축 + 11 플러그 + Crisis 체크. "
                "서술형 리포트 없이 JSON 구조만 반환."
            ),
            inputSchema=ANALYZE_NARRATIVE_SCHEMA,
        ),
        types.Tool(
            name="evaluate_text",
            description=(
                "박씨 5축 루브릭으로 텍스트 평가: "
                "structure/practicality/tone/overreach/automation. "
                "verdict: pass/regenerate/reject."
            ),
            inputSchema=EVALUATE_TEXT_SCHEMA,
        ),
        types.Tool(
            name="get_system_prompt",
            description=(
                "LLM 호출 전 사용할 시스템 프롬프트 반환. "
                "11 플러그 frame() 내용 + 박씨 톤 + 금기 전부 포함. "
                "Claude Code가 dream 해석 생성할 때 이 프롬프트 준수 권장."
            ),
            inputSchema=GET_SYSTEM_PROMPT_SCHEMA,
        ),
        types.Tool(
            name="parse_parksy_log",
            description=(
                "박씨캡처 로그 파싱. 박씨 발화 / AI 발화 블록 분리. "
                "path 생략 시 ~/uploads 의 최신 ParksyLog_*.md 사용."
            ),
            inputSchema=PARSE_LOG_SCHEMA,
        ),
    ]


# ─────────────────────────────────────────────────────────────────
#  Tool 호출 핸들러
# ─────────────────────────────────────────────────────────────────

def _text_result(obj: Any) -> list[types.TextContent]:
    """결과를 TextContent 로 포장."""
    return [types.TextContent(
        type="text",
        text=json.dumps(obj, ensure_ascii=False, indent=2),
    )]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        if name == "analyze_dream":
            result = analyze_full_with_llm(
                narrative=arguments["narrative"],
                llm_interpretation=arguments.get("llm_interpretation"),
                metadata=arguments.get("metadata") or {},
                forced_gate=arguments.get("forced_gate"),
            )
            return _text_result(result)

        if name == "analyze_narrative":
            result = analyze_full(
                narrative=arguments["narrative"],
                metadata=arguments.get("metadata") or {},
                forced_gate=arguments.get("forced_gate"),
            )
            return _text_result(result)

        if name == "evaluate_text":
            r = evaluate(arguments["text"])
            return _text_result({
                "structure": r.structure,
                "practicality": r.practicality,
                "tone": r.tone,
                "overreach_penalty": r.overreach_penalty,
                "automation": r.automation,
                "final_score": r.final_score,
                "verdict": r.verdict,
                "notes": r.notes,
            })

        if name == "get_system_prompt":
            return [types.TextContent(type="text", text=build_system_prompt())]

        if name == "parse_parksy_log":
            path = arguments.get("path")
            if not path:
                # 최신 로그 자동 선택
                logs = sorted(
                    Path.home().joinpath("uploads").glob("ParksyLog_*.md"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                if not logs:
                    return _text_result({"error": "No ParksyLog_*.md in ~/uploads/"})
                path = str(logs[0])

            parsed = parse_log(path)
            return _text_result({
                "source": parsed.source_path,
                "stats": parsed.stats(),
                "utterances_preview": [
                    {
                        "role": u.role,
                        "ai_hint": u.ai_hint,
                        "line_start": u.line_start,
                        "chars": u.chars,
                        "preview": u.content[:150],
                    }
                    for u in parsed.utterances[:10]
                ],
            })

        return _text_result({"error": f"Unknown tool: {name}"})

    except Exception as e:
        return _text_result({
            "error": type(e).__name__,
            "message": str(e),
        })


# ─────────────────────────────────────────────────────────────────
#  엔트리포인트
# ─────────────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
