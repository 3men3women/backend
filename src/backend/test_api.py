#!/usr/bin/env python
"""API 테스트 스크립트"""
import os
import sys
import django

# Django 설정
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testemo.settings')
django.setup()

from emodia.serializers import EmotionVideoSerializer
from emodia.models import EmotionVideo

print("=== EmotionVideo API 테스트 ===\n")

# 첫 번째 영상 조회
video = EmotionVideo.objects.first()
if video:
    print(f"첫 번째 영상:")
    print(f"  ID: {video.id}")
    print(f"  난이도: {video.difficulty}")
    print(f"  부위: {video.body_part}")
    print(f"  운동 종류: {video.exercise_type}")
    print(f"  시간: {video.duration_minutes}분")
    print(f"  파일명: {video.original_filename}")
    print(f"  영상 경로: {video.video}")

    # Serializer 테스트
    serializer = EmotionVideoSerializer(video)
    print(f"\nSerializer 결과:")
    import json
    print(json.dumps(serializer.data, indent=2, ensure_ascii=False))
else:
    print("영상이 없습니다.")
