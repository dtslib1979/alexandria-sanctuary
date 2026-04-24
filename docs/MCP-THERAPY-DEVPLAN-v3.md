# MCP-THERAPY 개발 계획 v3.0 (SOTA-Grounded)

**선행**: `WHITEPAPER-v1.0.md`
**대체**: `DEVPLAN-TASKS.md` v2.0, `DEVPLAN-TASKS-v2.1.md` (archive/)
**작성**: 2026-04-24 Claude Opus 4.7

> **v3 원칙**: 모든 TASK에 (a) SOTA 참조 URL, (b) 담당 에이전트, (c) verify 커맨드, (d) 실패 시 에스컬 경로가 박혀 있어야 한다. Phase 0 Sprint 0.1·0.4·CrisisDetector 은 **완료 증명** 포함.

---

## 0. 완료 증명 (Phase 0 부분 완료)

| TASK | 상태 | 증거 |
|------|:---:|------|
| T0.1.1 디렉토리 골격 | ✅ | `git log --oneline` |
| T0.1.2 학파 README 8장 | ✅ | 8/8 파일 생성 |
| T0.1.3 아카이브 정리 | ✅ | `docs/archive/` 이동 완료 |
| T0.1.4 커밋 + push | ✅ | commit `6e42a20` |
| **T1.2.7.1 CrisisDetector** | ✅ | **pytest 41/41, L2 100%/0%** |

**위 5개 TASK는 v3 기준 완전 합격**. 나머지 53개도 동일 수준 증명 필요.

---

## 1. 에이전트 Lane (v2.1 유지)

| Lane | 에이전트 | tmux 세션 | 주 담당 |
|------|---------|----------|--------|
| A | Opus | `tab_claude` | 아키텍처, 복잡 플러그, orchestration |
| B | Sonnet | `phone_claude` | 큐레이션, 일반 구현 |
| C | Aider+DeepSeek | `phone_aider` | 코드 diff 편집, 테스트 |
| D | Haiku | `tab_aider` | 템플릿, 리네이밍 |
| E | Vast.ai | 원격 | LoRA 학습 |

---

## 2. TASK 카드 표준 포맷 (v3)

```yaml
TASK: T<phase>.<sprint>.<seq>
title: <목적>
agent_primary: <Lane>
sota_reference:
  - title: <프로젝트/논문>
    url: <URL>
    why: <왜 이걸 참조하는가>
depends_on: [<TASK IDs>]
blocks: [<TASK IDs>]
estimated_min: <분>
briefing: |
  <자기완결 컨텍스트>
instruction: |
  <커맨드 수준>
verify: |
  <bash>
outputs: [<파일>]
on_failure: <에스컬>
commit_message: <헌법 포맷>
```

---

## 3. PHASE 1 — MVP (2~3주, $5 버퍼, 71 TASK)

### Sprint 1.1 — LangGraph 기반 세팅 (신규)

#### TASK T1.1.1
```yaml
TASK: T1.1.1
title: LangGraph + 의존성 세팅
agent_primary: aider_deepseek
sota_reference:
  - title: LangGraph 공식
    url: https://langchain-ai.github.io/langgraph/
    why: 7 Gate + 10 Plug + Crisis 브랜칭 그래프 자연 표현
  - title: StateGraph API
    url: https://langchain-ai.github.io/langgraph/reference/graphs/
    why: 노드 정의 + conditional edges
depends_on: []
blocks: [T1.5.1]
estimated_min: 20

instruction: |
  1. cd ~/alexandria-sanctuary
  2. pip install langgraph langchain-core pydantic
  3. mcp/train/requirements.txt 업데이트:
     langgraph>=0.2.0
     langchain-core>=0.3.0
     pydantic>=2.0
     jinja2>=3.1
  4. mcp/graph/__init__.py (빈 파일) 생성
  5. mcp/graph/state.py 파일 생성, TypedDict 정의:
     class TherapyState(TypedDict):
         narrative: str
         metadata: dict
         forced_gate: str | None
         crisis_verdict: dict | None
         axis_profile: dict | None
         plug_weights: dict | None
         raw_output: str | None
         sanitized_output: str | None
         final_report: dict | None

verify: |
  python3 -c "from mcp.graph.state import TherapyState; print('OK')"
  pip show langgraph | head -3

outputs:
  - mcp/graph/state.py
  - mcp/graph/__init__.py

commit_message: "feat: LangGraph 세팅 + TherapyState (T1.1.1)"
```

