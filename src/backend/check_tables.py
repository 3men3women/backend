#!/usr/bin/env python
"""데이터베이스 테이블 및 데이터 확인 스크립트"""
import os
import sys
import django

# Django 설정
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testemo.settings')
django.setup()

from django.db import connection

# 테이블 목록 조회
with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

print("=== 데이터베이스 테이블 목록 ===\n")
for table in tables:
    table_name = table[0]
    print(f"📋 {table_name}")

    # 각 테이블의 레코드 수 조회
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"   → {count}개의 레코드")

# EmotionVideo 테이블 상세 정보
print("\n\n=== emodia_emotionvideo 테이블 상세 ===\n")
with connection.cursor() as cursor:
    cursor.execute("DESCRIBE emodia_emotionvideo;")
    columns = cursor.fetchall()

    print("컬럼 구조:")
    for col in columns:
        print(f"  - {col[0]} ({col[1]})")

    # 데이터 샘플
    cursor.execute("SELECT id, difficulty, body_part, exercise_type, duration_minutes, original_filename FROM emodia_emotionvideo LIMIT 5;")
    rows = cursor.fetchall()

    print("\n샘플 데이터:")
    for row in rows:
        print(f"  ID {row[0]}: {row[1]} | {row[2]} | {row[3]} | {row[4]}분 | {row[5]}")
