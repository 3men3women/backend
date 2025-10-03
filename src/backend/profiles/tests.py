from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """유저가 생성될 때 자동으로 Profile도 생성"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """유저 저장될 때 Profile도 저장"""
    if hasattr(instance, "profile"):
        instance.profile.save()
