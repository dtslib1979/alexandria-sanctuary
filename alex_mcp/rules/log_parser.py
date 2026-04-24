"""
박씨캡처 로그 파서 — ParksyLog_*.md 를 발화 단위로 분해.

박씨 로그 구조 (관찰 기반):
- 박씨 발화: AI 응답 사이에 낀 장문의 한국어 블록. 문단 끝 "분석해 봐", "쓸만한 거 있냐",
             "이건 ~가 얘기한 거야" 같은 지시/평가 문구 포함.
- AI 발화: "답변" / "더 보기" / 번호 (1, 2, 3...) / 이모지 헤더로 시작하는 블록.
- Perplexity 브릿지 평가: "이건 ~했다", "쓸만한 부분" 같은 분석 코멘트.

참조: uploads/ParksyLog_20260424_082123.md (5808줄)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────────
#  박씨 발화 시그니처 (로그 관찰 기반)
# ─────────────────────────────────────────────────────────────────

# 박씨 지시/질문 문구 (발화 블록 끝에 자주 등장)
PARKSY_DIRECTIVE_MARKERS = [
    r"분석해\s*봐", r"쓸만한\s*거\s*있",
    r"맞\s*냐\?", r"틀려\?", r"적합하냐",
    r"어때\?", r"평가해", r"어떻게\s*할",
    r"이거\s*맞", r"이게\s*맞", r"씨발",
    r"정신\s*차려", r"대답해",
    r"야\s*,?\s*이건", r"야\s*이거",
    r"그럼\s*", r"그러니까",
    r"MCP", r"아키텍처",
]

# 박씨 발화 내부 어휘 (단언형 종결·추임새·비속어)
PARKSY_TONE_MARKERS = [
    r"~?거든", r"~?잖아", r"~?거야",
    r"근데", r"그러니까", r"그러면",
    r"씨발", r"개새끼", r"병신", r"지랄",
    r"존나", r"뭐야", r"~?냐\?",
]

# AI 발화 시그니처 (답변 블록 시작)
AI_START_MARKERS = [
    r"^답변\s*$",
    r"^더\s*보기\s*$",
    r"^\d+\.\s+",          # 번호 리스트
    r"^#{1,6}\s+",         # 마크다운 헤더
    r"^---\s*$",           # 구분선
    r"^\s*요약하면",
    r"^\s*짧게\s*말하면",
    r"^\s*결론만\s*말하면",
    r"^\s*맞다\.\s",
]

# Perplexity 특유 (로그 분석 결과)
PERPLEXITY_MARKERS = [
    r"\[\d+\]",            # 인용 각주
    r"Sources:",
    r"## ",                # 섹션 헤더
    r"\*\*\w+\*\*",        # 볼드 주제
]


@dataclass
class Utterance:
    """발화 1블록."""
    role: str                 # "parksy" | "ai" | "system" | "unknown"
    ai_hint: Optional[str]    # "perplexity" | "gemini" | "grok" | "chatgpt" | "claude" | None
    content: str
    line_start: int
    line_end: int
    chars: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ParsedLog:
    source_path: str
    total_lines: int
    utterances: list[Utterance] = field(default_factory=list)

    def stats(self) -> dict:
        parksy = [u for u in self.utterances if u.role == "parksy"]
        ai = [u for u in self.utterances if u.role == "ai"]
        return {
            "source": self.source_path,
            "total_lines": self.total_lines,
            "total_utterances": len(self.utterances),
            "parksy_count": len(parksy),
            "parksy_total_chars": sum(u.chars for u in parksy),
            "ai_count": len(ai),
            "ai_total_chars": sum(u.chars for u in ai),
            "ai_hints": {
                hint: len([u for u in ai if u.ai_hint == hint])
                for hint in {"perplexity", "gemini", "grok", "chatgpt", "claude", None}
                if any(u.ai_hint == hint for u in ai)
            },
        }


# ─────────────────────────────────────────────────────────────────
#  역할 분류 휴리스틱
# ─────────────────────────────────────────────────────────────────

AI_STRONG_MARKERS = [
    r"^\s*맞다\.\s",                # Perplexity 전형 시작
    r"^\s*요약하면",
    r"^\s*결론만\s*말하면",
    r"^\s*짧게\s*말하면",
    r"^\s*질문\s*의\s*내용을\s*정리",  # Perplexity 자기 지시문
    r"^\s*\d+\s*단계\s*완료",
    r"\[\d+\]",                     # 인용 각주
    r"## \d",                        # 마크다운 섹션
]

# Perplexity 특유의 "너/네" 2인칭 + 분석 톤
AI_PARKSY_IMITATION = [
    r"네가\s*지금",
    r"너\s*입장에서",
    r"네\s*구조",
    r"너\s*말이\s*맞",
    r"네\s*기준으로",
]


def _is_parksy(block: str) -> bool:
    """박씨 발화 판정 (개선판)."""
    if not block.strip():
        return False

    # 1. AI 강한 시그널 있으면 박씨 아님
    for pat in AI_STRONG_MARKERS:
        if re.search(pat, block, re.MULTILINE):
            return False

    # 2. 1000자 넘으면 박씨 아닐 확률 큼 (긴 서술 = AI)
    #    (단, 첫 꿈 진술은 수동 예외 처리 필요)
    if len(block) > 1000:
        return False

    # 3. "너/네가 ~" 2인칭 분석 톤이 3회 이상이면 AI
    imitation_hits = sum(1 for p in AI_PARKSY_IMITATION if re.search(p, block))
    if imitation_hits >= 3:
        return False

    # 4. 지시/질문 마커가 하나라도 있으면 박씨
    for pat in PARKSY_DIRECTIVE_MARKERS:
        if re.search(pat, block):
            return True

    # 5. 박씨 욕/톤 마커 2개 이상 + 400자 이하 = 박씨
    tone_hits = sum(1 for pat in PARKSY_TONE_MARKERS if re.search(pat, block))
    if tone_hits >= 2 and len(block) < 400:
        return True

    return False


def _is_ai_start(line: str) -> bool:
    for pat in AI_START_MARKERS:
        if re.match(pat, line):
            return True
    return False


def _detect_ai_hint(block: str) -> Optional[str]:
    """AI 발화에서 어떤 모델인지 힌트 추출."""
    lower = block.lower()
    if "perplexity" in lower or "[1]" in block or "Sources:" in block:
        return "perplexity"
    if "gemini" in lower:
        return "gemini"
    if "grok" in lower:
        return "grok"
    if "chatgpt" in lower or "openai" in lower:
        return "chatgpt"
    if "claude" in lower:
        return "claude"
    return None


# ─────────────────────────────────────────────────────────────────
#  블록 분해 (로그 구조 기반)
# ─────────────────────────────────────────────────────────────────

BLOCK_SEPARATOR_PATTERNS = [
    r"^￼\s*$",           # 이모지 구분자 (박씨캡처 APK 특유)
    r"^\s*더\s*보기\s*$",
    r"^\s*\d+\s*$",      # 숫자만 (토큰 카운트 등)
    r"^─+$",
]


def _is_block_separator(line: str) -> bool:
    for pat in BLOCK_SEPARATOR_PATTERNS:
        if re.match(pat, line.strip()):
            return True
    return False


def parse(md_path: str | Path) -> ParsedLog:
    """
    ParksyLog_*.md → ParsedLog.
    """
    path = Path(md_path)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # 프론트매터 스킵
    start_idx = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start_idx = i + 1
                break

    utterances: list[Utterance] = []
    current_block: list[str] = []
    current_start = start_idx

    def flush(end_idx: int):
        nonlocal current_block, current_start
        if not current_block:
            return
        content = "\n".join(current_block).strip()
        if not content:
            current_block = []
            current_start = end_idx + 1
            return

        if _is_parksy(content):
            role = "parksy"
            hint = None
        else:
            role = "ai"
            hint = _detect_ai_hint(content)

        utterances.append(Utterance(
            role=role,
            ai_hint=hint,
            content=content,
            line_start=current_start,
            line_end=end_idx,
            chars=len(content),
        ))
        current_block = []
        current_start = end_idx + 1

    for i in range(start_idx, len(lines)):
        line = lines[i]
        if _is_block_separator(line):
            flush(i - 1)
            continue
        current_block.append(line)
    flush(len(lines) - 1)

    return ParsedLog(
        source_path=str(path),
        total_lines=len(lines),
        utterances=utterances,
    )


# ─────────────────────────────────────────────────────────────────
#  CLI self-test
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import sys

    log_path = sys.argv[1] if len(sys.argv) > 1 else str(
        Path.home() / "uploads" / "ParksyLog_20260424_082123.md"
    )
    parsed = parse(log_path)
    stats = parsed.stats()
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"\n첫 박씨 발화 (샘플):")
    for u in parsed.utterances[:20]:
        if u.role == "parksy":
            print(f"  [L{u.line_start}-{u.line_end}] {u.content[:80]}...")
            break
