from rest_framework import serializers
from django.contrib.auth.models import User
from .models import EmotionRecord, EmotionVideo, WorkoutSession, PoseFrame, Sports


class EmotionVideoSerializer(serializers.ModelSerializer):
    # video를 절대 URL로 반환
    video = serializers.SerializerMethodField()

    class Meta:
        model = EmotionVideo
        fields = ["id", "video", "created_at"]

    def get_video(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.video.url)  # 절대 경로 반환
        return obj.video.url


class EmotionRecordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    emotion_emoji = serializers.CharField(read_only=True)
    emotion_name = serializers.CharField(read_only=True)
    emotion_display = serializers.CharField(source='get_emotion_display', read_only=True)
    sports_display = serializers.CharField(source='get_sports_display', read_only=True)

    # ✅ 추가: 관련 영상
    videos = serializers.SerializerMethodField()

    class Meta:
        model = EmotionRecord
        fields = [
            'id',
            'user',
            'username',
            'date',
            'emotion',
            'emotion_score',
            'emotion_display',
            'emotion_emoji',
            'emotion_name',
            'memo',
            'sports',
            'sports_display',
            'created_at',
            'updated_at',
            'videos',   # 👈 새 필드
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'emotion_score']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def validate_date(self, value):
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("미래 날짜는 기록할 수 없습니다.")
        return value

    def validate(self, data):
        user = self.context['request'].user
        date = data.get('date')
        if self.instance:
            existing = EmotionRecord.objects.filter(user=user, date=date).exclude(id=self.instance.id)
        else:
            existing = EmotionRecord.objects.filter(user=user, date=date)
        if existing.exists():
            raise serializers.ValidationError({
                'date': '이미 해당 날짜에 감정을 기록했습니다. 수정하려면 기존 기록을 편집해주세요.'
            })
        return data

    def get_videos(self, obj):
        """sports_id 기준으로 EmotionVideo 조회"""
        videos = obj.related_videos
        return EmotionVideoSerializer(videos, many=True, context=self.context).data


class EmotionRecordListSerializer(serializers.ModelSerializer):
    emotion_emoji = serializers.CharField(read_only=True)
    emotion_name = serializers.CharField(read_only=True)
    sports_display = serializers.CharField(source='get_sports_display', read_only=True)

    class Meta:
        model = EmotionRecord
        fields = [
            'id',
            'date',
            'emotion',
            'emotion_score',
            'emotion_emoji',
            'emotion_name',
            'memo',
            'sports',
            'sports_display',
        ]


class WorkoutSessionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    sports_name = serializers.CharField(source='sports.name', read_only=True)

    class Meta:
        model = WorkoutSession
        fields = ['id', 'user', 'username', 'sports', 'sports_name', 'start_time', 'end_time', 'duration']
        read_only_fields = ['id', 'user', 'start_time']

    def validate_sports(self, value):
        """sports가 유효한 Sports 객체인지 확인"""
        if not value:
            raise serializers.ValidationError("스포츠를 선택해주세요.")
        if not Sports.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("존재하지 않는 스포츠입니다.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class PoseFrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoseFrame
        fields = ['id', 'session', 'timestamp', 'keypoints', 'feedback']
        read_only_fields = ['id', 'feedback']


class SportsSerializer(serializers.ModelSerializer):
    videos = EmotionVideoSerializer(many=True, read_only=True)

    class Meta:
        model = Sports
        fields = ['id', 'name', 'videos']
