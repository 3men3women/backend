from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from datetime import date, datetime
from django.db.models import Q

from .models import EmotionRecord
from .serializers import EmotionRecordSerializer, EmotionRecordListSerializer

class EmotionRecordListCreateView(generics.ListCreateAPIView):
    """
    감정 기록 목록 조회 및 생성 API
    GET: 로그인한 사용자의 감정 기록 목록 조회 (관리자는 전체 조회 가능)
    POST: 새로운 감정 기록 생성
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EmotionRecordListSerializer
        return EmotionRecordSerializer

    def get_queryset(self):
        # 관리자는 전체 조회 가능, 일반 사용자는 자기 기록만
        qs = EmotionRecord.objects.all() if (
            self.request.user.is_staff or self.request.user.is_superuser
        ) else EmotionRecord.objects.filter(user=self.request.user)

        # 관리자가 특정 user_id를 지정해서 필터링
        user_id = self.request.query_params.get("user_id")
        if user_id and (self.request.user.is_staff or self.request.user.is_superuser):
            qs = qs.filter(user_id=user_id)

        # 년월 필터링 (선택사항)
        year = self.request.query_params.get("year")
        month = self.request.query_params.get("month")
        if year and month:
            qs = qs.filter(date__year=year, date__month=month)
        elif year:
            qs = qs.filter(date__year=year)

        return qs

class EmotionRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    특정 감정 기록 조회, 수정, 삭제 API
    GET: 특정 감정 기록 조회
    PUT/PATCH: 감정 기록 수정
    DELETE: 감정 기록 삭제
    """
    serializer_class = EmotionRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """현재 로그인한 사용자의 감정 기록만 접근 가능"""
        return EmotionRecord.objects.filter(user=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_emotion_by_date(request, date_str):
    """
    특정 날짜의 감정 기록 조회 API
    URL: /emotions/date/2025-09-21/
    """
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': '날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용해주세요.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        emotion_record = EmotionRecord.objects.get(
            user=request.user, 
            date=target_date
        )
        serializer = EmotionRecordSerializer(emotion_record)
        return Response(serializer.data)
    except EmotionRecord.DoesNotExist:
        return Response(
            {'message': '해당 날짜에 기록된 감정이 없습니다.'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    ##ff
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_emotion(request):
    """
    감정 기록 생성 또는 수정 API
    같은 날짜에 기록이 있으면 수정, 없으면 생성
    POST: /emotions/save/
    """
    target_date = request.data.get('date')
    
    if not target_date:
        return Response(
            {'error': '날짜를 입력해주세요.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # 기존 기록이 있는지 확인
        emotion_record = EmotionRecord.objects.get(
            user=request.user, 
            date=target_date
        )
        # 수정
        serializer = EmotionRecordSerializer(
            emotion_record, 
            data=request.data, 
            context={'request': request}
        )
    except EmotionRecord.DoesNotExist:
        # 새로 생성
        serializer = EmotionRecordSerializer(
            data=request.data, 
            context={'request': request}
        )
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_emotion_calendar(request, year, month):
    """
    월별 감정 캘린더 데이터 조회 API
    URL: /emotions/calendar/2025/9/
    """
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        return Response(
            {'error': '년도와 월은 숫자여야 합니다.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    emotions = EmotionRecord.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    )
    
    # 날짜별로 정리
    calendar_data = {}
    for emotion in emotions:
        day = emotion.date.day
        calendar_data[day] = {
            'id': emotion.id,
            'emotion': emotion.emotion,
            'emotion_emoji': emotion.emotion_emoji,
            'emotion_name': emotion.emotion_name,
            'memo': emotion.memo
        }
    
    return Response({
        'year': year,
        'month': month,
        'emotions': calendar_data
    })

# Create your views here.
