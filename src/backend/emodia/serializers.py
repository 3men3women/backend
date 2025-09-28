from rest_framework import serializers
from django.contrib.auth.models import User
from .models import EmotionRecord

class EmotionRecordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    emotion_emoji = serializers.CharField(read_only=True)
    emotion_name = serializers.CharField(read_only=True)
    emotion_display = serializers.CharField(source='get_emotion_display', read_only=True)
    sports_display = serializers.CharField(source='get_sports_display', read_only=True)

    class Meta:
        model = EmotionRecord
        fields = [
            'id',
            'user',
            'username', 
            'date',
            'emotion',
            'emotion_score',     # ✅ 추가
            'emotion_display',
            'emotion_emoji',
            'emotion_name',
            'memo',
            'sports',           
            'sports_display',   
            'created_at',
            'updated_at'
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
            'emotion_score',   # ✅ 추가
            'emotion_emoji',
            'emotion_name',
            'memo',
            'sports',
            'sports_display',
        ]
