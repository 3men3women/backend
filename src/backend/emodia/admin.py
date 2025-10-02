from django.contrib import admin
from .models import Sports, EmotionVideo, EmotionRecord


@admin.register(Sports)
class SportsAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(EmotionVideo)
class EmotionVideoAdmin(admin.ModelAdmin):
    list_display = ("id", "sports", "video", "created_at")
    list_filter = ("sports",)
    search_fields = ("sports__name",)


@admin.register(EmotionRecord)
class EmotionRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date", "emotion", "emotion_score", "sports", "created_at")
    list_filter = ("emotion", "sports")
    search_fields = ("user__username", "memo")