#### TASK T1.1.2
```yaml
TASK: T1.1.2
title: Plug 추상 베이스 클래스
agent_primary: aider_deepseek
sota_reference:
  - title: Python abc 모듈
    url: https://docs.python.org/3/library/abc.html
    why: 플러그 인터페이스 강제
depends_on: [T1.1.1]
blocks: [T1.3.*, T1.2.*]
estimated_min: 20

instruction: |
  mcp/plugs/__init__.py (빈) + mcp/plugs/base.py 생성.
  v0.3 §4.1 코드 그대로.

verify: |
  python3 -c "from mcp.plugs.base import Plug; print(Plug.__name__)"

outputs:
  - mcp/plugs/base.py
  - mcp/plugs/__init__.py

commit_message: "feat: Plug 추상 베이스 (T1.1.2)"
```

### Sprint 1.2 — 백그라운드 플러그 2종

#### TASK T1.2.1
```yaml
TASK: T1.2.1
title: ParksyProfilePlug (고정 가중치 1.0)
agent_primary: sonnet
sota_reference:
  - title: parksy_voice_filter.md
    url: https://github.com/dtslib1979/dtslib-papyrus/blob/main/filters/parksy_voice_filter.md
    why: 박씨 톤 마스터 필터
depends_on: [T1.1.2]
estimated_min: 15

instruction: |
  mcp/plugs/parksy_profile.py — v0.3 §4 코드 그대로
  VOICE_FILTER_PATH 로드 + frame() 에 verdict_template 반환.

verify: |
  python3 -c "
  from mcp.plugs.parksy_profile import ParksyProfilePlug
  p = ParksyProfilePlug()
  assert p.score({}) == 1.0
  print('OK')
  "

commit_message: "feat: ParksyProfilePlug (T1.2.1)"
```

#### TASK T1.2.2
```yaml
TASK: T1.2.2
title: EnvTriggerPlug (장소/날짜/애니버서리)
agent_primary: sonnet
sota_reference:
  - title: Anniversary Reaction (Solace Stone)
    url: https://solacestoneco.com/anniversary-reactions
    why: 날짜 기반 심리 트리거 검증
depends_on: [T1.1.2]
estimated_min: 25

instruction: |
  v0.3 §4 스펙 그대로.
  PARKSY_ANNIVERSARIES = {"03-13": [...]} 박기.

verify: |
  python3 -c "
  from mcp.plugs.env_trigger import EnvTriggerPlug
  v = EnvTriggerPlug().score({
      'narrative': '옛 방에서 잤다',
      'metadata': {'date': '2026-03-13'}
  })
  assert v > 0.5
  "

commit_message: "feat: EnvTriggerPlug (T1.2.2)"
```

### Sprint 1.2.5 — 5축 도메인 ISA

#### TASK T1.2.5.1
```yaml
TASK: T1.2.5.1
title: mcp/core/axes.py — 5축 추상 + 구현
agent_primary: sonnet
sota_reference:
  - title: "A Survey of LLMs in Psychotherapy"
    url: https://arxiv.org/html/2502.11095v1
    why: 심리 분석 축 설계 참고
  - title: 박씨 2026-04-24 로그 F(꿈)=Grief∘Guilt∘Eros∘Rage
    url: "~/uploads/ParksyLog_20260424_082123.md"
    why: 원천 요구사항
depends_on: [T1.1.2]
estimated_min: 30

instruction: |
  v2.1 패치 §Sprint 1.2.5.1 그대로. Grief/Guilt/Eros/Rage/Liberation.

verify: |
  python3 -c "
  from mcp.core.axes import ALL_AXES, GriefAxis, LiberationAxis
  assert len(ALL_AXES) == 5
  assert GriefAxis().extract('어머니 죽는 꿈', {'is_dream': True}) > 0.3
  "

commit_message: "feat: 5축 도메인 ISA (T1.2.5.1)"
```

