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
        verbose_name="Main Goal"
    )
    routine_time = models.TimeField(null=True, blank=True, help_text="Routine alarm time", verbose_name="Routine Time")
    routine_days = models.JSONField(null=True, blank=True, help_text="Routine days list", verbose_name="Routine Days")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.user.username} Profile"
