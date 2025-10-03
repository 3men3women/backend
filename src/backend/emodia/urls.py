from django.urls import path
from . import views

app_name = 'emodia'

urlpatterns = [
    # 감정 기록 목록 조회 및 생성
    path('emotions/', views.EmotionRecordListCreateView.as_view(), name='emotion-list-create'),

    # 특정 감정 기록 조회, 수정, 삭제 (ID 기반)
    path('emotions/<int:pk>/', views.EmotionRecordDetailView.as_view(), name='emotion-detail'),

    # 특정 날짜의 감정 기록 조회
    path('emotions/date/<str:date_str>/', views.get_emotion_by_date, name='emotion-by-date'),

    # 감정 기록 생성 또는 수정 (스마트 저장)
    path('emotions/save/', views.create_or_update_emotion, name='emotion-save'),

    # 월별 감정 캘린더 데이터 조회
    path('emotions/calendar/<int:year>/<int:month>/', views.get_emotion_calendar, name='emotion-calendar'),

    # 운동 세션
    path('workout/start/', views.start_workout_session, name='workout-start'),
    path('workout/<int:session_id>/end/', views.end_workout_session, name='workout-end'),
    path('workout/sessions/', views.get_workout_sessions, name='workout-sessions'),

    # 포즈 좌표 전송
    path('pose/submit/', views.submit_pose_frame, name='pose-submit'),
]