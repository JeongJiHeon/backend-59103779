# Architecture Documentation

## 시스템 아키텍처

### 전체 구조

```
┌─────────────────┐
│   Client/UI     │
└────────┬────────┘
         │ HTTP/HTTPS
         ▼
┌─────────────────────────────────┐
│    FastAPI Application          │
│  ┌──────────────────────────┐  │
│  │   API Routes (v1)        │  │
│  │  - Auth                  │  │
│  │  - Users                 │  │
│  │  - Calendar Events       │  │
│  │  - Google Auth           │  │
│  │  - AI Agent              │  │
│  └──────────┬───────────────┘  │
│             │                   │
│  ┌──────────▼───────────────┐  │
│  │   Business Services      │  │
│  │  - User Service          │  │
│  │  - Calendar Service      │  │
│  │  - Google Calendar Svc   │  │
│  │  - Agent Service         │  │
│  └──────────┬───────────────┘  │
│             │                   │
│  ┌──────────▼───────────────┐  │
│  │   Data Access Layer      │  │
│  │  - SQLAlchemy Models     │  │
│  │  - Database Session      │  │
│  └──────────┬───────────────┘  │
└─────────────┼───────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌─────────┐      ┌──────────┐      ┌─────────────────┐
│PostgreSQL│      │  Redis   │      │ Google Calendar │
│Database  │      │  Cache   │      │      API        │
└─────────┘      └──────────┘      └─────────────────┘
```

## 레이어 구조

### 1. API Layer (app/api/)
- **역할**: HTTP 요청 처리, 응답 생성
- **구성요소**:
  - Routes: API 엔드포인트 정의
  - Dependencies: 공통 의존성 (인증, DB 세션)
  - Middleware: CORS, 보안 헤더

### 2. Service Layer (app/services/)
- **역할**: 비즈니스 로직 구현
- **구성요소**:
  - UserService: 사용자 관리
  - CalendarService: 캘린더 이벤트 관리
  - GoogleCalendarService: 구글 캘린더 연동
  - AgentService: AI 에이전트 로직

### 3. Data Layer (app/db/)
- **역할**: 데이터 영속성 관리
- **구성요소**:
  - Models: SQLAlchemy ORM 모델
  - Session: 데이터베이스 세션 관리
  - Base: 공통 베이스 모델

### 4. Schema Layer (app/schemas/)
- **역할**: 데이터 검증 및 직렬화
- **구성요소**:
  - Request Schemas: 입력 데이터 검증
  - Response Schemas: 출력 데이터 구조
  - Common Schemas: 공통 스키마

### 5. Core Layer (app/core/)
- **역할**: 핵심 설정 및 유틸리티
- **구성요소**:
  - Config: 환경 설정 관리
  - Security: 인증/인가 로직
  - Logging: 로깅 설정

## 데이터 흐름

### 1. 인증 플로우

```
Client → POST /auth/register
  ↓
API Layer (auth.py)
  ↓
UserService.create_user()
  ↓
Password Hashing (security.py)
  ↓
Database (User Model)
  ↓
JWT Token Generation
  ↓
Response with Tokens
```

### 2. 캘린더 이벤트 생성 플로우

```
Client → POST /events (with JWT)
  ↓
Authentication Middleware
  ↓
API Layer (calendar_events.py)
  ↓
CalendarService.create_event()
  ↓
Database (CalendarEvent Model)
  ↓
[Optional] GoogleCalendarService.create_event()
  ↓
Response with Event Data
```

### 3. AI 에이전트 플로우

```
Client → POST /agent/tasks
  ↓
API Layer (agent.py)
  ↓
AgentService.create_task()
  ↓
Background Task Processing
  ↓
AgentService.process_task()
  ↓
NLP Processing (_parse_natural_language)
  ↓
Extract Event Information
  ↓
Save Task Result
  ↓
Client → POST /agent/tasks/{id}/create-event
  ↓
CalendarService.create_event()
  ↓
Response with Event Data
```

## 데이터베이스 스키마

### ERD (Entity Relationship Diagram)

```
┌──────────────────┐
│      Users       │
├──────────────────┤
│ id (PK)          │
│ email (UNIQUE)   │
│ name             │
│ password_hash    │
│ is_google_connected │
│ created_at       │
│ updated_at       │
│ is_active        │
└────────┬─────────┘
         │ 1
         │
         │ N
    ┌────┴────────────────────────────────┐
    │                                     │
    ▼                                     ▼
┌──────────────────┐              ┌──────────────────┐
│ CalendarEvents   │              │ GoogleCredentials│
├──────────────────┤              ├──────────────────┤
│ id (PK)          │              │ id (PK)          │
│ user_id (FK)     │              │ user_id (FK)     │
│ google_event_id  │              │ access_token     │
│ title            │              │ refresh_token    │
│ description      │              │ token_uri        │
│ location         │              │ client_id        │
│ start_time       │              │ client_secret    │
│ end_time         │              │ scopes           │
│ timezone         │              │ expiry           │
│ is_synced        │              │ created_at       │
│ is_all_day       │              │ updated_at       │
│ created_at       │              └──────────────────┘
│ updated_at       │
│ is_active        │
└──────────────────┘
         │
         │
         ▼
┌──────────────────┐
│   AgentTasks     │
├──────────────────┤
│ id (PK)          │
│ user_id (FK)     │
│ input_text       │
│ status           │
│ result           │
│ error_message    │
│ created_at       │
│ updated_at       │
│ is_active        │
└──────────────────┘
```

