"""
영상 파일을 기반으로 EmotionVideo 데이터를 생성하는 Django 관리 명령어
"""
import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from emodia.models import EmotionVideo


class Command(BaseCommand):
    help = '영상 파일을 기반으로 EmotionVideo 데이터 생성'

    def handle(self, *args, **options):
        # media/videos 디렉토리 경로
        videos_dir = os.path.join(settings.BASE_DIR, 'media', 'videos')

        if not os.path.exists(videos_dir):
            self.stdout.write(self.style.ERROR(f'디렉토리를 찾을 수 없습니다: {videos_dir}'))
            return

        # 기존 데이터 삭제 여부 확인
        if EmotionVideo.objects.exists():
            self.stdout.write(self.style.WARNING(f'기존 영상 데이터 {EmotionVideo.objects.count()}개가 있습니다.'))
            response = input('기존 데이터를 모두 삭제하고 새로 생성하시겠습니까? (yes/no): ')
            if response.lower() == 'yes':
                deleted_count = EmotionVideo.objects.all().delete()[0]
                self.stdout.write(self.style.SUCCESS(f'{deleted_count}개의 기존 데이터를 삭제했습니다.'))

        # 영상 파일 목록 가져오기
        video_files = [f for f in os.listdir(videos_dir) if f.endswith('.mp4')]

        if not video_files:
            self.stdout.write(self.style.ERROR('영상 파일을 찾을 수 없습니다.'))
            return

        created_count = 0
        error_count = 0

        for filename in video_files:
            try:
                # 파일명 파싱: 난이도_부위_운동종류_시간.mp4
                name_without_ext = filename.replace('.mp4', '')
                parts = name_without_ext.split('_')

                if len(parts) < 4:
                    self.stdout.write(self.style.WARNING(f'파일명 형식이 올바르지 않습니다: {filename}'))
                    error_count += 1
                    continue

                difficulty = parts[0]
                body_part = parts[1]
                exercise_type = parts[2]
                duration_str = parts[3]

                # 시간 파싱 (예: "10분" -> 10)
                duration_match = re.search(r'(\d+)분', duration_str)
                if duration_match:
                    duration_minutes = int(duration_match.group(1))
                else:
                    self.stdout.write(self.style.WARNING(f'시간 정보를 파싱할 수 없습니다: {filename}'))
                    error_count += 1
                    continue

                # EmotionVideo 객체 생성
                video_path = os.path.join('videos', filename)

                emotion_video = EmotionVideo.objects.create(
                    video=video_path,
                    difficulty=difficulty,
                    body_part=body_part,
                    exercise_type=exercise_type,
                    duration_minutes=duration_minutes,
                    original_filename=filename
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'생성됨: {difficulty} | {body_part} | {exercise_type} | {duration_minutes}분'
                    )
                )
                created_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'{filename} 처리 중 오류: {str(e)}'))
                error_count += 1

        # 결과 요약
        self.stdout.write(self.style.SUCCESS(f'\n총 {created_count}개의 영상이 생성되었습니다.'))
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'{error_count}개의 파일 처리 중 오류가 발생했습니다.'))
