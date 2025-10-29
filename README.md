# Google Calendar Agent API

구글 캘린더 작성 에이전트를 위한 완전한 FastAPI 백엔드 애플리케이션입니다. 자연어 입력을 통해 AI가 자동으로 캘린더 이벤트를 생성하고 관리할 수 있습니다.

## 주요 기능

### 인증 및 사용자 관리
- ✅ JWT 기반 인증 시스템
- ✅ 사용자 등록 및 로그인
- ✅ 액세스 토큰 및 리프레시 토큰
- ✅ 비밀번호 해싱 (bcrypt)

### 캘린더 이벤트 관리
- ✅ 캘린더 이벤트 CRUD 작업
- ✅ 날짜 범위별 이벤트 필터링
- ✅ 구글 캘린더 동기화
- ✅ 타임존 지원

### 구글 캘린더 연동
- ✅ OAuth 2.0 인증
- ✅ 구글 캘린더 이벤트 생성/수정/삭제
- ✅ 양방향 동기화

### AI 에이전트
- ✅ 자연어 입력 처리
- ✅ 자동 이벤트 정보 추출
- ✅ 비동기 작업 처리
- ✅ 작업 상태 추적

## 기술 스택

### 백엔드 프레임워크
- **FastAPI** - 최신 Python 웹 프레임워크
- **Python 3.11+** - 프로그래밍 언어
- **Uvicorn** - ASGI 서버

### 데이터베이스
- **PostgreSQL** - 주 데이터베이스
- **SQLAlchemy** - ORM (비동기 지원)
- **Alembic** - 데이터베이스 마이그레이션

### 캐싱
- **Redis** - 캐싱 및 세션 관리

### 인증 및 보안
- **JWT (python-jose)** - JSON Web Token
- **Passlib + Bcrypt** - 비밀번호 해싱
- **CORS Middleware** - 크로스 오리진 지원

### 외부 API
- **Google Calendar API** - 구글 캘린더 연동
- **Google OAuth 2.0** - 구글 인증

### 개발 도구
- **Pytest** - 테스트 프레임워크
- **Docker & Docker Compose** - 컨테이너화
- **Loguru** - 로깅

## 프로젝트 구조

```
.
├── app/
│   ├── api/
│   │   ├── deps.py              # API 의존성
│   │   └── routes/
│   │       └── v1/
│   │           ├── health.py    # 헬스체크
│   │           ├── auth.py      # 인증
│   │           ├── users.py     # 사용자 관리
│   │           ├── calendar_events.py  # 캘린더 이벤트
│   │           ├── google_auth.py      # 구글 OAuth
│   │           └── agent.py     # AI 에이전트
│   ├── core/
│   │   ├── config.py           # 설정 관리
│   │   ├── security.py         # 보안 유틸리티
│   │   └── logging.py          # 로깅 설정
│   ├── db/
│   │   ├── base.py             # 베이스 모델
│   │   ├── session.py          # 데이터베이스 세션
│   │   └── models/             # SQLAlchemy 모델
│   │       ├── user.py
│   │       ├── calendar_event.py
│   │       ├── google_credential.py
│   │       └── agent_task.py
│   ├── schemas/                # Pydantic 스키마
│   ├── services/               # 비즈니스 로직
│   └── main.py                 # 애플리케이션 진입점
├── alembic/                    # 데이터베이스 마이그레이션
├── tests/                      # 테스트
├── docker-compose.yml          # Docker Compose 설정
├── Dockerfile                  # Docker 이미지
├── requirements.txt            # Python 의존성
└── .env.example               # 환경 변수 예시
```

## 설치 및 실행

### 1. 사전 요구사항

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (선택사항)

### 2. 로컬 개발 환경 설정

#### 2.1 저장소 클론

```bash
git clone <repository-url>
cd workspace
```

#### 2.2 가상 환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

#### 2.3 의존성 설치

```bash
pip install -r requirements.txt
```

#### 2.4 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정
```

필수 환경 변수:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/calendar_agent
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

#### 2.5 데이터베이스 마이그레이션

```bash
alembic upgrade head
```

#### 2.6 애플리케이션 실행

```bash
uvicorn app.main:app --reload
```

API 문서: http://localhost:8000/docs

### 3. Docker로 실행

#### 3.1 Docker Compose로 전체 스택 실행

```bash
docker-compose up -d
```

서비스:
- **API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

#### 3.2 로그 확인

```bash
docker-compose logs -f api
```

#### 3.3 중지

```bash
docker-compose down
```

## API 문서

### API 엔드포인트

#### 인증 (Authentication)

| 메소드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/v1/auth/register` | 사용자 등록 |
| POST | `/api/v1/auth/login` | 로그인 |
| POST | `/api/v1/auth/refresh` | 토큰 갱신 |

#### 사용자 (Users)

| 메소드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/v1/users/me` | 현재 사용자 정보 |
| PUT | `/api/v1/users/me` | 사용자 정보 수정 |
| DELETE | `/api/v1/users/me` | 사용자 삭제 |

#### 캘린더 이벤트 (Calendar Events)

| 메소드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/v1/events` | 이벤트 생성 |
| GET | `/api/v1/events` | 이벤트 목록 |
| GET | `/api/v1/events/{id}` | 이벤트 조회 |
| PUT | `/api/v1/events/{id}` | 이벤트 수정 |
| DELETE | `/api/v1/events/{id}` | 이벤트 삭제 |