## 보안 아키텍처

### 인증 흐름

```
1. User Registration
   └─> Password Hashing (Bcrypt)
   └─> Store in Database

2. User Login
   └─> Verify Password
   └─> Generate JWT Access Token (30 min)
   └─> Generate JWT Refresh Token (7 days)
   └─> Return Tokens

3. Authenticated Requests
   └─> Extract JWT from Header
   └─> Verify Token Signature
   └─> Extract User ID
   └─> Load User from Database
   └─> Process Request
```

### 보안 레이어

1. **Transport Security**
   - HTTPS (프로덕션)
   - CORS Policy
   - Security Headers

2. **Authentication**
   - JWT Tokens
   - Password Hashing (Bcrypt)
   - Token Expiration

3. **Authorization**
   - User-based Access Control
   - Resource Ownership Validation

4. **Data Protection**
   - Input Validation (Pydantic)
   - SQL Injection Prevention (ORM)
   - XSS Protection

## 확장성 고려사항

### 수평 확장 (Horizontal Scaling)

```
┌─────────────┐
│Load Balancer│
└──────┬──────┘
       │
   ┌───┴────────────────┐
   │                    │
   ▼                    ▼
┌──────┐            ┌──────┐
│ API  │            │ API  │
│ Pod 1│            │ Pod 2│
└───┬──┘            └───┬──┘
    │                   │
    └─────────┬─────────┘
              │
        ┌─────┴──────┐
        │            │
        ▼            ▼
    ┌───────┐   ┌───────┐
    │  DB   │   │ Redis │
    │Primary│   │Cluster│
    └───┬───┘   └───────┘
        │
        ▼
    ┌───────┐
    │  DB   │
    │Replica│
    └───────┘
```

### 성능 최적화

1. **Database**
   - Connection Pooling
   - Async Operations
   - Proper Indexing
   - Query Optimization

2. **Caching**
   - Redis for Session Data
   - Response Caching
   - Query Result Caching

3. **Application**
   - Async/Await Pattern
   - Background Tasks
   - Pagination
   - Lazy Loading

## 모니터링 및 로깅

### 로깅 레벨

```
ERROR   - 에러 발생 시
WARNING - 경고 사항
INFO    - 주요 이벤트
DEBUG   - 디버깅 정보
```

### 모니터링 포인트

1. **Application Metrics**
   - Request Rate
   - Response Time
   - Error Rate
   - Active Users

2. **Infrastructure Metrics**
   - CPU Usage
   - Memory Usage
   - Disk I/O
   - Network Traffic

3. **Business Metrics**
   - User Registrations
   - Events Created
   - Google Calendar Syncs
   - Agent Task Success Rate

## 배포 전략

### CI/CD Pipeline

```
Code Push → GitHub
    ↓
Run Tests (pytest)
    ↓
Build Docker Image
    ↓
Push to Registry
    ↓
Deploy to Staging
    ↓
Integration Tests
    ↓
Manual Approval
    ↓
Deploy to Production
    ↓
Health Check
    ↓
Monitor Metrics
```

### 환경 분리

1. **Development**
   - Local Development
   - Docker Compose
   - Debug Mode Enabled

2. **Staging**
   - Production-like Environment
   - Integration Testing
   - Performance Testing

3. **Production**
   - High Availability
   - Monitoring & Alerting
   - Backup & Recovery

## 기술적 의사결정

### FastAPI 선택 이유
- ✅ 높은 성능 (Starlette 기반)
- ✅ 자동 API 문서화
- ✅ Type Hints 지원
- ✅ 비동기 처리 지원
- ✅ 현대적인 Python 기능 활용

### PostgreSQL 선택 이유
- ✅ ACID 트랜잭션 보장
- ✅ 복잡한 쿼리 지원
- ✅ JSON 데이터 타입 지원
- ✅ 우수한 확장성
- ✅ 활발한 커뮤니티

### SQLAlchemy ORM 선택 이유
- ✅ 비동기 지원
- ✅ 강력한 ORM 기능
- ✅ 마이그레이션 도구 (Alembic)
- ✅ Type Safety
- ✅ 유연한 쿼리 작성

### Redis 선택 이유
- ✅ 빠른 인메모리 캐싱
- ✅ 다양한 데이터 구조
- ✅ TTL 지원
- ✅ 세션 관리에 최적
- ✅ 확장 가능

## 향후 개선 사항

### 단기 (1-3개월)
- [ ] LLM 통합 (더 정확한 자연어 처리)
- [ ] Rate Limiting 구현
- [ ] 이메일 알림 시스템
- [ ] 이벤트 반복 기능

### 중기 (3-6개월)
- [ ] WebSocket 지원 (실시간 업데이트)
- [ ] 다중 캘린더 지원
- [ ] 팀/그룹 기능
- [ ] 고급 검색 기능

### 장기 (6-12개월)
- [ ] 모바일 앱 개발
- [ ] AI 기반 스케줄 최적화
- [ ] 통합 알림 센터
- [ ] 분석 대시보드
