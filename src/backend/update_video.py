#!/usr/bin/env python
"""영상 데이터 업데이트 스크립트"""
import os
import sys
import django

# Django 설정
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testemo.settings')
django.setup()

from emodia.models import EmotionVideo

# 기존 파일명으로 조회
old_filename = "초급_목어깨_통증완화스트레칭_10분.mp4"
new_filename = "초급_목어깨_스트레칭_10분.mp4"
new_exercise_type = "스트레칭"

try:
    # 파일명으로 영상 찾기
    video = EmotionVideo.objects.get(original_filename=old_filename)

    print(f"기존 데이터:")
    print(f"  ID: {video.id}")
    print(f"  파일명: {video.original_filename}")
    print(f"  운동 종류: {video.exercise_type}")
    print(f"  영상 경로: {video.video}")

    # 업데이트
    video.original_filename = new_filename
    video.exercise_type = new_exercise_type
    video.video = f"videos/{new_filename}"
    video.save()

    print(f"\n업데이트 완료:")
    print(f"  새 파일명: {video.original_filename}")
    print(f"  새 운동 종류: {video.exercise_type}")
    print(f"  새 영상 경로: {video.video}")

except EmotionVideo.DoesNotExist:
    print(f"영상을 찾을 수 없습니다: {old_filename}")
except Exception as e:
    print(f"오류 발생: {e}")
