from rest_framework import serializers
from django.contrib.auth.models import User
from .models import EmotionRecord

class EmotionRecordSerializer(serializers.ModelSerializer):
    """
    감정 기록을 위한 Serializer
    """
    # 사용자 정보 (읽기 전용)
    username = serializers.CharField(source='user.username', read_only=True)
    
    # 감정 이모지와 이름 (읽기 전용)
    emotion_emoji = serializers.CharField(read_only=True)
    emotion_name = serializers.CharField(read_only=True)
    
    # 감정 선택지 표시 (읽기 전용)
    emotion_display = serializers.CharField(source='get_emotion_display', read_only=True)
    
    class Meta:
        model = EmotionRecord
        fields = [
            'id',
            'user',
            'username', 
            'date',
            'emotion',
            'emotion_display',
            'emotion_emoji',
            'emotion_name',
            'memo',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """
        감정 기록 생성 시 현재 로그인한 사용자를 자동으로 설정
        """
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    
    def validate_date(self, value):
        """
        날짜 유효성 검사
        """
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("미래 날짜는 기록할 수 없습니다.")
        return value
    
    def validate(self, data):
        """
        전체 데이터 유효성 검사 - 중복 날짜 체크
        """
        user = self.context['request'].user
        date = data.get('date')
        
        # 수정인 경우는 자기 자신 제외하고 중복 체크
        if self.instance:
            existing = EmotionRecord.objects.filter(
                user=user, 
                date=date
            ).exclude(id=self.instance.id)
        else:
            existing = EmotionRecord.objects.filter(
                user=user, 
                date=date
            )
        
        if existing.exists():
            raise serializers.ValidationError({
                'date': '이미 해당 날짜에 감정을 기록했습니다. 수정하려면 기존 기록을 편집해주세요.'
            })
        
        return data

class EmotionRecordListSerializer(serializers.ModelSerializer):
    """
    감정 기록 목록 조회를 위한 간단한 Serializer
    """
    emotion_emoji = serializers.CharField(read_only=True)
    emotion_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = EmotionRecord
        fields = [
            'id',
            'date', 
            'emotion',
            'emotion_emoji',
            'emotion_name',
            'memo'
        ]