#### TASK T1.2.5.2 ~ T1.2.5.4 (v2.1 패치 이식, 내용 동일)

### Sprint 1.2.6 — MENTAL_CORE 앙상블 확정

#### TASK T1.2.6.1 🔄 (v2.1 재작성)
```yaml
TASK: T1.2.6.1
title: MENTAL_CORE 앙상블 매트릭스 + 결정 로그
agent_primary: opus
sota_reference:
  - title: MentaLLaMA GitHub
    url: https://github.com/SteveKGYang/MentalLLaMA
    why: 분석 레이어 SOTA (IMHI 105K, 19K 벤치)
  - title: Mental-Alpaca 논문
    url: https://dl.acm.org/doi/10.1145/3643540
    why: Mental-Alpaca vs GPT-4 +4.8% balanced accuracy
  - title: Qwen2.5 HF
    url: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct
    why: 한국어 + Apache 2.0 + parksy LLM v4 재활용
depends_on: []
estimated_min: 40

instruction: |
  1. docs/MENTAL_CORE_SELECTION.md 작성:
     - Qwen2.5 vs MentaLLaMA vs Mental-Alpaca vs Llama-3.1 비교표
     - 7 기준 (한국어 / 도메인 / 라이선스 / FT / 추론 / 선행자산 / 비용)
     - **앙상블 결정**: Qwen2.5 (톤) + MentaLLaMA (분석)
     - Mental-Alpaca는 Phase 2 A/B 후보
  2. docs/mental_core_decision.json (구조화)
  3. 비용 영향: LoRA 1회 → 2회 ($1.50 → $3.00)

verify: |
  test -f docs/MENTAL_CORE_SELECTION.md
  python3 -c "
  import json
  d = json.load(open('docs/mental_core_decision.json'))
  assert 'ensemble' in d
  assert d['ensemble']['tone'] == 'Qwen/Qwen2.5-7B-Instruct'
  assert d['ensemble']['analysis'] == 'klyang/MentaLLaMA-chat-7B'
  "

commit_message: "docs: MENTAL_CORE 앙상블 결정 (T1.2.6.1)"
```

#### TASK T1.2.6.2
```yaml
TASK: T1.2.6.2
title: mcp/config.py — 앙상블 상수
agent_primary: opus
depends_on: [T1.2.6.1]
estimated_min: 15

instruction: |
  mcp/config.py 에 MENTAL_CORE dict. v0.3과 달리 ENSEMBLE:
  {
    "tone": {"model": "Qwen/Qwen2.5-7B-Instruct", "lora": "mcp/models/therapy-tone-lora-v1"},
    "analysis": {"model": "klyang/MentaLLaMA-chat-7B", "lora": "mcp/models/therapy-analysis-lora-v1"},
    "composition": "analysis_first_tone_second"
  }

verify: |
  python3 -c "from mcp.config import MENTAL_CORE; assert 'ensemble' in str(MENTAL_CORE).lower() or 'tone' in MENTAL_CORE"

commit_message: "feat: MENTAL_CORE 앙상블 config (T1.2.6.2)"
```

### Sprint 1.2.7 — 가드레일 시스템

#### TASK T1.2.7.1 ✅ **완료 증명 있음**
```yaml
TASK: T1.2.7.1
title: CrisisDetector 2-level 위기 감지
agent_primary: opus
sota_reference:
  - title: Verily MH Guardrail (npj Digital Medicine 2026)
    url: https://www.nature.com/articles/s41746-026-02579-5
    why: "p<0.001 높은 민감도 — 2-level 구조 근거"
  - title: Between Help and Harm
    url: https://arxiv.org/html/2509.24857v1
    why: LLM crisis 평가 벤치
  - title: Korea 1393 카테고리
    url: https://www.koreaherald.com/article/10560473
    why: 한국어 패턴 수집
status: ✅ COMPLETED 2026-04-24
proof: |
  pytest mcp/tests/test_crisis_detector.py
  → 41 passed
  L2 정탐: 10/10 = 100%
  L2 오탐:  0/20 =  0%
  박씨 2026-04-24 꿈: level=0 ✓

commit: "feat: CrisisDetector 2-level + 꿈/부정/3인칭 예외 (T1.2.7.1)"
```

