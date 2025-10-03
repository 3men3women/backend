"""
ML 학습을 위한 유틸리티 함수들
향후 ML 도입 시 사용할 특징 추출 및 데이터 처리 함수
"""

import math
from typing import Dict, List, Optional


def get_keypoint(keypoints: List[Dict], name: str) -> Optional[Dict]:
    """키포인트 리스트에서 특정 이름의 키포인트 추출"""
    for kp in keypoints:
        if kp.get('name') == name:
            return kp
    return None


def euclidean_distance(kp1: Dict, kp2: Dict) -> float:
    """두 키포인트 간 유클리드 거리"""
    dx = kp1['x'] - kp2['x']
    dy = kp1['y'] - kp2['y']
    return math.sqrt(dx * dx + dy * dy)


def calculate_angle(p1: Dict, p2: Dict, p3: Dict) -> float:
    """
    세 점으로 이루는 각도 계산 (p2가 꼭짓점)
    반환값: 0~180도
    """
    # 벡터 계산
    v1_x = p1['x'] - p2['x']
    v1_y = p1['y'] - p2['y']
    v2_x = p3['x'] - p2['x']
    v2_y = p3['y'] - p2['y']

    # 내적과 외적
    dot = v1_x * v2_x + v1_y * v2_y
    det = v1_x * v2_y - v1_y * v2_x

    # 각도 계산 (라디안 → 도)
    angle_rad = math.atan2(det, dot)
    angle_deg = math.degrees(angle_rad)

    return abs(angle_deg)


def calculate_symmetry(keypoints: List[Dict]) -> float:
    """
    좌우 대칭성 계산
    반환값: 0~1 (1이 완벽한 대칭)
    """
    left_shoulder = get_keypoint(keypoints, 'left_shoulder')
    right_shoulder = get_keypoint(keypoints, 'right_shoulder')
    left_elbow = get_keypoint(keypoints, 'left_elbow')
    right_elbow = get_keypoint(keypoints, 'right_elbow')

    if not all([left_shoulder, right_shoulder, left_elbow, right_elbow]):
        return 0.0

    # 어깨 중심선
    center_x = (left_shoulder['x'] + right_shoulder['x']) / 2

    # 좌우 거리 차이
    left_dist = abs(left_elbow['x'] - center_x)
    right_dist = abs(right_elbow['x'] - center_x)

    # 대칭성 점수
    if left_dist + right_dist == 0:
        return 1.0

    symmetry = 1 - abs(left_dist - right_dist) / (left_dist + right_dist)
    return max(0.0, min(1.0, symmetry))


