# API 명세서

## **Base URL**
- **감정 기록 및 캘린더 API**: `http://127.0.0.1:8000/api/`
- **회원가입 및 로그인 API**: `http://127.0.0.1:8000/users/`

---

## **1. 감정 기록 관리**

### **1.1 감정 기록 목록 조회 및 생성**
- **URL**: `/emotions/`
- **Method**: `GET`, `POST`
- **Authentication**: Required (Token)
- **Permissions**: `IsAuthenticated`

#### **GET 요청**
- **설명**: 로그인한 사용자의 감정 기록 목록을 조회합니다.
- **쿼리 파라미터**:
  - `year` (선택): 특정 년도 필터링
  - `month` (선택): 특정 월 필터링
- **응답**:
  ```json
  [
      {
          "id": 1,
          "date": "2025-09-21",
          "emotion": "happy",
          "emotion_emoji": "😊",
          "emotion_name": "행복",
          "memo": "오늘은 정말 좋은 하루였어요!"
      },
      ...
  ]
  ```

#### **POST 요청**
- **설명**: 새로운 감정 기록을 생성합니다.
- **Body**:
  ```json
  {
      "date": "2025-09-21",
      "emotion": "happy",
      "memo": "오늘은 정말 좋은 하루였어요!"
  }
  ```
- **응답**:
  ```json
  {
      "id": 1,
      "user": 1,
      "username": "testuser",
      "date": "2025-09-21",
      "emotion": "happy",
      "emotion_display": "😊 행복",
      "emotion_emoji": "😊",
      "emotion_name": "행복",
      "memo": "오늘은 정말 좋은 하루였어요!",
      "created_at": "2025-09-21T12:00:00Z",
      "updated_at": "2025-09-21T12:00:00Z"
  }
  ```

---

### **1.2 특정 감정 기록 조회, 수정, 삭제**
- **URL**: `/emotions/{id}/`
- **Method**: `GET`, `PUT`, `PATCH`, `DELETE`
- **Authentication**: Required (Token)
- **Permissions**: `IsAuthenticated`

#### **GET 요청**
- **설명**: 특정 감정 기록을 조회합니다.
- **응답**:
  ```json
  {
      "id": 1,
      "user": 1,
      "username": "testuser",
      "date": "2025-09-21",
      "emotion": "happy",
      "emotion_display": "😊 행복",
      "emotion_emoji": "😊",
      "emotion_name": "행복",
      "memo": "오늘은 정말 좋은 하루였어요!",
      "created_at": "2025-09-21T12:00:00Z",
      "updated_at": "2025-09-21T12:00:00Z"
  }
  ```

#### **PUT/PATCH 요청**
- **설명**: 감정 기록을 수정합니다.
- **Body**:
  ```json
  {
      "emotion": "sad",
      "memo": "오늘은 조금 우울했어요."
  }
  ```
- **응답**:
  ```json
  {
      "id": 1,
      "user": 1,
      "username": "testuser",
      "date": "2025-09-21",
      "emotion": "sad",
      "emotion_display": "😰 우울",
      "emotion_emoji": "😰",
      "emotion_name": "우울",
      "memo": "오늘은 조금 우울했어요.",
      "created_at": "2025-09-21T12:00:00Z",
      "updated_at": "2025-09-21T12:30:00Z"
  }
  ```

#### **DELETE 요청**
- **설명**: 특정 감정 기록을 삭제합니다.
- **응답**:
  ```json
  {
      "message": "감정 기록이 삭제되었습니다."
  }
  ```

---

## **2. 날짜 기반 조회**

### **2.1 특정 날짜의 감정 기록 조회**
- **URL**: `/emotions/date/{date}/`
- **Method**: `GET`
- **Authentication**: Required (Token)
- **Permissions**: `IsAuthenticated`

#### **GET 요청**
- **설명**: 특정 날짜의 감정 기록을 조회합니다.
- **응답**:
  ```json
  {
      "id": 1,
      "user": 1,
      "username": "testuser",
      "date": "2025-09-21",
      "emotion": "happy",
      "emotion_display": "😊 행복",
      "emotion_emoji": "😊",
      "emotion_name": "행복",
      "memo": "오늘은 정말 좋은 하루였어요!",
      "created_at": "2025-09-21T12:00:00Z",
      "updated_at": "2025-09-21T12:00:00Z"
  }
  ```

---

### **2.2 감정 기록 생성 또는 수정**
- **URL**: `/emotions/save/`
- **Method**: `POST`
- **Authentication**: Required (Token)
- **Permissions**: `IsAuthenticated`

#### **POST 요청**
- **설명**: 같은 날짜에 기록이 있으면 수정, 없으면 생성합니다.
- **Body**:
  ```json
  {
      "date": "2025-09-21",
      "emotion": "happy",
      "memo": "오늘은 정말 좋은 하루였어요!"
  }
  ```
- **응답**:
  ```json
  {
      "id": 1,
      "user": 1,
      "username": "testuser",
      "date": "2025-09-21",
      "emotion": "happy",
      "emotion_display": "😊 행복",
      "emotion_emoji": "😊",
      "emotion_name": "행복",
      "memo": "오늘은 정말 좋은 하루였어요!",
      "created_at": "2025-09-21T12:00:00Z",
      "updated_at": "2025-09-21T12:00:00Z"
  }
  ```

---

## **3. 캘린더 데이터**

### **3.1 월별 감정 캘린더 데이터 조회**
- **URL**: `/emotions/calendar/{year}/{month}/`
- **Method**: `GET`
- **Authentication**: Required (Token)
- **Permissions**: `IsAuthenticated`

#### **GET 요청**
- **설명**: 월별 감정 캘린더 데이터를 조회합니다.
- **응답**:
  ```json
  {
      "year": 2025,
      "month": 9,
      "emotions": {
          "21": {
              "id": 1,
              "emotion": "happy",
              "emotion_emoji": "😊",
              "emotion_name": "행복",
              "memo": "오늘은 정말 좋은 하루였어요!"
          },
          ...
      }
  }
  ```

---

## **4. 회원가입 및 로그인**

### **4.1 회원가입**
- **Base URL**: `http://127.0.0.1:8000/users/`
- **URL**: `/register/`
- **Method**: `POST`
- **Authentication**: Not Required

#### **POST 요청**
- **설명**: 새로운 사용자 계정을 생성합니다.
- **Body**:
  ```json
  {
      "username": "testuser",
      "email": "testuser@example.com",
      "password": "password123",
      "password2": "password123"
  }
  ```
- **응답**:
  ```json
  {
      "id": 1,
      "username": "testuser",
      "email": "testuser@example.com"
  }
  ```

---

### **4.2 로그인**
- **Base URL**: `http://127.0.0.1:8000/users/`
- **URL**: `/login/`
- **Method**: `POST`
- **Authentication**: Not Required

#### **POST 요청**
- **설명**: 사용자 인증을 통해 토큰을 발급받습니다.
- **Body**:
  ```json
  {
      "username": "testuser",
      "password": "password123"
  }
  ```
- **응답**:
  ```json
  {
      "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
      "user": {
          "id": 1,
          "username": "testuser",
          "email": "testuser@example.com"
      }
  }
  ```

---

## **Authentication**
- 모든 API는 Token 기반 인증을 사용합니다.
- 헤더에 `Authorization: Token {your_token}`을 포함해야 합니다.

---

이 명세서를 기반으로 프론트엔드와 백엔드 간의 통신을 원활히 진행할 수 있습니다! 추가 요청이 있다면 말씀해주세요. 😊