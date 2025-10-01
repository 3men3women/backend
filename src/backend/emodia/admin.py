from django.contrib import admin
from .models import Sports, EmotionVideo, EmotionRecord


@admin.register(Sports)
class SportsAdmin(admin.ModelAdmin):
    list_display = ("id", "name")  # 리스트 화면에 표시할 컬럼


@admin.register(EmotionVideo)
class EmotionVideoAdmin(admin.ModelAdmin):
    list_display = ("id", "sports", "video", "created_at")  # 영상 목록에 스포츠/경로 표시
    list_filter = ("sports",)  # 필터링 기능
    search_fields = ("sports__name",)  # 검색 기능


@admin.register(EmotionRecord)
class EmotionRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date", "emotion", "emotion_score", "sports", "created_at")
    list_filter = ("emotion", "sports")  # 필터링 기능
    search_fields = ("user__username", "memo")  # 검색 기능