#### TASK T1.2.7.2
```yaml
TASK: T1.2.7.2
title: OutputSanitizer — 의료/처방/강제형 필터
agent_primary: opus
sota_reference:
  - title: Guardrails AI
    url: https://github.com/guardrails-ai/guardrails
    why: 구조화 출력 검증 패턴
  - title: "Production LLM Guardrails 비교 (Premai)"
    url: https://blog.premai.io/production-llm-guardrails-nemo-guardrails-ai-llama-guard-compared/
    why: 다층 필터링 베스트 프랙티스
depends_on: [T1.1.2]
estimated_min: 40

instruction: |
  v2.1 §T1.2.7.2 코드 그대로. 추가로:
  - BLOCKED_PATTERNS 12개 (의료 진단, 처방)
  - SOFTEN_MAP 8개 (강제형 → 제안형)
  - 재생성 요청 시그널 리턴

verify: |
  python3 -c "
  from mcp.safety.output_sanitizer import filter
  r = filter('당신은 우울증입니다 약을 복용하세요')
  assert r.blocked
  r2 = filter('매일 산책해야 한다')
  assert r2.modified and '방법이다' in r2.output
  "

commit_message: "feat: OutputSanitizer (T1.2.7.2)"
```

#### TASK T1.2.7.3
```yaml
TASK: T1.2.7.3
title: Escalation 메시지 + 연락처 스키마
agent_primary: sonnet
sota_reference:
  - title: 중앙자살예방센터 1393
    url: https://www.spckorea.or.kr
    why: 공식 연락처
  - title: 정신건강위기상담 1577-0199
    url: https://www.mohw.go.kr/
    why: 24h 크라이시스
depends_on: []
estimated_min: 15

instruction: |
  v2.1 §T1.2.7.3 그대로.

verify: |
  python3 -c "
  from mcp.safety.escalation import escalation_response
  r = escalation_response()
  assert '1393' in r['escalation_message']
  assert '1577-0199' in r['escalation_message']
  "

commit_message: "feat: Escalation 응답 (T1.2.7.3)"
```

#### TASK T1.2.7.4
```yaml
TASK: T1.2.7.4
title: AuditLog (SQLite)
agent_primary: aider_deepseek
sota_reference:
  - title: Python sqlite3
    url: https://docs.python.org/3/library/sqlite3.html
    why: stdlib, 의존성 최소
depends_on: [T1.2.7.1]
estimated_min: 25

instruction: |
  v2.1 §T1.2.7.4 — 해시만 저장, 원문 미저장.
  DB: mcp/safety/audit.db (.gitignore)

verify: |
  python3 -c "
  from mcp.safety.audit_log import log_event, query_recent
  log_event({'crisis_level': 1, 'flagged_terms': ['힘들어']})
  assert len(query_recent(30)) >= 1
  "

commit_message: "feat: AuditLog SQLite (T1.2.7.4)"
```

#### TASK T1.2.7.5, T1.2.7.6, T1.2.7.7 (v2.1 그대로)

### Sprint 1.3 — 7 Gate 플러그 (v2.0 이식 + SOTA 참조 추가)

#### TASK T1.3.1 — FreudPlug
```yaml
TASK: T1.3.1
title: FreudPlug (Gate I)
agent_primary: opus
sota_reference:
  - title: Freud Dream Interpretation (Simply Psychology)
    url: https://www.simplypsychology.org/dream-interpretation.html
    why: 소원성취/응축/전위/초자아 개념
  - title: Stanford Encyclopedia of Philosophy - Psychoanalysis
    url: https://plato.stanford.edu/entries/psychoanalysis/
    why: 정통 이론 정리
depends_on: [T1.1.2, T0.2.1]
estimated_min: 35

instruction: |
  v2.0 §T1.3.1 그대로. cautions에 "엄마 죽이고 싶은 충동 환원 금지".

verify: |
  (v2.0 동일)

commit_message: "feat: FreudPlug Gate I (T1.3.1)"
```

