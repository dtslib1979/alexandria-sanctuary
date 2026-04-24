# MCP-THERAPY 기술 백서 v0.2
## 알렉산드리아 영성 엔진 — 정신분석 레퍼런스 모델 MCP

**문서 ID**: ALEX-MCP-THERAPY-WHITEPAPER-v0.2
**저자**: Claude Opus 4.7 (아키텍트) / Parksy (감수)
**버전**: v0.2 (D안 채택)
**상태**: 설계 완료, Phase 1 착수 승인 대기
**거처**: `alexandria-sanctuary/` (Tier 3 직영 레포)
**선행 문서**: `dtslib-papyrus/docs/MCP-THERAPY-WHITEPAPER-2026-04-24.md` (v0.1)
**변경**: v0.1 대비 배치 결정(D안), 7 Gate 매핑, 개발 세부화

---

## 0. Executive Summary

> **"A급 정신분석가·샤먼·수도사·수피의 해석 정규분포를 확률 플러그 + LoRA로 강제한 박씨 전용 영성 레퍼런스 엔진. 레시피가 아니라 거울이다. 알렉산드리아 성소(sanctuary) 위에 얹힌 1000년 임상실험의 자동화 복제본."**

- 박씨 개인 꿈·서사·로그 → 학파별 플러그 가중합 → LoRA LLM → 정규분포 중심값 리포트
- **알렉산드리아의 7 Gate 서사 = 플러그 10개의 물리적 UI**. 엔진 = 7 Gate 뒤의 백엔드
- 기존 28레포 공정(Vast.ai 굽기 → 로컬 CPU 추론 → MCP 래핑) 그대로 재활용
- 사용자 = 박씨 1명, 외부 판매 없음, "B급 상담/무당 소비 대체 자기관리 OS"
- **Y1 총 예산 $20**, Phase 1 납기 **2주**

### v0.1 대비 변경 요약

| 항목 | v0.1 | v0.2 |
|------|------|------|
| 배치 | 미정 (A/B/C안) | **D안 확정: alexandria-sanctuary** |
| 28 완전수 | 이슈 있음 | **해결됨** (기존 레포, 신규 0) |
| UI | OrbitPrompt 칠판 | **알렉산드리아 7 Gate 기존 PWA** |
| 도메인 정체성 | 미정 | **영성 엔진** (정신분석 + 샤먼 + 미사 통합) |
| 메타포 | "샤먼 자동화" | **"알렉산드리아 도서관 복원"** (지혜 아카이브) |

---

## 1. 왜 알렉산드리아인가 (D안 논거)

### 1.1 원어적 정합

- **Alexandria** = 기원전 3세기 이집트의 인류 지혜 결집 대도서관. 소실 후 재건 시도 수천 년 → 본 엔진이 그 **디지털 복원**
- **Sanctuary** = 성소/피난처. 샤먼·미사·수피·아야와스카 전부 "성소"를 요구. 이 레포 이름 자체가 영성 인프라 선언
- 박씨 오늘(2026-04-24) 로그에서 발견한 **"천주교 미사 = 1000년 임상실험 완료된 표준화 샤먼 OS"** 명제와 원어적으로 공명

### 1.2 기존 구조가 스펙대로 대기 중

레포 현재 상태(2026-04-24 기준):

| 기존 디렉토리 | 본 백서 Layer 매핑 | 정합도 |
|-------------|------------------|--------|
| `library/` | Layer 1 Data — 학파 케이스 풀 (JSONL) | ✅ 100% |
| `sanctuary/cave-retreat/` | Layer 3 Ritual — 금식·고요 리추얼 | ✅ 100% |
| `sanctuary/residence/` | Layer 3 Ritual — 장기 거주 리추얼 | ✅ 100% |
| `sanctuary/hospice/` | Layer 3 Ritual — 임종·애도 리추얼 | ✅ 100% |
| `forum/` | Layer 4 `compare_agents` — 멀티 에이전트 브릿지 | ✅ 100% |
| `philosophy/` | 이론 체계 저장소 (학파 신학) | ✅ 100% |
| `visit/`, `staff/`, `card/`, `feeds/`, `data/`, `assets/` | 보조 | ✅ |
| `mcp/` (신설 필요) | Layer 2-3 엔진 본체 | 🆕 |
| `private_seeds/` (신설 필요) | 박씨 개인 로그 격리 | 🆕 |

