from django.db import models 
from django.contrib.auth.models import User

class EmotionRecord(models.Model):
    """
    사용자의 일별 감정 기록을 저장하는 모델
    """
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

    # 점수 매핑
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

    SPORTS_CHOICES = [
        (1, "목풀기"),
        (2, "헬스"),
        (3, "축구"),
        (4, "농구"),
        (5, "수영"),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='emotion_records',
        verbose_name='사용자'
    )
    date = models.DateField(verbose_name='날짜', help_text='감정을 기록한 날짜')
    emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES, verbose_name='감정 상태')
    emotion_score = models.IntegerField(default=0, verbose_name="감정 점수")  # ✅ 추가
    memo = models.TextField(blank=True, null=True, verbose_name='감정 메모', help_text='오늘 하루는 어땠나요? 간단한 힘들평을 남겨보세요...')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시간')

    sports = models.IntegerField(
        choices=SPORTS_CHOICES,
        blank=True,
        null=True,
        verbose_name="교정 기록",
        help_text="오늘 한 운동교정"
    )

    class Meta:
        unique_together = ['user', 'date']
        verbose_name = '감정 기록'
        verbose_name_plural = '감정 기록들'
        ordering = ['-date']

    def __str__(self):
        emotion_display = dict(self.EMOTION_CHOICES).get(self.emotion, self.emotion)
        return f"{self.user.username} - {self.date} ({emotion_display})"

    @property
    def emotion_emoji(self):
        emotion_display = dict(self.EMOTION_CHOICES).get(self.emotion, '')
        return emotion_display.split(' ')[0] if emotion_display else ''

    @property  
    def emotion_name(self):
        emotion_display = dict(self.EMOTION_CHOICES).get(self.emotion, '')
        return emotion_display.split(' ')[1] if len(emotion_display.split(' ')) > 1 else ''

    def save(self, *args, **kwargs):
        # ✅ 감정에 따른 점수를 자동으로 저장
        self.emotion_score = self.EMOTION_SCORES.get(self.emotion, 0)
        super().save(*args, **kwargs)
