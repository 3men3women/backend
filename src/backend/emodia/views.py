from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from datetime import date, datetime
from django.db.models import Q
from django.utils import timezone

from .models import EmotionRecord, WorkoutSession, PoseFrame, Sports, EmotionVideo
from .serializers import (
    EmotionRecordSerializer,
    EmotionRecordListSerializer,
    WorkoutSessionSerializer,
    PoseFrameSerializer,
    SportsSerializer,
    EmotionVideoSerializer
)

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


# ========== 운동 세션 & 포즈 좌표 API ==========

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_workout_session(request):
    """운동 세션 시작"""
    serializer = WorkoutSessionSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def end_workout_session(request, session_id):
    """운동 세션 종료"""
    try:
        session = WorkoutSession.objects.get(id=session_id, user=request.user)
    except WorkoutSession.DoesNotExist:
        return Response({'error': '세션을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

    session.end_time = timezone.now()
    duration_seconds = (session.end_time - session.start_time).total_seconds()
    session.duration = int(duration_seconds)
    session.save()

    serializer = WorkoutSessionSerializer(session)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_pose_frame(request):
    """실시간 포즈 좌표 전송 + 피드백 반환"""
    serializer = PoseFrameSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 저장
    pose_frame = serializer.save()

    # 운동 타입에 따른 피드백 생성
    exercise_type = request.data.get('exercise_type', 'neck_left')
    feedback = generate_feedback(pose_frame.keypoints, exercise_type)
    pose_frame.feedback = feedback
    pose_frame.save()

    return Response({
        'id': pose_frame.id,
        'feedback': feedback
    }, status=status.HTTP_201_CREATED)


def generate_feedback(keypoints, exercise_type='neck_left'):
    """
    운동 타입별 자세 피드백
    exercise_type: 'neck_left', 'neck_right', 'shoulder_left', 'shoulder_right'
    """
    if exercise_type == 'neck_left':
        return feedback_neck_left(keypoints)
    elif exercise_type == 'neck_right':
        return feedback_neck_right(keypoints)
    elif exercise_type == 'shoulder_left':
        return feedback_shoulder_left(keypoints)
    elif exercise_type == 'shoulder_right':
        return feedback_shoulder_right(keypoints)
    else:
        return feedback_neck_left(keypoints)  # 기본값


def feedback_neck_left(keypoints):
    """목 왼쪽 스트레칭 피드백"""
    feedback = {
        'status': 'good',
        'messages': [],
        'corrections': {},
        'angles': {},
        'has_warnings': False
    }

    try:
        nose = next((k for k in keypoints if k['name'] == 'nose'), None)
        left_ear = next((k for k in keypoints if k['name'] == 'left_ear'), None)
        right_ear = next((k for k in keypoints if k['name'] == 'right_ear'), None)
        left_shoulder = next((k for k in keypoints if k['name'] == 'left_shoulder'), None)
        right_shoulder = next((k for k in keypoints if k['name'] == 'right_shoulder'), None)

        if not all([nose, left_shoulder, right_shoulder]):
            feedback['status'] = 'warning'
            feedback['messages'].append('얼굴과 어깨가 잘 보이지 않습니다')
            return feedback

        # 어깨 수평 체크
        shoulder_y_diff = abs(left_shoulder['y'] - right_shoulder['y'])
        if shoulder_y_diff > 0.15:
            feedback['has_warnings'] = True
            feedback['messages'].append('⚠️ 어깨를 수평으로 유지하세요')

        # 머리 왼쪽 기울기 체크
        shoulder_center_x = (left_shoulder['x'] + right_shoulder['x']) / 2
        nose_offset = nose['x'] - shoulder_center_x
        feedback['angles']['nose_offset'] = round(nose_offset, 3)

        if nose_offset < -0.04:  # 왼쪽으로 기울임
            tilt_amount = abs(nose_offset)
            if tilt_amount > 0.09:
                feedback['messages'].append('✓ 좋습니다! 목 스트레칭이 잘 되고 있습니다')
            elif tilt_amount > 0.06:
                feedback['messages'].append('✓ 조금 더 천천히 당겨보세요')
            else:
                feedback['has_warnings'] = True
                feedback['messages'].append('→ 머리를 왼쪽으로 더 기울이세요')
        elif nose_offset > 0.04:
            feedback['has_warnings'] = True
            feedback['messages'].append('⚠️ 반대 방향입니다. 왼쪽으로 기울이세요')
        else:
            feedback['has_warnings'] = True
            feedback['messages'].append('→ 머리를 왼쪽 어깨 방향으로 천천히 기울이세요')

        # 과도한 기울기 방지
        if left_ear and right_ear:
            ear_y_diff = left_ear['y'] - right_ear['y']
            if ear_y_diff > 0.25:
                feedback['has_warnings'] = True
                feedback['messages'].append('⚠️ 너무 많이 기울였습니다. 천천히 돌아오세요')

        if feedback['has_warnings']:
            feedback['status'] = 'warning'

    except Exception as e:
        feedback['status'] = 'warning'
        feedback['messages'].append(f'인식 오류: {str(e)}')

    return feedback


def feedback_neck_right(keypoints):
    """목 오른쪽 스트레칭 피드백"""
    feedback = {
        'status': 'good',
        'messages': [],
        'corrections': {},
        'angles': {},
        'has_warnings': False
    }

    try:
        nose = next((k for k in keypoints if k['name'] == 'nose'), None)
        left_ear = next((k for k in keypoints if k['name'] == 'left_ear'), None)
        right_ear = next((k for k in keypoints if k['name'] == 'right_ear'), None)
        left_shoulder = next((k for k in keypoints if k['name'] == 'left_shoulder'), None)
        right_shoulder = next((k for k in keypoints if k['name'] == 'right_shoulder'), None)

        if not all([nose, left_shoulder, right_shoulder]):
            feedback['status'] = 'warning'
            feedback['messages'].append('얼굴과 어깨가 잘 보이지 않습니다')
            return feedback

        # 어깨 수평 체크
        shoulder_y_diff = abs(left_shoulder['y'] - right_shoulder['y'])
        if shoulder_y_diff > 0.15:
            feedback['has_warnings'] = True
            feedback['messages'].append('⚠️ 어깨를 수평으로 유지하세요')

        # 머리 오른쪽 기울기 체크
        shoulder_center_x = (left_shoulder['x'] + right_shoulder['x']) / 2
        nose_offset = nose['x'] - shoulder_center_x
        feedback['angles']['nose_offset'] = round(nose_offset, 3)

        if nose_offset > 0.04:  # 오른쪽으로 기울임
            tilt_amount = abs(nose_offset)
            if tilt_amount > 0.09:
                feedback['messages'].append('✓ 좋습니다! 목 스트레칭이 잘 되고 있습니다')
            elif tilt_amount > 0.06:
                feedback['messages'].append('✓ 조금 더 천천히 당겨보세요')
            else:
                feedback['has_warnings'] = True
                feedback['messages'].append('→ 머리를 오른쪽으로 더 기울이세요')
        elif nose_offset < -0.04:
            feedback['has_warnings'] = True
            feedback['messages'].append('⚠️ 반대 방향입니다. 오른쪽으로 기울이세요')
        else:
            feedback['has_warnings'] = True
            feedback['messages'].append('→ 머리를 오른쪽 어깨 방향으로 천천히 기울이세요')

        # 과도한 기울기 방지
        if left_ear and right_ear:
            ear_y_diff = right_ear['y'] - left_ear['y']
            if ear_y_diff > 0.25:
                feedback['has_warnings'] = True
                feedback['messages'].append('⚠️ 너무 많이 기울였습니다. 천천히 돌아오세요')

        if feedback['has_warnings']:
            feedback['status'] = 'warning'

    except Exception as e:
        feedback['status'] = 'warning'
        feedback['messages'].append(f'인식 오류: {str(e)}')

    return feedback


def feedback_shoulder_left(keypoints):
    """어깨 왼쪽 스트레칭 피드백"""
    feedback = {
        'status': 'good',
        'messages': [],
        'corrections': {},
        'angles': {},
        'has_warnings': False
    }

    try:
        left_shoulder = next((k for k in keypoints if k['name'] == 'left_shoulder'), None)
        right_shoulder = next((k for k in keypoints if k['name'] == 'right_shoulder'), None)
        left_elbow = next((k for k in keypoints if k['name'] == 'left_elbow'), None)
        right_elbow = next((k for k in keypoints if k['name'] == 'right_elbow'), None)
        left_wrist = next((k for k in keypoints if k['name'] == 'left_wrist'), None)

        if not all([left_shoulder, right_shoulder]):
            feedback['status'] = 'warning'
            feedback['messages'].append('어깨가 잘 보이지 않습니다')
            return feedback

        # 어깨 수평 체크
        shoulder_y_diff = abs(left_shoulder['y'] - right_shoulder['y'])
        if shoulder_y_diff > 0.15:
            feedback['has_warnings'] = True
            feedback['messages'].append('⚠️ 어깨를 수평으로 유지하세요')

        # 왼팔이 몸 앞으로 교차했는지 체크
        if left_wrist and right_shoulder:
            # 왼쪽 손목이 오른쪽 어깨 방향으로 이동
            wrist_cross = left_wrist['x'] - right_shoulder['x']
            if wrist_cross > -0.1:  # 충분히 교차
                feedback['messages'].append('✓ 좋습니다! 어깨 스트레칭이 잘 되고 있습니다')
            else:
                feedback['has_warnings'] = True
                feedback['messages'].append('→ 왼팔을 오른쪽으로 더 당겨보세요')

        if not feedback['messages']:
            feedback['messages'].append('→ 왼팔을 가슴 앞으로 교차시켜주세요')
            feedback['has_warnings'] = True

        if feedback['has_warnings']:
            feedback['status'] = 'warning'

    except Exception as e:
        feedback['status'] = 'warning'
        feedback['messages'].append(f'인식 오류: {str(e)}')

    return feedback


def feedback_shoulder_right(keypoints):
    """어깨 오른쪽 스트레칭 피드백"""
    feedback = {
        'status': 'good',
        'messages': [],
        'corrections': {},
        'angles': {},
        'has_warnings': False
    }

    try:
        left_shoulder = next((k for k in keypoints if k['name'] == 'left_shoulder'), None)
        right_shoulder = next((k for k in keypoints if k['name'] == 'right_shoulder'), None)
        right_elbow = next((k for k in keypoints if k['name'] == 'right_elbow'), None)
        right_wrist = next((k for k in keypoints if k['name'] == 'right_wrist'), None)

        if not all([left_shoulder, right_shoulder]):
            feedback['status'] = 'warning'
            feedback['messages'].append('어깨가 잘 보이지 않습니다')
            return feedback

        # 어깨 수평 체크
        shoulder_y_diff = abs(left_shoulder['y'] - right_shoulder['y'])
        if shoulder_y_diff > 0.15:
            feedback['has_warnings'] = True
            feedback['messages'].append('⚠️ 어깨를 수평으로 유지하세요')

        # 오른팔이 몸 앞으로 교차했는지 체크
        if right_wrist and left_shoulder:
            # 오른쪽 손목이 왼쪽 어깨 방향으로 이동
            wrist_cross = right_wrist['x'] - left_shoulder['x']
            if wrist_cross < 0.1:  # 충분히 교차
                feedback['messages'].append('✓ 좋습니다! 어깨 스트레칭이 잘 되고 있습니다')
            else:
                feedback['has_warnings'] = True
                feedback['messages'].append('→ 오른팔을 왼쪽으로 더 당겨보세요')

        if not feedback['messages']:
            feedback['messages'].append('→ 오른팔을 가슴 앞으로 교차시켜주세요')
            feedback['has_warnings'] = True

        if feedback['has_warnings']:
            feedback['status'] = 'warning'

    except Exception as e:
        feedback['status'] = 'warning'
        feedback['messages'].append(f'인식 오류: {str(e)}')

    return feedback


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workout_sessions(request):
    """사용자의 운동 세션 목록"""
    sessions = WorkoutSession.objects.filter(user=request.user)
    serializer = WorkoutSessionSerializer(sessions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sports_list(request):
    """Sports 목록 및 관련 비디오 조회"""
    sports = Sports.objects.all()
    serializer = SportsSerializer(sports, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_videos_list(request):
    """
    운동 영상 목록 조회 API
    필터링 옵션:
    - difficulty: 난이도 (초급, 중급, 고급, 자세교정)
    - body_part: 부위 (전신, 목, 어깨, 목어깨, 등, 골반, 코어)
    - exercise_type: 운동 종류 (스트레칭, 요가, 필라테스, 운동 등)
    - duration_min: 최소 시간(분)
    - duration_max: 최대 시간(분)
    """
    videos = EmotionVideo.objects.all()

    # 필터링
    difficulty = request.query_params.get('difficulty')
    if difficulty:
        videos = videos.filter(difficulty=difficulty)

    body_part = request.query_params.get('body_part')
    if body_part:
        videos = videos.filter(body_part=body_part)

    exercise_type = request.query_params.get('exercise_type')
    if exercise_type:
        videos = videos.filter(exercise_type=exercise_type)

    duration_min = request.query_params.get('duration_min')
    if duration_min:
        videos = videos.filter(duration_minutes__gte=int(duration_min))

    duration_max = request.query_params.get('duration_max')
    if duration_max:
        videos = videos.filter(duration_minutes__lte=int(duration_max))

    # 정렬
    ordering = request.query_params.get('ordering', 'difficulty')
    videos = videos.order_by(ordering)

    serializer = EmotionVideoSerializer(videos, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_detail(request, video_id):
    """특정 영상 상세 조회"""
    try:
        video = EmotionVideo.objects.get(id=video_id)
        serializer = EmotionVideoSerializer(video, context={'request': request})
        return Response(serializer.data)
    except EmotionVideo.DoesNotExist:
        return Response({'error': '영상을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)


# Create your views here.
