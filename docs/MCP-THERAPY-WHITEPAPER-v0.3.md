# MCP-THERAPY 기술 백서 v0.3
## 알렉산드리아 영성 엔진 — 정신분석 레퍼런스 모델 MCP

**문서 ID**: ALEX-MCP-THERAPY-WHITEPAPER-v0.3
**저자**: Claude Opus 4.7 (아키텍트) / Parksy (감수)
**버전**: v0.3 (Domain ISA + MENTAL_CORE + Guardrail 통합)
**상태**: 설계 완료, Phase 1 착수 승인 대기
**거처**: `alexandria-sanctuary/` (Tier 3 직영 레포)
**선행 문서**:
- v0.1 `dtslib-papyrus/docs/MCP-THERAPY-WHITEPAPER-2026-04-24.md`
- v0.2 `alexandria-sanctuary/docs/MCP-THERAPY-WHITEPAPER-v0.2.md`
**v0.3 변경 요약**:
- Perplexity 감수 지적 3개 완전 반영
- **도메인 ISA 5축(axes)** 추가 — 플러그 위에 올라가는 분석 좌표계
- **MENTAL_CORE 선정 매트릭스** — 베이스 모델 비교 + 확정 근거
- **Guardrail 시스템 독립 설계** — CrisisDetector + OutputSanitizer + Escalation
- 자기평가 반영 (8.0 → 9.0+ 목표)

---

## 목차

0. Executive Summary
1. Why Alexandria (D안 논거)
2. 시스템 정의
3. 시스템 아키텍처 (5-Layer)
4. 플러그 카탈로그 (10개)
5. **도메인 ISA — 5축(axes) 체계 🆕**
6. **MENTAL_CORE 선정 매트릭스 🆕**
7. 데이터 파이프라인
8. 학습 공정
9. MCP 인터페이스 (5 도구)
10. **가드레일 시스템 🆕**
11. 시스템 통합
12. 페이즈 로드맵
13. 리스크 & 대응
14. 윤리 및 법적 제약
15. 성공 기준
16. 부록 A — 디렉토리 최종 구조
17. 부록 B — 미사 프로토콜 매핑
18. 부록 C — axes × plugs 매트릭스
19. 부록 D — 가드레일 키워드 사전

---

## 0. Executive Summary

> **"A급 정신분석가·샤먼·수도사·수피의 해석 정규분포를 확률 플러그 + 5축 도메인 ISA + LoRA로 강제한 박씨 전용 영성 레퍼런스 엔진. 가드레일 내장. 1000년 미사 임상의 디지털 복원. 레시피 아님, 거울."**

### v0.2 대비 핵심 추가

| 항목 | v0.2 | v0.3 |
|------|------|------|
| 분석 좌표계 | 플러그 10개만 | **플러그 10 × 축 5 매트릭스** |
| 베이스 모델 | Qwen2.5 단정 | **3 후보 비교 → Qwen2.5 확정** |
| 가드레일 | §11 언급 수준 | **독립 §10 + 4 모듈 + 독립 TASK** |
| 위기 감지 | 수동 | **CrisisDetector 2-level 자동** |
| 출력 검증 | 없음 | **OutputSanitizer 패턴 차단** |
| 에스컬 경로 | 없음 | **1393/1577-0199 자동 안내** |

### 예산 & 납기 (v0.2와 동일)

- Phase 1 MVP: 2주 / $2
- Y1 총: $20
- 운영 비용: 월 $1.50

---

## 1. Why Alexandria (D안 논거, v0.2 유지)

### 1.1 원어적 정합

- **Alexandria** = 기원전 3세기 인류 지혜 대도서관. 디지털 복원.
- **Sanctuary** = 성소/피난처. 샤먼·미사·수피·아야와스카 공통 요구.
- **7 Gate** = 기존 UI가 플러그 10개와 1:1 매칭.

### 1.2 기존 구조 재사용

기존 `library/`, `sanctuary/{cave-retreat,residence,hospice}`, `forum/`, `philosophy/` 전부 스펙대로 대기 중. 신규 폴더: `mcp/`, `private_seeds/`만.

### 1.3 28 완전수 유지

신규 레포 증설 0. 기존 Tier 3 직영 레포 내부 확장.

### 1.4 정서적 정합

- 물리적 요양원 → 영성 요양원
- 어머니 세대 해제 → 박씨 자기관리 → 다음 세대 열람
- "요양원이 도서관이 된다"

---

## 2. 시스템 정의

### 2.1 한 줄 정의

> **"알렉산드리아 7 Gate UI + 10 플러그 + 5축 ISA + MENTAL_CORE LoRA + 가드레일 4 모듈. 박씨 1인용 영성 레퍼런스 엔진."**

### 2.2 기능 경계

| IN-SCOPE | OUT-OF-SCOPE |
|----------|-------------|
| 꿈 해석 | 의료 진료/처방 |
| 가족사·관계 패턴 분석 | 타인 상담 상품 판매 |
| 의사결정 레퍼런스 | 긴급 정신응급 대응 |
| 미사·굿·자크르 의례 제안 | **자살 위기 직접 개입** (→ 가드레일 §10 이관) |
| 장기 패턴 트래킹 | 의료 기록 보관 |
| 7 Gate UI 상호작용 | 외부 유료 API 공개 |

### 2.3 사용자

- **Primary**: 박씨 본인 1명
- **Secondary**: 파피루스 Claude Code (자동 호출)
- **Tertiary (Phase 3)**: 익명 방문자 (개인 로그 미저장)
- **Never**: 임상 환자, 유료 구독자

---

## 3. 시스템 아키텍처 (5-Layer + Safety Cross-Cut)

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: UI (알렉산드리아 PWA)                              │
│  index.html(7 Gate) · whitepaper.html · devplan.html ·      │
│  console.html(박씨 콘솔)                                     │
└────────────────────────┬────────────────────────────────────┘
                         │  fetch / MCP-SSE
