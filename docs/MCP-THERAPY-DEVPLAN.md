# MCP-THERAPY 개발 계획 (DEVPLAN)

**대상**: Alexandria MCP-Therapy Engine
**선행 문서**: `docs/MCP-THERAPY-WHITEPAPER-v0.2.md`
**작성**: 2026-04-24 Claude Opus 4.7
**납기**: Phase 1 종료 2026-05-08 (2주)
**예산**: Phase 1 $2 / Y1 $20

> **원칙**: 모든 태스크는 "커맨드 수준" 또는 "파일 수준"으로 분해. 박씨가 읽고 "이거 당장 해라"로 던질 수 있는 해상도.

---

## 0. Phase 0 — 씨앗 (1주, $0)

### Sprint 0.1 — 디렉토리 골격 (1일)

```bash
cd ~/alexandria-sanctuary
mkdir -p mcp/{plugs,prompts/per_school,models,train,tests}
mkdir -p library/{freud,jung,family,shaman_ko,sufi,ayahuasca,mass,parksy_seeds}
mkdir -p private_seeds
echo "private_seeds/" >> .gitignore
echo "mcp/models/*.gguf" >> .gitignore
echo "mcp/models/*.safetensors" >> .gitignore
```

**산출물**:
- 신규 디렉토리 11개
- `.gitignore` 업데이트

**커밋**:
```
feat: MCP-Therapy 엔진 골격 생성 + private_seeds 격리
```

---

### Sprint 0.2 — 학파 README 8장 (1일)

각 `library/{school}/README.md` 작성. 해당 학파의:
- 핵심 개념 5개
- 수집 대상 논문/책 10개
- JSONL 스키마 예시 1건

**산출물**:
- `library/freud/README.md`
- `library/jung/README.md`
- `library/family/README.md`
- `library/shaman_ko/README.md`
- `library/sufi/README.md`
- `library/ayahuasca/README.md`
- `library/mass/README.md`
- `library/parksy_seeds/README.md`

---

### Sprint 0.3 — DEVPLAN 공개 (1일)

`devplan.html` 페이지 제작 (Phase 진행 대시보드). 박씨가 매일 접속해서 진척도 확인.

**산출물**:
- `devplan.html` (체크리스트 UI, 알렉산드리아 디자인 톤)

---

### Sprint 0.4 — Claude 학파 요약 자동화 (2일)

`mcp/train/collect_school_cases.py` 작성. 박씨가 URL/PDF 경로 JSON으로 던지면 Claude API로 요약 → JSONL 자동 변환.

```python
# mcp/train/collect_school_cases.py
import anthropic, json, sys

def summarize_to_case(source_text: str, school: str) -> dict:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=f"You are a {school} school case curator. Output JSONL.",
        messages=[{"role": "user", "content": source_text}]
    )
    return json.loads(response.content[0].text)
```

**산출물**:
- `mcp/train/collect_school_cases.py`
- `mcp/train/sources_queue.json` (수집 대기 목록)

---

### Sprint 0.5 — 재현 테스트 골든 셋 (1일)

2026-04-24 박씨캡처 로그(5808줄)에서 "최종 만점 리포트" 추출 → 재현 테스트 기준값으로 저장.

```python
# mcp/tests/test_replay_20260424.py
GOLDEN_ONE_LINE = "과거 돌봄 OS는 거의 종료됐고, 지금 나는 그 잔여 리듬과 '케어 없는 상태에서도 살아있을 수 있는가'라는 질문을 함께 처리하는 중이다."

GOLDEN_ACTIVE_PLUGS = ["freud", "jung", "family_systems", "env_trigger", "narrative_meta", "shaman_ko"]
```

**산출물**:
- `mcp/tests/test_replay_20260424.py`
- `mcp/tests/fixtures/parksy_dream_20260424.json` (입력 정규화)

**검증 기준**: Phase 1 끝나면 이 테스트 통과해야 함.

---

## 1. Phase 1 — MVP (2주, $2)

### Week 1: 데이터 + 엔진 골격

#### Day 1 (월) — 플러그 스켈레톤 전체 10개

각 플러그 클래스 스켈레톤만 먼저. 로직은 나중.

```python
# mcp/plugs/base.py
from abc import ABC, abstractmethod

class Plug(ABC):
    name: str = ""
    gate_id: str | None = None
    weight_default: float = 0.10
    keywords_trigger: list[str] = []

    def score(self, ctx: dict) -> float:
        hits = sum(1 for k in self.keywords_trigger if k in ctx.get("narrative", ""))
        return min(self.weight_default + hits * 0.08, 0.45)

    @abstractmethod
    def frame(self, ctx: dict) -> dict: ...
```