#### 구글 캘린더 (Google Calendar)

| 메소드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/v1/google/auth-url` | OAuth URL 생성 |
| GET | `/api/v1/google/callback` | OAuth 콜백 |
| GET | `/api/v1/google/status` | 연결 상태 확인 |
| DELETE | `/api/v1/google/disconnect` | 연결 해제 |

#### AI 에이전트 (Agent)

| 메소드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/v1/agent/tasks` | 에이전트 작업 생성 |
| GET | `/api/v1/agent/tasks` | 작업 목록 |
| GET | `/api/v1/agent/tasks/{id}` | 작업 조회 |
| POST | `/api/v1/agent/tasks/{id}/create-event` | 작업에서 이벤트 생성 |

#### 헬스체크 (Health Check)

| 메소드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/v1/health` | API 헬스체크 |
| GET | `/api/v1/health/db` | 데이터베이스 헬스체크 |

### 인터랙티브 API 문서

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 테스트

### 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_auth.py

# 상세 출력
pytest -v

# 커버리지와 함께 실행
pytest --cov=app --cov-report=html
```

### 테스트 종류

- **Unit Tests**: 개별 함수 및 메소드 테스트
- **Integration Tests**: API 엔드포인트 테스트
- **End-to-End Tests**: 전체 워크플로우 테스트

## 사용 예시

### 1. 사용자 등록 및 로그인

```bash
# 사용자 등록
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "SecurePass123"
  }'

# 응답
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 2. 캘린더 이벤트 생성

```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "팀 회의",
    "description": "주간 팀 미팅",
    "location": "회의실 A",
    "start_time": "2025-10-30T10:00:00Z",
    "end_time": "2025-10-30T11:00:00Z",
    "timezone": "Asia/Seoul",
    "sync_to_google": false
  }'
```

### 3. AI 에이전트로 이벤트 생성

```bash
# 자연어로 작업 생성
curl -X POST http://localhost:8000/api/v1/agent/tasks \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "내일 오후 3시에 팀 회의를 회의실 B에서 1시간 동안 진행"
  }'

# 응답에서 task_id 확인 후 이벤트 생성
curl -X POST http://localhost:8000/api/v1/agent/tasks/{task_id}/create-event \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. 구글 캘린더 연동

```bash
# OAuth URL 받기
curl -X GET http://localhost:8000/api/v1/google/auth-url \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 브라우저에서 auth_url 방문하여 인증
# 콜백 후 자동으로 연결됨

# 연결 상태 확인
curl -X GET http://localhost:8000/api/v1/google/status \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 보안

### 인증
- JWT 기반 인증 시스템
- 액세스 토큰 (30분 유효)
- 리프레시 토큰 (7일 유효)

### 비밀번호
- Bcrypt 해싱
- 최소 8자 이상
- 대문자, 소문자, 숫자 포함 필수

### API 보안
- HTTPS 사용 권장 (프로덕션)
- CORS 정책 설정
- 보안 헤더 추가
- Rate Limiting (선택사항)

## 데이터베이스 마이그레이션

### 새 마이그레이션 생성

```bash
alembic revision --autogenerate -m "Add new table"
```

### 마이그레이션 적용

```bash
# 최신 버전으로 업그레이드
alembic upgrade head

# 특정 버전으로 업그레이드
alembic upgrade <revision>

# 한 단계 롤백
alembic downgrade -1
```

### 마이그레이션 이력 확인

```bash
alembic history
alembic current
```

## 배포

### 프로덕션 설정

1. 환경 변수 설정
```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<strong-random-key>
DATABASE_URL=<production-database-url>
ALLOWED_ORIGINS=https://yourdomain.com
```

2. HTTPS 설정
3. 데이터베이스 백업 설정
4. 로깅 모니터링 설정
5. Rate Limiting 활성화

### Docker로 배포

```bash
# 프로덕션 이미지 빌드
docker build -t calendar-agent-api:latest .

# 컨테이너 실행
docker run -d \
  --name calendar-agent-api \
  -p 8000:8000 \
  --env-file .env.production \
  calendar-agent-api:latest
```

## 문제 해결

### 데이터베이스 연결 오류

```bash
# PostgreSQL이 실행 중인지 확인
docker-compose ps

# 로그 확인
docker-compose logs postgres

# 연결 테스트
psql -h localhost -U postgres -d calendar_agent
```

### 마이그레이션 오류

```bash
# 마이그레이션 상태 확인
alembic current

# 데이터베이스 초기화 (개발 환경만)
alembic downgrade base
alembic upgrade head
```

## 개발 가이드

### 코드 스타일
- PEP 8 준수
- Type hints 사용
- Docstrings 작성

### 커밋 메시지
- feat: 새로운 기능
- fix: 버그 수정
- docs: 문서 변경
- test: 테스트 추가/수정
- refactor: 코드 리팩토링

## 라이선스

This project is licensed under the MIT License.

## 기여

버그 리포트, 기능 제안, Pull Request를 환영합니다!

## 연락처

문의사항이 있으시면 이슈를 생성해주세요.

---

**Google Calendar Agent API** - AI-powered Calendar Management System
