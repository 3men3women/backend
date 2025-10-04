from django.contrib import admin
from django.utils.html import format_html
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "main_goal_display", "routine_time", "routine_days_display", "created_at", "updated_at")
    list_filter = ("main_goal", "created_at", "routine_time")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ('사용자 정보', {
            'fields': ('user',)
        }),
        ('목표 및 루틴', {
            'fields': ('main_goal', 'routine_time', 'routine_days')
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def main_goal_display(self, obj):
        goal_dict = dict(Profile._meta.get_field('main_goal').choices)
        goal_text = goal_dict.get(obj.main_goal, obj.main_goal)
        return goal_text if obj.main_goal else '-'
    main_goal_display.short_description = '주요 목표'

    def routine_days_display(self, obj):
        if obj.routine_days:
            days_map = {
                'mon': '월', 'tue': '화', 'wed': '수',
                'thu': '목', 'fri': '금', 'sat': '토', 'sun': '일'
            }
            if isinstance(obj.routine_days, list):
                days = [days_map.get(d, d) for d in obj.routine_days]
                return ', '.join(days)
            return str(obj.routine_days)
        return '-'
    routine_days_display.short_description = '루틴 요일'
