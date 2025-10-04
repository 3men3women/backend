#!/usr/bin/env python
"""영상 데이터 확인 스크립트"""
import os
import sys
import django

# Django 설정
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testemo.settings')
django.setup()

from emodia.models import EmotionVideo

# 전체 영상 수
videos = EmotionVideo.objects.all()
print(f'\n총 {videos.count()}개의 영상\n')

# 난이도별
print('=== 난이도별 ===')
for difficulty in ['초급', '중급', '고급', '자세교정']:
    count = videos.filter(difficulty=difficulty).count()
    print(f'{difficulty}: {count}개')

# 부위별
print('\n=== 부위별 ===')
for body_part in ['전신', '목', '어깨', '목어깨', '등', '골반', '코어']:
    count = videos.filter(body_part=body_part).count()
    if count > 0:
        print(f'{body_part}: {count}개')

# 운동 종류별
print('\n=== 운동 종류별 ===')
exercise_types = videos.values_list('exercise_type', flat=True).distinct()
for ex_type in exercise_types:
    count = videos.filter(exercise_type=ex_type).count()
    print(f'{ex_type}: {count}개')

# 시간별
print('\n=== 시간별 ===')
durations = videos.values_list('duration_minutes', flat=True).distinct().order_by('duration_minutes')
for duration in durations:
    count = videos.filter(duration_minutes=duration).count()
    print(f'{duration}분: {count}개')

# 샘플 데이터 출력
print('\n=== 샘플 데이터 (처음 5개) ===')
for video in videos[:5]:
    print(f'{video}')