#### TASK T1.3.2 — JungPlug
```yaml
sota_reference:
  - title: C.G. Jung Institute
    url: https://www.cgjungny.org/
    why: 원형/Self/개성화 정통
  - title: Jungian dream analysis guide
    url: https://www.sterlinginstitute.org/jungian-dream-analysis
    why: 지휘자=Self 상징 근거
```

#### TASK T1.3.3 — FamilySystemsPlug
```yaml
sota_reference:
  - title: Bowen Center for the Study of the Family
    url: https://www.thebowencenter.org/
    why: 분화/삼각관계/다세대 전승 이론 본산
```

#### TASK T1.3.4 — ShamanKoPlug
```yaml
sota_reference:
  - title: 한국무속학회 (KISS)
    url: https://kiss.kstudy.com/Detail/Ar?key=4026927
    why: 국내 무속 아카데믹 레퍼런스
```

#### TASK T1.3.5 — SufiPlug
```yaml
sota_reference:
  - title: "Sufi Healing and Modern Psychiatry (Mad in America)"
    url: https://www.madinamerica.com/2019/11/sufi-healing-modern-psychiatry/
    why: 수피 vs 정신의학 비교 현장 기록
```

#### TASK T1.3.6 — AyahuascaPlug
```yaml
sota_reference:
  - title: Frontiers in Psychiatry (Ayahuasca)
    url: https://www.frontiersin.org/search?query=ayahuasca%20psychiatry
    why: 의료 과학 프레임
```

#### TASK T1.3.7 — MassProtocolPlug ⭐
```yaml
sota_reference:
  - title: 한국 천주교 주교회의 미사경본
    url: https://cbck.or.kr/
    why: 6단계 전례 공식 순서
  - title: "Ritual and Mental Health (PMC)"
    url: https://pmc.ncbi.nlm.nih.gov/articles/PMC5954391/
    why: 의례의 심리학적 효과 연구
```

#### TASK T1.3.8 — NarrativeMetaPlug
```yaml
sota_reference:
  - title: Lacan's discourse theory
    url: https://nosubject.com/Four_Discourses
    why: 꿈 속 주체의 타자 욕망 되묻기
```

### Sprint 1.4 — 레지스트리 + 테스트 (v2.0 유지)

### Sprint 1.5 — LangGraph Orchestrator 🔄 **v2.0 수정**

#### TASK T1.5.1
```yaml
TASK: T1.5.1
title: LangGraph 기반 therapy_graph.py
agent_primary: opus
sota_reference:
  - title: LangGraph StateGraph tutorial
    url: https://langchain-ai.github.io/langgraph/tutorials/introduction/
    why: 본 프로젝트 그래프 구현 직접 참조
  - title: LangGraph conditional edges
    url: https://langchain-ai.github.io/langgraph/how-tos/branching/
    why: CrisisDetect → Escalate 브랜칭
depends_on: [T1.2.5.2, T1.2.7.1, T1.2.7.2, T1.2.7.3, T1.4.1]
blocks: [T1.5.2]
estimated_min: 90

instruction: |
  mcp/graph/therapy_graph.py 작성:

  from langgraph.graph import StateGraph, END, START
  from mcp.graph.state import TherapyState
  from mcp.safety.crisis_detector import detect
  from mcp.safety.escalation import escalation_response
  from mcp.safety.output_sanitizer import filter as sanitize
  from mcp.safety.audit_log import log_event
  from mcp.core.axes_weighter import axis_distribution
  from mcp.plug_orchestrator import compute_weights

  def node_crisis_check(state: TherapyState) -> TherapyState:
      v = detect(state['narrative'], state.get('metadata'))
      state['crisis_verdict'] = v.to_dict()
      return state

  def route_after_crisis(state: TherapyState) -> str:
      return "escalate" if state['crisis_verdict']['level'] == 2 else "analyze"

  def node_escalate(state: TherapyState) -> TherapyState:
      state['final_report'] = escalation_response()
      log_event({'crisis_level': 2, ...})
      return state

  def node_axis_extract(state): ...
  def node_plug_score(state): ...
  def node_axis_weight(state): ...
  def node_compose_prompt(state): ...
  def node_mentallama_analyze(state): ...
  def node_qwen_tone(state): ...
  def node_sanitize(state): ...
  def node_audit(state): ...

  def build_graph():
      g = StateGraph(TherapyState)
      g.add_node("crisis_check", node_crisis_check)
      g.add_node("escalate", node_escalate)
      g.add_node("axis_extract", node_axis_extract)
      g.add_node("plug_score", node_plug_score)
      g.add_node("axis_weight", node_axis_weight)
      g.add_node("compose_prompt", node_compose_prompt)
      g.add_node("mentallama_analyze", node_mentallama_analyze)
      g.add_node("qwen_tone", node_qwen_tone)
      g.add_node("sanitize", node_sanitize)
      g.add_node("audit", node_audit)

      g.add_edge(START, "crisis_check")
      g.add_conditional_edges("crisis_check", route_after_crisis, {
          "escalate": "escalate", "analyze": "axis_extract"
      })
      g.add_edge("escalate", END)
      g.add_edge("axis_extract", "plug_score")
      g.add_edge("plug_score", "axis_weight")
      g.add_edge("axis_weight", "compose_prompt")
      g.add_edge("compose_prompt", "mentallama_analyze")
      g.add_edge("mentallama_analyze", "qwen_tone")
      g.add_edge("qwen_tone", "sanitize")
      g.add_edge("sanitize", "audit")
      g.add_edge("audit", END)

      return g.compile()

verify: |
  python3 -c "
  from mcp.graph.therapy_graph import build_graph
  graph = build_graph()
  result = graph.invoke({
      'narrative': '어머니 돌아가시는 꿈',
      'metadata': {'is_dream': True}
  })
  assert 'crisis_verdict' in result
  assert result['crisis_verdict']['level'] == 0  # 꿈 예외
  "

commit_message: "feat: LangGraph therapy_graph (T1.5.1)"
```

