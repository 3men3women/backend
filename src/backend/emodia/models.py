from django.db import models
from django.contrib.auth.models import User

class EmotionRecord(models.Model):
    """
    사용자의 일별 감정 기록을 저장하는 모델
    """
    
    # 감정 종류 선택지
    EMOTION_CHOICES = [
        ('happy', '😊 행복'),
        ('sad', '😰 우울'),
        ('angry', '😡 화남'),
        ('lonely', '😔 외로움'),
        ('excited', '😊 신남'),
        ('anxious', '🤗 불안'),
        ('calm', '😌 평온'),
        ('grateful', '🙏 감사'),
    ]
    
    # 사용자 (외래키)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='emotion_records',
        verbose_name='사용자'
    )
    
    # 기록 날짜
    date = models.DateField(
        verbose_name='날짜',
        help_text='감정을 기록한 날짜'
    )
    
    # 감정 상태
    emotion = models.CharField(
        max_length=20,
        choices=EMOTION_CHOICES,
        verbose_name='감정 상태'
    )
    
    # 감정에 대한 메모 (선택사항)
    memo = models.TextField(
        blank=True,
        null=True,
        verbose_name='감정 메모',
        help_text='오늘 하루는 어땠나요? 간단한 힘들평을 남겨보세요...'
    )
    
    # 기록 생성 시간
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성 시간'
    )
    
    # 기록 수정 시간  
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정 시간'
    )
    
    class Meta:
        # 한 사용자가 하루에 하나의 감정만 기록할 수 있도록 제약
        unique_together = ['user', 'date']
        verbose_name = '감정 기록'
        verbose_name_plural = '감정 기록들'
        # 최신 날짜 순으로 정렬
        ordering = ['-date']
    
    def __str__(self):
        emotion_display = dict(self.EMOTION_CHOICES).get(self.emotion, self.emotion)
        return f"{self.user.username} - {self.date} ({emotion_display})"
    
    @property
    def emotion_emoji(self):
        """감정의 이모지만 반환"""
        emotion_display = dict(self.EMOTION_CHOICES).get(self.emotion, '')
        return emotion_display.split(' ')[0] if emotion_display else ''
    
    @property  
    def emotion_name(self):
        """감정의 한글 이름만 반환"""
        emotion_display = dict(self.EMOTION_CHOICES).get(self.emotion, '')
        return emotion_display.split(' ')[1] if len(emotion_display.split(' ')) > 1 else ''

# Create your models here.
