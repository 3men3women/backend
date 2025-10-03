# ML 도입 가이드

이 문서는 향후 룰베이스 시스템을 ML 기반으로 전환할 때 사용하는 가이드입니다.

## 📁 파일 구조

```
backend/src/backend/emodia/
├── models.py               # DB 모델 (ML 인프라 포함)
│   ├── ExpertPoseTemplate  # 전문가 자세 템플릿
│   ├── FeedbackRating      # 사용자 피드백 평가
│   └── MLModel             # 학습된 모델 메타데이터
│
├── ml_utils.py            # 특징 추출 유틸리티
│   ├── extract_features()  # 키포인트 → 특징 벡터
│   ├── calculate_angle()   # 각도 계산
│   └── calculate_similarity() # 포즈 유사도
│
├── train_model.py         # 모델 학습 스크립트
│   ├── load_training_data()
│   ├── train_model()
│   └── train_and_save_model()
│
└── admin.py               # Django Admin 설정
```

---

## 🚀 ML 도입 단계

### Phase 1: 데이터 수집 (현재 완료)

**이미 구현된 것:**
- ✅ `PoseFrame` 모델로 사용자 포즈 자동 저장
- ✅ `ExpertPoseTemplate` 모델 준비됨
- ✅ Django Admin 인터페이스 구축

**다음 작업:**
1. 전문가에게 표준 자세 수집 요청
2. Admin 페이지에서 템플릿 등록

```python
# Django Admin → Expert Pose Templates → ADD
{
  "sports": "목풀기",
  "exercise_phase": "peak",  # 정점
  "quality_level": "perfect",
  "keypoints": [...],  # 전문가 포즈 좌표
  "description": "목을 왼쪽으로 30도 기울인 완벽한 자세"
}
```

**필요한 데이터 양:**
- 최소: 운동당 50개 템플릿
- 권장: 운동당 100~200개 템플릿
- 각 품질별 균등 분포:
  - perfect: 30%
  - good: 40%
  - acceptable: 20%
  - warning: 10%

---

### Phase 2: 모델 학습

**1. 마이그레이션 실행**

```bash
cd backend
poetry run python src/backend/manage.py makemigrations
poetry run python src/backend/manage.py migrate
```

**2. 모델 학습**

```bash
poetry run python src/backend/manage.py shell
```

```python
from emodia.train_model import train_and_save_model

# 목풀기 운동 모델 학습
ml_model = train_and_save_model(
    sports_id=1,
    trained_by="김전문가"
)

# 출력 예시:
# ✅ 데이터 로드 완료: 100개 샘플
#    - perfect: 30개
#    - good: 40개
#    - acceptable: 20개
#    - warning: 10개
# ✅ 학습 완료!
#    - 정확도: 87.5%
#    - 교차 검증 평균: 85.2% (+/- 3.4%)
```

**3. 모델 활성화**

```python
from emodia.train_model import activate_model

activate_model(ml_model.id)
# ✅ 모델 활성화 완료: 목풀기 - random_forest v20250103_143022
```

---

### Phase 3: 예측 로직 통합

**현재 (룰베이스):**
```python
# views.py의 generate_feedback()
def generate_feedback(keypoints):
    if nose_offset > 0.09:
        return "좋습니다"
```

**ML 버전:**
```python
# views.py
import joblib
from .models import MLModel
from .ml_utils import extract_features, normalize_features

def generate_feedback_ml(keypoints, sports_id):
    # 활성 모델 로드
    ml_model = MLModel.objects.get(sports_id=sports_id, is_active=True)
    model = joblib.load(ml_model.model_file.path)

    # 특징 추출
    features = extract_features(keypoints)
    X = [normalize_features(features)]

    # 예측
    quality = model.predict(X)[0]  # 'perfect', 'good', 'acceptable', 'warning'
    confidence = model.predict_proba(X)[0]

    # 피드백 생성
    if quality == 'perfect':
        return {
            'status': 'good',
            'messages': ['✓ 완벽합니다!'],
            'confidence': float(confidence.max())
        }
    elif quality == 'good':
        return {
            'status': 'good',
            'messages': ['✓ 좋습니다! 조금 더 당겨보세요'],
            'confidence': float(confidence.max())
        }
    # ... 나머지 처리
```

