from django.db import models
from django.contrib.auth.models import User


class Sports(models.Model):
    """스포츠 종류"""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class EmotionVideo(models.Model):
    """스포츠별로 연결된 영상"""
    sports = models.ForeignKey(Sports, related_name="videos", on_delete=models.CASCADE)
    video = models.FileField(upload_to="videos/")  # media/videos/ 폴더 안에 저장
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sports.name} - {self.video.name}"


class EmotionRecord(models.Model):
    """사용자의 일별 감정 기록"""

    EMOTION_CHOICES = [
        ('sad', '😰 우울'),
        ('tired', '🥱 지침'),
        ('anxious', '😰 불안'),
        ('angry', '😡 분노'),
        ('neutral', '😐 보통'),
        ('calm', '😌 차분'),
        ('excited', '🤩 설렘'),
        ('happy', '😊 행복'),
    ]

    # 감정 → 점수 매핑
    EMOTION_SCORES = {
        'sad': 0,
        'tired': 1,
        'anxious': 2,
        'angry': 3,
        'neutral': 4,
        'calm': 5,
        'excited': 6,
        'happy': 7,
    }

    # 점수 → 스포츠 매핑 (Sports.id와 매핑)
    SCORE_TO_SPORTS = {
        0: 1,  # sad → 목풀기
        1: 1,  # tired → 목풀기
        2: 2,  # anxious → 어깨풀기
        3: 1,  # angry → 목풀기
        4: 2,  # neutral → 어깨풀기
        5: 2,  # calm → 어깨풀기
        6: 2,  # excited → 어깨풀기
        7: 1,  # happy → 목풀기
    }

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='emotion_records',
        verbose_name='사용자'
    )
    date = models.DateField(verbose_name='날짜')
    emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES, verbose_name='감정 상태')
    emotion_score = models.IntegerField(default=0, verbose_name="감정 점수")
    memo = models.TextField(blank=True, null=True, verbose_name='메모')

    # ✅ 24.07.29 추가 필드 (StartPage 6단계)
    intensity = models.IntegerField(default=50, null=True, blank=True, verbose_name='감정 강도')
    tags = models.JSONField(default=list, null=True, blank=True, verbose_name='태그')
    mood_after = models.CharField(max_length=50, null=True, blank=True, verbose_name='운동 후 기분')
    voice_of_mind = models.TextField(null=True, blank=True, verbose_name='마음의 소리')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시간')

    # ✅ FK로 변경 (드롭다운 지원)
    sports = models.ForeignKey(
        Sports,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="records",
        verbose_name="자동 매핑된 스포츠"
    )

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name = '감정 기록'
        verbose_name_plural = '감정 기록들'

    def __str__(self):
        emotion_display = dict(self.EMOTION_CHOICES).get(self.emotion, self.emotion)
        return f"{self.user.username} - {self.date} ({emotion_display})"

    @property
    def emotion_emoji(self):
        return dict(self.EMOTION_CHOICES).get(self.emotion, '').split(' ')[0]

    @property
    def emotion_name(self):
        parts = dict(self.EMOTION_CHOICES).get(self.emotion, '').split(' ')
        return parts[1] if len(parts) > 1 else ''

    def save(self, *args, **kwargs):
        # ✅ 감정 → 점수
        self.emotion_score = self.EMOTION_SCORES.get(self.emotion, 0)

        # ✅ 점수 → 스포츠 자동 매핑 (FK 저장)
        sports_id = self.SCORE_TO_SPORTS.get(self.emotion_score, None)
        self.sports = Sports.objects.filter(id=sports_id).first() if sports_id else None

        super().save(*args, **kwargs)

    @property
    def related_videos(self):
        """이 감정 기록에 연결된 영상들"""
        return EmotionVideo.objects.filter(sports=self.sports)


