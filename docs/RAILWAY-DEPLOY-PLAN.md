# Alexandria MCP-Therapy · Railway 배포 세부 계획서

**작성**: 2026-04-24
**상태**: 헌법 개정 완료, 박씨 승인 시 착수
**타겟**: Railway Hobby ($5/월)
**납기**: 90분
**선행 커밋**: `68606bc` (v1.4 + 매뉴얼 완료)

---

## 0. 헌법 개정 요약 (방금 완료)

### Before (2026-04-18)
> "클라우드 서버 영구 포기. PC를 서버로 전환도 금지. Oracle/GCP/AWS/Azure 전부."

### After (2026-04-24)
> "원칙 유지. **단 MCP 앱(alexandria-therapy)만 예외** — Railway Hobby 배포 허용. 박씨 멀티 디바이스 접근 + 앱 백업이 근거."

**적용 범위**:
- ✅ alexandria-therapy MCP (본 건)
- ✅ 미래 박씨 직접 만든 MCP 앱
- ❌ 일반 VM 임차 여전히 금지
- ❌ "서버 있으면 좋겠다" 발상 여전히 금지

메모리 파일:
- `feedback_no_cloud_server.md` (개정 반영)
- `project_alexandria_mcp_railway.md` (신규)
- `MEMORY.md` 인덱스 업데이트

---

## 1. 박씨가 원하는 최종 상태

```
박씨 폰 Claude Code ─────┐
박씨 탭 Claude Code ─────┤
박씨 WSL PC ─────────────┼─→ https://alexandria-therapy.up.railway.app/mcp
박씨 외부 PC ────────────┤          (24/7 가용, SSE)
(선택) 친구 Claude Code ─┘

              Railway 서버
              ├── alex_mcp.server_http (SSE)
              ├── rules/ (박씨 규칙)
              ├── plugs/ (11개)
              ├── core/ (axes + plutchik)
              └── safety/ (crisis_detector)
```

- 박씨 PC 꺼져 있어도 폰에서 사용 가능
- 박씨 PC 고장 나도 엔진은 Railway에 살아있음
- git 커밋 = 자동 배포 (Railway GitHub 연동)

---

## 2. 기술 설계

### 2.1 Transport 선택

| 옵션 | 장점 | 단점 | 채택 |
|---|---|---|:--:|
| **Streamable HTTP** (MCP 공식 2026 표준) | 양방향, 세션 유지, 미래 표준 | 클라이언트 호환성 제한 | **권장** |
| SSE (Server-Sent Events) | 넓은 호환성, 단방향 스트림 | 2025 deprecated 예정 | 백업 |
| WebSocket | 실시간 | 세션 관리 복잡 | ❌ |
| stdio | 로컬 단순 | 원격 불가 | 유지 (병행) |

**결정**: Streamable HTTP 우선, SSE fallback. stdio 은 로컬 테스트용 유지.

### 2.2 서버 파일 구조

```
alexandria-sanctuary/
├── alex_mcp/
│   ├── server.py              # 기존 stdio (유지)
│   ├── server_http.py         # 🆕 HTTP SSE 서버 (Railway용)
│   └── ... (기존 모듈 전부 재활용)
├── Dockerfile                 # 🆕 Railway 빌드
├── railway.toml               # 🆕 Railway 설정
├── requirements.txt           # 갱신 (mcp, uvicorn, fastapi)
└── .dockerignore              # 🆕
```

### 2.3 server_http.py 설계

```python
"""
MCP HTTP SSE 서버 — Railway 배포용.
기존 stdio 서버의 모든 도구 재활용.
"""
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse
import uvicorn
import os

# 기존 stdio 서버에서 tool 핸들러만 import
from alex_mcp.server import app as mcp_app

# SSE transport
sse = SseServerTransport("/mcp/messages/")

async def handle_sse(request):
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_app.run(
            streams[0], streams[1], mcp_app.create_initialization_options()
        )

async def health(request):
    return JSONResponse({"status": "ok", "service": "alexandria-therapy"})

routes = [
    Route("/health", endpoint=health),
    Route("/mcp/sse", endpoint=handle_sse),
    Mount("/mcp/messages/", app=sse.handle_post_message),
]

app = Starlette(routes=routes)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 2.4 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 의존성 먼저 (레이어 캐시)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 복사
COPY alex_mcp/ ./alex_mcp/

# 포트
EXPOSE 8000

# Railway가 PORT env 주입
CMD ["python", "-m", "alex_mcp.server_http"]
```