10개 플러그 각각 `mcp/plugs/{name}.py` 생성:
- `freud.py` / `jung.py` / `family.py` / `shaman_ko.py` / `sufi.py`
- `ayahuasca.py` / `mass.py` / `env_trigger.py` / `narrative_meta.py` / `parksy_profile.py`

**커밋**: `feat: 10개 플러그 스켈레톤`

---

#### Day 2 (화) — Orchestrator + 프롬프트 빌더

```python
# mcp/plug_orchestrator.py
from mcp.plugs import ALL_PLUGS
from jinja2 import Environment, FileSystemLoader

def compute_weights(narrative, metadata, forced_gate=None) -> dict:
    """백서 §4.3 로직 그대로"""
    ...

def compose_prompt(narrative, metadata, forced_gate=None) -> str:
    weights = compute_weights(narrative, metadata, forced_gate)
    env = Environment(loader=FileSystemLoader("mcp/prompts"))
    tmpl = env.get_template("therapy_system.jinja")
    return tmpl.render(weights=weights, plugs=ALL_PLUGS, ...)
```

**산출물**:
- `mcp/plug_orchestrator.py`
- `mcp/prompts/therapy_system.jinja` (마스터 시스템 프롬프트)
- `mcp/prompts/per_school/freud.jinja` 등 10개

**테스트**: 2026-04-24 로그 입력 → 프롬프트 출력 눈으로 검증

---

#### Day 3-4 (수-목) — 케이스 수집 스프린트

박씨 10분 + Claude 자동화.

```bash
# 박씨가 대기열에 URL 던진다
echo '{"school":"freud","url":"https://..."}' >> mcp/train/sources_queue.json

# Claude가 자동 실행
python3 mcp/train/collect_school_cases.py --queue mcp/train/sources_queue.json
```

**목표량 (Day 3-4 합산)**:
- Freud 50, Jung 50, Family 40, Shaman_ko 30, Sufi 20, Ayahuasca 15, Mass 15
- 총 220 케이스 (박씨 큐레이션 제외)

**자동화**: `.github/workflows/curate-daily.yml` (일 1회 배치 옵션)

---

#### Day 5 (금) — dataset_builder

```python
# mcp/train/dataset_builder.py
import json, glob

def build():
    all_cases = []
    for path in glob.glob("library/**/*.jsonl", recursive=True):
        for line in open(path):
            all_cases.append(json.loads(line))
    # private_seeds 추가
    for path in glob.glob("private_seeds/*.jsonl"):
        for line in open(path):
            all_cases.append(json.loads(line))

    # ChatML 포맷 변환
    with open("mcp/train/therapy_dataset_v1.jsonl", "w") as f:
        for case in all_cases:
            f.write(json.dumps(to_chatml(case), ensure_ascii=False) + "\n")

    print(f"Built {len(all_cases)} samples")

if __name__ == "__main__":
    build()
```

**산출물**: `mcp/train/therapy_dataset_v1.jsonl` (250+ 샘플)

---

### Week 2: 학습 + 추론 + MCP

#### Day 6 (월) — Vast.ai 학습 준비

```bash
# 로컬에서 dataset 검증
python3 mcp/train/dataset_builder.py
wc -l mcp/train/therapy_dataset_v1.jsonl  # 목표 ≥ 250

# Vast.ai 인스턴스 생성 (RTX 3090, $0.21/hr)
vastai search offers 'gpu_name=RTX_3090 reliability>0.95' -o 'dph+'
vastai create instance <ID> --image pytorch/pytorch:2.1.0-cuda12.1-cudnn8-devel \
  --disk 50 --onstart-cmd "pip install peft accelerate bitsandbytes"

# 인스턴스 IP 확보 (GraphQL, SDK 금지)
curl 'https://api.runpod.io/graphql' ...  # or vastai GraphQL
```

**산출물**:
- Vast.ai 인스턴스 running
- 학습 데이터 scp 전송

---

#### Day 7 (화) — LoRA 학습 (~2시간)

```python
# mcp/train/train_lora.py
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, TrainingArguments, Trainer

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct", load_in_4bit=True)
lora_cfg = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj","v_proj"], lora_dropout=0.05)
model = get_peft_model(model, lora_cfg)

args = TrainingArguments(
    output_dir="./therapy-lora-v1",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=2e-4,
    fp16=True,
    save_strategy="epoch",
)
trainer = Trainer(model=model, args=args, train_dataset=load_dataset(...))
trainer.train()
model.save_pretrained("./therapy-lora-v1-final")
```

**실행**:
```bash
ssh vast "cd /workspace && python train_lora.py 2>&1 | tee train.log"
```

**검증**:
- loss 감소 확인
- final checkpoint 165MB 정도

**다운로드**:
```bash
scp -P <port> vast:/workspace/therapy-lora-v1-final/* mcp/models/
```

**Pod terminate (박씨 확인 후)**

---

#### Day 8 (수) — GGUF 변환 + 로컬 추론

