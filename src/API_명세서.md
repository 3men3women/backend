# Emodia API 명세서

## 개요
Emodia는 사용자의 일일 감정 상태를 기록하고, 감정에 따라 적절한 운동을 추천하는 감정 케어 플랫폼입니다.

### 기술 스택
- **Backend**: Django 4.0 + Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**: MySQL
- **File Storage**: Django File Field (Local Media)

### Base URL
```
http://127.0.0.1:8000
```

---

## 인증 (Authentication)

### JWT 토큰 발급
모든 API 요청에는 Authorization 헤더에 JWT 토큰이 필요합니다.
```
Authorization: Bearer <access_token>
```

### 토큰 갱신
```http
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "<refresh_token>"
}
```

---

## 1. 사용자 관리 (Users)

### 1.1 회원가입
```http
POST /users/register/
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "password2": "password123"
}
```

**응답 예시:**
```json
{
    "msg": "회원가입 성공",
    "user_id": 1,
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 1.2 일반 로그인
```http
POST /users/login/
Content-Type: application/json

{
    "username": "testuser",
    "password": "password123"
}
```

**응답 예시:**
```json
{
    "msg": "로그인 성공",
    "user_id": 1,
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 1.3 카카오 로그인
```http
GET /users/kakao/login/
```
카카오 로그인 페이지로 리다이렉트됩니다.

### 1.4 카카오 로그인 콜백
```http
GET /users/kakao/callback/?code=<authorization_code>
```
카카오 인증 완료 후 프론트엔드로 JWT 토큰과 함께 리다이렉트됩니다.

---

## 2. 프로필 관리 (Profiles)

### 2.1 내 프로필 조회/수정
```http
GET /profiles/me/
Authorization: Bearer <access_token>
```

```http
PUT /profiles/me/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "main_goal": "relax",
    "routine_time": "09:00:00"
}
```

**main_goal 옵션:**
- `relax`: 목, 어깨 뭉침 완화
- `sleep`: 수면의 질 개선
- `stress`: 스트레스 관리
- `habit`: 꾸준한 기록 습관 만들기
- `energy`: 에너지 회복

**응답 예시:**
```json
{
    "id": 1,
    "main_goal": "relax",
    "routine_time": "09:00:00",
    "created_at": "2025-10-02T10:00:00Z",
    "updated_at": "2025-10-02T10:00:00Z"
}
```

---

## 3. 감정 기록 관리 (Emotions)

### 3.1 감정 기록 목록 조회
```http
GET /api/emotions/
Authorization: Bearer <access_token>
```

**쿼리 파라미터:**
- `year`: 년도 필터링 (예: 2025)
- `month`: 월 필터링 (예: 10)
- `user_id`: 관리자 전용 - 특정 사용자의 기록 조회

**응답 예시:**
```json
[
    {
        "id": 1,
        "date": "2025-10-02",
        "emotion": "happy",
        "emotion_emoji": "😊",
        "emotion_name": "행복",
        "emotion_score": 7,
        "memo": "오늘은 정말 좋은 하루였다!",
        "sports": {
            "id": 1,
            "name": "목풀기"
        },
        "related_videos": [
            {
                "id": 1,
                "video_url": "/media/videos/neckstretch.mp4"
            }
        ],
        "created_at": "2025-10-02T10:00:00Z"
    }
]
```

### 3.2 감정 기록 생성
```http
POST /api/emotions/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "date": "2025-10-02",
    "emotion": "happy",
    "memo": "오늘은 정말 좋은 하루였다!"
}
```

**감정 옵션 (emotion):**
- `sad`: 😰 우울 (점수: 0)
- `tired`: 🥱 지침 (점수: 1)
- `anxious`: 😰 불안 (점수: 2)
- `angry`: 😡 분노 (점수: 3)
- `neutral`: 😐 보통 (점수: 4)
- `calm`: 😌 차분 (점수: 5)
- `excited`: 🤩 설렘 (점수: 6)
- `happy`: 😊 행복 (점수: 7)

### 3.3 특정 감정 기록 조회
```http
GET /api/emotions/{id}/
Authorization: Bearer <access_token>
```

### 3.4 감정 기록 수정
```http
PUT /api/emotions/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "emotion": "calm",
    "memo": "수정된 메모"
}
```

### 3.5 감정 기록 삭제
```http
DELETE /api/emotions/{id}/
Authorization: Bearer <access_token>
```

### 3.6 특정 날짜의 감정 기록 조회
```http
GET /api/emotions/date/2025-10-02/
Authorization: Bearer <access_token>
```

### 3.7 감정 기록 생성/수정 (스마트 저장)
```http
POST /api/emotions/save/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "date": "2025-10-02",
    "emotion": "happy",
    "memo": "오늘은 정말 좋은 하루였다!"
}
```
> 같은 날짜에 기록이 있으면 수정, 없으면 새로 생성됩니다.

### 3.8 월별 감정 캘린더 조회
```http
GET /api/emotions/calendar/2025/10/
Authorization: Bearer <access_token>
```

**응답 예시:**
```json
{
    "year": 2025,
    "month": 10,
    "emotions": {
        "1": {
            "id": 1,
            "emotion": "happy",
            "emotion_emoji": "😊",
            "emotion_name": "행복",
            "memo": "좋은 하루"
        },
        "2": {
            "id": 2,
            "emotion": "tired",
            "emotion_emoji": "🥱",
            "emotion_name": "지침",
            "memo": "피곤한 하루"
        }
    }
}
```

---

## 4. 스포츠 및 영상 추천 시스템

### 감정 점수에 따른 자동 운동 추천
감정 기록 생성 시 자동으로 다음과 같이 운동이 매핑됩니다:

| 감정 | 점수 | 추천 운동 |
|------|------|-----------|
| 😰 우울 (sad) | 0 | 목풀기 |
| 🥱 지침 (tired) | 1 | 목풀기 |
| 😰 불안 (anxious) | 2 | 어깨풀기 |
| 😡 분노 (angry) | 3 | 목풀기 |
| 😐 보통 (neutral) | 4 | 어깨풀기 |
| 😌 차분 (calm) | 5 | 어깨풀기 |
| 🤩 설렘 (excited) | 6 | 어깨풀기 |
| 😊 행복 (happy) | 7 | 목풀기 |

### 운동 영상 조회
감정 기록 조회 시 `related_videos` 필드에서 추천된 운동 영상을 확인할 수 있습니다.

**영상 파일 접근:**
```
GET /media/videos/{filename}
```

---

## 5. 에러 응답

### 인증 관련 에러
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 권한 관련 에러
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 유효성 검사 에러
```json
{
    "emotion": ["This field is required."],
    "date": ["Enter a valid date."]
}
```

### 404 에러
```json
{
    "detail": "Not found."
}
```

---

## 6. 관리자 기능

### Admin 페이지
```
GET /admin/
```

관리자는 다음 기능을 사용할 수 있습니다:
- 모든 사용자의 감정 기록 조회 (`?user_id=<id>` 파라미터 사용)
- 스포츠 종목 관리
- 운동 영상 업로드 및 관리

---

## 7. 미디어 파일 처리

### 파일 업로드
운동 영상은 관리자 페이지를 통해 업로드 가능하며, `/media/videos/` 경로에 저장됩니다.

### 파일 접근
```
GET /media/videos/{filename}
```

---

## 8. CORS 설정

현재 다음 도메인에서의 요청을 허용합니다:
- `http://localhost:3000` (프론트엔드 개발 서버)

---

## 주요 특징

1. **JWT 인증**: 토큰 기반 인증으로 보안성 확보
2. **카카오 소셜 로그인**: 간편한 로그인 경험 제공
3. **자동 운동 추천**: 감정 상태에 따른 맞춤형 운동 추천
4. **캘린더 뷰**: 월별 감정 기록을 캘린더 형태로 제공
5. **미디어 파일 지원**: 운동 영상 스트리밍 지원
6. **프로필 관리**: 개인 목표 및 루틴 시간 설정

## 데이터베이스 구조

### 주요 모델
- **User**: Django 기본 사용자 모델
- **Profile**: 사용자 프로필 (목표, 루틴 시간)
- **EmotionRecord**: 일일 감정 기록
- **Sports**: 운동 종목 (목풀기, 어깨풀기)
- **EmotionVideo**: 운동별 영상 파일