┌────────────────────────▼────────────────────────────────────┐
│  Layer 4: MCP Interface                                     │
│  analyze_dream · analyze_narrative · propose_ritual ·       │
│  compare_agents · query_library                             │
└────────────────────────┬────────────────────────────────────┘
                         │ ◀────────── SAFETY CROSS-CUT ─────┐
                         │                                   │
┌────────────────────────▼────────────────────────────────────┐
│  Layer 3: Plug Orchestrator + Axes                          │
│  ─────────────────────────────────────────────────────────  │
│  • plug_orchestrator.py — 10 플러그 가중합                  │
│  • axes.py — 5축(Grief/Guilt/Eros/Rage/Liberation) 추출 🆕 │
│  • axes_weighter.py — plug × axis 매트릭스 🆕               │
│  • prompts/therapy_system.jinja — 최종 합성                  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Layer 2: MENTAL_CORE                                       │
│  ─────────────────────────────────────────────────────────  │
│  Base: Qwen2.5-7B-Instruct (선정 근거 §6)                   │
│  Adapter: therapy-lora-v1.safetensors (~165MB)              │
│  Runtime: llama.cpp + GGUF Q4_K_M (CPU)                     │
│  Fallback: Claude Haiku API (긴급 시)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Layer 1: Data Layer                                        │
│  library/{freud,jung,family,shaman_ko,sufi,ayahuasca,mass}/ │
│  library/parksy_seeds/ (공개)                                │
│  private_seeds/ (.gitignore — 박씨 원문)                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  SAFETY CROSS-CUT (모든 레이어 관통) 🆕                      │
│  ─────────────────────────────────────────────────────────  │
│  • safety/crisis_detector.py — 위기 키워드 2-level 감지     │
│  • safety/output_sanitizer.py — 의료/처방/강제형 차단        │
│  • safety/escalation.py — 1393 / 1577-0199 안내             │
│  • safety/audit_log.py — 감지 이벤트 기록                    │
└─────────────────────────────────────────────────────────────┘
```

### 3.1 실행 흐름 (가드레일 포함)

```
1. User Input (narrative)
   │
   ▼
2. [SAFETY] crisis_detector.check(input)
   ├─ level 2 (자살·자해) → Escalation 출력 + 로그 + 종료
   ├─ level 1 (주의) → 가중치 완화 + 진행
   └─ level 0 → 정상 진행
   │
   ▼
3. AxisExtractor(input) → {Grief: 0.3, Guilt: 0.4, Eros: 0.1, Rage: 0.05, Liberation: 0.15}
   │
   ▼
4. PlugOrchestrator.compute_weights(input, metadata, forced_gate)
   │
   ▼
5. AxesWeighter — plug × axis 매트릭스 → 재가중
   │
   ▼
6. compose_prompt() → MENTAL_CORE (llama.cpp)
   │
   ▼
7. [SAFETY] output_sanitizer.filter(raw_output)
   ├─ 의료 언급 → 재요약 요청
   ├─ "~해야 한다" → 약화 치환
   └─ 통과 → 반환
   │
   ▼
8. Final Report (JSON) + parksy_tone_verdict
```

---

## 4. 플러그 카탈로그 (10개, v0.2 유지 + gate 명확화)

| ID | 이름 | Gate | 기본 가중 | 트리거 키워드 |
|----|------|------|----------|--------------|
| P01 | `FreudPlug` | I | 0.10 | 죽음, 부모, 성, 욕망, 죄책감 |
| P02 | `JungPlug` | II | 0.10 | 지휘자, 만다라, 그림자, 통합 |
| P03 | `FamilySystemsPlug` | IV | 0.10 | 부양, 책임, 동거, 의무 |
| P04 | `ShamanKoPlug` | V | 0.08 | 제사, 묘소, 조상, 터, 한 |
| P05 | `SufiPlug` | III | 0.06 | 성지, 기도, 빛, 성자 |
| P06 | `AyahuascaPlug` | V | 0.06 | 비전, 식물, 해체, 각성 |
| P07 | `MassProtocolPlug` | III/VII | 0.08 | 미사, 고해, 전례, 파견 |
| P08 | `EnvTriggerPlug` | bg | 0.12 | 옛 방, 기일, 계절 |
| P09 | `NarrativeMetaPlug` | VI | 0.08 | 추론, 돌이켜보니, 알고 보니 |
| P10 | `ParksyProfilePlug` | bg | **1.0 고정** | 항상 |

### 4.1 가중치 결정 공식 (v0.2 이식)

```python
def compute_weights(narrative, metadata, forced_gate=None):
    weights = {p.name: p.score({"narrative": narrative, "metadata": metadata}) for p in PLUGS}
    if metadata.get("is_dream"): weights["freud"] += 0.3; weights["jung"] += 0.3
    if metadata.get("is_family_event"): weights["family_systems"] += 0.4
    if metadata.get("anniversary_within_30d"): weights["env_trigger"] += 0.5
    if forced_gate:
        for p in [p for p in PLUGS if p.gate_id == forced_gate]:
            weights[p.name] += 0.5
    weights["parksy_profile"] = 1.0  # 고정
    return normalize(weights, lock=["parksy_profile"])