def extract_features(keypoints: List[Dict]) -> Dict[str, float]:
    """
    키포인트에서 ML 학습용 특징 추출

    Args:
        keypoints: 포즈 키포인트 리스트 [{name, x, y, score}, ...]

    Returns:
        특징 딕셔너리
    """
    features = {}

    # 키포인트 추출
    nose = get_keypoint(keypoints, 'nose')
    left_ear = get_keypoint(keypoints, 'left_ear')
    right_ear = get_keypoint(keypoints, 'right_ear')
    left_shoulder = get_keypoint(keypoints, 'left_shoulder')
    right_shoulder = get_keypoint(keypoints, 'right_shoulder')
    left_elbow = get_keypoint(keypoints, 'left_elbow')
    right_elbow = get_keypoint(keypoints, 'right_elbow')
    left_wrist = get_keypoint(keypoints, 'left_wrist')
    right_wrist = get_keypoint(keypoints, 'right_wrist')

    # === 기본 측정값 ===

    # 1. 머리 기울기 (코의 어깨 중심선 대비 오프셋)
    if nose and left_shoulder and right_shoulder:
        shoulder_center_x = (left_shoulder['x'] + right_shoulder['x']) / 2
        features['nose_offset'] = nose['x'] - shoulder_center_x
    else:
        features['nose_offset'] = 0.0

    # 2. 어깨 Y축 차이 (수평 체크)
    if left_shoulder and right_shoulder:
        features['shoulder_y_diff'] = abs(left_shoulder['y'] - right_shoulder['y'])
    else:
        features['shoulder_y_diff'] = 0.0

    # 3. 귀 Y축 차이 (머리 기울기)
    if left_ear and right_ear:
        features['ear_y_diff'] = left_ear['y'] - right_ear['y']
    else:
        features['ear_y_diff'] = 0.0

    # === 각도 측정 ===

    # 4. 목 기울기 각도
    if nose and left_shoulder and right_shoulder:
        features['neck_tilt_angle'] = calculate_angle(
            left_shoulder,
            {'x': shoulder_center_x, 'y': (left_shoulder['y'] + right_shoulder['y']) / 2},
            nose
        )
    else:
        features['neck_tilt_angle'] = 0.0

    # 5. 어깨 기울기 각도
    if left_shoulder and right_shoulder:
        # 수평선과의 각도
        dx = right_shoulder['x'] - left_shoulder['x']
        dy = right_shoulder['y'] - left_shoulder['y']
        features['shoulder_tilt_angle'] = abs(math.degrees(math.atan2(dy, dx)))
    else:
        features['shoulder_tilt_angle'] = 0.0

    # === 거리 측정 ===

    # 6. 코-어깨 거리
    if nose and left_shoulder:
        features['nose_to_left_shoulder_dist'] = euclidean_distance(nose, left_shoulder)
    else:
        features['nose_to_left_shoulder_dist'] = 0.0

    # 7. 어깨 너비
    if left_shoulder and right_shoulder:
        features['shoulder_width'] = euclidean_distance(left_shoulder, right_shoulder)
    else:
        features['shoulder_width'] = 0.0

    # === 대칭성 ===

    # 8. 좌우 대칭성
    features['symmetry'] = calculate_symmetry(keypoints)

    # === 신뢰도 ===

    # 9. 평균 키포인트 신뢰도
    scores = [kp['score'] for kp in keypoints if 'score' in kp]
    features['avg_confidence'] = sum(scores) / len(scores) if scores else 0.0

    # 10. 최소 키포인트 신뢰도
    features['min_confidence'] = min(scores) if scores else 0.0

    return features


def calculate_similarity(keypoints1: List[Dict], keypoints2: List[Dict]) -> float:
    """
    두 포즈 간 유사도 계산

    Args:
        keypoints1: 사용자 포즈
        keypoints2: 전문가 템플릿 포즈

    Returns:
        유사도 (0~1, 1이 완전히 동일)
    """
    features1 = extract_features(keypoints1)
    features2 = extract_features(keypoints2)

    # 각 특징별 차이 계산
    total_diff = 0.0
    feature_count = 0

    for key in features1.keys():
        if key in features2:
            diff = abs(features1[key] - features2[key])
            total_diff += diff
            feature_count += 1

    if feature_count == 0:
        return 0.0

    # 평균 차이를 유사도로 변환 (차이가 작을수록 유사도 높음)
    avg_diff = total_diff / feature_count
    similarity = 1 / (1 + avg_diff)  # 0~1 범위로 정규화

    return similarity


def normalize_features(features: Dict[str, float]) -> List[float]:
    """
    특징 딕셔너리를 ML 모델 입력용 벡터로 변환

    Args:
        features: extract_features()로 추출한 특징

    Returns:
        정규화된 특징 벡터 (리스트)
    """
    # 특징 순서 고정 (학습 시와 예측 시 순서가 동일해야 함)
    feature_order = [
        'nose_offset',
        'shoulder_y_diff',
        'ear_y_diff',
        'neck_tilt_angle',
        'shoulder_tilt_angle',
        'nose_to_left_shoulder_dist',
        'shoulder_width',
        'symmetry',
        'avg_confidence',
        'min_confidence',
    ]

    return [features.get(key, 0.0) for key in feature_order]


def get_feature_names() -> List[str]:
    """ML 모델에 사용되는 특징 이름 목록 반환"""
    return [
        'nose_offset',
        'shoulder_y_diff',
        'ear_y_diff',
        'neck_tilt_angle',
        'shoulder_tilt_angle',
        'nose_to_left_shoulder_dist',
        'shoulder_width',
        'symmetry',
        'avg_confidence',
        'min_confidence',
    ]
