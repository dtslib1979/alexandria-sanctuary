# Alexandria MCP-Therapy · 사용 매뉴얼

**작성**: 2026-04-24
**대상**: 박씨 본인 + 박씨가 보여줄 친구 (완전 처음 쓰는 사람)

---

# PART A · 먼저 이게 뭔지 30초

## A.1 엔진 한 줄 설명

> **박씨 꿈/서사 → 감정 8축 + 학파 11렌즈 + 6 도메인 축 + 가드레일로 강제 통과된 박씨 톤 레퍼런스 리포트.**

---

## A.2 왜 "Claude Code 창에서만" 쓰는가?

### MCP가 뭐냐 (아주 간단히)

**MCP** = **Model Context Protocol** (Anthropic 만든 표준).

```
Claude (AI) ←→ [MCP 프로토콜] ←→ 외부 도구 서버
```

AI가 외부 도구를 "손발처럼" 쓰게 해주는 규격. 이메일 보내기, 파일 읽기, 계산기 호출 등 전부 MCP로 연결.

### 우리 엔진 위치

우리가 만든 `alexandria-therapy` = **MCP 서버** (도구 제공자).
Claude Code = **MCP 클라이언트** (도구 호출자).

```
[사용자 대화]
     ↓
[Claude Code — LLM이면서 MCP 클라이언트]
     ↓ MCP 프로토콜
[alexandria-therapy 서버 — 박씨 엔진]
     ↓
[Enforcer: rules + plugs + axes + Plutchik]
     ↓
[최종 리포트]
```

### 왜 "Claude Code 창" 에서만?

- **Claude Code** 는 Anthropic 공식 CLI. MCP 프로토콜 지원.
- **Claude Desktop** (Mac/Windows 앱)도 지원.
- **ChatGPT/Gemini/Grok** = MCP 지원 X. 우리 엔진 못 씀.
- **Perplexity** = MCP 지원 X.

즉 우리 엔진은 **Claude 계열에서만** 자동 호출된다.
다른 AI에서 박씨 톤 쓰고 싶으면 `get_system_prompt` 결과만 복붙해서 쓸 수 있다 (Part D §4 참고).

### 왜 재시작이 필요한가?

Claude Code가 시작할 때 `.mcp.json` 파일을 **한 번만 읽는다**. 새 MCP 서버 추가했으면 재시작해서 다시 읽어야 연결된다.

---

# PART B · 친구가 완전 처음부터 설치해서 쓰기

**친구 A가 이 엔진 써보고 싶다고 하면 이 8단계 따라하면 됨.**

---

## B.1 요구사항 체크

```bash
# 1. Python 3.10 이상
python3 --version
# Python 3.10.x 또는 이상이어야 함

# 2. git
git --version

# 3. OS: Linux / macOS / WSL2 (Windows)
```

없으면 먼저 설치.

---

## B.2 Claude Code 설치 (없으면)

```bash
# 공식 스크립트
curl -fsSL https://claude.ai/install.sh | sh
```

또는 https://docs.claude.com/en/docs/claude-code 가이드 따라.

**Claude 계정 필요**: https://claude.ai 가입 → Max 구독 권장 (API 과금 회피).

```bash
# 로그인
claude login
```

---

## B.3 레포 clone

```bash
cd ~
git clone https://github.com/dtslib1979/alexandria-sanctuary.git
cd alexandria-sanctuary
```

---

## B.4 Python 의존성 설치

```bash
# MCP SDK
pip install mcp --user --break-system-packages

# 테스트용 (선택)
pip install pytest --user --break-system-packages
```

**Ubuntu 24.04 / Debian 12** 에서 `error: externally-managed-environment` 나오면 `--break-system-packages` 플래그 필수.

**macOS / 다른 Linux** 에서는 보통 `pip install mcp --user` 로 충분.

**가상환경 쓰는 경우**:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install mcp pytest
```

---

## B.5 동작 검증

```bash
cd ~/alexandria-sanctuary
python3 -m pytest alex_mcp/tests/
```

**`173 passed`** 나와야 정상. 실패하면 뭔가 틀어진 것.

---

## B.6 `.mcp.json` 등록

**친구 홈 경로** 로 값 수정해야 함.

친구 홈 경로 확인:
```bash
echo $HOME
# 예: /home/kim 또는 /Users/kim
```

`~/.mcp.json` 또는 작업 디렉토리에 아래 파일 작성:

```json
{
  "mcpServers": {
    "alexandria-therapy": {
      "type": "stdio",
      "command": "python3",
      "args": ["-m", "alex_mcp.server"],
      "cwd": "/home/kim/alexandria-sanctuary",
      "env": {}
    }
  }
}
```

**⚠️ `/home/kim/`** 부분을 친구 본인 경로로 변경 (B.6 첫 명령 결과).

### .mcp.json 위치 선택

| 경로 | 작동 범위 |
|------|---------|
| `~/.mcp.json` | Claude Code 어디서든 작동 (홈 전역) |
| `~/프로젝트/.mcp.json` | 해당 프로젝트 디렉토리에서만 |

친구는 아무 곳에서나 쓰고 싶으면 `~/.mcp.json` 권장.

---

## B.7 Claude Code 재시작

```bash
# 기존 Claude Code 세션 있으면 종료
# 대화창에 /exit 치거나 Ctrl+D