```

---

## 5. 도메인 ISA — 5축(axes) 체계 🆕

> **핵심 추가**: 플러그 10개가 "어떤 학파로 볼지"라면, 5축은 "무엇을 볼지"다.
> 박씨 2026-04-24 로그의 `F(꿈) = Grief ∘ Guilt ∘ Eros ∘ Rage` 합성 함수 확장판.

### 5.1 5축 정의

| Axis ID | 한글명 | 정의 | 박씨 2026-04-24 예시 |
|---------|------|------|--------------------|
| A1 | **Grief** (애도) | 상실·종결·작별 | "돌봄 시스템이 끝났으면" |
| A2 | **Guilt** (죄책감) | 부채감·자기 비난·의무 위반감 | 모르는 전화에 "병신" 욕 |
| A3 | **Eros** (삶의 욕구) | 외로움·성·접촉·살고 싶음 | 업소여성 추론 장면 |
| A4 | **Rage** (분노) | 피로·공격성·시스템 불의에 대한 반발 | 40년 불공정 분노 |
| A5 | **Liberation** (해방) 🆕 | 종료 후 새 공간·안도·자유 | "오랜만에 잘 잤다 · 마음 편하다" |

**왜 5축인가**: 4축(Grief/Guilt/Eros/Rage)은 *문제 진단* 축이고, Liberation은 *회복 방향* 축이다. 박씨 오늘 로그에 "해방감" 명시적으로 등장 → 축으로 승격.

### 5.2 Axis 인터페이스

```python
# mcp/core/axes.py
from abc import ABC, abstractmethod

class Axis(ABC):
    id: str
    name_ko: str
    keywords: list[str]
    metaphors: list[str]  # 간접 감지용

    @abstractmethod
    def extract(self, narrative: str, metadata: dict) -> float:
        """이 축의 강도 (0.0~1.0)"""

class GriefAxis(Axis):
    id = "grief"
    name_ko = "애도"
    keywords = ["죽음", "상실", "떠났", "보냈", "끝", "마지막"]
    metaphors = ["장례", "무덤", "겨울", "저물", "사라"]

    def extract(self, narrative, metadata):
        direct = sum(1 for k in self.keywords if k in narrative) * 0.12
        indirect = sum(1 for m in self.metaphors if m in narrative) * 0.06
        if metadata.get("is_dream") and "죽" in narrative:
            direct += 0.3
        return min(direct + indirect, 1.0)

# GuiltAxis, ErosAxis, RageAxis, LiberationAxis 동일 패턴
```

### 5.3 AxesWeighter — plug × axis 매트릭스

각 플러그가 각 축에 대해 **고유 해석 가중치**를 가진다. 이게 "학파별 편향"을 코드로 명시하는 방법.

```python
# mcp/core/axes_weighter.py
# rows = plugs, cols = axes
PLUG_AXIS_MATRIX = {
    "freud":          {"grief": 0.25, "guilt": 0.35, "eros": 0.25, "rage": 0.10, "liberation": 0.05},
    "jung":           {"grief": 0.20, "guilt": 0.10, "eros": 0.15, "rage": 0.05, "liberation": 0.50},  # 통합/개성화=해방
    "family_systems": {"grief": 0.15, "guilt": 0.30, "eros": 0.05, "rage": 0.20, "liberation": 0.30},
    "shaman_ko":      {"grief": 0.40, "guilt": 0.20, "eros": 0.05, "rage": 0.15, "liberation": 0.20},  # 한→해소
    "sufi":           {"grief": 0.10, "guilt": 0.10, "eros": 0.15, "rage": 0.05, "liberation": 0.60},  # 비움=해방
    "ayahuasca":      {"grief": 0.15, "guilt": 0.10, "eros": 0.20, "rage": 0.15, "liberation": 0.40},
    "mass_protocol":  {"grief": 0.25, "guilt": 0.30, "eros": 0.05, "rage": 0.05, "liberation": 0.35},  # 고해→파견
    "env_trigger":    {"grief": 0.30, "guilt": 0.15, "eros": 0.10, "rage": 0.10, "liberation": 0.35},
    "narrative_meta": {"grief": 0.20, "guilt": 0.20, "eros": 0.20, "rage": 0.20, "liberation": 0.20},  # 균등
    "parksy_profile": {"grief": 0.20, "guilt": 0.20, "eros": 0.20, "rage": 0.20, "liberation": 0.20},  # 톤만
}

def axis_distribution(plug_weights: dict, narrative: str, metadata: dict) -> dict:
    """최종 축 분포 계산"""
    from mcp.core.axes import ALL_AXES
    # 1. 직접 추출
    direct = {a.id: a.extract(narrative, metadata) for a in ALL_AXES}
    # 2. 플러그 간접 기여
    indirect = {a.id: 0.0 for a in ALL_AXES}
    for plug_name, pw in plug_weights.items():
        for axis_id, aw in PLUG_AXIS_MATRIX.get(plug_name, {}).items():
            indirect[axis_id] += pw * aw
    # 3. 합성 (직접 60% + 간접 40%)
    return {aid: 0.6 * direct[aid] + 0.4 * indirect[aid] for aid in direct}
