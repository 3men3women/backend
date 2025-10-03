"""
ML 모델 학습 스크립트
향후 전문가 데이터가 충분히 쌓이면 이 스크립트를 실행하여 모델 학습

사용법:
    cd backend/src/backend
    poetry run python manage.py shell
    >>> from emodia.train_model import train_and_save_model
    >>> train_and_save_model(sports_id=1)
"""

import os
import joblib
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Django 모델 import는 실제 실행 시에만 작동
try:
    from .models import ExpertPoseTemplate, MLModel, Sports
    from .ml_utils import extract_features, normalize_features, get_feature_names
except:
    print("⚠️  Django 환경에서 실행해주세요")


def load_training_data(sports_id):
    """
    전문가 템플릿 데이터 로드

    Args:
        sports_id: 스포츠 ID (1: 목풀기, 2: 어깨풀기 등)

    Returns:
        X: 특징 벡터 리스트
        y: 라벨 리스트
    """
    templates = ExpertPoseTemplate.objects.filter(
        sports_id=sports_id,
        is_active=True
    )

    if templates.count() < 10:
        raise ValueError(f"⚠️  학습 데이터가 부족합니다. 최소 10개 필요 (현재: {templates.count()}개)")

    X = []
    y = []

    for template in templates:
        # 특징 추출
        if template.features:
            # 이미 계산된 특징 사용
            features = template.features
        else:
            # 실시간 계산
            features = extract_features(template.keypoints)

        # 특징 벡터로 변환
        feature_vector = normalize_features(features)
        X.append(feature_vector)
        y.append(template.quality_level)

    print(f"✅ 데이터 로드 완료: {len(X)}개 샘플")
    print(f"   - perfect: {y.count('perfect')}개")
    print(f"   - good: {y.count('good')}개")
    print(f"   - acceptable: {y.count('acceptable')}개")
    print(f"   - warning: {y.count('warning')}개")

    return np.array(X), np.array(y)


def train_model(X, y):
    """
    RandomForest 모델 학습

    Args:
        X: 특징 벡터
        y: 라벨

    Returns:
        model: 학습된 모델
        metrics: 성능 지표
    """
    # 데이터 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\n📊 데이터 분할:")
    print(f"   - 학습 데이터: {len(X_train)}개")
    print(f"   - 테스트 데이터: {len(X_test)}개")

    # 모델 학습
    print(f"\n🔄 모델 학습 중...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'  # 불균형 데이터 처리
    )
    model.fit(X_train, y_train)

    # 예측
    y_pred = model.predict(X_test)

    # 성능 평가
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n✅ 학습 완료!")
    print(f"   - 정확도: {accuracy:.2%}")

    # 교차 검증
    cv_scores = cross_val_score(model, X, y, cv=5)
    print(f"   - 교차 검증 평균: {cv_scores.mean():.2%} (+/- {cv_scores.std() * 2:.2%})")

    # 상세 분류 리포트
    print(f"\n📈 분류 리포트:")
    print(classification_report(y_test, y_pred))

    # Confusion Matrix
    print(f"\n🔍 혼동 행렬:")
    print(confusion_matrix(y_test, y_pred))

    # Feature Importance
    print(f"\n🎯 중요 특징 (Top 5):")
    feature_names = get_feature_names()
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:5]

    for i, idx in enumerate(indices):
        print(f"   {i+1}. {feature_names[idx]}: {importances[idx]:.3f}")

    metrics = {
        'accuracy': accuracy,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
    }

    return model, metrics


def save_model(model, sports_id, metrics, trained_by="System"):
    """
    모델을 파일로 저장하고 DB에 메타데이터 기록

    Args:
        model: 학습된 모델
        sports_id: 스포츠 ID
        metrics: 성능 지표
        trained_by: 학습 담당자
    """
    # 모델 파일 저장
    os.makedirs('ml_models', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"ml_models/posture_model_sports{sports_id}_{timestamp}.pkl"

    joblib.dump(model, filename)
    print(f"\n💾 모델 저장: {filename}")

    # DB에 메타데이터 저장
    sports = Sports.objects.get(id=sports_id)

    ml_model = MLModel.objects.create(
        sports=sports,
        model_type='random_forest',
        version=f"v{timestamp}",
        model_file=filename,
        accuracy=metrics['accuracy'],
        precision=None,  # classification_report에서 추출 가능
        recall=None,
        f1_score=None,
        training_samples=len(ExpertPoseTemplate.objects.filter(sports_id=sports_id, is_active=True)),
        trained_by=trained_by,
        is_active=False,  # 수동으로 활성화 필요
        notes=f"CV: {metrics['cv_mean']:.2%} (+/- {metrics['cv_std'] * 2:.2%})"
    )

    print(f"✅ DB 기록 완료: MLModel ID={ml_model.id}")

    return ml_model


def train_and_save_model(sports_id, trained_by="System"):
    """
    전체 학습 파이프라인 실행

    Args:
        sports_id: 스포츠 ID
        trained_by: 학습 담당자 이름

    Returns:
        ml_model: 저장된 MLModel 객체
    """
    print(f"🚀 ML 모델 학습 시작: Sports ID={sports_id}")
    print("=" * 60)

    try:
        # 1. 데이터 로드
        X, y = load_training_data(sports_id)

        # 2. 모델 학습
        model, metrics = train_model(X, y)

        # 3. 모델 저장
        ml_model = save_model(model, sports_id, metrics, trained_by)

        print("\n" + "=" * 60)
        print("✅ 학습 완료!")
        print(f"   - 모델 ID: {ml_model.id}")
        print(f"   - 정확도: {ml_model.accuracy:.2%}")
        print(f"   - 활성화: python manage.py shell")
        print(f"     >>> from emodia.models import MLModel")
        print(f"     >>> model = MLModel.objects.get(id={ml_model.id})")
        print(f"     >>> model.is_active = True")
        print(f"     >>> model.save()")

        return ml_model

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        raise


def activate_model(model_id):
    """
    특정 모델을 활성화 (기존 활성 모델은 비활성화)

    Args:
        model_id: 활성화할 MLModel ID
    """
    try:
        new_model = MLModel.objects.get(id=model_id)

        # 기존 활성 모델 비활성화
        MLModel.objects.filter(
            sports=new_model.sports,
            is_active=True
        ).update(is_active=False)

        # 새 모델 활성화
        new_model.is_active = True
        new_model.save()

        print(f"✅ 모델 활성화 완료: {new_model}")

    except MLModel.DoesNotExist:
        print(f"❌ 모델을 찾을 수 없습니다: ID={model_id}")


# ========== 사용 예시 ==========

"""
# Django shell에서 실행:

from emodia.train_model import train_and_save_model, activate_model

# 1. 모델 학습
ml_model = train_and_save_model(sports_id=1, trained_by="홍길동")

# 2. 모델 활성화
activate_model(ml_model.id)

# 3. 모델 로드 및 예측 (views.py에서 사용)
from emodia.models import MLModel
import joblib

active_model = MLModel.objects.get(sports_id=1, is_active=True)
model = joblib.load(active_model.model_file.path)

# 예측
from emodia.ml_utils import extract_features, normalize_features
features = extract_features(keypoints)
X = [normalize_features(features)]
prediction = model.predict(X)[0]  # 'perfect', 'good', 'acceptable', 'warning'
"""