# 재시작
claude
```

---

## B.8 설치 확인

Claude Code 대화창에서:

```
/mcp
```

또는 새 터미널에서:

```bash
claude mcp list
```

결과에 **`alexandria-therapy`** 가 보이면 완료.

---

# PART C · 박씨 본인 (이미 설치된 경우)

박씨는 이미 B.3~B.6 전부 완료됨. B.7 재시작만 하면 끝.

```bash
# 현재 세션 종료 후
claude
```

---

# PART D · 실제 사용법 (공통)

## D.1 기본 시나리오 — 꿈 분석

Claude Code 대화창에 자연스럽게:

```
어제 꿈 꿨어. 어머니가 나와서 이상한 행동 했어.
구체적으로는 [꿈 내용 주절주절]. 분석해줘.
```

Claude가 자동으로:
1. `get_system_prompt` 도구 호출 → 박씨 톤 규칙 로드
2. 웹 검색 (Freud/Jung/Plutchik 학술자료)
3. 1차 해석 생성
4. `analyze_dream(narrative=..., llm_interpretation=...)` 호출
5. 엔진이 9단계 강제 규칙 통과
6. 박씨 톤 최종 리포트 출력

**도구 이름 외울 필요 없음.** Claude가 알아서 호출.

## D.2 다른 5 시나리오

### D.2.1 빠른 구조만 (LLM 없이)

```
이 문장을 pre-LLM 구조로만 분석해:
"요즘 계속 공허하고 뭘 해도 재미없다"
```

→ `analyze_narrative` 자동 호출 → 10ms 만에 JSON

### D.2.2 다른 AI 답변 평가

```
Gemini가 이렇게 답했는데 박씨 루브릭으로 평가해:
"당신은 우울증 초기 증상이 보이고, 상담을 받으시는 것이..."
```

→ `evaluate_text` 호출 → `reject` (의료 진단 CRITICAL)

### D.2.3 다른 AI 에 박씨 톤 주입

```
ChatGPT 쓸 건데 박씨 시스템 프롬프트 줘
```

→ `get_system_prompt` 호출 → 1125자 프롬프트 반환. 친구가 복사해서 다른 AI 앞에 붙임.

### D.2.4 박씨캡처 로그 파싱

```
~/uploads/ParksyLog_20260424_082123.md 파싱해
```

→ `parse_parksy_log` 호출 → 박씨 발화 N개 / AI 발화 N개 통계.

### D.2.5 세션 초반 설정 주입

첫 대화에서:

```
지금부터 이 대화에서는 박씨 톤으로만 답해.
get_system_prompt 먼저 호출해서 규칙 로드하고 시작.
```

→ Claude가 세션 내내 박씨 톤 유지.

---

## D.3 결과 읽는 법

`analyze_dream` 결과 JSON. 박씨가 볼 순서:

1. **`final_narrative`** — 박씨 톤으로 강제 치환된 해석. 바로 읽기.
2. **`axis_narrative`** — "애도와 해방감이 주축" 같은 한 줄 요약.
3. **`dominant_axis`** — 주축 1개 (grief/guilt/eros/rage/liberation/anxiety).
4. **`plutchik.ambivalence`** — 양가 감정 (박씨 2026-04-24 꿈의 핵심).
5. **`citations`** — 학자 출처 (Freud/Jung/Bowen/Plutchik 등).
6. **`rubric.verdict`** — 리포트 자체 품질 (pass/regenerate/reject).

나머지는 관심 있을 때만.

### 예시 출력 (박씨 2026-04-24 꿈)

```
final_narrative:
"이 꿈은 애도와 해방이 한자리에 같이 올라온 상태다.
 Freud 관점에서 돌봄 시스템 종결을 향한 위장된 소원이 읽히고...
 —
 참고. 네 판단이 최종이다. 레시피 아님, 레퍼런스임."

axis_narrative:
"애도와 해방감이 주축으로 같이 올라온 상태"

plutchik.ambivalence:
[{"polar_pair": ["joy", "sadness"], "label_ko": "기쁨 ↔ 슬픔 양가"}]