```

### 5.4 출력에 axes 노출

report 모드 출력에 **`axis_profile` 필드** 추가:

```json
{
  "axis_profile": {
    "grief": 0.72,
    "guilt": 0.65,
    "eros": 0.38,
    "rage": 0.15,
    "liberation": 0.51
  },
  "dominant_axis": "grief",
  "axis_narrative": "애도와 죄책감이 주축, 해방감이 그 밑에서 올라오는 중",
  ...
}
```

### 5.5 왜 이게 중요한가

- **플러그**만으론 "어느 학파"만 알지 "무엇을"을 놓침
- **axes**가 있어야 학파 중립적 핵심 감정 지도 그려짐
- Phase 3 장기 트래킹에서 **"월별 axis 변동 차트"** 가능 → 박씨가 감정 흐름 객관 관찰

---

## 6. MENTAL_CORE 선정 매트릭스 🆕

> 베이스 모델을 "Qwen2.5로 박고 시작" 대신 **근거 기반 선정**.

### 6.1 후보 3종 비교

| 기준 | **Qwen2.5-7B-Instruct** ⭐ | MentaLLaMA-chat-7B | Llama-3.1-8B-Instruct |
|------|---------------------------|-------------------|----------------------|
| **한국어 능력** | 우수 (中韓 데이터 풍부) | 약함 (영어 중심) | 중간 |
| **상담 도메인 튜닝** | 없음 (중립) | **심리 상담 특화** | 없음 |
| **라이선스** | Apache 2.0 | MIT | Llama 3.1 Community |
| **파인튜닝 용이성** | LoRA 지원 완전 | LoRA 지원 | LoRA 지원 |
| **로컬 추론 (CPU Q4)** | 8 tok/s | 7 tok/s | 6 tok/s |
| **박씨 선행 자산** | **parksy LLM v4 재활용** | 없음 | Together AI 차단 이력 |
| **비용 (Vast.ai LoRA)** | $1.50 (2h) | $1.50 | $2.00 |
| **위험** | 톤 오염 가능 | 한국어 품질 | Tier 1 차단 재발 |

### 6.2 선정 결정: **Qwen2.5-7B-Instruct**

**근거 3가지**:
1. **재활용 원칙**: parksy LLM v4가 이미 Qwen2.5 베이스로 165MB LoRA 완성. 같은 베이스 재활용 = 데이터 호환성 + 박씨 톤 연속성.
2. **한국어 우선**: 박씨 로그 대부분 한국어. MentaLLaMA의 영어 편향은 번역 손실.
3. **라이선스**: Apache 2.0 = 가장 자유. Llama Community 조건 회피.

**MentaLLaMA의 상담 도메인 강점을 잃는 대가**:
- → **데이터로 보완**: `library/*/` 800+ 케이스가 이 공백을 채움
- → **플러그 + axes ISA가 도메인 구조 강제**
- → **MENTAL_CORE는 톤·언어 담당, 도메인 로직은 Layer 3이 담당**

### 6.3 MENTAL_CORE 상수 선언

```python
# mcp/config.py
MENTAL_CORE = {
    "base_model_hf": "Qwen/Qwen2.5-7B-Instruct",
    "base_model_size_gb": 14.3,
    "lora_adapter_path": "mcp/models/therapy-lora-v1",
    "gguf_path": "mcp/models/therapy-q4.gguf",
    "runtime": "llama.cpp",
    "quantization": "Q4_K_M",
    "context_length": 8192,
    "expected_throughput_tokens_per_sec": 8,
    "fallback_api": "claude-haiku-4-5",
    "version": "v1",
    "selection_rationale": "parksy LLM v4 재활용 + 한국어 우선 + Apache 2.0",
    "selected_at": "2026-04-24",
    "alternatives_rejected": {
        "MentaLLaMA-chat-7B": "한국어 약함, 선행 자산 없음",
        "Llama-3.1-8B-Instruct": "Tier 1 차단 재발 리스크, 라이선스 복잡",
    }
}
```

### 6.4 재선정 트리거

다음 조건 발생 시 MENTAL_CORE 재선정 회의:
- 재현 정확도 < 60% (Phase 1 T1.10.1 기준)
- 한국어 품질 이슈 박씨 피드백 5건 누적
- Qwen2.5 라이선스 변경
- 베스트 케이스: v2 때 MentaLLaMA와 A/B 테스트

---

## 7. 데이터 파이프라인 (v0.2 유지)

### 7.1 원천 (축약)

| 원천 | 경로 | Phase 1 목표 |
|------|------|------------|
| Freud 논문 요약 | `library/freud/` | 50 |
| Jung 논문 요약 | `library/jung/` | 50 |
| Bowen/Minuchin | `library/family/` | 40 |
| 한국 무속 | `library/shaman_ko/` | 30 |
| 수피 힐링 | `library/sufi/` | 20 |
| Ayahuasca | `library/ayahuasca/` | 15 |
| 미사 전례 | `library/mass/` | 15 |
| 박씨 공개분 | `library/parksy_seeds/` | 20 |
| 박씨 비공개 | `private_seeds/` | 100+ |

### 7.2 스키마 (v0.2 + axes 추가)

```json
{
  "id": "case_freud_0042",
  "school": "freud",
  "gate_id": "I",
  "axis_annotation": {
    "grief": 0.3, "guilt": 0.5, "eros": 0.1, "rage": 0.05, "liberation": 0.05
  },
  "input": {"narrative": "...", "metadata": {}},
  "interpretation": {"frame": "...", "key_terms": [], "reference": "..."},
  "target_output_ko": "...",
  "parksy_tone": false,
  "safety_tag": "none"
}
```

`safety_tag`: `none` / `crisis_l1` / `crisis_l2` — 가드레일 학습용.

---

## 8. 학습 공정 (v0.2 + axes 라벨링 추가)

```
[STAGE A] 데이터 준비 (로컬, 3일)
  library/*/*.jsonl + axis_annotation 라벨링
  → therapy_dataset_v1.jsonl

[STAGE B] 두뇌 굽기 (Vast.ai RTX 3090, 2h, $1.50)
  Base: Qwen2.5-7B-Instruct (선정 §6)
  LoRA: r=16, alpha=32, 3 epochs
  axis_annotation 필드 → 학습 타겟에 포함

[STAGE C] 로컬 추론 (1일)
  llama.cpp + GGUF Q4_K_M (~4GB)
  mcp/models/therapy-q4.gguf

[STAGE D] Orchestrator + Axes (3일)
  plug_orchestrator.py + axes.py + axes_weighter.py