**하이브리드 버전 (추천):**
```python
def generate_feedback_hybrid(keypoints, sports_id):
    # 1. 안전 검사 (룰베이스)
    if is_dangerous(keypoints):
        return {'status': 'danger', 'messages': ['⚠️ 위험! 중단하세요']}

    # 2. ML 예측
    try:
        ml_result = generate_feedback_ml(keypoints, sports_id)
        return ml_result
    except MLModel.DoesNotExist:
        # ML 모델이 없으면 룰베이스로 폴백
        return generate_feedback(keypoints)
```

---

## 📊 모델 성능 모니터링

### Admin 페이지에서 확인

http://127.0.0.1:8000/admin/emodia/mlmodel/

- **정확도**: 80% 이상 목표
- **교차 검증**: 편차 5% 이내
- **중요 특징**: `nose_offset`, `shoulder_y_diff` 등

### 사용자 피드백 수집

```python
# views.py에 API 추가
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_feedback(request):
    """사용자가 피드백 유용성 평가"""
    FeedbackRating.objects.create(
        pose_frame_id=request.data['pose_frame_id'],
        user=request.user,
        is_helpful=request.data['is_helpful'],
        accuracy_rating=request.data.get('rating'),
        comment=request.data.get('comment', '')
    )
    return Response({'status': 'ok'})
```

---

## 🔄 모델 재학습 주기

**언제 재학습?**
1. 새로운 전문가 템플릿 추가 (50개 이상)
2. 사용자 피드백 부정적 비율 30% 초과
3. 새로운 운동 종류 추가
4. 3개월마다 정기 재학습

**재학습 방법:**
```python
# 새 버전 학습
new_model = train_and_save_model(sports_id=1, trained_by="김전문가")

# 성능 비교 후 활성화
if new_model.accuracy > old_model.accuracy:
    activate_model(new_model.id)
```

---

## 🧪 테스트

### 단위 테스트
```python
# tests.py
from emodia.ml_utils import extract_features

def test_feature_extraction():
    keypoints = [
        {'name': 'nose', 'x': 0.5, 'y': 0.3, 'score': 0.9},
        {'name': 'left_shoulder', 'x': 0.4, 'y': 0.5, 'score': 0.85},
        # ...
    ]
    features = extract_features(keypoints)

    assert 'nose_offset' in features
    assert -1 <= features['nose_offset'] <= 1
```

### A/B 테스트
```python
# 50% 룰베이스, 50% ML로 테스트
import random

def generate_feedback_ab_test(keypoints, sports_id):
    if random.random() < 0.5:
        method = 'rule_based'
        result = generate_feedback(keypoints)
    else:
        method = 'ml'
        result = generate_feedback_ml(keypoints, sports_id)

    # 로깅
    log_ab_test(method, result, user_feedback)

    return result
```

---

## 📈 예상 개선 효과

| 지표 | 룰베이스 | ML 예상 |
|------|---------|---------|
| 정확도 | ~70% | ~85% |
| 개인 맞춤 | ❌ | ✅ |
| 복잡한 자세 | ❌ | ✅ |
| 유지보수 | 수동 | 자동 학습 |

---

## 🛠 트러블슈팅

### 문제: 모델 정확도가 낮음 (< 70%)

**원인:**
- 데이터 부족 (< 50개)
- 데이터 불균형 (perfect만 많음)
- 노이즈 데이터

**해결:**
```python
# 1. 데이터 증강
from sklearn.utils import resample

# 소수 클래스 오버샘플링
perfect_samples = resample(perfect_data, n_samples=100)
```

### 문제: 모델 로딩 실패

**원인:**
- 파일 경로 문제
- scikit-learn 버전 불일치

**해결:**
```python
# settings.py에 경로 설정
MEDIA_ROOT = BASE_DIR / 'media'

# 버전 확인
poetry show scikit-learn
```

---

## 📚 추가 학습 자료

- [scikit-learn 공식 문서](https://scikit-learn.org/)
- [포즈 추정 논문](https://arxiv.org/abs/2104.02300)
- [Django ML 통합 가이드](https://docs.djangoproject.com/)

---

## ✅ 체크리스트

**ML 도입 전:**
- [ ] 전문가 템플릿 50개 이상 수집
- [ ] 품질별 균등 분포 확인
- [ ] 테스트 환경 구축

**ML 도입 후:**
- [ ] 정확도 80% 이상 확인
- [ ] A/B 테스트로 효과 검증
- [ ] 사용자 피드백 수집 시작
- [ ] 모니터링 대시보드 구축

---

**문의:** 개발팀
