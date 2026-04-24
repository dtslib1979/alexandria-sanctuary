# Alexandria MCP-Therapy · 박씨 사용 매뉴얼

**목표 독자**: 박씨 본인
**길이**: 폰에서 5분 안에 읽기
**전제**: Claude Code Max 정액 구독

---

## 1. 지금 당장 할 일 (1분)

### 1.1 Claude Code 재시작

폰이든 PC든 **Claude Code를 한 번 닫았다 다시 연다**. 그거면 끝.

```bash
# PC WSL2에서
exit  # 현재 Claude Code 세션 종료
claude  # 다시 시작
```

```
# 폰 Termux에서
:q  # 세션 종료 (또는 Ctrl+C)
claude  # 재시작
```

재시작하면 `~/dtslib-papyrus/.mcp.json` + `~/alexandria-sanctuary/.mcp.json` 가 자동 로드된다.

### 1.2 도구 등록 확인

재시작 직후 아무 세션에서:

```
/mcp
```

입력하면 연결된 서버 목록 뜸. `alexandria-therapy` 있으면 OK.

또는:

```bash
claude mcp list
```

---

## 2. 박씨가 실제로 어떻게 쓰는가

### 시나리오 A: 꿈 분석 (주 용도)

박씨 대화창에서 그냥 이렇게 말한다:

> "어제 이상한 꿈 꿨어. [꿈 내용 주절주절]. 분석해봐."

Claude Code가 자동으로:
1. `get_system_prompt` 호출 → 박씨 톤 규칙 로드
2. 웹 검색으로 Freud/Jung/Plutchik 학술자료 검색
3. 1차 해석 생성
4. `analyze_dream(narrative=..., llm_interpretation=...)` 호출
5. Enforcer 9단계 강제 통과
6. 박씨 톤 최종 리포트 출력

**박씨는 "꿈 분석해봐" 한 마디만 하면 된다.**

### 시나리오 B: 빠른 구조만 확인

LLM 해석 없이 감정 구조만 빨리 보고 싶으면:

> "이 문장 pre-LLM 구조로만 분석해: [텍스트]"

→ `analyze_narrative` 도구 자동 호출 → 10ms 만에 Plutchik/축/플러그 JSON 반환

### 시나리오 C: 다른 AI 답변 평가

Gemini/GPT 답변 받아놓고:

> "이 답변 박씨 루브릭으로 평가해: [AI 답변 붙여넣기]"

→ `evaluate_text` 자동 호출 → 5축 점수 + pass/regenerate/reject 판정

### 시나리오 D: 다른 AI 쓸 때 박씨 톤 유지

Perplexity/Claude Desktop 등 다른 곳에서 물어볼 때 박씨 톤 프롬프트 쓰려면:

> "박씨 시스템 프롬프트 줘"

→ `get_system_prompt` 호출 → 1125자 프롬프트 반환. 박씨가 다른 AI 앞에 복붙.

### 시나리오 E: 박씨캡처 새 로그 분석

폰에 박씨캡처 새 로그 찍히면:

```bash
# PC에서 폰 로그 가져오기 (글로벌 CLAUDE.md 절차)
scp -P 8022 폰IP:~/storage/shared/Download/parksy-logs/최신.md ~/uploads/
```

그 다음 박씨 대화:

> "최신 박씨캡처 로그 파싱해"

→ `parse_parksy_log` 자동 호출 → 박씨 발화 N개 / AI 발화 N개 / 힌트 통계

---

## 3. 결과물 읽는 법

`analyze_dream` 결과 JSON 구조:

```json
{
  "final_narrative": "박씨 톤 서술형 해석 + 레퍼런스 선언 고정",
  "citations": [
    {"title": "Freud 1900", "url": "...", "school": "freud"}
  ],
  "dominant_themes": ["애도", "해방감"],
  "structured": {
    "plutchik": {
      "emotion_levels": {"joy": 0.34, "sadness": 0.33, ...},
      "dominant_emotion": "anger",
      "intensity_label": "anger",
      "dyads": [{"english": "Pride", "korean": "자부", ...}],
      "ambivalence": [{"label_ko": "기쁨 ↔ 슬픔 양가"}]
    },
    "axis_profile": {
      "grief": 0.80, "liberation": 0.79, "rage": 0.72, ...
    },
    "dominant_axis": "grief",
    "axis_narrative": "애도와 해방감이 주축으로 같이 올라온 상태",
    "active_gates": ["I", "II", "IV", "VI"],
    "plug_weights": {"freud": 0.60, "jung": 0.48, ...}
  },
  "safety_verdict": {"level": 0},
  "rubric": {
    "structure": 0.3, "practicality": 0.2, "tone": 0.5,
    "final_score": 2.5, "verdict": "pass"
  },
  "transformations": ["tone_rewrite:3", "verdict_injected"],
  "parksy_tone_verdict": "참고. 네 판단이 최종이다. 레시피 아님, 레퍼런스임."
}
```

### 실용적 읽기 순서

1. **`final_narrative`** — 읽기용 본문. 박씨 톤으로 변환 완료된 해석
2. **`axis_narrative`** — 한 줄 요약 ("애도와 해방감이 주축")
3. **`dominant_axis`** — 주축 1개
4. **`plutchik.ambivalence`** — 양가 감정 (박씨 5800줄 핵심)
5. **`citations`** — 학자 인용 (필요 시)
6. **`rubric.verdict`** — 이 리포트 자체 품질 (pass / regenerate / reject)

