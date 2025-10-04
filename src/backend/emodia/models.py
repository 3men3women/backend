from django.db import models
from django.contrib.auth.models import User


class Sports(models.Model):
    """스포츠 종류"""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class EmotionVideo(models.Model):
    """스포츠별로 연결된 영상"""
    DIFFICULTY_CHOICES = [
        ('초급', '초급'),
        ('중급', '중급'),
        ('고급', '고급'),
        ('자세교정', '자세교정'),
    ]

    BODY_PART_CHOICES = [
        ('전신', '전신'),
        ('목', '목'),
        ('어깨', '어깨'),
        ('목어깨', '목어깨'),
        ('등', '등'),
        ('골반', '골반'),
        ('코어', '코어'),
    ]

    EXERCISE_TYPE_CHOICES = [
        ('스트레칭', '스트레칭'),
        ('요가', '요가'),
        ('필라테스', '필라테스'),
        ('운동', '운동'),
        ('이완스트레칭', '이완스트레칭'),
        ('통증완화스트레칭', '통증완화스트레칭'),
        ('모닝스트레칭', '모닝스트레칭'),
        ('오른쪽스트레칭', '오른쪽스트레칭'),
        ('왼쪽스트레칭', '왼쪽스트레칭'),
    ]

    sports = models.ForeignKey(Sports, related_name="videos", on_delete=models.CASCADE, null=True, blank=True)
    video = models.FileField(upload_to="videos/")  # media/videos/ 폴더 안에 저장

    # 영상 분류 정보
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name='Difficulty', blank=True, null=True)
    body_part = models.CharField(max_length=20, choices=BODY_PART_CHOICES, verbose_name='Body Part', blank=True, null=True)
    exercise_type = models.CharField(max_length=50, choices=EXERCISE_TYPE_CHOICES, verbose_name='Exercise Type', blank=True, null=True)
    duration_minutes = models.IntegerField(verbose_name='Duration (minutes)', blank=True, null=True)

    # 원본 파일명 (참고용)
    original_filename = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Exercise Video'
        verbose_name_plural = 'Exercise Videos'
        ordering = ['difficulty', 'body_part', 'duration_minutes']

    def __str__(self):
        return f"{self.difficulty}_{self.body_part}_{self.exercise_type}_{self.duration_minutes}분"


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
        verbose_name='User'
    )
    date = models.DateField(verbose_name='Date')
    emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES, verbose_name='Emotion')
    emotion_score = models.IntegerField(default=0, verbose_name="Emotion Score")
    memo = models.TextField(blank=True, null=True, verbose_name='Memo')

    # ✅ 24.07.29 추가 필드 (StartPage 6단계)
    intensity = models.IntegerField(default=50, null=True, blank=True, verbose_name='Intensity')
    tags = models.JSONField(default=list, null=True, blank=True, verbose_name='Tags')
    mood_after = models.CharField(max_length=50, null=True, blank=True, verbose_name='Mood After')
    voice_of_mind = models.TextField(null=True, blank=True, verbose_name='Voice of Mind')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    # ✅ FK로 변경 (드롭다운 지원)
    sports = models.ForeignKey(
        Sports,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="records",
        verbose_name="Sports (Auto-mapped)"
    )

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name = 'Emotion Record'
        verbose_name_plural = 'Emotion Records'

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
    duration = models.IntegerField(default=0, help_text="Workout duration (seconds)")

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.user.username} - {self.sports.name} ({self.start_time})"


class PoseFrame(models.Model):
    """실시간 포즈 좌표 기록"""
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='pose_frames')
    timestamp = models.FloatField(help_text="Elapsed time since session start (seconds)")
    keypoints = models.JSONField(help_text="Pose keypoints coordinate data")
    feedback = models.JSONField(null=True, blank=True, help_text="Correction feedback data")

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
    exercise_phase = models.CharField(max_length=20, choices=PHASE_CHOICES, help_text="Exercise phase")
    quality_level = models.CharField(max_length=20, choices=QUALITY_CHOICES, help_text="Pose quality")
    keypoints = models.JSONField(help_text="Correct pose coordinates")

    # 메타데이터
    description = models.TextField(help_text="Pose description (e.g., neck tilted 30 degrees to the left)")
    created_by = models.CharField(max_length=100, help_text="Expert name")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, help_text="Whether to use for ML training")

    # ML 특징 (자동 계산, 캐싱용)
    features = models.JSONField(null=True, blank=True, help_text="Extracted feature vector")

    class Meta:
        ordering = ['sports', 'exercise_phase', 'quality_level']
        verbose_name = 'Expert Pose Template'
        verbose_name_plural = 'Expert Pose Templates'

    def __str__(self):
        return f"{self.sports.name} - {self.get_exercise_phase_display()} ({self.get_quality_level_display()})"


class FeedbackRating(models.Model):
    """사용자 피드백 평가 (ML 학습용)"""
    pose_frame = models.ForeignKey(PoseFrame, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # 피드백 유용성
    is_helpful = models.BooleanField(help_text="Was this feedback helpful?")
    accuracy_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="Feedback accuracy (1-5)"
    )

    # 사용자 코멘트
    comment = models.TextField(blank=True, help_text="Additional comment")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Feedback Rating'
        verbose_name_plural = 'Feedback Ratings'

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
    version = models.CharField(max_length=50, help_text="Model version (e.g., v1.0)")

    # 모델 파일
    model_file = models.FileField(upload_to='ml_models/', help_text="Saved model file (.pkl)")

    # 성능 지표
    accuracy = models.FloatField(null=True, blank=True, help_text="Accuracy")
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)

    # 학습 정보
    training_samples = models.IntegerField(help_text="Number of training samples")
    trained_at = models.DateTimeField(auto_now_add=True)
    trained_by = models.CharField(max_length=100)

    # 배포 상태
    is_active = models.BooleanField(default=False, help_text="Currently active model")
    notes = models.TextField(blank=True, help_text="Model description and changes")

    class Meta:
        ordering = ['-trained_at']
        verbose_name = 'ML Model'
        verbose_name_plural = 'ML Models'

    def __str__(self):
        return f"{self.sports.name} - {self.model_type} {self.version}"