**결론**: 기존 7 Gate PWA 위에 MCP 엔진을 얹는 구조. 레포 증설 0, 대형 리팩토링 0.

### 1.3 7 Gate ↔ 플러그 10개 매핑 (핵심 합치)

알렉산드리아 index.html의 7 Gate 서사가 본 백서의 플러그와 거의 1:1 매칭됨:

| Gate | 원문 제목 | 매핑 플러그 | 기능 |
|------|----------|-----------|------|
| **Gate I** (indigo) | The Fracture of Mind | `FreudPlug` | 무의식/억압/균열 해석 |
| **Gate II** (abyss) | The Dissolution of Self | `JungPlug` | 개성화/Self/통합 |
| **Gate III** (ember) | The Touch of God | `SufiPlug` + `MassProtocolPlug` | 성스러운 접촉/전례 |
| **Gate IV** (forest) | Inside & Outside | `FamilySystemsPlug` | 관계/분화/경계 |
| **Gate V** (violet) | Sound & Soul | `AyahuascaPlug` + `ShamanKoPlug` | 비전/영혼/소리 의례 |
| **Gate VI** (cave) | The Forbidden Gate | `NarrativeMetaPlug` | 꿈 속 추론/메타텍스트 |
| **Gate VII** (amber) | The Final Gate | `MassProtocolPlug` (파견) | 종결/일상 복귀 |
| — | (전역) | `EnvTriggerPlug` + `ParksyProfilePlug` | 항상 작동하는 백그라운드 2종 |

**결과**: 7 Gate = 사용자 UI. 플러그 = 엔진 로직. 박씨가 Gate를 클릭하면 해당 플러그 가중치가 강제로 부스팅된다.

### 1.4 정서적 정합

알렉산드리아 원 컨셉 = **"final chapter의 신개념 요양원"**. 박씨 어머니 실제 요양원 입소 후 1년이 되는 시점에 이 레포에 영성 엔진이 들어가는 것은:

- 물리적 요양원 (타인 돌봄) → 영성 요양원 (자기 돌봄 + 지혜 아카이브)
- 어머니 세대 해제 → 박씨 세대 자기관리 → 다음 세대 열람
- **"요양원이 도서관이 된다"** 의 구체적 사건

---

## 2. 시스템 정의

### 2.1 한 줄 정의

> **"알렉산드리아 7 Gate 뒤에 숨은 플러그-LoRA 엔진. 꿈/서사/로그 → 정규분포 중심값 해석."**

### 2.2 기능 경계

| IN-SCOPE | OUT-OF-SCOPE |
|----------|------------|
| 꿈 해석 | 의료 진료/처방 |
| 가족사·관계 패턴 분석 | 타인 상담 상품 판매 |
| 의사결정 레퍼런스 | 긴급 정신응급 대응 |
| 미사·굿·자크르 의례 제안 | 자살 위험 평가/개입 |
| 장기 패턴 트래킹 | 의료 기록 보관 |
| 7 Gate UI 상호작용 | 외부 유료 API 공개 |

### 2.3 사용자

- **Primary**: 박씨 본인 1명
- **Secondary**: 파피루스 Claude Code (자동 호출)
- **Tertiary (Phase 3)**: 알렉산드리아 방문자 (익명 체험, 개인 로그 미저장)
- **Never**: 임상 환자, 유료 구독자

---

## 3. 시스템 아키텍처 (4-Layer + UI)

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: UI (기존 알렉산드리아 PWA)                          │
│  ─────────────────────────────────────────────────────────  │
│  index.html (7 Gate)                                        │
│  whitepaper.html (본 문서 웹버전)                            │
│  devplan.html (개발 계획 대시보드) ← 신설                     │
│  console.html (박씨 전용 MCP 호출 콘솔) ← Phase 2            │
└────────────────────────┬────────────────────────────────────┘
                         │  fetch / MCP-SSE