```bash
cd ~/llama.cpp  # 이미 있는 경우
python convert_lora_to_gguf.py --lora ~/alexandria-sanctuary/mcp/models/therapy-lora-v1-final \
  --base Qwen/Qwen2.5-7B-Instruct --outfile therapy-q4.gguf --quantize Q4_K_M

mv therapy-q4.gguf ~/alexandria-sanctuary/mcp/models/
```

**로컬 테스트**:
```bash
./llama-cli -m ~/alexandria-sanctuary/mcp/models/therapy-q4.gguf \
  -p "$(cat test_prompt.txt)" -n 500
```

**검증**: 8 tok/s 이상, 박씨 톤 유지 확인

---

#### Day 9 (목) — MCP 서버

```python
# mcp/server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.plug_orchestrator import compose_prompt
import subprocess

app = Server("alexandria-therapy")

@app.call_tool()
async def analyze_dream(narrative: str, sleep_context: dict = None,
                        forced_gate: str = None, mode: str = "report"):
    prompt = compose_prompt(narrative, sleep_context or {}, forced_gate)
    result = subprocess.run(
        ["./llama-cli", "-m", "mcp/models/therapy-q4.gguf", "-p", prompt, "-n", "800"],
        capture_output=True, text=True
    )
    return parse_output(result.stdout, mode)

# analyze_narrative / propose_ritual / compare_agents / query_library 동일 패턴

async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())
```

**등록**:
```json
// ~/dtslib-papyrus/.mcp.json 에 추가
{
  "mcpServers": {
    "alexandria-therapy": {
      "command": "python3",
      "args": ["/home/dtsli/alexandria-sanctuary/mcp/server.py"],
      "env": {}
    }
  }
}
```

Claude Code 재시작 → `analyze_dream` 등 5개 도구 노출 확인.

---

#### Day 10 (금) — 재현 테스트 + 튜닝

```bash
cd ~/alexandria-sanctuary
pytest mcp/tests/test_replay_20260424.py -v
```

**기대**: 재현 정확도 ≥ 80%.

실패 시 대응:
- 80~70%: 프롬프트 튜닝 (plug 가중치 조정, system 프롬프트 수정)
- 70~50%: 데이터 큐레이션 재검수 + 1 epoch 추가 학습 ($0.75)
- < 50%: **실패 선언 → v2 설계**

**Phase 1 종료 커밋**:
```
feat: Phase 1 MVP — MCP-Therapy v1 LoRA + 5개 도구 + 재현 테스트 {통과/실패}
```

---

## 2. Phase 2 — Gate UI 연결 (4주, $6)

### Week 3-4: UI 레이어

#### Sprint 2.1 — whitepaper.html / devplan.html 공개 (본 세션에서 이미 착수)

#### Sprint 2.2 — console.html (박씨 MCP 콘솔)

- 좌: 7 Gate 선택 UI (index.html과 동일 디자인)
- 중: narrative 입력 textarea
- 우: 리포트 렌더링
- 하단: parksy-audio TTS 재생 버튼

```javascript
async function analyzeDream(narrative, gate) {
  const res = await fetch('/mcp/analyze_dream', {
    method: 'POST',
    body: JSON.stringify({narrative, forced_gate: gate})
  });
  const report = await res.json();
  renderReport(report);
}
```

#### Sprint 2.3 — Gate 클릭 → MCP 연동

index.html gcard-link를 console.html?gate=I 식으로 수정.

### Week 5: 리추얼 모듈

#### Sprint 2.4 — propose_ritual → sanctuary/ 서브페이지 생성

`sanctuary/cave-retreat/` `residence/` `hospice/` 각각 리추얼 동적 생성.

#### Sprint 2.5 — parksy-audio TTS 연결

```bash
~/parksy-audio/scripts/split_inference.py --text "{report.one_line}" \
  --output /tmp/narration.wav --split all_punct --pause 0.3
```

### Week 6: 케이스 확장 + 통합

#### Sprint 2.6 — 케이스 800+로 확장

박씨 주간 10분 큐레이션 × 4주 = 500 케이스 추가 목표.

#### Sprint 2.7 — compare_agents 구현

Perplexity/Gemini/Grok/ChatGPT/Claude API 5개 병렬 호출 → 브릿지 리포트.

---

## 3. Phase 3 — 순환 (지속, 월 $1.50)

### 월 1회 자동 재학습 cron

```bash
# ~/.config/systemd/user/therapy-retrain.timer
[Timer]
OnCalendar=monthly
```

### 피드백 루프

console.html 하단에 👍 / 👎 버튼. 피드백 10건 누적 시 재학습 트리거.

### 공개 배포 (선택)

Phase 3 후반: parksy.kr/dream-archive/ 에 공개 가능분만 (library/parksy_seeds/) 배포.