### Sprint 1.6 — 데이터 수집 (v2.0 유지)

### Sprint 1.7 — LoRA 학습 2단계 🔄 **v2.0 수정**

#### TASK T1.7.1 ~ T1.7.5 — Stage 1 (Qwen2.5 톤) — v2.0 그대로

#### TASK T1.7.6 🆕 Stage 2 (MentaLLaMA 한국어 정렬)
```yaml
TASK: T1.7.6
title: MentaLLaMA 한국어 정렬 LoRA 학습
agent_primary: vastai_remote
lane: E
sota_reference:
  - title: MentaLLaMA fine-tuning notebook
    url: https://github.com/SteveKGYang/MentalLLaMA#training
    why: 공식 학습 절차
depends_on: [T1.7.5]
blocks: [T1.8.*]
estimated_min: 120
cost_estimate: $1.50

instruction: |
  Stage 1과 동일 패턴, base=MentaLLaMA-chat-7B로 교체.
  한국어 번역 layer + 박씨 도메인 300건 정렬 학습.

verify: |
  # 로컬 inference 테스트
  (Stage 3 이후)

outputs:
  - mcp/models/therapy-analysis-lora-v1/

commit_message: (원격)
```

### Sprint 1.8 — GGUF × 2 + 로컬 추론

Stage 1 Qwen + Stage 2 MentaLLaMA 둘 다 GGUF 변환 필요.

### Sprint 1.9 — MCP 서버 (LangGraph 호출)

#### TASK T1.9.1 🔄
```yaml
TASK: T1.9.1
title: mcp/server.py — LangGraph 기반 5 도구
agent_primary: opus
sota_reference:
  - title: MCP Python SDK
    url: https://github.com/modelcontextprotocol/python-sdk
    why: stdio_server 공식 패턴
depends_on: [T1.5.1]
estimated_min: 60

instruction: |
  각 도구가 build_graph().invoke(state) 호출하도록 재설계.
  v2.0 T1.9.1 의 subprocess 호출 패턴 제거.

verify: |
  python3 -c "import mcp.server; print('OK')"
  claude mcp list | grep alexandria

commit_message: "feat: MCP 서버 LangGraph 래퍼 (T1.9.1)"
```

### Sprint 1.10 — 재현 테스트