### 2.5 railway.toml

```toml
[build]
builder = "DOCKERFILE"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### 2.6 requirements.txt

```
mcp>=0.9.0
uvicorn>=0.27.0
starlette>=0.36.0
pydantic>=2.0.0
```

---

## 3. 6 단계 실행 계획 (총 90분)

### Step 1 (25분) · server_http.py 작성

- alex_mcp/server_http.py 생성
- stdio 서버의 모든 tool 재활용 (`from alex_mcp.server import app`)
- SSE endpoint + /health 엔드포인트
- 로컬 테스트: `python -m alex_mcp.server_http` → `curl localhost:8000/health`

**성공 기준**: localhost 에서 curl 로 /health 응답 받음. MCP client 로 SSE 연결 가능.

### Step 2 (15분) · Dockerfile + railway.toml + requirements.txt

- 위 스펙대로 3 파일 작성
- 로컬 빌드 검증: `docker build -t alex-test .` (Docker 있으면)
- 없으면 스킵하고 Railway 빌드에서 확인

**성공 기준**: Dockerfile 문법 오류 없음.

### Step 3 (15분) · Railway 프로젝트 생성 + 배포

```bash
# Option A: Railway CLI
npm install -g @railway/cli
railway login
railway init          # 프로젝트 이름: alexandria-therapy
railway up            # 현재 디렉토리 배포

# Option B: GitHub 연동 (권장)
# Railway 대시보드에서 GitHub 레포 선택 → 자동 배포
```

**성공 기준**: Railway 대시보드에서 배포 로그 성공. URL 발급 (`https://alexandria-therapy-production.up.railway.app`).

### Step 4 (10분) · 원격 검증

```bash
# Health
curl https://alexandria-therapy-production.up.railway.app/health
# → {"status": "ok", "service": "alexandria-therapy"}

# MCP inspector (옵션)
npx @modelcontextprotocol/inspector sse https://...up.railway.app/mcp/sse
# → 5개 도구 보여야 함
```

**성공 기준**: health 200, MCP 도구 5개 노출.

### Step 5 (10분) · 박씨 디바이스 .mcp.json 업데이트

파피루스 `.mcp.json` 에 URL 추가:

```json
{
  "mcpServers": {
    "alexandria-therapy-local": {
      "type": "stdio",
      "command": "python3",
      "args": ["-m", "alex_mcp.server"],
      "cwd": "/home/dtsli/alexandria-sanctuary"
    },
    "alexandria-therapy-remote": {
      "type": "sse",
      "url": "https://alexandria-therapy-production.up.railway.app/mcp/sse"
    }
  }
}
```

두 엔드포인트 공존 (로컬 + 원격). 박씨가 선택 가능.

박씨 폰/탭 `.mcp.json` 도 같이 배포 (원격만 있어도 OK).

### Step 6 (15분) · 실제 호출 + 텔레그램 보고

- Claude Code 재시작
- 박씨 2026-04-24 꿈 입력 → `analyze_dream` 호출
- 원격 서버가 응답하는지 확인
- 결과 텔레그램 전송

**성공 기준**: 폰 Claude Code 에서 박씨 꿈 분석 답변 수신.

---

## 4. 박씨 실사용 흐름 (배포 후)

### 폰에서

```
박씨 폰 Termux → claude
박씨: "어제 이런 꿈 꿨어 [내용] 분석해봐"
   ↓ Claude Code → Railway 원격 MCP 호출
   ↓ enforcer 통과
박씨 폰 화면에 리포트 표시
```

PC 켜져 있을 필요 없음.

### 탭에서도 동일

### 외부 PC에서 (출장/친구집)

- `.mcp.json` 에 URL 한 줄만 복사
- Claude Code 로그인
- 동일하게 사용

### 친구에게 공유 (박씨 허용 시)

- URL + (v2 에서 API key) 만 전달
- 친구는 `git clone` / `pip install` 필요 없음
- 친구 Claude Code → 박씨 엔진 직접 호출
- **LLM 과금은 친구 본인 Claude Code 구독**
- 박씨 부담: Railway $5/월만

---

## 5. 비용 분석

