from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    
    main_goal = models.CharField(
        max_length=50,
        choices=[
            ("relax", "목, 어깨 뭉침 완화"),
            ("sleep", "수면의 질 개선"),
            ("stress", "스트레스 관리"),
            ("habit", "꾸준한 기록 습관 만들기"),
            ("energy", "에너지 회복"),
        ],
        null=True,
        blank=True,
    )
    routine_time = models.TimeField(null=True, blank=True, help_text="루틴 알람 시간")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"