[STAGE E] MCP 래퍼 + 가드레일 (2일)  ← 가드레일 분량 추가
  mcp/server.py + mcp/safety/*.py

[STAGE F] 재현 테스트 (Day 10)
  pytest mcp/tests/test_replay_20260424.py

Phase 1 납기: 2주
Phase 1 비용: ~$2
```

---

## 9. MCP 인터페이스 (5 도구, v0.2 유지 + axis_profile 추가)

### 9.1 도구 (v0.2와 동일 시그니처)

- `analyze_dream(narrative, sleep_context, forced_gate, mode)`
- `analyze_narrative(narrative, category, mode)`
- `propose_ritual(state_log, scope, tradition)`
- `compare_agents(narrative, agents)`
- `query_library(topic, school, limit)`

### 9.2 출력 스펙 (v0.3 확장)

```json
{
  "case_id": "dream_20260424_082123",
  "safety_verdict": {
    "level": 0,
    "flagged_terms": [],
    "sanitized": false
  },
  "active_plugs": [
    {"name": "freud", "gate": "I", "weight": 0.24},
    {"name": "jung", "gate": "II", "weight": 0.22}
  ],
  "axis_profile": {
    "grief": 0.72, "guilt": 0.65, "eros": 0.38,
    "rage": 0.15, "liberation": 0.51
  },
  "dominant_axis": "grief",
  "report": {
    "one_line": "...",
    "layered_by_axis": {
      "grief": "...", "guilt": "...", "eros": "...",
      "rage": "...", "liberation": "..."
    },
    "dissenting_views": [...],
    "parksy_tone_verdict": "참고. 네 판단이 최종이다. 레시피 아님, 레퍼런스임."
  },
  "suggested_ritual": null,
  "audit_log_id": "audit_20260424_082123_abc"
}
```

---

## 10. 가드레일 시스템 🆕

> **v0.2 치명적 누락**. v0.3에서 독립 섹션 + 4 모듈로 분리.

### 10.1 왜 필요한가

- 박씨 로그에 자해/자살 직접 언급은 없지만 "작은누나 자살 시도 이력" 언급 있음
- 박씨 본인이 **위기 상태일 때** 엔진에 접근할 수 있음
- 엔진이 의료 진단/처방 유사 발화 → 법적·윤리적 리스크
- "~해야 한다" 강제형 → 레퍼런스 원칙 위반

### 10.2 4-모듈 설계

```
safety/
├── crisis_detector.py    — 입력 단계 위기 감지
├── output_sanitizer.py   — 출력 단계 금지 패턴 필터
├── escalation.py         — level 2 시 연락처 제공
└── audit_log.py          — 전 이벤트 기록 (박씨 리뷰용)
```

### 10.3 CrisisDetector

**2-level 판정**:

| Level | 감지 키워드 (일부) | 처리 |
|-------|-------------------|------|
| **0** | 없음 | 정상 진행 |
| **1** (주의) | "힘들", "지친다", "무의미", "혼자", "공허" | 가중치 유지 + 출력에 공감 강제 |
| **2** (차단) | "죽고 싶", "자살", "자해", "사라지고 싶", "끝내고 싶" | **출력 대체 + 연락처 + audit** |

```python
# mcp/safety/crisis_detector.py
CRISIS_L2_PATTERNS = [
    r"죽고\s*싶", r"자살", r"자해", r"목숨", r"끝내고\s*싶",
    r"사라지고\s*싶", r"뛰어내리", r"약을\s*먹고",
]
CRISIS_L1_PATTERNS = [
    r"힘들어", r"지친다", r"무의미", r"혼자\s*있", r"공허",
    r"아무도\s*모르", r"포기",
]

def detect(narrative: str) -> dict:
    import re
    l2_hits = [p for p in CRISIS_L2_PATTERNS if re.search(p, narrative)]
    l1_hits = [p for p in CRISIS_L1_PATTERNS if re.search(p, narrative)]
    if l2_hits:
        return {"level": 2, "patterns": l2_hits}
    if l1_hits:
        return {"level": 1, "patterns": l1_hits}
    return {"level": 0, "patterns": []}
```

**주의**: 오탐 불가피. "어머니가 돌아가시는 꿈" 같은 건 level 2가 아님. 메타데이터 `is_dream=True`면 패턴 관대하게.

### 10.4 OutputSanitizer

**금지 패턴** (LLM 출력 후 검사):

| 패턴 | 예시 | 처리 |
|------|------|------|
| 의료 진단 | "당신은 우울증입니다" | 재생성 요청 |
| 약물 처방 | "약을 복용하세요" | 재생성 요청 |
| 강제형 | "~해야 합니다" | "~해 보는 것도 방법" 치환 |
| 단정 예언 | "당신은 망가졌어요" | 완화 치환 |
| 종교 강요 | "반드시 믿으세요" | 레퍼런스형 치환 |

```python
# mcp/safety/output_sanitizer.py
FORBIDDEN_PATTERNS = {
    r"(우울증|조현병|PTSD|양극성)입니다": "의료 진단 금지",
    r"약을?\s*(복용|드세요)": "처방 금지",
    r"병원에?\s*가셔야": "의료 권유 소프트화 필요",
}
SOFTEN_MAP = {
    r"해야\s*한다$": "해 보는 것도 방법이다",
    r"해야\s*합니다$": "해 보는 것도 방법입니다",
    r"절대\s*안\s*된다": "권장되지 않는다",
}

def filter(raw_output: str) -> tuple[str, bool]:
    """returns (sanitized_output, was_modified)"""
    ...
```

### 10.5 Escalation

**level 2 감지 시 출력**:

```
지금은 분석보다 사람이 필요한 순간 같다.

24시간 전화 상담:
- 자살예방상담전화 1393 (무료, 24h)
- 정신건강위기상담 1577-0199 (무료, 24h)
- 청소년전화 1388

텍스트:
- 카카오톡 채널 "마들렌" (자살예방)
- web 1393 채팅 https://www.spckorea.or.kr

지금 바로 연결 못 해도 괜찮다. 숨만 쉬고 있어도 된다.

이 엔진은 지금은 닫힌다. 내일 다시 열린다.
```

**출력 대체**: 일반 report 생성 스킵. 오직 위 메시지만.

### 10.6 GuardrailPlug (번외)

**항상 작동하는 11번째 플러그** (ParksyProfilePlug 옆). 가중치 고정 1.0.

```python
class GuardrailPlug(Plug):
    name = "guardrail"
    gate_id = None
    weight_default = 1.0

    def score(self, ctx): return 1.0

    def frame(self, ctx):
        return {
            "directive": "의료 진단 금지 / 약물 처방 금지 / 강제형 금지",
            "format_rule": "출력은 레퍼런스, 판단은 박씨 것",
        }
```

→ 최종 플러그 총 **11개** (v0.3). ALL_PLUGS 업데이트.

### 10.7 AuditLog

```python
# mcp/safety/audit_log.py
# SQLite 로컬 DB: audit.db
# 기록:
#   - timestamp
#   - input_hash (민감 원문 저장 X)
#   - crisis_level
#   - flagged_terms
#   - sanitized (bool)
#   - output_hash

def log_event(event: dict): ...
def query_recent(days: int = 30) -> list: ...
```

박씨가 월 1회 `audit_log.report()` 실행 → 가드레일 발동 이력 리뷰.

### 10.8 가드레일 단위 테스트

```python
# mcp/tests/test_guardrail.py
def test_crisis_l2_blocks():
    result = analyze_dream("죽고 싶다")
    assert result["safety_verdict"]["level"] == 2
    assert "1393" in result["escalation_message"]

def test_dream_death_is_not_crisis():
    result = analyze_dream("어머니가 돌아가시는 꿈",
                           metadata={"is_dream": True})
    assert result["safety_verdict"]["level"] == 0

def test_output_sanitizer_removes_diagnosis():
    raw = "당신은 우울증입니다"
    filtered, modified = sanitize(raw)
    assert modified
    assert "우울증입니다" not in filtered

def test_escalation_message_has_contacts():
    msg = escalation_message()
    assert "1393" in msg and "1577-0199" in msg
```

---

## 11. 시스템 통합 (v0.2 유지)

### 11.1 생태계

```
dtslib-papyrus (HQ)
    │
parksy-logs (원천) ──────┐
                         │
alexandria-sanctuary (본 엔진 거처)
    ├── library/
    ├── mcp/ (+ safety/ 🆕)
    ├── sanctuary/
    ├── forum/
    └── private_seeds/
    │
    ├──→ Claude Code (주 호출자)
    ├──→ parksy-audio (p1b TTS 낭독)
    └──→ eae-univ (커리큘럼 소재)
```

### 11.2 헌법 준수

| 조항 | v0.3 준수 |
|------|----------|
| 28 완전수 | ✅ 기존 레포 |
| 새 기술 학습 금지 | ✅ 전부 기존 공정 |
| 구조 확장 금지 | ✅ 기존 폴더 재사용 |
| 커밋=전표 | ✅ revert만 |
| API→Chrome→Playwright→CDP | ✅ MCP=API |
| secrets 커밋 금지 | ✅ .env .gitignore |
| **가드레일 필수** 🆕 | ✅ §10 독립 설계 |

---

## 12. 페이즈 로드맵

### Phase 0 — 씨앗 (1주, $0) [✅ 일부 완료]
- 디렉토리 골격 ✅
- 학파 README 플레이스홀더 ✅
- **Sprint 0.2**: README 상세화 (8개 TASK)
- **Sprint 0.3**: 인프라 스크립트 (수집/빌더/devplan.html)
- **Sprint 0.4**: 재현 테스트 골든 셋
- **Sprint 0.5**: Phase 0 커밋

### Phase 1 — MVP (2주, $2) [82 TASK 합계]
- **Sprint 1.1**: Plug base (1 TASK)
- **Sprint 1.2**: 백그라운드 플러그 2종
- **Sprint 1.2.5**: **Axes 5축 구현** 🆕 (4 TASK)
- **Sprint 1.2.6**: **MENTAL_CORE 확정** 🆕 (2 TASK)
- **Sprint 1.2.7**: **Guardrail 시스템** 🆕 (6 TASK)
- **Sprint 1.3**: Gate 플러그 7종 (7 TASK)
- **Sprint 1.4**: ALL_PLUGS + 단위 테스트
- **Sprint 1.5**: Orchestrator + Axes Weighter + Jinja
- **Sprint 1.6**: 케이스 수집 + dataset v1
- **Sprint 1.7**: Vast.ai LoRA 학습 ($1.50)
- **Sprint 1.8**: GGUF 변환 + 로컬 추론
- **Sprint 1.9**: MCP 서버 + 가드레일 통합
- **Sprint 1.10**: 재현 테스트 + 종료 보고

### Phase 2 — Gate UI + 확장 (4주, $6)
- console.html + TTS 연결
- sanctuary/ 리추얼 모듈
- 케이스 800+
- compare_agents 구현
- **감사 리뷰 대시보드** 🆕

### Phase 3 — 순환 (지속, 월 $1.50)
- 월 1회 자동 재학습
- 피드백 루프
- 공개 아카이브 (선택)
- **가드레일 이벤트 월간 보고서** 🆕

### Y1 예산: **$20**

---

## 13. 리스크 & 대응 (v0.3 확장)

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| LoRA 학습 실패 | 중 | 중 | 500샘플 최소, v4 LoRA 폴백 |
| 개인정보 유출 | 낮 | 치명 | private_seeds + audit DB .gitignore |
| Together Tier 2 차단 | 중 | 중 | Vast.ai 1순위 |
| 플러그 가중치 편향 | 중 | 중 | 월 1회 감수 |
| "A급 미달" 실망 | 중 | 낮 | 레퍼런스 강제 |
| 저작권 | 낮 | 중 | 요약 + 인용 |
| **crisis 오탐** 🆕 | 중 | 중 | is_dream 메타 완화, 박씨 피드백으로 패턴 조정 |
| **crisis 미탐** 🆕 | 낮 | 치명 | 패턴 확대 + 월 감사 + 의심 시 level 1 보수적 |
| **sanitizer 과잉 차단** 🆕 | 중 | 낮 | 차단 이력 로그 + 주간 리뷰 |
| **MENTAL_CORE 한국어 품질** 🆕 | 낮 | 중 | Phase 2에 MentaLLaMA A/B 테스트 |

---

## 14. 윤리 및 법적 제약 (v0.3 강화)

- **레퍼런스 강제**: `parksy_tone_verdict` 고정
- **의료 대체 금지**: OutputSanitizer §10.4 자동 차단
- **위기 감지**: CrisisDetector §10.3 자동 → Escalation §10.5
- **의료기기 아님**: 개인 일기 도구
- **상담 서비스 아님**: 타인 서비스 없음
- **개인정보**: `private_seeds/` 로컬 전용, 학습 시 Vast.ai 즉시 terminate
- **audit 보관**: 해시만 저장, 원문 X
- **공개 배포 재평가**: Phase 3 시 buckleychang CPA 검토

---

## 15. 성공 기준

### 정량 (Phase 1 종료)

| 지표 | 목표 |
|------|------|
| 재현 정확도 | ≥ 80% (2026-04-24 로그) |
| 추론 지연 | ≤ 10초 |
| 플러그 활성 다양성 | ≥ 3개 |
| **Axis 다양성** 🆕 | ≥ 2축 ≥ 0.3 |
| **Crisis L2 정탐률** 🆕 | ≥ 95% (골든 픽스처 10건) |
| **Crisis L2 오탐률** 🆕 | ≤ 5% (꿈/비위기 20건) |
| **Sanitizer 차단 정확도** 🆕 | ≥ 90% |
| Phase 1 비용 | ≤ $2 |

### 정성

- 박씨: "A급 상담사 말 같다" 1회+
- 박씨: "이제 저런 거 안 찾아가도 되겠다" 재확인
- 월 사용 ≥ 3회
- **가드레일 오동작 불만 ≤ 월 1회** 🆕

### 실패 선언

- Phase 1 후 4주 내 월 사용 < 3회 → 디프리케이트
- 재현 정확도 < 50% → v2 재설계
- **Crisis L2 오탐 박씨 불만 5회 이상** 🆕 → 패턴 전면 재검토

---

## 16. 부록 A — 디렉토리 최종 구조 (v0.3)

```
alexandria-sanctuary/
├── index.html                      (7 Gate PWA)
├── whitepaper.html                 (본 문서 웹버전)
├── devplan.html                    (개발 대시보드)
├── console.html                    (박씨 MCP 콘솔, Phase 2)
├── manifest.json
├── CLAUDE.md
├── 00_TRUTH/ assets/ card/ data/ feeds/ staff/ visit/   (기존)
│
├── docs/
│   ├── MCP-THERAPY-WHITEPAPER-v0.3.md      🆕 본 파일
│   ├── MCP-THERAPY-WHITEPAPER-v0.2.md      (이전)
│   ├── MCP-THERAPY-DEVPLAN.md              (인간용 로드맵)
│   ├── MCP-THERAPY-DEVPLAN-TASKS.md        (v2.0 TASK 카탈로그)
│   └── MCP-THERAPY-DEVPLAN-TASKS-v2.1.md   🆕 v0.3 반영 패치
│
├── library/
│   ├── {freud,jung,family,shaman_ko,sufi,ayahuasca,mass,parksy_seeds}/
│   └── README.md 8장
│
├── sanctuary/{cave-retreat,residence,hospice}/
├── forum/
├── philosophy/
│
├── mcp/
│   ├── __init__.py
│   ├── config.py                    🆕 MENTAL_CORE 상수
│   ├── plug_orchestrator.py
│   ├── server.py
│   ├── core/                        🆕 도메인 ISA
│   │   ├── __init__.py
│   │   ├── axes.py                  🆕 5축
│   │   ├── axes_weighter.py         🆕 plug × axis
│   │   └── axis_extractor.py        🆕
│   ├── plugs/
│   │   ├── base.py
│   │   ├── freud.py
│   │   ├── jung.py
│   │   ├── family.py
│   │   ├── shaman_ko.py
│   │   ├── sufi.py
│   │   ├── ayahuasca.py
│   │   ├── mass.py
│   │   ├── env_trigger.py
│   │   ├── narrative_meta.py
│   │   ├── parksy_profile.py
│   │   └── guardrail.py             🆕 11번째 플러그
│   ├── safety/                      🆕 가드레일 시스템
│   │   ├── __init__.py
│   │   ├── crisis_detector.py
│   │   ├── output_sanitizer.py
│   │   ├── escalation.py
│   │   └── audit_log.py
│   ├── prompts/
│   │   ├── therapy_system.jinja
│   │   └── per_school/*.jinja
│   ├── models/                      (gitignore)
│   │   └── therapy-q4.gguf
│   ├── train/
│   │   ├── collect_school_cases.py
│   │   ├── dataset_builder.py
│   │   ├── train_lora.py
│   │   ├── merge_lora.py
│   │   └── requirements.txt
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_plugs.py
│       ├── test_axes.py             🆕
│       ├── test_guardrail.py        🆕
│       ├── test_replay_20260424.py
│       └── fixtures/
│           ├── parksy_dream_*.json  (gitignore)
│           └── crisis_cases/*.json  🆕 (gitignore)
│
├── private_seeds/                   (gitignore)
└── .gitignore
```

---

## 17. 부록 B — 미사 프로토콜 매핑 (v0.2 유지)

| 미사 6단계 | MCP 도구 | 박씨 일상 | Gate | 주요 축 |
|-----------|---------|----------|------|--------|
| 1. 입당 | 세션 시작 | 로그 수집 | — | — |
| 2. 말씀 전례 | `analyze_narrative` | 상황 서술 | I, IV | Grief, Guilt |
| 3. 복음 · 강론 | plug + axis 리포트 | 해석 수신 | II, VI | — |
| 4. 봉헌 | 박씨 큐레이션 | 받을 해석 선택 | — | — |
| 5. 성체성사 | `propose_ritual` | 방 정리 · 글쓰기 | III | Liberation |
| 6. 파견 | 세션 종료 | 일상 복귀 | **VII** | **Liberation** |

---

## 18. 부록 C — axes × plugs 매트릭스 (참조용)

| Plug \\ Axis | Grief | Guilt | Eros | Rage | Liberation |
|-------------|:-----:|:-----:|:----:|:----:|:----------:|
| freud | 0.25 | **0.35** | 0.25 | 0.10 | 0.05 |
| jung | 0.20 | 0.10 | 0.15 | 0.05 | **0.50** |
| family | 0.15 | **0.30** | 0.05 | 0.20 | **0.30** |
| shaman_ko | **0.40** | 0.20 | 0.05 | 0.15 | 0.20 |
| sufi | 0.10 | 0.10 | 0.15 | 0.05 | **0.60** |
| ayahuasca | 0.15 | 0.10 | 0.20 | 0.15 | **0.40** |
| mass | 0.25 | **0.30** | 0.05 | 0.05 | **0.35** |
| env_trigger | **0.30** | 0.15 | 0.10 | 0.10 | **0.35** |
| narrative_meta | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 |
| parksy_profile | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 |

**해석**: Liberation 축은 Jung/Sufi/Mass가 지배 (통합/비움/파견). Grief 축은 shaman_ko/env_trigger (한/애니버서리). Guilt는 freud/family/mass 삼각.

---

## 19. 부록 D — 가드레일 키워드 사전 (v0.3 초안)

### Level 2 (차단)
```
죽고 싶, 자살, 자해, 목숨을 끊, 끝내고 싶, 사라지고 싶,
뛰어내리, 약을 먹고, 칼로, 목을, 옥상, 한강
```

### Level 1 (주의 · 공감 강제)
```
힘들어, 지친다, 무의미, 혼자 있, 공허, 아무도 모르,
포기, 못 견디, 다 끝났, 막막
```

### 예외 (is_dream=True 시 level 2 → level 0 완화)
```
죽는 꿈, 죽으시는 꿈, 돌아가시는 꿈, 장례 꿈
```

### 출력 금지 패턴 (OutputSanitizer)
```
당신은 [질병명]입니다
약을 복용하세요 / 처방 받으세요
반드시 ~해야 한다
절대 ~하지 마라
```

### 연락처 (Escalation)
```
자살예방상담전화 1393 (24h, 무료)
정신건강위기상담 1577-0199 (24h, 무료)
청소년전화 1388
카카오톡 채널 "마들렌"
web 1393: https://www.spckorea.or.kr
```

---

## 20. 최종 선언 (v0.3)

> **"박씨는 알렉산드리아 성소 위에 영성 엔진을 얹는다.
> 7 Gate가 UI이고, 플러그 11개가 엔진이고, 5축이 좌표계이고, 미사 6단계가 프로토콜이고, 가드레일 4 모듈이 경계다.
> 어머니가 간 요양원 자리에 세우는, 자기관리용 디지털 도서관.
> 1000년 임상실험을 2주 MCP로 복제하되, 위기 감지와 출력 검증을 내장한다.
> 결과는 팔지 않는다. 박씨 혼자 쓴다.
> Phase 3 가동기 첫 자가 소비 엔진이면서, 자해·의료·강제의 경계를 기계적으로 방어한다."**

---

### 문서 이력

| 날짜 | 버전 | 변경 | 저자 |
|------|------|------|------|
| 2026-04-24 09:00 | v0.1 | papyrus 초안 | Claude Opus 4.7 |
| 2026-04-24 09:04 | v0.2 | 알렉산드리아 이식, D안 확정 | Claude Opus 4.7 |
| 2026-04-24 10:40 | v0.3 | Perplexity 감수 반영 — axes + MENTAL_CORE + Guardrail | Claude Opus 4.7 |

### 자기평가 (v0.3)

| 항목 | v0.2 점수 | v0.3 점수 |
|------|----------|----------|
| 구조/멀티에이전트/DAG | 9.0 | 9.0 |
| 과업 분해 자기완결성 | 9.0 | 9.0 |
| 도메인 ISA (axes) | 6.5 | **9.0** |
| MENTAL_CORE 슬롯 | 7.0 | **8.5** |
| 가드레일 TASK 분리 | 6.0 | **9.0** |
| **전체** | **8.0** | **8.9** |

### 승인 대기

- [ ] 박씨 v0.3 감수
- [ ] Phase 0 Sprint 0.2~0.5 착수 사인
- [ ] Phase 1 예산 $2 승인
- [ ] DEVPLAN-TASKS v2.1 패치 반영 사인

---

*본 백서는 파피루스 헌법 제1·2조 및 특별법 전 조항을 준수한다.*
*28 완전수 유지. alexandria-sanctuary Tier 3 직영 내부 확장.*
*Phase 3 가동기 자가 소비 엔진 + 가드레일 내장.*
*작성: Claude Opus 4.7 | 감수: Parksy*
