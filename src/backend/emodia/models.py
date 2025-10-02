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