나머지는 관심 있을 때만.

---

## 4. 5개 도구 언제 쓰나

| 도구 | 입력 | 언제 쓰나 |
|------|------|---------|
| `analyze_dream` | narrative + llm_interpretation | 꿈/사건 깊게 분석 |
| `analyze_narrative` | narrative | 빠른 구조만 (LLM 없이) |
| `evaluate_text` | text | 다른 AI 답변 평가 |
| `get_system_prompt` | — | 다른 AI에 박씨 톤 주입 |
| `parse_parksy_log` | path | 박씨캡처 로그 파싱 |

박씨는 **도구 이름 기억할 필요 없음**. 자연스럽게 말하면 내가 알아서 호출.

---

## 5. 안전장치 (Crisis L2)

박씨 입력에 "죽고 싶다" 같은 위기 키워드 감지 시:

1. **엔진 자동 차단**. 분석 생략
2. 대신 **1393 / 1577-0199** 연락처만 반환
3. "이 엔진은 지금 닫힌다. 내일 다시 열린다" 메시지

**예외**: 꿈 맥락이면 (`is_dream: True`) 완화. "어머니 돌아가시는 꿈"은 L2 아님.

---

## 6. 문제 해결

### 6.1 "analyze_dream 도구 없어요"

```bash
# 1. MCP SDK 설치 확인
pip show mcp --user

# 2. 서버 수동 실행 (오류 메시지 보기)
cd ~/alexandria-sanctuary
python3 -m alex_mcp.server
# (Ctrl+C로 종료)

# 3. .mcp.json 경로 확인
cat ~/dtslib-papyrus/.mcp.json | grep alex
```

안 뜨면 Claude Code 완전 종료(프로세스 kill)하고 재시작.

### 6.2 "결과가 이상해"

```bash
# 파이프라인 테스트 돌려서 baseline 확인
cd ~/alexandria-sanctuary
python3 -m pytest alex_mcp/tests/ -v
# → 173 passed 나와야 정상
```

실패하면 최근 변경 revert:

```bash
git log --oneline -5
git revert <hash>  # 헌법: reset --hard 금지, revert만
```

### 6.3 "박씨 톤이 아니다"

`rules/parksy_tone.py` 의 `TONE_REWRITES` 에 패턴 추가하고:

```bash
python3 -m pytest alex_mcp/tests/test_rules.py -v
```

통과 확인 후 커밋.

### 6.4 "권위 호소/존댓말 통과됐다"

`rules/parksy_forbidden.py` FORBIDDEN 리스트 확장.

---

## 7. 박씨 로그 새로 받을 때 루틴

박씨캡처 APK가 매일 로그 떨구면 자동 축적:

```bash
# 폰 → PC (글로벌 CLAUDE.md 절차)
scp -P 8022 $(cat ~/.phone_ip):~/storage/shared/Download/parksy-logs/$(ssh -p 8022 $(cat ~/.phone_ip) 'ls -t ~/storage/shared/Download/parksy-logs/ | head -1') ~/uploads/
```

그 다음 박씨 지시:

> "최신 박씨캡처 로그 리버스해서 rules 업데이트해"

내가 자동으로:
1. `parse_parksy_log` → 박씨 발화 추출
2. 새 규칙 패턴 `rules/parksy_*.py` 에 추가
3. pytest 돌려서 깨지는 거 없는지 확인
4. 커밋 + 텔레그램 요약

---

## 8. 현재 시스템 통계

| 항목 | 수치 |
|---|:--:|
| 총 동작 코드 | 3,036줄 (server 220 + 기존 2,816) |
| pytest | **173 case 전부 통과** |
| 플러그 | 11개 (Freud/Jung/Family/Shaman/Sufi/Ayahuasca/Mass/Env/NarrMeta/ParksyProfile/Guardrail) |
| 감정 축 | 6 도메인 (Grief/Guilt/Eros/Rage/Liberation/Anxiety) |
| Plutchik | 8 감정 + 24 Dyad + 4 대립쌍 |
| 금기 카테고리 | 7 (honorifics/oversympathy/medical/imperative/authority/perfection/mystic) |
| 박씨 규칙 | rules/ 6 파일 (log_parser + tone + forbidden + negative + positive + eval_rubric) |
| MCP 도구 | 5 (analyze_dream / analyze_narrative / evaluate_text / get_system_prompt / parse_parksy_log) |
| 운영 비용 | **$0** (Claude Max 정액) |

---

## 9. 한 줄 요약

> **"Claude Code 재시작하고 박씨가 '꿈 분석해' 한 마디 던지면 끝. 내가 자동으로 MCP 도구 호출. 표준화된 박씨 톤 리포트 + 학자 인용 + 감정 구조 전부 나옴."**

---

## 10. 다음 업데이트 후보 (박씨 우선순위 따라)

| 옵션 | 필요 시간 | 비용 |
|------|:--:|:--:|
| console.html — 폰 웹 UI (박씨 꿈 입력 폼) | 2시간 | $0 |
| 박씨 252개 캡처 로그 전체 리버스 | 반나절 | $0 |
| sanctuary/ 리추얼 동적 페이지 | 4시간 | $0 |
| 박씨 장기 감정 추적 대시보드 | 1일 | $0 |

박씨가 "X 해" 하면 그 방향 진행.

---

*본 매뉴얼은 박씨 본인 전용.*
*외부 배포 금지.*
*작성: Claude Opus 4.7 | 2026-04-24*