#### TASK T1.10.1 🔄 (v1.0 성공기준 반영)
```yaml
verify 추가:
  - safety_verdict.level == 0 (꿈 예외)
  - axis_profile 모두 포함
  - active_plugs 교집합 골든 ≥ 80%
  - audit_log 1건 기록
  - end-to-end latency ≤ 15초
```

---

## 4. PHASE 2 — Gate UI + SOTA 가드레일 통합 (4주, $8)

### 신규 Sprint 2.0 — 외부 가드레일 프레임워크 통합
- T2.0.1: Llama Guard 3 설치 + Input 레이어 추가 ([HF](https://huggingface.co/meta-llama/Llama-Guard-3-8B))
- T2.0.2: Guardrails AI 구조화 출력 ([Repo](https://github.com/guardrails-ai/guardrails))
- T2.0.3: NeMo Guardrails 대화 흐름 ([NVIDIA](https://github.com/NVIDIA-NeMo/Guardrails))

### Sprint 2.1 ~ 2.5 (v2.0 유지)

---

## 5. PHASE 3 — 순환 (지속, 월 $2)

(v2.0 유지)

---

## 6. 예산 재조정

| Phase | v2.1 | v3.0 | 증감 사유 |
|-------|:---:|:---:|--------|
| 0 | $0 | $0 | — |
| 1 | $2.10 | **$5.00** | MentaLLaMA 추가 학습 + 재실행 버퍼 |
| 2 | $6 | **$8** | Llama Guard/Guardrails AI/NeMo 통합 테스트 |
| 3 | $1.50/월 | $2/월 | 앙상블 재학습 |
| **Y1** | **$20** | **$30** | 현실 반영 |

---

## 7. 에이전트 디스패치 매트릭스 (v3)

| Sprint | Lane A (Opus) | Lane B (Sonnet) | Lane C (Aider) | Lane E (Vast) |
|--------|--------------|-----------------|---------------|---------------|
| 1.1 | — | — | T1.1.1, T1.1.2 | — |
| 1.2 | — | T1.2.1, T1.2.2 | — | — |
| 1.2.5 | T1.2.5.3 | T1.2.5.1, T1.2.5.2 | T1.2.5.4 | — |
| 1.2.6 | T1.2.6.1, T1.2.6.2 | — | — | — |
| 1.2.7 | T1.2.7.1✅, T1.2.7.2, T1.2.7.6 | T1.2.7.3, T1.2.7.5 | T1.2.7.4, T1.2.7.7 | — |
| 1.3 | T1.3.1, T1.3.2, T1.3.7, T1.3.8 | T1.3.3~6 | — | — |
| 1.4 | — | — | T1.4.* | — |
| 1.5 | T1.5.1 | — | — | — |
| 1.6 | — | T1.6.* | T1.6.3 | — |
| 1.7 | T1.7.1, T1.7.5 | — | T1.7.2 | T1.7.3, T1.7.6 |
| 1.8 | — | — | T1.8.* | — |
| 1.9 | T1.9.1, T1.9.2 | — | — | — |
| 1.10 | T1.10.* | — | — | — |

---

## 8. 지금 당장 호출 가능한 TASK 3개

(박씨 → 해당 Lane 세션)

```
1. phone_aider  → "T1.1.1 실행"   (LangGraph 세팅)
2. phone_claude → "T1.2.1 실행"   (ParksyProfilePlug)
3. phone_claude → "T1.2.5.1 실행" (5축 구현)
```

모두 독립 · 병렬 가능.

---

## 9. 문서 이력

| 버전 | 변경 | 근거 |
|------|------|------|
| v2.0 | 45 TASK 초안 | — |
| v2.1 | +13 (axes/MENTAL_CORE/가드레일) | Perplexity |
| **v3.0** | **SOTA 참조 + LangGraph + 앙상블 + CrisisDetector 완료 증명** | **커뮤니티 리서치** |

---

*본 DEVPLAN v3은 모든 TASK에 외부 SOTA 참조를 박아둔다.*
*에이전트가 콜드 스타트로 받아도 링크 타고 가서 근거 확인 가능.*
*CrisisDetector는 이미 증명됨. 나머지 70개도 같은 수준으로.*