class WorkoutSession(models.Model):
    """운동 세션 기록"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_sessions')
    sports = models.ForeignKey(Sports, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0, help_text="운동 시간(초)")

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.user.username} - {self.sports.name} ({self.start_time})"


class PoseFrame(models.Model):
    """실시간 포즈 좌표 기록"""
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='pose_frames')
    timestamp = models.FloatField(help_text="세션 시작 후 경과 시간(초)")
    keypoints = models.JSONField(help_text="포즈 키포인트 좌표 데이터")
    feedback = models.JSONField(null=True, blank=True, help_text="교정 피드백 데이터")

    class Meta:
        ordering = ['session', 'timestamp']

    def __str__(self):
        return f"Frame at {self.timestamp}s"


# ========== ML 인프라 모델 (향후 사용) ==========

class ExpertPoseTemplate(models.Model):
    """전문가가 제공한 표준 자세 템플릿"""
    QUALITY_CHOICES = [
        ('perfect', '완벽'),
        ('good', '좋음'),
        ('acceptable', '수용 가능'),
        ('warning', '경고'),
    ]

    PHASE_CHOICES = [
        ('start', '시작'),
        ('middle', '중간'),
        ('peak', '정점'),
        ('end', '종료'),
    ]

    sports = models.ForeignKey(Sports, on_delete=models.CASCADE, related_name='expert_templates')
    exercise_phase = models.CharField(max_length=20, choices=PHASE_CHOICES, help_text="운동 단계")
    quality_level = models.CharField(max_length=20, choices=QUALITY_CHOICES, help_text="자세 품질")
    keypoints = models.JSONField(help_text="정답 포즈 좌표")

    # 메타데이터
    description = models.TextField(help_text="자세 설명 (예: 목을 왼쪽으로 30도 기울인 상태)")
    created_by = models.CharField(max_length=100, help_text="전문가 이름")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, help_text="ML 학습에 사용 여부")

    # ML 특징 (자동 계산, 캐싱용)
    features = models.JSONField(null=True, blank=True, help_text="추출된 특징 벡터")

    class Meta:
        ordering = ['sports', 'exercise_phase', 'quality_level']
        verbose_name = '전문가 자세 템플릿'
        verbose_name_plural = '전문가 자세 템플릿들'

    def __str__(self):
        return f"{self.sports.name} - {self.get_exercise_phase_display()} ({self.get_quality_level_display()})"


class FeedbackRating(models.Model):
    """사용자 피드백 평가 (ML 학습용)"""
    pose_frame = models.ForeignKey(PoseFrame, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # 피드백 유용성
    is_helpful = models.BooleanField(help_text="이 피드백이 도움이 되었나요?")
    accuracy_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="피드백 정확도 (1-5)"
    )

    # 사용자 코멘트
    comment = models.TextField(blank=True, help_text="추가 의견")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '피드백 평가'
        verbose_name_plural = '피드백 평가들'

    def __str__(self):
        return f"Rating by {self.user.username} - {'👍' if self.is_helpful else '👎'}"


class MLModel(models.Model):
    """학습된 ML 모델 메타데이터"""
    MODEL_TYPE_CHOICES = [
        ('rule_based', '룰베이스'),
        ('random_forest', 'Random Forest'),
        ('neural_network', 'Neural Network'),
        ('hybrid', '하이브리드'),
    ]

    sports = models.ForeignKey(Sports, on_delete=models.CASCADE, related_name='ml_models')
    model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES)
    version = models.CharField(max_length=50, help_text="모델 버전 (예: v1.0)")

    # 모델 파일
    model_file = models.FileField(upload_to='ml_models/', help_text="저장된 모델 파일 (.pkl)")

    # 성능 지표
    accuracy = models.FloatField(null=True, blank=True, help_text="정확도")
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)

    # 학습 정보
    training_samples = models.IntegerField(help_text="학습 데이터 수")
    trained_at = models.DateTimeField(auto_now_add=True)
    trained_by = models.CharField(max_length=100)

    # 배포 상태
    is_active = models.BooleanField(default=False, help_text="현재 사용 중인 모델")
    notes = models.TextField(blank=True, help_text="모델 설명 및 변경사항")

    class Meta:
        ordering = ['-trained_at']
        verbose_name = 'ML 모델'
        verbose_name_plural = 'ML 모델들'

    def __str__(self):
        return f"{self.sports.name} - {self.model_type} {self.version}"