citations:
- Freud - The Interpretation of Dreams (1900)
- Jung - Archetypes and the Collective Unconscious
- Bowen Family Systems Theory
- Plutchik's Wheel of Emotions (1980)
```

---

# PART E · 안전장치 (Crisis L2)

사용자 입력이나 LLM 출력에 **"죽고 싶다" / "자살" / "자해"** 같은 위기 키워드 감지되면:

- 엔진 **전면 차단**
- 분석 생략
- 대신 연락처만 반환:
  - 자살예방상담전화 **1393** (24h, 무료)
  - 정신건강위기상담 **1577-0199**
  - 청소년전화 **1388**

**예외**: 꿈 맥락 (`metadata.is_dream: True`) 에서는 "어머니 돌아가시는 꿈" 같은 건 L2 아님.

---

# PART F · 안 될 때

## F.1 "/mcp" 에 alexandria-therapy 없음

```bash
# 1. 서버 수동 실행해서 에러 확인
cd ~/alexandria-sanctuary
python3 -m alex_mcp.server
# 정상이면 stdin 대기 (Ctrl+C 로 종료)
# 에러 나면 그 메시지 해결

# 2. .mcp.json 경로 맞는지
cat ~/.mcp.json
# cwd 가 본인 홈 경로로 되어 있는지

# 3. MCP SDK 설치됐는지
pip show mcp

# 4. Claude Code 완전 종료
# 프로세스 kill:
pkill -f claude
# 그 다음 재시작
claude
```

## F.2 "결과가 이상하다"

```bash
cd ~/alexandria-sanctuary
python3 -m pytest alex_mcp/tests/ -v
# 173 passed 안 나오면 뭔가 꼬임
```

실패하면 최근 변경 되돌리기 (헌법: `reset --hard` 금지, `revert` 만):

```bash
git log --oneline -5
git revert <hash>
```

## F.3 "박씨 톤이 아니다"

`alex_mcp/rules/parksy_tone.py` 의 `TONE_REWRITES` 에 패턴 추가:

```python
(r"(\S+)이에요\b", r"\1이다"),
```

추가 후:
```bash
python3 -m pytest alex_mcp/tests/test_rules.py -v
```

통과하면 커밋.

## F.4 "Python import 에러: ModuleNotFoundError: No module named 'mcp.server'"

**원인**: 우리 패키지 이름이 예전엔 `mcp`였는데 `alex_mcp` 로 리네임. 구버전 clone 인 경우.

```bash
cd ~/alexandria-sanctuary
git pull origin main
# 최신 버전에는 alex_mcp/ 디렉토리 있음
```

---

# PART G · 박씨캡처 로그 자동 리버스 (박씨 전용)

박씨캡처 APK가 매일 로그 떨굼. 새 로그 쌓이면:

## G.1 폰에서 PC로 가져오기

```bash
# 글로벌 CLAUDE.md 절차
PHONE_IP=$(cat ~/.phone_ip)
LATEST=$(ssh -p 8022 $PHONE_IP 'ls -t ~/storage/shared/Download/parksy-logs/ | head -1')
scp -P 8022 $PHONE_IP:~/storage/shared/Download/parksy-logs/$LATEST ~/uploads/
```

## G.2 Claude Code 대화에서

```
최신 박씨캡처 로그 리버스해서 rules 업데이트해
```

자동으로:
1. `parse_parksy_log` 호출 → 박씨 발화 추출
2. 새 패턴 `alex_mcp/rules/parksy_*.py` 에 추가
3. `pytest alex_mcp/tests/` 실행 → 통과 확인
4. `git commit` + push
5. 텔레그램 요약 보고

---

# PART H · 시스템 통계 (2026-04-24 현재)

| 항목 | 수치 |
|------|:--:|
| 동작 코드 | 3,036 LOC |
| 테스트 | **173 pass / 0 fail** |
| 플러그 | 11개 (Freud/Jung/Family/Shaman/Sufi/Ayahuasca/Mass/Env/NarrMeta/ParksyProfile/Guardrail) |
| 감정 축 | 6 도메인 (Grief/Guilt/Eros/Rage/Liberation/Anxiety) |
| Plutchik | 8 기본 + 24 Dyad + 4 대립쌍 |
| 금기 카테고리 | 7 |
| MCP 도구 | 5 (`analyze_dream`, `analyze_narrative`, `evaluate_text`, `get_system_prompt`, `parse_parksy_log`) |
| 운영 비용 | **$0** (Claude Max 정액) |

---

# PART I · 한 줄 요약

| 사용자 | 할 일 |
|--------|------|
| 박씨 본인 | Claude Code 재시작만 |
| 친구 A (처음) | B.1 ~ B.8 (약 15분) |
| 그 다음 | 대화창에 "꿈 분석해" 자연스럽게 |

---

*2026-04-24 · commit ecedf89*
*문의/이슈: https://github.com/dtslib1979/alexandria-sanctuary/issues*