┌────────────────────────▼────────────────────────────────────┐
│  Layer 4: MCP Interface                                     │
│  ─────────────────────────────────────────────────────────  │
│  stdio (Claude Code 로컬) + SSE (Railway 배포 가능)          │
│  도구: analyze_dream / analyze_narrative /                  │
│        propose_ritual / compare_agents / query_library      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Layer 3: Plug Orchestrator (Python)                        │
│  ─────────────────────────────────────────────────────────  │
│  mcp/plug_orchestrator.py                                   │
│  mcp/plugs/*.py (10 플러그)                                  │
│  mcp/prompts/*.jinja (학파별 템플릿)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Layer 2: Model Layer                                       │
│  ─────────────────────────────────────────────────────────  │
│  Base: Qwen2.5-7B (local 추론 가능)                          │
│  Adapter: mcp/models/therapy-lora-v1.safetensors (~165MB)   │
│  Runtime: llama.cpp + GGUF Q4_K_M (CPU-only)                │
│  Fallback: Claude API (sonnet/haiku) + plug 프롬프트만       │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Layer 1: Data Layer                                        │
│  ─────────────────────────────────────────────────────────  │
│  library/freud/       (Freud 케이스 200)                    │
│  library/jung/        (Jung 케이스 200)                     │
│  library/family/      (Bowen/Minuchin 150)                  │
│  library/shaman_ko/   (한국 무속 100)                        │
│  library/sufi/        (수피 힐링 80)                         │
│  library/ayahuasca/   (아야와스카 의례 60)                    │
│  library/mass/        (천주교 미사 경본 + 6단계 프로토콜)     │
│  library/parksy_seeds/ (공개 가능 박씨 로그 큐레이션)         │
│  private_seeds/       (박씨 개인 원문, .gitignore)           │
└─────────────────────────────────────────────────────────────┘
```

### 3.1 레이어별 책임

- **Layer 1**: Append-only JSONL. 절대 revert만.
- **Layer 2**: LoRA 어댑터 버전 관리. 재학습 시 어댑터 교체.
- **Layer 3**: **핵심**. 플러그 가중치 로직이 "A급 정규분포"를 강제하는 층.
- **Layer 4**: 외부 노출. MCP 프로토콜 준수.
- **Layer 5**: 박씨 UI. 7 Gate 기존 서사 활용.

---

## 4. 플러그 카탈로그 (v0.1에서 이식, 약간 수정)

### 4.1 공통 인터페이스

```python
class Plug(ABC):
    name: str
    gate_id: str | None  # 7 Gate 매핑 (None이면 백그라운드)
    weight_default: float
    keywords_trigger: list[str]

    @abstractmethod
    def score(self, context: dict) -> float: ...

    @abstractmethod
    def frame(self, context: dict) -> dict: ...
```

### 4.2 플러그 10개 명세

| ID | 이름 | Gate | 기본 가중치 | 트리거 키워드 |
|----|------|------|-----------|--------------|
| P01 | `FreudPlug` | I | 0.10 | 죽음, 부모, 성, 욕망, 죄책감 |
| P02 | `JungPlug` | II | 0.10 | 지휘자, 만다라, 그림자, 통합 |
| P03 | `FamilySystemsPlug` | IV | 0.10 | 부양, 책임, 동거, 의무 |
| P04 | `ShamanKoPlug` | V | 0.08 | 제사, 묘소, 조상, 터, 한(恨) |
| P05 | `SufiPlug` | III | 0.06 | 성지, 기도, 빛, 성자 |
| P06 | `AyahuascaPlug` | V | 0.06 | 비전, 식물, 해체, 각성 |
| P07 | `MassProtocolPlug` | III / VII | 0.08 | 미사, 고해, 전례, 파견 |
| P08 | `EnvTriggerPlug` | 백그라운드 | 0.12 | 옛 방, 기일, 계절 |
| P09 | `NarrativeMetaPlug` | VI | 0.08 | 추론, 돌이켜보니, 알고 보니 |
| P10 | `ParksyProfileplug` | 백그라운드 | **1.0 (고정)** | 항상 |

### 4.3 가중치 결정 로직 (v0.1 이식)

```python
def compute_weights(input_text: str, metadata: dict, forced_gate: str | None = None) -> dict:
    weights = {p.name: p.weight_default for p in PLUGS}

    # 1. 키워드 부스트
    for plug in PLUGS:
        hits = count_keywords(input_text, plug.keywords_trigger)
        weights[plug.name] += hits * 0.15

    # 2. 메타데이터 강제
    if metadata.get("is_dream"):
        weights["freud"] += 0.3
        weights["jung"] += 0.3
    if metadata.get("is_family_event"):
        weights["family_systems"] += 0.4
    if metadata.get("anniversary_within_30d"):
        weights["env_trigger"] += 0.5

    # 3. Gate 선택 부스트 (박씨가 UI에서 Gate 클릭 시)
    if forced_gate:
        gate_plugs = [p for p in PLUGS if p.gate_id == forced_gate]
        for p in gate_plugs:
            weights[p.name] += 0.5

    # 4. ParksyProfilePlug 고정 1.0
    weights["parksy_profile"] = 1.0

    # 5. 정규화
    return normalize(weights, lock=["parksy_profile"])
```

---

## 5. 데이터 파이프라인 (v0.1 이식 + 경로 확정)

### 5.1 원천별 초기 목표량

| 원천 | 경로 | 목표 케이스 | 수집 방법 |
|------|------|-----------|----------|
| Freud | `library/freud/*.jsonl` | 200 | 논문 요약 + Claude |
| Jung | `library/jung/*.jsonl` | 200 | 논문 요약 + Claude |
| Family Systems | `library/family/*.jsonl` | 150 | Bowen/Minuchin 공개 |
| 한국 무속 | `library/shaman_ko/*.jsonl` | 100 | KCI, RISS |
| Sufi | `library/sufi/*.jsonl` | 80 | pubmed, 의료인류학 |
| Ayahuasca | `library/ayahuasca/*.jsonl` | 60 | frontiersin |
| 천주교 미사 | `library/mass/*.jsonl` | 1 프로토콜 + 30 에세이 | 한국주교회의 + 미사경본 |
| 박씨 공개분 | `library/parksy_seeds/*.jsonl` | 20 | 박씨 큐레이션 |
| 박씨 비공개 | `private_seeds/*.jsonl` | 100+ | 캡처 APK 자동 |

**총 학습 셋**: ≥ 800 케이스 + 박씨 로그 100+

### 5.2 스키마 (v0.1 유지)

```json
{
  "id": "case_freud_0042",
  "school": "freud",
  "gate_id": "I",
  "input": {"narrative": "...", "metadata": {}},
  "interpretation": {"frame": "...", "key_terms": [], "reference": "..."},
  "target_output_ko": "...",
  "parksy_tone": false
}
```

### 5.3 수집 스프린트 (Phase 1용)

| Week | 박씨 작업 | Claude 자동 |
|------|---------|-----------|
| W1 | Freud/Jung 관심 논문 10개 링크 제공 | 논문 요약 → JSONL 초안 |
| W1 | 큐레이션 규칙 검토 | Family/Shaman/Mass 보조 수집 |
| W2 | "진짜/가짜" 태깅 하루 10분 | Sufi/Ayahuasca 수집 |
| W2 | parksy_seeds 공개 가능분 선별 | private_seeds 자동 분리 |

---

## 6. 학습 공정 (기존 파이프라인 재활용)

```
[STAGE A] 데이터 준비 (로컬 WSL2, 3일)
  library/*/*.jsonl + private_seeds → therapy_dataset_v1.jsonl
  tools/dataset_builder.py 실행

