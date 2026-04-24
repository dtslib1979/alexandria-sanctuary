# Alexandria MCP-Therapy · Railway 배포용
# 파피루스 eae_mcp_writer 502 해결 패턴 이식:
# - python:3.11-slim (MCP SDK 호환성)
# - EXPOSE 8000 (Railway 엣지 프록시 포트 디스커버리)
# - CMD python -m alex_mcp.server --sse

FROM python:3.11-slim

WORKDIR /app

# 의존성 먼저 (레이어 캐시)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 복사
COPY alex_mcp/ ./alex_mcp/

# Railway 엣지 프록시 포트 디스커버리
EXPOSE 8000

# SSE 모드 실행 (RAILWAY_ENVIRONMENT 자동 감지, PORT 환경변수 준수)
CMD ["python", "-m", "alex_mcp.server", "--sse"]
