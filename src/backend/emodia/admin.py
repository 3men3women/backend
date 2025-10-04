from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Sports, EmotionVideo, EmotionRecord,
    WorkoutSession, PoseFrame,
    ExpertPoseTemplate, FeedbackRating, MLModel
)


@admin.register(Sports)
class SportsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "video_count", "record_count")
    search_fields = ("name",)

    def video_count(self, obj):
        return obj.videos.count()
    video_count.short_description = '영상 수'

    def record_count(self, obj):
        return obj.records.count()
    record_count.short_description = '기록 수'


@admin.register(EmotionVideo)
class EmotionVideoAdmin(admin.ModelAdmin):
    list_display = ("id", "difficulty", "body_part", "exercise_type", "duration_minutes", "video_preview", "sports", "created_at")
    list_filter = ("difficulty", "body_part", "exercise_type", "duration_minutes", "sports")
    search_fields = ("original_filename", "exercise_type", "body_part")
    readonly_fields = ("created_at", "video_preview_large")

    fieldsets = (
        ('영상 정보', {
            'fields': ('video', 'video_preview_large', 'original_filename')
        }),
        ('분류', {
            'fields': ('difficulty', 'body_part', 'exercise_type', 'duration_minutes', 'sports')
        }),
        ('타임스탬프', {
            'fields': ('created_at',)
        }),
    )

    def video_preview(self, obj):
        if obj.video:
            return format_html('<a href="{}" target="_blank">🎥 영상 보기</a>', obj.video.url)
        return '-'
    video_preview.short_description = '영상'

    def video_preview_large(self, obj):
        if obj.video:
            return format_html(
                '<video width="640" height="360" controls><source src="{}" type="video/mp4">Your browser does not support the video tag.</video>',
                obj.video.url
            )
        return '-'
    video_preview_large.short_description = '영상 미리보기'


@admin.register(EmotionRecord)
class EmotionRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date", "emotion_display", "emotion_score", "intensity", "sports", "mood_after", "created_at")
    list_filter = ("emotion", "sports", "date", "intensity")
    search_fields = ("user__username", "memo", "voice_of_mind")
    readonly_fields = ("emotion_score", "created_at", "updated_at")

    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'date', 'emotion', 'emotion_score')
        }),
        ('감정 상세', {
            'fields': ('intensity', 'tags', 'voice_of_mind')
        }),
        ('운동 관련', {
            'fields': ('sports', 'mood_after')
        }),
        ('메모', {
            'fields': ('memo',)
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def emotion_display(self, obj):
        return f"{obj.emotion_emoji} {obj.emotion_name}"
    emotion_display.short_description = '감정'


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "sports", "start_time", "end_time", "duration_display", "pose_frame_count")
    list_filter = ("sports", "start_time")
    search_fields = ("user__username",)
    readonly_fields = ("start_time",)

    def duration_display(self, obj):
        if obj.duration:
            minutes = obj.duration // 60
            seconds = obj.duration % 60
            return f"{minutes}분 {seconds}초"
        return "-"
    duration_display.short_description = '운동 시간'

    def pose_frame_count(self, obj):
        return obj.pose_frames.count()
    pose_frame_count.short_description = '포즈 프레임 수'


@admin.register(PoseFrame)
class PoseFrameAdmin(admin.ModelAdmin):
    list_display = ("id", "session_info", "timestamp_display", "has_feedback", "has_ratings")
    search_fields = ("session__id", "session__user__username")
    list_filter = ("session__sports", "session__start_time")

    def session_info(self, obj):
        return f"Session #{obj.session.id} - {obj.session.user.username}"
    session_info.short_description = '세션'

    def timestamp_display(self, obj):
        return f"{obj.timestamp:.1f}초"
    timestamp_display.short_description = '타임스탬프'

    def has_feedback(self, obj):
        if obj.feedback:
            return format_html('<span style="color: blue;">✓</span>')
        return '-'
    has_feedback.short_description = '피드백'

    def has_ratings(self, obj):
        count = obj.ratings.count()
        if count > 0:
            return format_html('<span style="color: green;">✓ {}개</span>', count)
        return '-'
    has_ratings.short_description = '사용자 평가'


# ========== ML 인프라 Admin ==========

@admin.register(ExpertPoseTemplate)
class ExpertPoseTemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "sports", "exercise_phase", "quality_level", "created_by", "is_active", "created_at")
    list_filter = ("sports", "quality_level", "exercise_phase", "is_active")
    search_fields = ("description", "created_by")
    readonly_fields = ("created_at",)

    fieldsets = (
        ('기본 정보', {
            'fields': ('sports', 'exercise_phase', 'quality_level', 'is_active')
        }),
        ('포즈 데이터', {
            'fields': ('keypoints', 'features'),
            'description': 'keypoints: 전문가 포즈 좌표 (JSON), features: 자동 계산된 특징 (선택사항)'
        }),
        ('메타데이터', {
            'fields': ('description', 'created_by', 'created_at')
        }),
    )

    actions = ['extract_features_action']

    def extract_features_action(self, request, queryset):
        """선택한 템플릿의 특징 자동 추출"""
        from .ml_utils import extract_features

        count = 0
        for template in queryset:
            if template.keypoints:
                template.features = extract_features(template.keypoints)
                template.save()
                count += 1

        self.message_user(request, f'{count}개 템플릿의 특징을 추출했습니다.')

    extract_features_action.short_description = '선택한 템플릿의 특징 추출'


