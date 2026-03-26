# 001 — 채널 셋업 + 서세서 플랜 + YouTube 플레이리스트 설계

> 날짜: 2026-03-26
> 환경: Termux (핸드폰) — Claude Code
> 상태: 플레이리스트 생성 미완 → WSL2 환경에서 재개 예정

---

## 1. 작업 요약

### 1-1. 파피루스 본사 파싱 — 넥스트 서세서 플랜 확정

`dtslib-papyrus/docs/WHITEPAPER-BRANCH-STRATEGY-2026-03.md` 업데이트:

**정정사항:**
- 호야당 아저씨 = 파파플라이 (64세) → **동일 인물** (2개 레포 겸임)
- 제자 4명 → 실제 3인 (호야당/파파플라이 + 고씨 + 동선)

**서세서 2인 확정 (2026-03-26):**

| 순위 | 인물 | 관계 | 채널 | 조건 |
|------|------|------|------|------|
| **1순위** | 조카 (목사) | 혈연 조카 | `@one_spoon_bible` | 파이프라인 이해 + 운영 의지 |
| **2순위** | artrew | 지인 딸 미대생 | `@artrew-i1w` | 커머스 임상 후 합류 |

- 두 사람 모두 **28개 레포 전체 상속 가능** 대상
- 단계적 이관 조건: 박씨 파이프라인 이해 확인 후

---

### 1-2. Alexandria Sanctuary 레포 현황 파악

**진척도: 설계 70% / 구현 30%**

```
존재하는 것:
├── index.html (395줄, 메인 랜딩)
├── sanctuary/ (cave-retreat, hospice, residence)
├── philosophy/ (철학 페이지)
├── library/, forum/, visit/ (스켈레톤)
├── card/, staff/ (명함 + 스태프 포털)
├── 00_TRUTH/VISION_MASTER.md (비전 마스터)
└── assets/ (CSS 디자인 시스템, JS, SVG 엠블렘)

없는 것:
- YouTube 채널 연결 (0%)
- 실제 콘텐츠
- 목사/영성 파트너 연결
```

---

### 1-3. YouTube 채널 확인

**@alexandria-y6k**
- channel_id: `UCt-pTP_Bketi7o9R-2Q7tPA`
- 계정: B (`dtslib1979@gmail.com`)
- 토큰 상태: **만료** (재인증 필요)
- 플레이리스트: **0개** (미생성)

---

### 1-4. 플레이리스트 설계 (레포 구조 × 7게이트 매핑)

레포 디렉토리 구조와 VISION_MASTER.md 7게이트 세계관을 매핑해 9개 플레이리스트 설계:

| 플레이리스트 | 레포 경로 | 게이트 | 연결 파트너 |
|---|---|---|---|
| GATE 1 — 정신의 붕괴 | sanctuary/hospice | 조현병·치매 | — |
| GATE 2 — 자아의 소멸 | sanctuary/hospice | 치매·기억 | — |
| GATE 3 — 신의 접속 | philosophy | 성령·은사 | **조카 목사** |
| GATE 4 — 제도의 안과 밖 | philosophy | 크로스 종교 | **조카 목사** |
| GATE 5 — 소리와 영혼 | library | 성가·범패 | — |
| GATE 6 — 금기의 문 | sanctuary/cave-retreat | 홀로트로픽 | — |
| GATE 7 — 마지막 게이트 | sanctuary/residence | 입주 멤버십 | — |
| ≡크로스 종교 대담≡ | forum | 외부 파트너 | **조카 @one_spoon_bible** |
| 알렉산드리아 — 공간 이야기 | — | 세계관 | — |

---

### 1-5. YouTube 재인증 시도 — 미완

**문제:** `token_b.json` refresh_token 만료 (`invalid_grant`)

**시도한 것:**
- `reauth_b.py` — localhost:3000 콜백 서버 방식
- `reauth-and-create.py` — 재인증 + 플레이리스트 생성 원스텝

**차단 원인:**
- Termux 세션 = 핸드폰 환경
- Playwright MCP 미연결 (이 세션에 없음)
- OAuth 콜백 서버 포트 충돌 (3000번 중복 점유)

**결론: WSL2 환경에서 재개 필요**

---

## 2. 생성된 파일

```
dtslib-papyrus/tools/youtube/
├── create-alexandria-playlists.py   # 플레이리스트 9개 생성 스크립트
├── reauth_b.py                      # account B 재인증 (콜백 서버)
└── reauth-and-create.py             # 재인증 + 플레이리스트 원스텝
```

---

## 3. 다음 작업 (WSL2에서)

```
1. cd ~/dtslib-papyrus
2. python3 tools/youtube/reauth-and-create.py
   → Chrome 자동 열기 (Playwright headless=False)
   → dtslib1979@gmail.com 로그인 → 허용
   → 플레이리스트 9개 자동 생성
3. channel-playlists.json 결과 확인
4. feeds/wisdom.json에 YouTube 채널 연결 추가
5. staff/index.html에 조카 목사 파트너 등재
```

---

## 4. 연결 관계 (확정)

```
조카 목사 (@one_spoon_bible)
    │
    ├── dtslib-papyrus → 1순위 서세서 (28개 레포)
    └── alexandria-sanctuary
            ├── GATE 3, 4 콘텐츠 파트너
            └── ≡크로스 종교 대담≡ 플레이리스트 참여
```

---

*작성: Claude Code (Termux 세션) | 2026-03-26*
*다음 세션: WSL2 환경 — YouTube OAuth + 플레이리스트 생성 완료*