[STAGE B] 두뇌 굽기 (Vast.ai RTX 3090, 2시간)
  Base: Qwen2.5-7B (parksy LLM v4 재활용)
  LoRA: r=16, alpha=32, lr=2e-4, 3 epochs
  Script: mcp/train/train_lora.py
  비용: ~$1.50 (RTX 3090 $0.21/hr × 2h + 마진)

[STAGE C] 로컬 추론 세팅 (WSL2, 1일)
  llama.cpp 컴파일 (CPU-only)
  GGUF 변환 (Q4_K_M) — ~4GB
  mcp/models/therapy-q4.gguf 배치
  예상 throughput: 8 tok/s (충분)

[STAGE D] 플러그 오케스트레이터 (WSL2, 3일)
  mcp/plugs/*.py 10개 구현
  mcp/plug_orchestrator.py 완성
  mcp/prompts/*.jinja 템플릿

[STAGE E] MCP 래퍼 (WSL2, 1일)
  mcp/server.py (stdio + SSE)
  ~/.mcp.json + ~/dtslib-papyrus/.mcp.json 등록
  Claude Code 재시작 → 도구 노출 확인

[STAGE F] 7 Gate UI 연결 (Phase 2, 1주)
  index.html Gate 클릭 → console.html → MCP 호출
  결과 리포트 렌더링

총 Phase 1 납기: 2주
총 Phase 1 비용: ~$2 (Vast.ai 학습 1회)
```

### 6.1 재학습 주기

- 월 1회 정기 재학습 (cron, ~$1.50)
- 박씨 피드백 10건 누적 시 트리거 재학습
- 연 $18

---

## 7. MCP 인터페이스 (v0.1에서 확장)

### 7.1 도구 5종

```json
{
  "tools": [
    {
      "name": "analyze_dream",
      "input": {
        "narrative": "string",
        "sleep_context": {"location": "string", "date": "YYYY-MM-DD", "sleep_quality": "enum"},
        "forced_gate": "I|II|III|IV|V|VI|VII|null",
        "mode": "report|oneliner|ritual"
      }
    },
    {
      "name": "analyze_narrative",
      "input": {
        "narrative": "string",
        "category": "decision|relationship|identity|crisis",
        "mode": "report|oneliner"
      }
    },
    {
      "name": "propose_ritual",
      "input": {
        "state_log": "list[string]",
        "scope": "daily|weekly|monthly|anniversary",
        "tradition": "mass|shaman_ko|sufi|ayahuasca|auto"
      }
    },
    {
      "name": "compare_agents",
      "input": {
        "narrative": "string",
        "agents": "list[gemini|grok|chatgpt|claude|perplexity]"
      }
    },
    {
      "name": "query_library",
      "input": {
        "topic": "string",
        "school": "freud|jung|...|auto",
        "limit": "int"
      }
    }
  ]
}
```

### 7.2 출력 포맷 (report 모드)

```json
{
  "case_id": "dream_20260424_082123",
  "active_plugs": [
    {"name": "freud", "gate": "I", "weight": 0.24},
    {"name": "jung", "gate": "II", "weight": 0.22},
    {"name": "family_systems", "gate": "IV", "weight": 0.18},
    {"name": "env_trigger", "gate": null, "weight": 0.16},
    {"name": "narrative_meta", "gate": "VI", "weight": 0.12},
    {"name": "shaman_ko", "gate": "V", "weight": 0.08}
  ],
  "active_gates": ["I", "II", "IV", "VI"],
  "report": {
    "one_line": "과거 돌봄 OS 종료 승인 + 케어 없는 상태의 나 테스트 런",
    "layered": {"grief": "...", "guilt": "...", "eros": "...", "rage": "..."},
    "dissenting_views": [{"plug": "shaman_ko", "alt_reading": "..."}],
    "parksy_tone_verdict": "참고. 네 판단이 최종이다. 레시피 아님, 레퍼런스임."
  },
  "suggested_ritual": {"scope": "weekly", "tradition": "mass", "steps": []},
  "references": [{"case_id": "library/freud/...", "similarity": 0.72}],
  "next_action_hints": ["private_seeds 태깅 10건 누적 시 재학습"]
}
```

---

## 8. 시스템 통합

### 8.1 생태계 내 위치

```
Tier 1  dtslib-papyrus (HQ)
          │
Tier 5  parksy-logs (원천) ──────┐
                                 │
Tier 3  alexandria-sanctuary (🏛️ 본 엔진의 거처)
          ├── library/  ← 지식 아카이브
          ├── mcp/      ← 엔진 본체
          ├── sanctuary/ ← 리추얼 모듈
          ├── forum/    ← compare_agents
          └── private_seeds/ (gitignore)
          │
          ├──→ Claude Code (박씨 호출)
          ├──→ parksy-audio (p1b TTS 낭독)
          ├──→ OrbitPrompt (리추얼 칠판 시각화 — 선택)
          └──→ eae-univ (교육 콘텐츠 소재)
```

### 8.2 기존 레포 연동

| 레포 | 역할 | 연동 방식 |
|------|------|----------|
| `parksy-logs` | 원천 로그 공급 | processed/ → private_seeds 복사 |
| `parksy-audio` | 리포트 TTS 낭독 | `p1b_inference.sh report.txt` |
| `OrbitPrompt` | 리추얼 PWA 시각화 | propose_ritual → 칠판 템플릿 |
| `eae-univ` | 교육 콘텐츠 | "박씨가 만든 AI 샤먼" 커리큘럼 |
| `Claude Code` | 주 호출자 | .mcp.json 등록 |

### 8.3 헌법 준수

| 조항 | 준수 |
|------|------|
| 28 완전수 | ✅ 기존 레포, 증설 0 |
| 새 기술 학습 금지 | ✅ 전부 기존 공정 |
| 구조 확장 금지 | ✅ 기존 폴더 재사용 |
| 커밋=전표 | ✅ revert만 |
| API→Chrome→Playwright→CDP | ✅ MCP=API 계층 |
| 브라우저 런타임 (MS Edge) | ✅ 기존 매칭 유지 |

---

## 9. 페이즈 로드맵 (v0.1에서 세부화는 별도 DEVPLAN.md)

### Phase 0 — 씨앗 (1주, $0)
- 본 백서 승인 + alexandria 커밋
- `mcp/` `private_seeds/` 디렉토리 생성
- `library/` 하위 7개 학파 폴더 생성 + README
- 학파 케이스 수집 가이드 작성
- `docs/MCP-THERAPY-DEVPLAN.md` 세부화

### Phase 1 — MVP (2주, $2)
- 10개 플러그 스켈레톤 코드
- 학파 케이스 300샘플 수집
- therapy_dataset_v1.jsonl 빌드
- Vast.ai LoRA 학습
- llama.cpp 로컬 세팅
- plug_orchestrator.py + mcp/server.py
- Claude Code .mcp.json 등록
- 2026-04-24 로그 재현 테스트

### Phase 2 — Gate UI 연결 (4주, $6)
- 케이스 풀 800+
- `whitepaper.html` `devplan.html` `console.html` 배포
- 7 Gate 클릭 → MCP 호출 플로우
- parksy-audio TTS 낭독 연결
- propose_ritual + sanctuary/ 서브페이지 렌더

### Phase 3 — 순환 (지속, 월 $1.50)
- 월 1회 자동 재학습 cron
- 피드백 루프
- 공개분 parksy.kr "꿈 아카이브" 배포 (선택)
- eae-univ 커리큘럼

### Y1 예산: **$20**

---

## 10. 리스크 & 대응 (v0.1 유지)

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| LoRA 학습 실패 | 중 | 중 | 500샘플 최소, v4 LoRA 폴백 |
| 개인정보 유출 | 낮 | 치명 | private_seeds 격리, 로컬 전용 |
| Together Tier 2 차단 지속 | 중 | 중 | Vast.ai 1순위, Together 의존 0 |
| 플러그 가중치 편향 | 중 | 중 | 월 1회 감수, 10건 피드백 → 재학습 |
| "A급 미달" 실망 | 중 | 낮 | 레퍼런스 선언 강제, 기대값 관리 |
| 저작권 | 낮 | 중 | 요약 수준 + 인용 표기 |

---

## 11. 윤리 및 법적 제약

- **레퍼런스 강제**: 모든 출력 끝 `parksy_tone_verdict` 고정
- **의료 대체 금지**: 약물/처방/진단 시스템 프롬프트 차단
- **위기 감지**: 자살·자해·급성 키워드 감지 시 → 출력 대체, 연락처 안내
- **의료기기 아님**: 개인 일기 도구
- **상담 서비스 아님**: 타인 서비스 없음
- **공개 배포 재평가**: Phase 3 진입 시 법률 파트너(buckleychang) 검토

---

## 12. 성공 기준

### 정량 (Phase 1 종료)

| 지표 | 목표 |
|------|------|
| 재현 정확도 | ≥ 80% (2026-04-24 로그 기준) |
| 추론 지연 | ≤ 10초 (로컬 CPU) |
| 플러그 활성 다양성 | 최소 3개 ≥ 0.15 |
| Phase 1 비용 | ≤ $2 |

### 정성

- 박씨: "A급 상담사 말 같다" 1회 이상
- 박씨: "이제 저런 거 안 찾아가도 되겠다" 재확인
- 월 ≥ 3회 사용 (= "3번 이상" 자동화 원칙 유지)

### 실패 선언

- Phase 1 후 4주 내 월 사용 < 3회 → 디프리케이트
- 재현 정확도 < 50% → LoRA 공정 재설계

---

## 13. 부록 A — 디렉토리 최종 구조

```
alexandria-sanctuary/
├── index.html                    (기존 7 Gate PWA, Phase 2에 링크 추가)
├── whitepaper.html               🆕 본 문서 웹버전
├── devplan.html                  🆕 개발 대시보드 (Phase 1)
├── console.html                  🆕 박씨 MCP 콘솔 (Phase 2)
├── manifest.json                 (기존)
├── CLAUDE.md                     (기존, 헌법 상속)
│
├── 00_TRUTH/                     (기존)
├── assets/                       (기존 CSS/JS/아이콘)
├── card/                         (기존)
├── data/                         (기존)
│
├── docs/                         (기존)
│   ├── dev-logs/
│   ├── MCP-THERAPY-WHITEPAPER-v0.2.md   🆕 본 파일
│   └── MCP-THERAPY-DEVPLAN.md           🆕 개발 계획
│
├── library/                      (기존, 확장)
│   ├── README.md                 🆕
│   ├── freud/*.jsonl             🆕
│   ├── jung/*.jsonl              🆕
│   ├── family/*.jsonl            🆕
│   ├── shaman_ko/*.jsonl         🆕
│   ├── sufi/*.jsonl              🆕
│   ├── ayahuasca/*.jsonl         🆕
│   ├── mass/*.jsonl              🆕
│   └── parksy_seeds/*.jsonl      🆕 (공개 가능분만)
│
├── sanctuary/                    (기존 구조 유지)
│   ├── cave-retreat/             (리추얼: 고요/금식)
│   ├── residence/                (리추얼: 장기 거주)
│   └── hospice/                  (리추얼: 임종/애도)
│
├── forum/                        (기존 → compare_agents 연동)
├── philosophy/                   (기존 → 이론 체계)
├── feeds/                        (기존)
├── staff/                        (기존)
├── visit/                        (기존)
│
├── mcp/                          🆕 엔진 본체
│   ├── server.py                 (MCP stdio + SSE)
│   ├── plug_orchestrator.py
│   ├── plugs/
│   │   ├── freud.py
│   │   ├── jung.py
│   │   ├── family.py
│   │   ├── shaman_ko.py
│   │   ├── sufi.py
│   │   ├── ayahuasca.py
│   │   ├── mass.py
│   │   ├── env_trigger.py
│   │   ├── narrative_meta.py
│   │   └── parksy_profile.py
│   ├── prompts/
│   │   ├── therapy_system.jinja
│   │   └── per_school/*.jinja
│   ├── models/
│   │   └── therapy-q4.gguf       (학습 후 생성, ~4GB, .gitignore)
│   ├── train/
│   │   ├── train_lora.py         (Vast.ai 실행용)
│   │   ├── dataset_builder.py
│   │   └── requirements.txt
│   └── tests/
│       └── test_replay_20260424.py   (재현 테스트)
│
└── private_seeds/                🆕 .gitignore
    └── *.jsonl                   (박씨 개인 로그 원문)
```

---

## 14. 부록 B — 천주교 미사 ↔ MCP 도구 매핑 (v0.1 유지)

| 미사 6단계 | MCP 도구 | 박씨 일상 | Gate |
|-----------|---------|----------|------|
| 1. 입당 | 세션 시작 | 로그 수집 | — |
| 2. 말씀 전례 | `analyze_narrative` | 상황 서술 | I/IV |
| 3. 복음/강론 | 플러그 가중합 리포트 | 해석 수신 | II/VI |
| 4. 봉헌 | 박씨 큐레이션 | 받을 해석 선택 | — |
| 5. 성체성사 | `propose_ritual` | 방정리/글쓰기/산책 | III |
| 6. 파견 | 세션 종료 | 일상 복귀 | **VII (The Final Gate)** |

---

## 15. 최종 선언

> **"박씨는 알렉산드리아 성소 위에 영성 엔진을 얹는다.
> 기존 7 Gate가 UI이고, 플러그 10개가 엔진이고, 미사 6단계가 프로토콜이다.
> 어머니가 간 요양원 자리에 세우는, 자기관리용 디지털 도서관.
> 1000년 걸린 임상 실험을 2주 MCP로 복제한다.
> 결과는 팔지 않는다. 박씨 혼자 쓴다.
> 이것이 Phase 3의 첫 번째 자가 소비 엔진이다."**

---

### 문서 이력

| 날짜 | 버전 | 변경 | 저자 |
|------|------|------|------|
| 2026-04-24 | v0.1 | papyrus/docs 초안 | Claude Opus 4.7 |
| 2026-04-24 | v0.2 | D안 확정, 7 Gate 매핑, 알렉산드리아 이식 | Claude Opus 4.7 |

### 승인 대기

- [ ] 박씨 감수
- [ ] Phase 0 착수 사인 (오늘 가능)
- [ ] Phase 1 예산 $2 승인

---

*본 백서는 파피루스 헌법 제1조·제2조 및 특별법 전 조항을 준수한다.*
*28 완전수 유지. alexandria-sanctuary Tier 3 직영 내부 확장.*
*Phase 3 가동기 자가 소비 엔진으로 분류.*