@admin.register(FeedbackRating)
class FeedbackRatingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "pose_frame_session", "is_helpful", "accuracy_rating", "created_at")
    list_filter = ("is_helpful", "accuracy_rating", "created_at")
    search_fields = ("user__username", "comment")
    readonly_fields = ("created_at",)

    def pose_frame_session(self, obj):
        return f"Session {obj.pose_frame.session.id}"
    pose_frame_session.short_description = '세션'


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = (
        "id", "sports", "model_type", "version",
        "accuracy_display", "training_samples",
        "is_active_display", "trained_at"
    )
    list_filter = ("sports", "model_type", "is_active", "trained_at")
    search_fields = ("version", "trained_by", "notes")
    readonly_fields = ("trained_at",)

    fieldsets = (
        ('기본 정보', {
            'fields': ('sports', 'model_type', 'version', 'is_active')
        }),
        ('모델 파일', {
            'fields': ('model_file',)
        }),
        ('성능 지표', {
            'fields': ('accuracy', 'precision', 'recall', 'f1_score')
        }),
        ('학습 정보', {
            'fields': ('training_samples', 'trained_by', 'trained_at', 'notes')
        }),
    )

    actions = ['activate_model_action']

    def accuracy_display(self, obj):
        if obj.accuracy:
            color = 'green' if obj.accuracy >= 0.8 else 'orange' if obj.accuracy >= 0.6 else 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1%}</span>',
                color, obj.accuracy
            )
        return '-'
    accuracy_display.short_description = '정확도'

    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">✓ 활성</span>')
        return format_html('<span style="color: gray;">비활성</span>')
    is_active_display.short_description = '상태'

    def activate_model_action(self, request, queryset):
        """선택한 모델 활성화 (각 스포츠별로 1개만)"""
        if queryset.count() != 1:
            self.message_user(request, '1개의 모델만 선택해주세요.', level='error')
            return

        model = queryset.first()

        # 같은 스포츠의 다른 모델 비활성화
        MLModel.objects.filter(sports=model.sports, is_active=True).update(is_active=False)

        # 선택한 모델 활성화
        model.is_active = True
        model.save()

        self.message_user(request, f'{model}을(를) 활성화했습니다.')

    activate_model_action.short_description = '선택한 모델 활성화'
