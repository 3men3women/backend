# 수정 테스트
# 개발브랜치 수정
# EmotionRecord 모델 설명
EmotionRecord 모델은 사용자의 일별 감정 기록을 저장하는 Django 모델입니다.
하루에 하나의 감정만 기록할 수 있으며, 감정 상태, 메모, 기록 일시 등을 포함합니다.
이 데이터는 달력(Calendar) UI와 연결되어 날짜별 감정 조회 및 월별 감정 패턴 분석에 활용됩니다.

1. 감정 기록
사용자별 날짜 단위 감정 기록 저장.
하루에 한 번만 기록 가능 (unique_together 제약).

2. 감정 메모
감정 상태 외에 자유롭게 메모 추가 가능.

3. 기록 관리
created_at, updated_at 필드로 생성 및 수정 시간 자동 기록.
ordering = ['-date'] → 최신 순으로 자동 정렬.

4. 헬퍼 메서드
__str__ : "username - 날짜 (감정)" 형태로 표시.
emotion_emoji : 감정의 이모지(😊)만 반환.
emotion_name : 감정의 한글 이름(행복)만 반환.