### 박씨 부담

| 항목 | 월 |
|---|:--:|
| Railway Hobby | $5 |
| 트래픽 (박씨 혼자 월 30회) | $0 (Hobby 포함) |
| 실질 지출 | **$5/월 (60,000원/년)** |

### Railway Hobby 크레딧

- 월 $5 크레딧 포함
- 실사용 ≤ $5 면 **실질 무료**
- 초과분만 유료

박씨 정신분석 엔진 = 순수 Python + 경량 요청. 월 30~100회 호출로는 크레딧 초과 가능성 낮음.

### LLM 과금

- **박씨 Claude Max 정액** = 박씨 본인 호출 시 과금 0
- **친구 Claude** = 친구 구독 과금 (박씨 무관)

---

## 6. 보안 및 운영

### v1 (즉시 배포)

- 인증 없음 (박씨 본인 URL만 아는 구조)
- 텔레그램으로 URL 전달 시에만 접근 가능
- 리스크: URL 유출 시 익명 호출 가능 (단, 악용 여지 낮음 — crisis 감지 + sanitizer 이미 내장)

### v2 (친구 공유 시, 2주 내)

- API key 헤더 추가 (`X-API-Key: ...`)
- Railway env variable 로 키 관리
- 박씨 + 친구별 다른 key 발급
- 요청 당 key 검증 → 유효 아니면 403

### v3 (필요 시)

- OAuth / JWT
- Rate limit (사용자별 분당 N회)
- Audit log DB (박씨 확인용)

---

## 7. 리스크 & 대응

| 리스크 | 대응 |
|------|------|
| Railway 502 재발 (파피루스 사례) | /health 엔드포인트 + Dockerfile EXPOSE + uvicorn host 0.0.0.0 전부 미리 반영 |
| Streamable HTTP 클라이언트 호환성 | SSE transport 로 fallback. Claude Code 최신 버전은 둘 다 지원 |
| MCP SDK Python 버전 이슈 | Python 3.11 고정 (Dockerfile) |
| 의존성 변경 시 로컬 stdio 깨짐 | server.py 와 server_http.py 분리 유지. 공통 부분만 공유 |
| Railway 월 $5 크레딧 초과 | 사용량 모니터링. 초과 시 v2 API key 로 접근 제한 |

---

## 8. 검증 체크리스트

Step 6 완료 시 모두 ✅ 나와야 함:

- [ ] `curl https://...up.railway.app/health` → 200
- [ ] MCP Inspector 로 연결 → 5 tools 노출
- [ ] 박씨 폰 Claude Code `/mcp` → `alexandria-therapy-remote` 보임
- [ ] 박씨 폰에서 꿈 입력 → 박씨 톤 리포트 반환
- [ ] `analyze_narrative` 호출 → pre-LLM 구조 반환
- [ ] `evaluate_text` 호출 → 루브릭 점수 반환
- [ ] `get_system_prompt` 호출 → 1125자 프롬프트
- [ ] crisis L2 문장 테스트 → 1393 에스컬레이션 반환
- [ ] Railway 대시보드 실시간 로그 확인

---

## 9. 다음 지시 대기

**(A) 지금 착수 — 90분 후 박씨 폰에서 원격 사용 가능**

나의 진행:
1. server_http.py 작성
2. Dockerfile + railway.toml + requirements.txt
3. 로컬 검증
4. Railway 배포 (박씨 Railway 계정 상태 확인 필요)
5. 엔드포인트 테스트
6. .mcp.json 업데이트
7. 박씨 2026-04-24 꿈 실제 원격 호출 + 텔레그램 보고

박씨 필요 액션:
- Railway 계정 로그인 상태 확인
- GitHub 연동 허용
- 비용 $5/월 승인

**(B) v2 API key 인증까지 포함 — 2시간**

**(C) v1만 먼저 + 박씨 확인 후 v2** — 권장

---

## 10. 문서 이력

| 날짜 | 버전 | 변경 |
|------|------|------|
| 2026-04-24 | v1.0 | 헌법 개정 + 배포 세부 플랜 |

---

*본 계획서는 박씨 헌법 개정 (feedback_no_cloud_server.md 2026-04-24) 근거.*
*project_alexandria_mcp_railway.md 메모리 연동.*
*작성: Claude Opus 4.7 | 2026-04-24*
