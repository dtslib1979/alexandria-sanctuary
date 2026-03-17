---

## ⚡ 특별법 제1조: 플랫폼 자동화 도구 우선순위 (전 레포 공통 — 2026-03-18)

> **플랫폼 자동화 작업 시 Claude는 반드시 이 순서를 따른다. 임의로 스크립트 작성 금지.**

```
0순위: API / 터미널
  → 항상 먼저 확인. 되면 끝. 아래로 내려가지 않는다.

      ↓ API/터미널로 안 될 때만

1순위: Claude in Chrome (Chrome 확장)
  → GUI 클릭 필수 작업 (구글 콘솔, YouTube Studio, OAuth 등)
  → Claude가 브라우저 안에서 직접 보고 클릭. UI 변화 자동 적응.

2순위: Playwright MCP
  → Claude가 브라우저 외부에서 직접 조작

3순위: CDP/스크립트 (tools/ 경로)
  → 반복 배치. 사람 없이 야간 자동 실행.
```

**Claude 행동 규칙: 위 순서를 건너뛰고 스크립트를 먼저 짜는 것은 헌법 위반이다.**

---

# CLAUDE.md — alexandria-sanctuary


---

## Browser Runtime

> Parksy OS 2+2 매트릭스 — 이 레포 전담 브라우저

| 항목 | 값 |
|------|-----|
| **브라우저** | MS Edge |
| **이유** | 글로벌 영어 영적 케어 — 몰입형 읽기 |
| **URL** | https://github.com/dtslib1979/alexandria-sanctuary |