### eae-univ 커리큘럼

"21세기 샤먼 만드는 법" 강의 녹화.

---

## 4. 체크리스트 (박씨 실시간 확인용)

### Phase 0 (이번 주)
- [ ] 디렉토리 골격 (Sprint 0.1)
- [ ] 학파 README 8장 (Sprint 0.2)
- [ ] devplan.html (Sprint 0.3)
- [ ] collect_school_cases.py (Sprint 0.4)
- [ ] 재현 테스트 골든 셋 (Sprint 0.5)

### Phase 1 (다음주 월~금 + 그 다음주 월~금)
- [ ] Day 1: 플러그 10 스켈레톤
- [ ] Day 2: Orchestrator + 프롬프트
- [ ] Day 3-4: 케이스 220+ 수집
- [ ] Day 5: dataset_builder
- [ ] Day 6: Vast.ai 준비
- [ ] Day 7: LoRA 학습 ($1.50)
- [ ] Day 8: GGUF + 로컬
- [ ] Day 9: MCP 서버 + 등록
- [ ] Day 10: 재현 테스트 ≥80%

### 예산 추적
- Phase 0: $0
- Phase 1: $2 (Vast.ai 학습)
- Phase 2: $6 (케이스 확장 중 재학습 1회 + TTS 등)
- Phase 3: $1.50/월

---

## 5. 의존성 그래프

```
Sprint 0.1 (디렉토리)
    └─→ 0.2 (README)
    └─→ 0.4 (collect script)
         └─→ Day 3-4 (케이스 수집)
              └─→ Day 5 (dataset_builder)
                   └─→ Day 6-7 (Vast.ai 학습)
                        └─→ Day 8 (GGUF)
                             └─→ Day 9 (MCP 서버)
                                  └─→ Day 10 (재현 테스트)
                                       └─→ Phase 2 진입

Sprint 0.5 (골든 셋) ──────────────────────┐
Sprint 0.3 (devplan.html) ────────┐        │
                                   ↓        ↓
                              Phase 2 Sprint 2.1 (whitepaper UI)
                              Day 10 재현 테스트

Day 1-2 (플러그 + Orchestrator) — 독립, 언제든 가능
```

---

## 6. 블로커 조건 + 에스컬레이션

| 블로커 | 감지 | 대응 |
|--------|------|------|
| Vast.ai RTX 3090 재고 없음 | 검색 결과 0 | RTX 4090 대안 ($0.30/hr × 2h = $0.60 초과분 승인) |
| LoRA loss 수렴 실패 | 3 epoch 후 loss 1.0 초과 | lr 1e-4로 낮춰 재실행 |
| GGUF 변환 에러 | llama.cpp 버전 이슈 | llama.cpp 최신 pull |
| 재현 정확도 < 50% | Day 10 테스트 | **Phase 1 실패 선언**, v2 설계 회의 |
| 박씨 큐레이션 시간 부족 | Day 4까지 케이스 150 미만 | Claude 자동 큐레이션 의존도 확대, 박씨 태깅은 최소 50건만 |
| huggingface-cli login 블로커 | base 모델 다운로드 실패 | 박씨 HF 계정 토큰 필요 (p1b 펜딩 건과 동일) |
| 28 완전수 재논쟁 | 박씨 선호 바뀜 | D안 유지 근거 재확인, 강제 변경 시 v0.3 |

---

## 7. 커밋 전략

모든 커밋 포맷 (파피루스 헌법 준수):

```
{type}: {description}

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

Phase별 예상 커밋 수:
- Phase 0: ~5건
- Phase 1: ~15건 (일 1~2건)
- Phase 2: ~20건
- Phase 3: 월 ~4건 (재학습 + 피드백 배치)

**squash 금지 / reset --hard 금지 / revert만**. 파피루스 헌법 §2 4대원칙.

---

## 8. 오늘 당장 할 일 (박씨 승인 즉시)

1. ✅ (완료) 백서 v0.2 작성 → `docs/MCP-THERAPY-WHITEPAPER-v0.2.md`
2. ✅ (완료) DEVPLAN 작성 → `docs/MCP-THERAPY-DEVPLAN.md` (본 파일)
3. ⏳ `whitepaper.html` 제작 (본 세션)
4. ⏳ `index.html` 링크 추가 (본 세션)
5. ⏳ Sprint 0.1 디렉토리 골격 생성 (본 세션 가능)
6. ⬜ `devplan.html` 제작 (다음 세션)
7. ⬜ 박씨: 학파 논문/링크 10개 목록 작성 → `mcp/train/sources_queue.json`
8. ⬜ Phase 1 Day 1 착수

---

*본 DEVPLAN은 백서 v0.2의 실행 계획서다.*
*작성자: Claude Opus 4.7 | 감수 대기: Parksy*
*2026-04-24*
